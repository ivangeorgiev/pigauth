import abc
from types import SimpleNamespace
from typing import Iterable

from ._auth import Permission


class MatchContext(SimpleNamespace):
    """MatchContext is passed to matchers"""
    pass


class PermissionMatcher:
    """Abstract PermissionMatcher"""
    for_modifier: str

    @abc.abstractmethod
    def matches(self, permission: Permission, context: MatchContext) -> bool:
        """Match permission"""


class RequiresMatcher(PermissionMatcher):
    """Matches modifiers required by permission against supplied modifiers"""
    def __init__(self, modifier_names: Iterable[str]):
        self.modifier_names = list(modifier_names)

    def matches(self, permission: Permission, context: MatchContext) -> bool:
        return all(
            [
                required_modifier in self.modifier_names
                for required_modifier in permission.requires
            ]
        )


class RegexMatcher(PermissionMatcher):
    """Matches permission ID against regular expression pattern"""
    def __init__(self, regex):
        self.regex = regex

    def matches(self, permission: Permission, context: MatchContext) -> bool:
        return bool(self.regex.fullmatch(permission.permission_id))


class AnyMatcher(PermissionMatcher):
    """Matches if any of the supplied matchers matches"""
    def __init__(self, matchers: Iterable[PermissionMatcher]) -> None:
        self.matchers = list(matchers)

    def matches(self, permission: Permission, context: MatchContext) -> bool:
        return any([matcher.matches(permission, context) for matcher in self.matchers])


class AllMatcher(PermissionMatcher):
    """Matches if all of the supplied matchers match"""
    def __init__(self, matchers: Iterable[PermissionMatcher]) -> None:
        self.matchers = list(matchers)

    def matches(self, permission: Permission, context: MatchContext) -> bool:
        return all([matcher.matches(permission, context) for matcher in self.matchers])


class ModifierMatcherFactory:
    """Create PermissionMatcher instance for modifier name"""
    MODIFIER_ATTR_NAME = "for_modifier"

    def __call__(self, modifier_name: str):
        for klass in PermissionMatcher.__subclasses__():
            if getattr(klass, self.MODIFIER_ATTR_NAME, None) == modifier_name:
                return klass()
        return None
