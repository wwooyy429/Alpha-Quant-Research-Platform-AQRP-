"""Supplemental static guard only. Not an operating-system sandbox."""

import ast

from aqrp.core.errors import ContractError

FORBIDDEN = {
    "open",
    "eval",
    "exec",
    "compile",
    "__import__",
    "getattr",
    "setattr",
    "globals",
    "locals",
    "os",
    "sys",
    "subprocess",
    "socket",
    "shutil",
    "importlib",
    "ctypes",
    "pickle",
}
ALLOWED_IMPORTS = {"fractions", "aqrp.factors.contracts", "aqrp.factors.input"}


def static_guard(source):
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise ContractError("INVALID_PLUGIN_SYNTAX", "source") from exc
    for node in ast.walk(tree):
        if isinstance(node, (ast.Global, ast.Nonlocal)):
            raise ContractError("UNSAFE_PLUGIN_SYNTAX", type(node).__name__)
        if isinstance(node, ast.Import) or (
            isinstance(node, ast.ImportFrom) and (node.level or node.module not in ALLOWED_IMPORTS)
        ):
            raise ContractError("UNSAFE_PLUGIN_IMPORT", "source")
        if isinstance(node, ast.Name) and node.id in FORBIDDEN:
            raise ContractError("UNSAFE_PLUGIN_NAME", node.id)
        if isinstance(node, ast.Attribute) and (
            node.attr in FORBIDDEN or node.attr.startswith("__")
        ):
            raise ContractError("UNSAFE_PLUGIN_ATTRIBUTE", node.attr)
    return "STATIC_GUARD_PASS_NOT_OS_SANDBOX"
