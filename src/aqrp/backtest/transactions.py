"""One durable immutable commit contains every Fill/Journal/account/capacity update."""

import hashlib
import os
import re
import uuid
from copy import deepcopy
from pathlib import Path

from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.experiments.ledger import immutable_write, mutex
from aqrp.portfolio.contracts import load

from .exact import freeze, thaw


def guard_path(path):
    path = Path(path).absolute()
    for p in (path, *path.parents):
        if p.is_symlink() or p.is_junction() or (p.is_file() and p.stat().st_nlink > 1):
            raise ContractError("SIMULATION_LINK_PATH_FORBIDDEN")
    return path


class TransactionStore:
    """Single writer, fail-closed recovery; uncommitted preparations never consume state."""

    def __init__(self, root, initial=None):
        self.root = guard_path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        with mutex(self.root / ".lock"):
            path = self.root / "initial.json"
            if not path.exists():
                if initial is None:
                    raise ContractError("TRANSACTION_INITIAL_STATE_MISSING")
                immutable_write(path, canonical(freeze(initial)))
            elif initial is not None and path.read_bytes() != canonical(freeze(initial)):
                raise ContractError("TRANSACTION_INITIAL_STATE_CONFLICT")
        self.recover()

    def recover(self):
        raw = guard_path(self.root / "initial.json").read_bytes()
        state = load(raw)
        if canonical(state) != raw:
            raise ContractError("TRANSACTION_NONCANONICAL_INITIAL")
        self.initial = thaw(state)
        self.initial_hash = hashlib.sha256(raw).hexdigest()
        self.records = []
        self.commands = {}
        previous = self.initial_hash
        paths = sorted(self.root.iterdir())
        for path in paths:
            guard_path(path)
            if path.name.startswith("commit-"):
                if not re.fullmatch(r"commit-\d{12}\.json", path.name) or not path.is_file():
                    raise ContractError("TRANSACTION_UNEXPECTED_COMMIT_FILE")
                item = load(path.read_bytes())
                seq = len(self.records) + 1
                body = {k: v for k, v in item.items() if k != "sha256"}
                if (
                    path.name != f"commit-{seq:012d}.json"
                    or item["commit_seq"] != seq
                    or item["previous"] != previous
                    or digest(body) != item["sha256"]
                    or item["pre_hash"] != digest(state)
                    or item["post_hash"] != digest(item["post_state"])
                    or item["command_id"] in self.commands
                    or canonical(item) != path.read_bytes()
                ):
                    raise ContractError("TRANSACTION_CHAIN_CORRUPTED")
                self.commands[item["command_id"]] = item
                self.records.append(item)
                state = item["post_state"]
                previous = item["sha256"]
        self.state = thaw(state)
        return deepcopy(self.state)

    def commit(self, command_id, payload, dispatch_key, transition, *, fault=None):
        """fault is a developer injection callback; never a permission/approval bypass."""
        uuid.UUID(command_id)
        with mutex(self.root / ".lock"):
            self.recover()
            payload_hash = digest(freeze(payload))
            if command_id in self.commands:
                prior = self.commands[command_id]
                if prior["payload_hash"] != payload_hash or prior["dispatch_key"] != dispatch_key:
                    raise ContractError("TRANSACTION_IDEMPOTENCY_CONFLICT")
                return prior
            post = deepcopy(self.state)
            records = transition(post)
            seq = len(self.records) + 1
            item = {
                "schema_version": "simulation-transaction/1.0.0",
                "commit_seq": seq,
                "previous": self.records[-1]["sha256"] if self.records else self.initial_hash,
                "command_id": command_id,
                "payload_hash": payload_hash,
                "payload": freeze(payload),
                "dispatch_key": dispatch_key,
                "pre_version": seq - 1,
                "post_version": seq,
                "pre_hash": digest(freeze(self.state)),
                "post_hash": digest(freeze(post)),
                "children": [{"child_seq": i, **freeze(v)} for i, v in enumerate(records)],
                "post_state": freeze(post),
            }
            item["sha256"] = digest(item)
            temp = self.root / ("prepared-" + str(uuid.uuid4()) + ".json")
            immutable_write(temp, canonical(item))
            if fault:
                fault("BEFORE_COMMIT")
            os.replace(temp, self.root / f"commit-{seq:012d}.json")
            if os.name != "nt":
                fd = os.open(self.root, os.O_RDONLY)
                try:
                    os.fsync(fd)
                finally:
                    os.close(fd)
            if fault:
                fault("AFTER_COMMIT")
            self.recover()
            return item
