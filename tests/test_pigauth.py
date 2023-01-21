from pigauth import Permission

class TestPermission:
    def test_new_should_create_instance_with_empty_requires(self):
        permission = Permission('eat.food')
        assert not permission.requires
