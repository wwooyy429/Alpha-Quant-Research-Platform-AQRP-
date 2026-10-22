"""Read-only, opt-in NTFS inheritance proof. Never creates accounts or changes ACLs."""

import base64
import json
import os
import stat
import subprocess
from pathlib import Path

from aqrp.core.canonical import digest
from aqrp.core.errors import ContractError

OWNER_RIGHTS = "S-1-3-4"
SYSTEM = "S-1-5-18"
ADMINS = "S-1-5-32-544"
READ = 0x1200A9
MODIFY = 0x1301BF
FULL = 0x1F01FF
CHANGE_SECURITY = 0xC0000


def read_descriptors(paths):
    """Get numeric ACEs for exact paths, without following a PowerShell recursive walk."""
    script = r"""$ErrorActionPreference='Stop'; $ProgressPreference='SilentlyContinue'
[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new($false)
Import-Module (Join-Path $PSHOME 'Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1') -ErrorAction Stop
$paths=ConvertFrom-Json ([Console]::In.ReadToEnd())
$rows=@(foreach($p in $paths) {
  $a=Get-Acl -LiteralPath $p
  @{path=$p;owner=$a.GetOwner([System.Security.Principal.SecurityIdentifier]).Value;
    protected=$a.AreAccessRulesProtected;
    entries=@($a.GetAccessRules($true,$true,[System.Security.Principal.SecurityIdentifier]) |
      ForEach-Object { @{sid=$_.IdentityReference.Value;type=$_.AccessControlType.ToString();
        mask=[int]$_.FileSystemRights;inheritance=[int]$_.InheritanceFlags;
        propagation=[int]$_.PropagationFlags;inherited=$_.IsInherited} })}
}); ConvertTo-Json -InputObject $rows -Depth 6 -Compress
"""
    raw = subprocess.check_output(
        [
            "powershell",
            "-NoProfile",
            "-NonInteractive",
            "-EncodedCommand",
            base64.b64encode(script.encode("utf-16le")).decode(),
        ],
        input=json.dumps([str(p) for p in paths]).encode("utf-8"),
    )
    return json.loads(raw)


class WindowsTreePolicy:
    """Trusted operator configuration; not request JSON. Strict protected roots remain.

    Only explicitly listed, operator-owned protected directory anchors may admit
    inherited children. Every ACE is checked against a closed role ACL, then every
    inherited ACE must exactly match its immediate parent's projected ACEs. No
    opaque allow/deny order, creator substitution, propagation variants or generic
    rights are accepted. OWNER RIGHTS denies implicit owner WRITE_DAC/WRITE_OWNER.
    """

    def __init__(
        self,
        root,
        *,
        owner,
        evaluator,
        research,
        auditor,
        inherited_roots=(),
        readonly_roots=(),
        key_file=None,
    ):
        self.root = Path(root).absolute()
        self.owner, self.evaluator = str(owner), str(evaluator)
        self.research, self.auditor = str(research), str(auditor)
        self.inherited_roots = frozenset(Path(p).absolute() for p in inherited_roots)
        self.readonly_roots = frozenset(Path(p).absolute() for p in readonly_roots)
        self.key_file = None if key_file is None else Path(key_file).absolute()
        roles = {self.owner, self.evaluator, self.research, self.auditor}
        if len(roles) != 4 or roles & {OWNER_RIGHTS, SYSTEM, ADMINS} or any(not r for r in roles):
            raise ContractError("INVALID_WINDOWS_PRINCIPALS")
        if ".." in self.root.parts or any(
            ".." in p.parts or not p.is_relative_to(self.root)
            for p in self.inherited_roots | self.readonly_roots
        ):
            raise ContractError("ACL_ANCHOR_OUTSIDE_ROOT")
        if self.key_file is not None and not self.key_file.is_relative_to(self.root):
            raise ContractError("ACL_KEY_OUTSIDE_ROOT")

    def is_readonly(self, path):
        return any(path.is_relative_to(p) for p in self.readonly_roots)

    @property
    def binding(self):
        return digest(
            {
                "profile": "WI-NTFS-CHAIN-1",
                "root": str(self.root),
                "owner": self.owner,
                "evaluator": self.evaluator,
                "research": self.research,
                "auditor": self.auditor,
                "inherited_roots": sorted(map(str, self.inherited_roots)),
                "readonly_roots": sorted(map(str, self.readonly_roots)),
                "key_file": None if self.key_file is None else str(self.key_file),
            }
        )

    def _entries(self, row, directory, *, readonly, auditor=True):
        flags = 3 if directory else 0  # ContainerInherit | ObjectInherit, otherwise none.
        entries = row["entries"]
        if any(
            type(e[k]) is not int for e in entries for k in ("mask", "inheritance", "propagation")
        ):
            raise ContractError("INVALID_ACL_METADATA", row["path"])
        expected = {
            (self.owner, "Allow", FULL, flags, 0),
            (SYSTEM, "Allow", FULL, flags, 0),
            (ADMINS, "Allow", FULL, flags, 0),
            (self.evaluator, "Allow", READ if readonly else MODIFY, flags, 0),
            (OWNER_RIGHTS, "Deny", CHANGE_SECURITY, flags, 0),
        }
        if auditor:
            expected.add((self.auditor, "Allow", READ, flags, 0))
        values = [
            (e["sid"], e["type"], e["mask"], e["inheritance"], e["propagation"]) for e in entries
        ]
        if len(values) != len(expected) or set(values) != expected:
            raise ContractError("UNPROVEN_WINDOWS_EFFECTIVE_ACL", row["path"])
        return values

    def verify(self, *, key_file=None, readonly=False):
        key_file = self.key_file if key_file is None else key_file
        if os.name != "nt":
            raise ContractError("WINDOWS_NTFS_REQUIRED")
        for p in (self.root, *self.root.parents):
            if p.is_symlink() or p.is_junction():
                raise ContractError("SEALED_PATH_LINK", str(p))
        self.verify_ancestors(read_descriptors(list(self.root.parents)))
        paths = [self.root]
        for base, dirs, files in os.walk(self.root, followlinks=False):
            paths.extend(Path(base) / n for n in sorted(dirs + files))
        paths.sort(key=lambda p: (len(p.parts), str(p)))
        before = {}
        for p in paths:
            s = p.lstat()
            if p.is_symlink() or p.is_junction() or (p.is_file() and s.st_nlink != 1):
                raise ContractError("SEALED_PATH_LINK", str(p))
            if not (stat.S_ISDIR(s.st_mode) or stat.S_ISREG(s.st_mode)):
                raise ContractError("SEALED_NON_FILE_OBJECT", str(p))
            before[p] = (s.st_dev, s.st_ino, stat.S_IFMT(s.st_mode))
        rows = read_descriptors(paths)
        self.verify_rows(rows, {p: p.is_dir() for p in paths}, key_file=key_file, readonly=readonly)
        # Fail closed if objects/path membership changed during metadata capture.
        after_paths = {self.root}
        for base, dirs, files in os.walk(self.root, followlinks=False):
            after_paths.update(Path(base) / n for n in dirs + files)
        if after_paths != set(before):
            raise ContractError("ACL_TREE_CHANGED")
        for p, old in before.items():
            s = p.lstat()
            if (
                (s.st_dev, s.st_ino, stat.S_IFMT(s.st_mode)) != old
                or p.is_junction()
                or s.st_nlink > 1
                and p.is_file()
            ):
                raise ContractError("ACL_TREE_CHANGED", str(p))
        if read_descriptors(paths) != rows:
            raise ContractError("ACL_TREE_CHANGED")
        return {
            "profile": "WI-NTFS-CHAIN-1",
            "objects": len(rows),
            "scope": "ACL proof only; actual three-token probes required",
            "descriptors": rows,
        }

    def verify_rows(self, rows, directory, *, key_file=None, readonly=False):
        """Pure proof, exposed for counterexamples; never substitutes for OS probes."""
        key_file = self.key_file if key_file is None else key_file
        by_path = {Path(r["path"]): r for r in rows}
        if len(by_path) != len(rows) or set(by_path) != set(directory) or self.root not in by_path:
            raise ContractError("INCOMPLETE_ACL_TREE")
        anchors = self.inherited_roots | self.readonly_roots | {self.root}
        if not anchors <= set(by_path):
            raise ContractError("MISSING_ACL_ANCHOR")
        if key_file is not None and (key_file not in by_path or directory[key_file]):
            raise ContractError("MISSING_OR_INVALID_OPERATOR_KEY")
        for p in sorted(by_path, key=lambda x: (len(x.parts), str(x))):
            r = by_path[p]
            if not p.is_relative_to(self.root) or r["owner"] not in (self.owner, self.evaluator):
                raise ContractError("UNTRUSTED_ACL_OWNER_OR_PATH", str(p))
            if self.is_readonly(p) and r["owner"] != self.owner:
                raise ContractError("OPERATOR_PREBUILT_INPUT_REQUIRED", str(p))
            protected = r["protected"]
            if type(protected) is not bool or any(
                type(e["inherited"]) is not bool for e in r["entries"]
            ):
                raise ContractError("INVALID_ACL_METADATA", str(p))
            self._entries(
                r,
                directory[p],
                readonly=readonly or self.is_readonly(p) or p == key_file,
                auditor=p != key_file,
            )
            if protected:
                if r["owner"] != self.owner or any(e["inherited"] for e in r["entries"]):
                    raise ContractError("UNTRUSTED_PROTECTED_ANCHOR", str(p))
            else:
                if p in anchors or p == key_file or p.parent not in by_path:
                    raise ContractError("UNPROVEN_INHERITANCE_ANCHOR", str(p))
                if not any(
                    p != a and p.is_relative_to(a)
                    for a in self.inherited_roots | self.readonly_roots
                ):
                    raise ContractError("INHERITANCE_NOT_ENABLED", str(p))
                parent = by_path[p.parent]
                if not directory[p.parent] or not all(e["inherited"] for e in r["entries"]):
                    raise ContractError("UNPROVEN_INHERITED_ACE", str(p))
                projected = [
                    {**e, "inheritance": 3 if directory[p] else 0, "inherited": True}
                    for e in parent["entries"]
                ]
                fields = ("sid", "type", "mask", "inheritance", "propagation", "inherited")
                if sorted(tuple(e[k] for k in fields) for e in r["entries"]) != sorted(
                    tuple(e[k] for k in fields) for e in projected
                ):
                    raise ContractError("INHERITED_ACE_MISMATCH", str(p))
        return True

    def verify_ancestors(self, rows):
        if {Path(r["path"]) for r in rows} != set(self.root.parents) or len(rows) != len(
            self.root.parents
        ):
            raise ContractError("INCOMPLETE_ACL_ANCESTORS")
        trusted = {self.owner, SYSTEM, ADMINS}
        for r in rows:
            if r["owner"] not in trusted or any(
                e["type"] == "Allow"
                and e["sid"] not in trusted
                and e["mask"] & (CHANGE_SECURITY | 0x10040 | 0xF0000000)
                and not e["propagation"] & 2  # InheritOnly ACE does not apply here.
                for e in r["entries"]
            ):
                raise ContractError("UNTRUSTED_ACL_ANCESTOR", r["path"])
