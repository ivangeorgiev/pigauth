import re
from unittest.mock import Mock
from pigauth._auth import Permission
from pigauth._matcher import ModifierMatcherFactory, PermissionMatcher, RequiresMatcher, RegexMatcher, MatchContext, AnyMatcher, AllMatcher

class DummyModifierMatcher(PermissionMatcher):
    for_modifier = 'I-Am-Bilbo'

class TestModifierMatcherFactory:
    def test_call_should_return_None_modifier_not_registered(self):
        # Given
        factory = ModifierMatcherFactory()
        # When
        matcher = factory("I-Am-Smeagol")
        # Then
        assert not matcher

    def test_call_should_return_instance_registered_modifier(self):
        # Given
        factory = ModifierMatcherFactory()
        # When
        matcher = factory("I-Am-Bilbo")
        # Then
        assert isinstance(matcher, DummyModifierMatcher)


class TestRequiresMatcher:
    def test_matches_should_return_True_requierd_modifier_present(self):
        # Given
        permission = Permission('water.drink', ['lemon'])
        matcher = RequiresMatcher(['lemon'])
        context = MatchContext()
        # When
        assert matcher.matches(permission, context)

    def test_matches_should_return_False_requierd_modifier_present(self):
        # Given
        permission = Permission('water.drink', ['lemon'])
        matcher = RequiresMatcher(['peper'])
        context = MatchContext()
        # When
        assert not matcher.matches(permission, context)

class TestRegexMatcher:
    def test_matches_should_return_True_permission_id_matches(self):
        # Given
        permission = Permission('water.drink')
        matcher = RegexMatcher(re.compile('water.*'))
        context = MatchContext()
        # When
        assert matcher.matches(permission, context)

    def test_matches_should_return_False_permission_id_doesnt_match(self):
        # Given
        permission = Permission('wasserer.drink')
        matcher = RegexMatcher(re.compile('water.*'))
        context = MatchContext()
        # When
        assert not matcher.matches(permission, context)


class TestAnyMatcher:
    def test_matches_should_return_True_any_matcher_returns_True(self):
        # Given
        permission = Permission('wasserer.drink')
        true_matcher = Mock()
        true_matcher.matches.return_value = True
        false_matcher = Mock()
        false_matcher.matches.return_value = False
        matcher = AnyMatcher([false_matcher, true_matcher, false_matcher])
        context = MatchContext()
        # When
        assert matcher.matches(permission, context)

    def test_matches_should_return_False_all_matchers_return_False(self):
        # Given
        permission = Permission('wasserer.drink')
        false_matcher = Mock()
        false_matcher.matches.return_value = False
        matcher = AnyMatcher([false_matcher, false_matcher, false_matcher])
        context = MatchContext()
        # When
        assert not matcher.matches(permission, context)

class TestAllMatcher:
    def test_matches_should_return_True_all_matchers_return_True(self):
        # Given
        permission = Permission('wasserer.drink')
        true_matcher = Mock()
        true_matcher.matches.return_value = True
        matcher = AllMatcher([true_matcher, true_matcher, true_matcher])
        context = MatchContext()
        # When
        assert matcher.matches(permission, context)

    def test_matches_should_return_False_any_matcher_returns_False(self):
        # Given
        permission = Permission('wasserer.drink')
        true_matcher = Mock()
        true_matcher.matches.return_value = True
        false_matcher = Mock()
        false_matcher.matches.return_value = False
        matcher = AllMatcher([false_matcher, true_matcher, false_matcher])
        context = MatchContext()
        # When
        assert not matcher.matches(permission, context)
