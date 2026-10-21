"""Append-only engineering events and exact version selection, no financial approval."""

from dataclasses import dataclass
from enum import StrEnum

from aqrp.core.errors import ContractError

from .admission import validate_admission
from .contracts import FactorRef, FactorSpec, identifier
from .versions import compatible


@dataclass(frozen=True)
class PinnedFactor:
    spec: FactorSpec


class EngineeringState(StrEnum):
    ENGINEERING_APPROVED = "ENGINEERING_APPROVED"
    DISABLED = "DISABLED"
    EMERGENCY_STOP = "EMERGENCY_STOP"
    ROLLBACK_SELECTION = "ROLLBACK_SELECTION"


@dataclass(frozen=True)
class RegistryEvent:
    seq: int
    action: EngineeringState
    ref: FactorRef
    actor: str
    reason: str
    evidence: str


class FactorRegistry:
    def __init__(self):
        self._specs = {}
        self._disabled = set()
        self._stopped = set()
        self._events = []
        self._selection = None

    @property
    def events(self):
        return tuple(self._events)

    @property
    def selection(self):
        return self._selection

    def _event(self, action, ref, actor, reason, evidence):
        for value in (actor, reason, evidence):
            identifier(value, "registry_event")
        return RegistryEvent(
            len(self._events) + 1, EngineeringState(action), ref, actor, reason, evidence
        )

    def validate_compatibility(self, ref):
        if not isinstance(ref, FactorRef):
            raise ContractError("EXACT_FACTOR_REF_REQUIRED", "ref")
        spec = self._specs.get((ref.factor_id, ref.factor_version))
        if spec is None or spec.ref != ref:
            raise ContractError("UNKNOWN_FACTOR", "ref")
        if not compatible(spec.api_compatibility):
            raise ContractError("INCOMPATIBLE_FACTOR_API", "api_compatibility")
        validate_admission(spec)
        return spec

    def register(self, reviewed_artifact, spec, *, actor, reason, evidence):
        if not isinstance(spec, FactorSpec) or reviewed_artifact != spec.implementation_version:
            raise ContractError("UNAPPROVED_FACTOR_ARTIFACT", "register")
        event = self._event("ENGINEERING_APPROVED", spec.ref, actor, reason, evidence)
        key = (spec.factor_id, spec.factor_version)
        if key in self._specs:
            if self._specs[key] != spec:
                raise ContractError("FACTOR_VERSION_CONFLICT", "register")
            validate_admission(spec)
            return self._specs[key].ref
        validate_admission(spec)
        if not compatible(spec.api_compatibility):
            raise ContractError("INCOMPATIBLE_FACTOR_API", "api_compatibility")
        self._specs[key] = spec
        self._events.append(event)
        return spec.ref

    def resolve(self, ref):
        spec = self.validate_compatibility(ref)
        if ref in self._disabled:
            raise ContractError("FACTOR_DISABLED", "resolve")
        return PinnedFactor(spec)

    def deactivate(self, ref, *, actor, reason, evidence, emergency=False):
        if type(emergency) is not bool:
            raise ContractError("INVALID_EMERGENCY_FLAG", "emergency")
        self.validate_compatibility(ref)
        event = self._event(
            "EMERGENCY_STOP" if emergency else "DISABLED", ref, actor, reason, evidence
        )
        self._disabled.add(ref)
        if emergency:
            self._stopped.add(ref)
        self._events.append(event)

    def rollback(self, approved_ref, *, actor, reason, evidence):
        spec = self.validate_compatibility(approved_ref)
        event = self._event("ROLLBACK_SELECTION", approved_ref, actor, reason, evidence)
        if approved_ref in self._stopped:
            raise ContractError("EMERGENCY_STOPPED", "rollback")
        self._disabled.discard(approved_ref)
        self._selection = approved_ref
        self._events.append(event)
        return PinnedFactor(spec)

    def check_pin(self, pin):
        if (
            not isinstance(pin, PinnedFactor)
            or self.validate_compatibility(pin.spec.ref) != pin.spec
        ):
            raise ContractError("INVALID_FACTOR_PIN", "pin")
        if pin.spec.ref in self._stopped:
            raise ContractError("EMERGENCY_STOPPED", "pin")
        return pin.spec
