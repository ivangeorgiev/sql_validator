from types import SimpleNamespace
from unittest.mock import patch, MagicMock
import pytest
from anyrule import Rule, RuleExecutor


@pytest.fixture(name="given_rule")
def rule_fixture():
    return Rule()


@pytest.fixture(name="given_context")
def context_fixture():
    return SimpleNamespace()


@pytest.fixture(name="given_rule_call_patch")
def rule_call_patch_fixture(given_rule):
    with patch.object(given_rule, "__call__") as p:
        yield p


class TestRuleExecutor:
    def test_should_call_rule(self, given_rule, given_context):
        executor = RuleExecutor()
        given_rule = MagicMock(spec=Rule)
        executor.execute(given_rule, given_context)
        given_rule.assert_called_once_with(given_context)

    def test_should_call_rule_children_if_not_set_in_context(self, given_rule, given_context):
        # GIVEN a rule with a child
        given_rule = MagicMock(spec=Rule)
        given_child = MagicMock(spec=Rule)
        given_rule.children = [given_child]
        # AND an executor
        executor = RuleExecutor()
        # WHEN the executor is called
        executor.execute(given_rule, given_context)
        # THEN the rule and its children should be called
        given_rule.assert_called_once_with(given_context)
        given_child.assert_called_once_with(given_context)


    def test_should_call_children_set_in_context(self, given_rule, given_context):
        # GIVEN a rule with a child
        given_rule = MagicMock(spec=Rule)
        given_child_not_in_context = MagicMock(spec=Rule)
        given_child_in_context = MagicMock(spec=Rule)
        given_rule.children = [given_child_not_in_context, given_child_in_context]
        # AND an executor
        executor = RuleExecutor()
        # AND children ilst to execute is set in context
        setattr(given_context, executor.execute_children_list_context_attr, [given_child_in_context])
        # WHEN the executor is called
        executor.execute(given_rule, given_context)
        # THEN the rule should be called
        given_rule.assert_called_once_with(given_context)
        # AND the child not mentioned in context should not be called
        given_child_not_in_context.assert_not_called()
        # AND the child mentioned in context should be called
        given_child_in_context.assert_called_once_with(given_context)
        # AND the context should be cleaned up
        assert not hasattr(given_context, RuleExecutor.execute_children_list_context_attr)
