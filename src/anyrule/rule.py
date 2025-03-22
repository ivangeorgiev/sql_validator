from anytree import NodeMixin


class Rule(NodeMixin):
    _name: str

    @property
    def name(self):
        """The name of the rule instance or the class name."""
        return getattr(self, "_name", None) or type(self).__name__

    @name.setter
    def name(self, value):
        self._name = value

    def __call__(self, context):
        """Execute the rule and return next rule."""


class IfRule(Rule):
    execute_children_list_context_attr = "__override_children_execute"

    def __call__(self, context):
        child_rule = self.then_rule if self.condition(context) else self.else_rule
        children_rules = [child_rule] if child_rule else []
        setattr(context, self.execute_children_list_context_attr, children_rules)

    @property
    def then_rule(self):
        if len(self.children) > 0:
            return self.children[0]

    @then_rule.setter
    def then_rule(self, value):
        else_rule = self.else_rule
        if else_rule:
            self.children = (value, else_rule)
        else:
            self.children = (value,)

    @property
    def else_rule(self):
        if len(self.children) > 1:
            return self.children[1]

    @else_rule.setter
    def else_rule(self, value):
        then_rule = self.then_rule
        if not then_rule:
            raise ValueError("Cannot set else rule without a then rule.")
        self.children = (then_rule, value)

    def condition(self, context) -> bool:
        raise NotImplementedError("Implement the condition method.")


class IfEvalRule(IfRule):
    def __init__(self, expression):
        self.expression = expression

    def condition(self, context) -> bool:
        result = eval(self.expression, vars(context), {})
        return result
