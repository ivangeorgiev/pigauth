"""

Synopsis
---------

```python

scheme = (
    Scheme()
    .add_permission(Permission("canteen.eat.fruit"))
    .add_permission(Permission("canteen.eat.meat"))
    .add_permission(Permission("canteen.eat.seafood", requires=["preview"]))
    .add_permission(Permission("canteen.eat.pasta", requires=["preview"]))
    .add_permission(Permission("canteen.cook.soup"))
    .add_role(Role("Cook", ["canteen.cook.*"]))
    .add_role(Role("Eater", ["canteen.eat.*"], is_default=True))
    .add_role(Role("Owner", ["*.eat.*|preview"]))
)

print(scheme.permissions)
print(scheme.roles)

resolver = Resolver(scheme)

grants = resolver.resolve(["canteen.eat.pasta|preview"], ["Cook"])
print(grants)

matcher = GrantsMatcher(grants)
print("Allowed canteen.eat.meat: ", matcher.matches(Permission("canteen.eat.meat")))
print(
    "Allowed canteen.eat.seafood: ",
    matcher.matches(Permission("canteen.eat.seafood", requires=["preview"])),
)
print(
    "Allowed canteen.eat.pasta: ",
    matcher.matches(Permission("canteen.eat.pasta", requires=["preview"])),
)

import json

print(json.dumps(dataclasses.asdict(scheme)))

```

"""

import abc
import dataclasses
import re
from types import SimpleNamespace
from typing import Iterable, List, Dict

PermissionId = str


@dataclasses.dataclass(frozen=True)
class Permission:
    permission_id: PermissionId
    requires: list = dataclasses.field(default_factory=list)


Permissions = List[Permission]
PermissionMap = Dict[PermissionId, Permission]

Grant = str
Grants = Iterable[Grant]

RoleId = str


@dataclasses.dataclass(frozen=True)
class Role:
    """Describe authorization role"""

    role_id: RoleId
    grants: Grants = dataclasses.field(default_factory=list)
    is_default: bool = False

    def __hash__(self) -> int:
        return hash(self.role_id)


Roles = List[Role]
RoleMap = Dict[RoleId, Role]
RoleGrants = Iterable[RoleId]


@dataclasses.dataclass(frozen=True)
class Scheme:
    """Describe authorization scheme"""

    roles: RoleMap = dataclasses.field(default_factory=dict)
    permissions: PermissionMap = dataclasses.field(default_factory=dict)

    def add_permission(self, permission: Permission):
        self.permissions[permission.permission_id] = permission
        return self

    def add_role(self, role: Role):
        self.roles[role.role_id] = role
        return self


class Resolver:
    scheme: Scheme

    def __init__(self, scheme: Scheme):
        self.scheme = scheme

    def resolve(self, permission_grants: Grants, role_grants: RoleGrants) -> Grants:
        """Resolve effective permits from given authorization scheme"""
        effective_grants = set(permission_grants)
        for role_id in self.resolve_roles(role_grants):
            effective_grants.update(self.scheme.roles[role_id].grants)
        return effective_grants

    def resolve_roles(self, role_grants: RoleGrants) -> RoleGrants:
        effective_grants = set(role_grants)
        for role in self.scheme.roles.values():
            if role.is_default:
                effective_grants.add(role.role_id)
        return effective_grants


class MatchContext(SimpleNamespace):
    pass


class IMatcher:
    modifier: str

    @abc.abstractmethod
    def matches(self, permission: Permission, context: MatchContext) -> bool:
        """Match permission"""


class RequiresMatcher(IMatcher):
    def __init__(self, modifiers: Iterable[str]):
        self.modifiers = list(modifiers)

    def matches(self, permission: Permission, context: MatchContext) -> bool:
        for required in permission.requires:
            if required not in self.modifiers:
                return False
        return True


class RegexMatcher(IMatcher):
    def __init__(self, regex):
        self.regex = regex

    def matches(self, permission: Permission, context: MatchContext) -> bool:
        return bool(self.regex.fullmatch(permission.permission_id))


class AllMatcher(IMatcher):
    def __init__(self, matchers: Iterable[IMatcher]) -> None:
        self.matchers = matchers

    def matches(self, permission: Permission, context: MatchContext) -> bool:
        for matcher in self.matchers:
            if not matcher.matches(permission, context):
                return False
        return True


class GrantParser:
    def parse(self, grant: Grant) -> IMatcher:
        expression, _, modifiers_str = grant.partition("|")
        modifiers = modifiers_str.split(",") if modifiers_str else []
        matchers = []
        matchers.append(self._get_expression_matcher(expression))
        matchers.append(self._get_requires_matcher(modifiers))
        for modifier in modifiers:
            matcher = self._get_matcher_for_modifier(modifier)
            if matcher:
                matchers.append(matcher)
        return AllMatcher(matchers)

    def _get_expression_matcher(self, expression: str):
        regex = re.compile(expression.replace(".", "\\.").replace("*", ".*"))
        return RegexMatcher(regex)

    def _get_requires_matcher(self, modifiers: Iterable[str]):
        return RequiresMatcher(modifiers)

    def _get_matcher_for_modifier(self, modifier: str):
        for klass in IMatcher.__subclasses__():
            if getattr(klass, "modifier", None) == modifier:
                return klass()
        return None


class GrantsMatcher(IMatcher):
    matchers: List[IMatcher]

    def __init__(self, grants: Grants):
        self.matchers = self._parse_grants(grants)

    def _parse_grants(self, grants: Grants):
        grant_parser = GrantParser()
        matchers = [grant_parser.parse(grant) for grant in grants]
        return matchers

    def matches(self, permission: Permission, context: MatchContext) -> bool:
        for matcher in self.matchers:
            if matcher.matches(permission, context):
                return True
        return False
