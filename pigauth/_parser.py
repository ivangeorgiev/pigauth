"""Permission expression parser"""

import abc
import re
from typing import Iterable

from ._auth import PermissionGrant
from ._matcher import RegexMatcher, AnyMatcher, AllMatcher, ModifierMatcherFactory, RequiresMatcher

class PermissionMatcher:
    pass

class Parser:
    @abc.abstractmethod
    def __call__(self, expression: str) -> Iterable[PermissionMatcher]:
        """Parse expression into matchers"""

class PatternParser(Parser):
    """Parse permission pattern segment"""
    def __call__(self, expression: str) -> Iterable[PermissionMatcher]:
        regex = re.compile(expression.replace(".", "\\.").replace("*", ".*"))
        yield RegexMatcher(regex)

class ModifierParser(Parser):
    """Parse permission expression modifier segment"""
    MODIFIER_DELIMITER = ','
    MODIFIER_ALTERNATIVE_DELIMITER = '+'

    def __init__(self, modifier_matcher_factory=None):
        self.modifier_matcher_factory = modifier_matcher_factory or ModifierMatcherFactory()

    def __call__(self, expression: str) -> Iterable[PermissionMatcher]:
        modifier_names = expression.split(self.MODIFIER_DELIMITER)
        yield RequiresMatcher(modifier_names)
        for modifier_name in modifier_names:
            modifier_alternatives = modifier_name.split(self.MODIFIER_ALTERNATIVE_DELIMITER)
            matchers_for_alternatives = []
            for alternative in modifier_alternatives:
                matcher = self.modifier_matcher_factory(alternative)
                if matcher:
                    matchers_for_alternatives.append(matcher)
            if not matchers_for_alternatives:
                continue
            if len(matchers_for_alternatives) > 1:
                yield AnyMatcher(matchers_for_alternatives)
            else:
                yield matchers_for_alternatives[0]

class PermissionExpressionParser(Parser):
    """Parse permission expression into PermissionMatchers"""
    MODIFIER_SEPARATOR = '|'
    _pattern_parser: PatternParser
    _modifier_parser: ModifierParser

    def __init__(self, pattern_parser = None, modifier_parser = None):
        self._pattern_parser = pattern_parser or PatternParser()
        self._modifier_parser = modifier_parser or ModifierParser()

    def __call__(self, expression: str) -> Iterable[PermissionMatcher]:
        pattern, _, modifier = expression.partition(self.MODIFIER_SEPARATOR)
        yield from self._pattern_parser(pattern)
        if modifier:
            yield from self._modifier_parser(modifier)

class PermissionGrantParser:
    """Parse permission grant into a single PermissionMatcher"""

    def __init__(self, expression_parser: Parser | None = None):
        self.expression_parser = expression_parser or PermissionExpressionParser()

    def __call__(self, grant: PermissionGrant) -> PermissionMatcher:
        matchers = list(self.expression_parser(grant))
        if len(matchers) > 1:
            return AllMatcher(matchers)
        return matchers[0]