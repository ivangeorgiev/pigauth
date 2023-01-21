"""Python Authorization Helper."""

from ._auth import (
    Resolver,
    Scheme,
    Role,
    Permission,
    GrantsMatcher,
    IMatcher,
    MatchContext,
)

__all__ = [
    "IMatcher",
    "GrantsMatcher",
    "MatchContext",
    "Permission",
    "Resolver",
    "Role",
    "Scheme",
]

__author__ = """Ivan Georgiev"""
__email__ = "ivan.georgiev@gmail.com"
__version__ = "0.1.0"
