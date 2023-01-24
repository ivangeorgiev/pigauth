from pigauth._auth import Scheme, Permission, Role, Resolver

class TestRole:
    def test_hash_should_return_role_id_hash(self):
        # Given
        role = Role('try.me')
        # When
        assert hash(role) == hash('try.me')

class TestScheme:
    def test_add_permission_should_add_permission_using_permission_id_as_key(self):
        # Given
        scheme = Scheme()
        permission = Permission('canteen.eat.fruit')
        # When
        scheme.add_permission(permission)
        # Then
        scheme.permissions['canteen.eat.fruit'] is permission

    def test_add_role_should_add_role_using_role_id_as_key(self):
        # Given
        scheme = Scheme()
        role = Role("CanteenUser", [])
        # When
        scheme.add_role(role)
        # Then
        scheme.roles['CanteenUser'] is role

class TestResolver:

    def test_resolve_roles_should_grant_passed_roles_and_default_role(self):
        # Given
        scheme = Scheme()
        default_role = Role("GuestUser", is_default=True)
        scheme.add_role(default_role)
        scheme.add_role(Role('Role1'))
        scheme.add_role(Role('Role2'))
        scheme.add_role(Role('OtherRole'))
        resolver = Resolver(scheme)
        # When
        actual_roles = resolver.resolve_roles(['Role1', 'Role2'])
        # Then
        assert sorted(list(actual_roles)) == sorted(['Role1', 'Role2', 'GuestUser'])

    def test_resolve_should_grant_passed_permissions_and_permissions_from_roles(self):
        # Given
        scheme = Scheme()
        scheme.add_role(Role('GuestUser', is_default=True, grants=['canteen.eat.*']))
        scheme.add_role(Role('Cook', grants=['canteen.cook.*']))
        resolver = Resolver(scheme)
        # When
        actual_grants = resolver.resolve(['canteen.read.menu'], ['Cook'])
        # Then
        assert sorted(actual_grants) == sorted(['canteen.eat.*', 'canteen.cook.*', 'canteen.read.menu'])
