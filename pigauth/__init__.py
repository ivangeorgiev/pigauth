"""Python Authorization Helper."""

from ._auth import (
    Resolver,
    Scheme,
    Role,
    Permission,
)
from ._matcher import MatchContext
from ._parser import PermissionGrantParser, PermissionGrantsParser

__all__ = [
    "MatchContext",
    "Permission",
    "PermissionGrantParser",
    "PermissionGrantsParser",
    "Resolver",
    "Role",
    "Scheme",
]

__author__ = """Ivan Georgiev"""
__email__ = "ivan.georgiev@gmail.com"
__version__ = "__version__ = '0.3.0'"
