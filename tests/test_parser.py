from unittest.mock import Mock, call
from pigauth._parser import PermissionExpressionParser, ModifierParser, PatternParser, PermissionGrantParser, PermissionGrantsParser
from pigauth._matcher import RegexMatcher, AnyMatcher, RequiresMatcher, AllMatcher

class TestExpressionParser:

    def test_init_should_create_default_parsers_not_passed(self):
        # Given
        # When
        parser = PermissionExpressionParser()
        # Then
        assert isinstance(parser._modifier_parser, ModifierParser)
        assert isinstance(parser._pattern_parser, PatternParser)


    def test_init_should_use_passed_values(self):
        # Given
        modifier_parser = Mock()
        pattern_parser = Mock()
        # When
        parser = PermissionExpressionParser(pattern_parser, modifier_parser)
        # Then
        assert parser._modifier_parser is modifier_parser
        assert parser._pattern_parser is pattern_parser

    def test_call_should_parse_expression_and_yield_pattern_matchers_and_modifier_matchers(self):
        # Given
        pattern_parser = Mock()
        expected_pattern_matcher = Mock()
        pattern_parser.return_value = iter([expected_pattern_matcher])
        modifier_parser = Mock()
        expected_modifier_matcher = Mock()
        modifier_parser.return_value = iter([expected_modifier_matcher])
        parser = PermissionExpressionParser(pattern_parser, modifier_parser)
        # When
        matchers = list(parser("pattern|modifier"))
        # Then
        pattern_parser.assert_called_once_with("pattern")
        modifier_parser.assert_called_once_with("modifier")
        assert matchers == [expected_pattern_matcher, expected_modifier_matcher]


class TestPatternParser:
    def test_call_should_return_regex_pattern_matcher(self):
        parser = PatternParser()
        (matcher,) = parser('canteen.eat.*')
        assert isinstance(matcher, RegexMatcher)
        assert matcher.regex.pattern == r'canteen\.eat\..*'


class TestModifierParser:
    def test_call_should_yield_RequiresMatcher_as_first_matcher(self):
        # Given
        factory = Mock()
        factory.return_value = None
        parser = ModifierParser(factory)
        # When
        (matcher,) = list(parser('a,b,c'))
        # Then
        assert isinstance(matcher, RequiresMatcher)
        assert matcher.modifier_names == ['a', 'b', 'c']


    def test_call_should_yield_modifiers_from_factory_skipping_none(self):
        # Given
        factory = Mock()
        matcher_1 = Mock()
        matcher_2 = Mock()
        factory.side_effect = [matcher_1, None, matcher_2]
        parser = ModifierParser(factory)
        # When
        matchers = list(parser('a,b,c'))
        # Then
        factory.assert_has_calls((call('a'), call('b'), call('c')))
        assert matchers[1:] == [matcher_1, matcher_2]

    def test_call_should_yield_AnyMatcher_for_alternatives(self):
        # Given
        factory = Mock()
        matcher_1 = Mock()
        matcher_2 = Mock()
        factory.side_effect = [matcher_1, None, matcher_2]
        parser = ModifierParser(factory)
        # When
        (_, matcher,) = list(parser('a+b+c'))
        # Then
        factory.assert_has_calls((call('a'), call('b'), call('c')))
        assert isinstance(matcher, AnyMatcher)
        assert matcher.matchers == [matcher_1, matcher_2]


class TestPermissionGrantParser:
    def test_call_should_return_AllMatcher_for_multiple_parsed_matchers(self):
        # Given
        expression_parser = Mock()
        matcher = Mock()
        expression_parser.return_value = [matcher, matcher]
        grant_parser = PermissionGrantParser(expression_parser)
        # When
        actual_matcher = grant_parser('kiss.me')
        # Then
        assert isinstance(actual_matcher, AllMatcher)
        assert actual_matcher.matchers == [matcher, matcher]

    def test_call_should_return_parsed_matcher_for_single_parsed_matcher(self):
        # Given
        expression_parser = Mock()
        matcher = Mock()
        expression_parser.return_value = [matcher]
        grant_parser = PermissionGrantParser(expression_parser)
        # When
        actual_matcher = grant_parser('kiss.me')
        # Then
        assert actual_matcher is matcher

class TestPermissionGrantsParser:
    def test_call_should_return_AnyMatcher_with_matcher_for_any_grant(self):
        # Given
        permission_grant_parser = Mock()
        matcher1 = Mock()
        matcher2 = Mock()
        permission_grant_parser.side_effect = [matcher1, matcher2]
        parser = PermissionGrantsParser(permission_grant_parser)
        # When
        actual_matcher = parser(['eat.meat', 'eat.fruit'])
        # Then
        assert isinstance(actual_matcher, AnyMatcher)
        actual_matcher.matchers == [matcher1, matcher2]
