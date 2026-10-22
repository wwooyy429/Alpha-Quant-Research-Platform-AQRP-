"""Sealed evaluator runtime. No account/ACL/service/scheduler deployment operations."""

import csv
import hashlib
import hmac
import io
import json
import os
import stat
import subprocess
import uuid
from pathlib import Path

from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.experiments.ledger import append_chain, immutable_write, mutex, read_chain

IS_WINDOWS = os.name == "nt"


def seal(payload, key):
    if len(key) < 32:
        raise ContractError("INVALID_OPERATOR_KEY")
    return {
        "payload": payload,
        "mac": hmac.new(key, canonical(payload), hashlib.sha256).hexdigest(),
    }


def verify_seal(envelope, key):
    expected = seal(envelope["payload"], key)["mac"]
    if not hmac.compare_digest(expected, envelope["mac"]):
        raise ContractError("OPERATOR_SEAL_MISMATCH")
    return envelope["payload"]


def identity():
    if IS_WINDOWS:
        raw = subprocess.check_output(["whoami", "/user", "/fo", "csv", "/nh"], text=True)
        return next(csv.reader(io.StringIO(raw.strip())))[1]
    return str(os.geteuid())


def _windows_permissions(path, allowed, research, *, readonly=False, auditor=None):
    import base64

    literal = str(path).replace("'", "''")
    script = f"$a=Get-Acl -LiteralPath '{literal}'; $w=[System.Security.AccessControl.FileSystemRights]::Write -bor [System.Security.AccessControl.FileSystemRights]::Delete -bor [System.Security.AccessControl.FileSystemRights]::ChangePermissions -bor [System.Security.AccessControl.FileSystemRights]::TakeOwnership -bor [System.Security.AccessControl.FileSystemRights]::DeleteSubdirectoriesAndFiles; @{{owner=$a.GetOwner([System.Security.Principal.SecurityIdentifier]).Value; protected=$a.AreAccessRulesProtected; entries=@($a.Access | ForEach-Object {{ @{{sid=$_.IdentityReference.Translate([System.Security.Principal.SecurityIdentifier]).Value; type=$_.AccessControlType.ToString(); writable=([int]$_.FileSystemRights -band [int]$w) -ne 0}} }})}} | ConvertTo-Json -Depth 5 -Compress"
    data = json.loads(
        subprocess.check_output(
            [
                "powershell",
                "-NoProfile",
                "-NonInteractive",
                "-EncodedCommand",
                base64.b64encode(script.encode("utf-16le")).decode(),
            ],
            text=True,
        )
    )
    if not data["protected"] or any(
        e["type"] == "Allow" and (e["sid"] not in allowed or e["sid"] == research)
        for e in data["entries"]
    ):
        raise ContractError("UNVERIFIED_ISOLATION")
    if auditor is not None and any(
        e["type"] == "Allow" and e["sid"] == auditor and e["writable"] for e in data["entries"]
    ):
        raise ContractError("WRITABLE_AUDITOR_DOMAIN")
    if readonly and any(
        e["type"] == "Allow"
        and e["sid"] not in (data["owner"], "S-1-5-18", "S-1-5-32-544")
        and e["writable"]
        for e in data["entries"]
    ):
        raise ContractError("WRITABLE_EVALUATOR_RUNTIME")
    return data["owner"]


def readonly_runtime(path, owner, allowed, research):
    if IS_WINDOWS:
        actual_owner = _windows_permissions(path, allowed, research, readonly=True)
        valid = actual_owner == owner
    else:
        s = path.stat()
        valid = str(s.st_uid) == owner and not stat.S_IMODE(s.st_mode) & 0o022
    if not valid:
        raise ContractError("UNTRUSTED_RUNTIME_OWNER_OR_WRITE_MODE")


class OperatorPolicy:
    """Constructed by the trusted operator, never deserialized from a research request."""

    def __init__(
        self,
        root,
        key_file,
        *,
        evaluator,
        research,
        auditor,
        trusted_owner,
        allowed_group_ids=(),
        windows_tree_policy=None,
    ):
        for raw in (Path(root).absolute(), Path(key_file).absolute()):
            if any(p.is_symlink() or p.is_junction() for p in (raw, *raw.parents)):
                raise ContractError("SEALED_PATH_LINK")
        self.root = Path(root).resolve(strict=True)
        self.key_file = Path(key_file).resolve(strict=True)
        self.evaluator = str(evaluator)
        self.research = str(research)
        self.auditor = str(auditor)
        self.owner = str(trusted_owner)
        self.groups = set(allowed_group_ids)
        self.windows_tree_policy = windows_tree_policy
        if windows_tree_policy is not None:
            from .windows_acl import WindowsTreePolicy

            if not isinstance(windows_tree_policy, WindowsTreePolicy) or (
                windows_tree_policy.root != self.root
                or windows_tree_policy.owner != self.owner
                or windows_tree_policy.evaluator != self.evaluator
                or windows_tree_policy.research != self.research
                or windows_tree_policy.auditor != self.auditor
                or windows_tree_policy.key_file != self.key_file
            ):
                raise ContractError("WINDOWS_TREE_POLICY_BINDING_MISMATCH")

    @property
    def principals(self):
        return {
            "evaluator": self.evaluator,
            "research": self.research,
            "auditor": self.auditor,
            "trusted_owner": self.owner,
        }

    def verify_host(self):
        if (
            identity() != self.evaluator
            or len(set(self.principals.values())) != 4
            or any(not v for v in self.principals.values())
        ):
            raise ContractError("WRONG_EVALUATOR_PRINCIPAL")
        if IS_WINDOWS:
            groups = subprocess.check_output(["whoami", "/groups", "/fo", "csv", "/nh"], text=True)
            privileges = subprocess.check_output(
                ["whoami", "/priv", "/fo", "csv", "/nh"], text=True
            )
            if any(sid in groups for sid in ("S-1-5-32-544", "S-1-5-32-551")) or any(
                name in privileges
                for name in (
                    "SeDebugPrivilege",
                    "SeBackupPrivilege",
                    "SeRestorePrivilege",
                    "SeTcbPrivilege",
                    "SeImpersonatePrivilege",
                )
            ):
                raise ContractError("ELEVATED_EVALUATOR_TOKEN")
        else:
            import pwd

            researcher = pwd.getpwuid(int(self.research))
            audit_user = pwd.getpwuid(int(self.auditor))
            auditor_groups = set(os.getgrouplist(audit_user.pw_name, audit_user.pw_gid))
            research_groups = set(os.getgrouplist(researcher.pw_name, researcher.pw_gid))
            if (
                os.geteuid() == 0
                or self.research == "0"
                or self.auditor == "0"
                or research_groups & self.groups
            ):
                raise ContractError("SHARED_OR_ELEVATED_PRINCIPAL")
        if IS_WINDOWS and self.windows_tree_policy is not None:
            self.windows_tree_policy.verify(key_file=self.key_file)
            return self.key_file.read_bytes()
        allowed = {self.owner, self.evaluator, self.auditor, "S-1-5-18", "S-1-5-32-544"}
        for path in [self.root, self.key_file, *self.root.rglob("*")]:
            if (
                path.is_symlink()
                or path.is_junction()
                or (path.is_file() and path.stat().st_nlink != 1)
            ):
                raise ContractError("SEALED_PATH_LINK")
            if IS_WINDOWS:
                owner = _windows_permissions(
                    path,
                    allowed - ({self.auditor} if path == self.key_file else set()),
                    self.research,
                    auditor=self.auditor,
                )
                if path in (self.root, self.key_file) and owner != self.owner:
                    raise ContractError("UNTRUSTED_OPERATOR_KEY_OWNER")
            else:
                s = path.stat()
                if any(
                    name in ("system.posix_acl_access", "system.posix_acl_default")
                    for name in os.listxattr(path)
                ):
                    raise ContractError("UNVERIFIED_EXTENDED_ACL")
                if (
                    path == self.key_file
                    and stat.S_IMODE(s.st_mode) & 0o040
                    and s.st_gid in auditor_groups
                ):
                    raise ContractError("OPERATOR_KEY_SHARED_WITH_AUDITOR")
                if (
                    str(s.st_uid) not in (self.owner, self.evaluator)
                    or stat.S_IMODE(s.st_mode) & 0o027
                    or (s.st_gid not in self.groups and stat.S_IMODE(s.st_mode) & 0o070)
                ):
                    raise ContractError("UNVERIFIED_ISOLATION")
        # Root/operator key must not be owned by evaluator or researcher.
        if not IS_WINDOWS and any(
            str(p.stat().st_uid) != self.owner for p in (self.root, self.key_file)
        ):
            raise ContractError("UNTRUSTED_OPERATOR_KEY_OWNER")
        return self.key_file.read_bytes()

    def authorize(self, bindings):
        key = self.verify_host()
        claims = verify_seal(json.loads((self.root / "authorization.json").read_bytes()), key)
        if (
            self.windows_tree_policy is not None
            and claims.get("windows_acl_policy_binding") != self.windows_tree_policy.binding
        ):
            raise ContractError("WINDOWS_ACL_PROFILE_NOT_AUTHORIZED")
        if (
            claims["bindings"] != bindings
            or claims.get("principals") != self.principals
            or claims["scope"] != "FINAL_TEST"
            or claims["profile"] != "P3-ISO-OS-1"
            or not claims["human_approval_record"]
        ):
            raise ContractError("FINAL_TEST_NOT_AUTHORIZED")
        required = {
            "dual_principal_negative_controls",
            "private_seed_and_backups",
            "runtime_readonly",
            "network_and_credentials",
            "auditor_access",
        }
        if not required <= set(claims.get("deployment_evidence", {})) or not claims.get(
            "runtime_artifacts"
        ):
            raise ContractError("DEPLOYMENT_EVIDENCE_INCOMPLETE")
        for row in [*claims["deployment_evidence"].values(), *claims["runtime_artifacts"]]:
            p = self.root / row["path"]
            if (
                p.is_symlink()
                or not p.resolve().is_relative_to(self.root)
                or hashlib.sha256(p.read_bytes()).hexdigest() != row["sha256"]
            ):
                raise ContractError("DEPLOYMENT_ARTIFACT_MISMATCH")
        for row in claims["runtime_artifacts"]:
            readonly_runtime(
                self.root / row["path"],
                self.owner,
                {self.owner, self.evaluator, self.auditor, "S-1-5-18", "S-1-5-32-544"},
                self.research,
            )
        return claims


class TestEvaluator:
    __test__ = False

    def __init__(self, control_root, policy=None):
        self.root = Path(control_root)
        self.policy = policy

    def process(self, bindings, evaluate, *, purpose):
        if purpose not in ("FINAL_TEST", "ENGINEERING_DEMO"):
            raise ContractError("INVALID_TEST_PURPOSE")
        if purpose == "FINAL_TEST":
            if self.policy is None:
                raise ContractError("UNVERIFIED_ISOLATION")
            claims = self.policy.authorize(bindings)
            if not self.root.resolve().is_relative_to(self.policy.root):
                raise ContractError("CONTROL_OUTSIDE_SEALED_ROOT")
            test_id = claims["holdout_lineage_id"]
        else:
            if self.policy is not None:
                raise ContractError("ENGINEERING_DEMO_CANNOT_USE_SEALED_POLICY")
            test_id = bindings["holdout_lineage_id"]
        self.root.mkdir(parents=True, exist_ok=True)
        request_id = str(uuid.uuid4())
        control = self.policy.root / "control" if purpose == "FINAL_TEST" else self.root
        control.mkdir(parents=True, exist_ok=True)
        chain = control / "access.jsonl"
        with mutex(control / ".lock"):
            records = read_chain(chain)
            # A crash after RESERVED always consumes the true holdout identity.
            if any(r["kind"] == "RESERVED" and r["payload"]["test_id"] == test_id for r in records):
                append_chain(
                    chain, "REJECTED_REPEAT", {"test_id": test_id, "request_id": request_id}
                )
                raise ContractError("TEST_ALREADY_CONSUMED_OR_CONTAMINATED")
            append_chain(
                chain,
                "RESERVED",
                {
                    "test_id": test_id,
                    "request_id": request_id,
                    "bindings_hash": digest(bindings),
                    "purpose": purpose,
                },
            )
        try:
            result = evaluate()
            immutable_write(self.root / (request_id + ".json"), canonical(result))
            status = "SUCCEEDED"
        except BaseException as exc:
            immutable_write(
                self.root / (request_id + "-failure.json"),
                canonical({"status": "FAILED_CONSUMED", "error_type": type(exc).__name__}),
            )
            with mutex(control / ".lock"):
                append_chain(
                    chain, "FAILED_CONSUMED", {"test_id": test_id, "request_id": request_id}
                )
            if purpose == "FINAL_TEST":
                return {
                    "request_id": request_id,
                    "status": "CONSUMED",
                    "purpose": purpose,
                    "independence_verified": True,
                }
            raise
        with mutex(control / ".lock"):
            append_chain(chain, status, {"test_id": test_id, "request_id": request_id})
        # The developer receives no Test labels, feedback, statistics or private paths.
        return {
            "request_id": request_id,
            "status": "CONSUMED" if purpose == "FINAL_TEST" else "COMPLETED",
            "purpose": purpose,
            "independence_verified": purpose == "FINAL_TEST",
        }

    def recover(self):
        if self.policy is not None:
            self.policy.verify_host()
        control = self.policy.root / "control" if self.policy is not None else self.root
        with mutex(control / ".lock"):
            rows = read_chain(control / "access.jsonl")
            done = {
                r["payload"]["request_id"]
                for r in rows
                if r["kind"] in ("SUCCEEDED", "FAILED_CONSUMED")
            }
            pending = [
                r
                for r in rows
                if r["kind"] == "RESERVED" and r["payload"]["request_id"] not in done
            ]
            for r in pending:
                append_chain(control / "access.jsonl", "FAILED_CONSUMED", r["payload"])
            return len(pending)
