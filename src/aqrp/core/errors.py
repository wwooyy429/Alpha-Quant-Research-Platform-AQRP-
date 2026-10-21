"""Structured errors compatible with contracts/1.0.0."""


class ContractError(ValueError):
    def __init__(self, code, field="", request_id="", retryable=False):
        self.code = code
        self.field = field
        self.request_id = request_id
        self.retryable = retryable
        super().__init__(f"{code}: {field}")


class TimestampResolutionError(ContractError):
    pass


class DataQualityError(ContractError):
    pass


class SnapshotMismatch(ContractError):
    pass


class TimeLeakageError(ContractError):
    pass


class UnsupportedCurrency(ContractError):
    pass
