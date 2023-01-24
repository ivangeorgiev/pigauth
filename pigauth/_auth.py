import dataclasses
from typing import Iterable, List, Dict

PermissionId = str


@dataclasses.dataclass(frozen=True)
class Permission:
    """Describe permission"""

    permission_id: PermissionId
    requires: list = dataclasses.field(default_factory=list)


Permissions = List[Permission]
PermissionMap = Dict[PermissionId, Permission]

PermissionGrant = str
PermissionGrants = Iterable[PermissionGrant]

RoleId = str


@dataclasses.dataclass(frozen=True)
class Role:
    """Describe authorization role"""

    role_id: RoleId
    grants: PermissionGrants = dataclasses.field(default_factory=list)
    is_default: bool = False

    def __hash__(self) -> int:
        """Implementing proper hash function makes the Role instances hashable.

        For example, Role instances can be used as dictionary indexes or in sets.
        """
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
    """Resolve effective grants against authorization scheme"""

    scheme: Scheme

    def __init__(self, scheme: Scheme):
        self.scheme = scheme

    def resolve(
        self, permission_grants: PermissionGrants, role_grants: RoleGrants
    ) -> PermissionGrants:
        """Resolve effective permission grants"""
        effective_grants = set(permission_grants)
        for role_id in self.resolve_roles(role_grants):
            effective_grants.update(self.scheme.roles[role_id].grants)
        return effective_grants

    def resolve_roles(self, role_grants: RoleGrants) -> RoleGrants:
        """Resolve effective role grants"""
        effective_grants = set(role_grants)
        for role in self.scheme.roles.values():
            if role.is_default:
                effective_grants.add(role.role_id)
        return effective_grants
