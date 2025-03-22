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
    execute_children_list_context_attr = "execute_children_list"

    def __call__(self, context):
        if self.condition(context):
            children_rules = self.get_then_rules()
        else:
            children_rules = self.get_else_rules()
        setattr(context, self.execute_children_list_context_attr, children_rules)

    def condition(self, context) -> bool:
        raise NotImplementedError("Implement the condition method.")

    def get_then_rules(self):
        if len(self.children) > 0:
            return (self.children[0],)
        return tuple()

    def get_else_rules(self):
        if len(self.children) > 1:
            return (self.children[1],)
        return tuple()


class IfEvalRule(IfRule):
    def __init__(self, expression):
        self.expression = expression

    def condition(self, context) -> bool:
        result = eval(self.expression, vars(context), {})
        return result
