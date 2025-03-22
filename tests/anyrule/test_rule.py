from types import SimpleNamespace
from anyrule import Rule, IfRule, IfEvalRule
import pytest

@pytest.fixture(name="given_context")
def context_fixture():
    return SimpleNamespace()

class TestRule:
    def test_should_use_class_name_as_name_if_not_set(self):
        rule = Rule()
        assert rule.name == "Rule"

    def test_should_use_specified_name(self):
        rule = Rule()
        rule.name = "Custom Name"
        assert rule.name == "Custom Name"


class TestIfRule:
    def test_should_set_then_rule_when_else_rule_is_not_set(self):
        rule = IfRule()
        then_rule = Rule()
        rule.then_rule = then_rule
        assert rule.then_rule == then_rule
        assert rule.else_rule is None

    def test_should_set_then_rule_when_else_rule_is_set(self):
        rule = IfRule()
        then_rule = Rule()
        rule.then_rule = Rule()  # We cannot set else rule without then rule
        else_rule = Rule()
        rule.else_rule = else_rule
        #
        rule.then_rule = then_rule
        # THEN then_rule is updated
        assert rule.then_rule == then_rule
        # AND else_rule is preserved
        assert rule.else_rule is else_rule



    def test_should_set_else_rule(self):
        rule = IfRule()
        then_rule = Rule()
        else_rule = Rule()
        rule.then_rule = then_rule
        rule.else_rule = else_rule
        assert rule.else_rule == else_rule

    def test_should_raise_error_if_setting_else_rule_without_then_rule(self):
        rule = IfRule()
        else_rule = Rule()
        with pytest.raises(ValueError) as err:
            rule.else_rule = else_rule
        assert "Cannot set else rule without a then rule" in str(err.value)

    def test_should_execute_then_rule_when_condition_evaluates_to_true(self, given_context):
        rule = IfRule()
        rule.condition = lambda _: True
        then_rule = Rule()
        rule.then_rule = then_rule
        rule(given_context)
        assert getattr(given_context, rule.execute_children_list_context_attr) == [then_rule]

    def test_should_execute_else_rule_when_condition_evaluates_to_false(self, given_context):
        rule = IfRule()
        rule.condition = lambda _: False
        then_rule = Rule()
        else_rule = Rule()
        rule.then_rule = then_rule
        rule.else_rule = else_rule
        rule(given_context)
        assert getattr(given_context, rule.execute_children_list_context_attr) == [else_rule]

    def test_should_not_execute_any_rule_if_no_then_or_else_rule(self, given_context):
        rule = IfRule()
        rule.condition = lambda _: True
        rule(given_context)
        assert getattr(given_context, rule.execute_children_list_context_attr) == []
        #
        rule.condition = lambda _: False
        rule(given_context)
        assert getattr(given_context, rule.execute_children_list_context_attr) == []

    def test_should_raise_not_implemented_error_for_condition(self):
        rule = IfRule()
        with pytest.raises(NotImplementedError):
            rule.condition({})

class TestIfEvalRule:
    def test_should_evaluate_expression_to_true(self, given_context):
        given_context.value = 10
        rule = IfEvalRule("value > 5")
        assert rule.condition(given_context)

    def test_should_evaluate_expression_to_false(self, given_context):
        given_context.value = 10
        rule = IfEvalRule("value < 5")
        assert not rule.condition(given_context)
