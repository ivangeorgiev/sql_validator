from unittest.mock import MagicMock, patch

import pytest
from anyrule.rules.base_rule import BaseRule
from anyrule.rules.context import RuleContext


@pytest.fixture(name="given_rule")
def rule_fixture():
    rule = BaseRule()
    return rule


@pytest.fixture(name="given_rule_with_mocked_execute")
def rule_execute_mock_fixture(given_rule):
    with patch.object(given_rule, "execute"):
        yield given_rule


@pytest.fixture(name="given_fake_context")
def fake_context_fixture():
    ctx = MagicMock(spec=RuleContext)
    return ctx


@pytest.fixture(name="given_child_rule")
def child_rule_fixture(given_rule):
    rule = BaseRule()
    given_rule.children.append(rule)
    return rule


@pytest.fixture(name="given_child_rule_with_mocked_execute")
def child_rule_with_mocked_execute_fixture(given_child_rule):
    with patch.object(given_child_rule, "execute"):
        yield given_child_rule


class TestBaseRule:
    def test_should_execute_rule_and_children_when_called(
        self,
        given_rule_with_mocked_execute,
        given_child_rule_with_mocked_execute,
        given_fake_context,
    ):
        rule = given_rule_with_mocked_execute
        child_rule = given_child_rule_with_mocked_execute
        rule(given_fake_context)
        rule.execute.assert_called_once_with(given_fake_context)
        child_rule.execute.assert_called_once_with(given_fake_context)
