from executor.exceptions import RuleError
from .context import Context
from .rule import Rule


class TreeVisitor:
    handler_name_prefix = "_visit_type_"

    def __init__(self, visit_handler=None, default_visit=None):
        self.visit_handler = visit_handler or self
        self.default_visit = default_visit or self._visit_any

    def visit(self, node, **kwargs):
        return self._visit_node(node, **kwargs) and self._visit_children(node, **kwargs)

    def _visit_node(self, node, **kwargs) -> bool:
        method = self._resolve_obj_visit(node)
        try:
            method(node, **kwargs)
        except StopIteration:
            return False
        return True

    def _visit_children(self, node, **kwargs) -> bool:
        return all(self.visit(child, **kwargs) for child in node.children)

    def _visit_any(self, node, **_):
        raise NotImplementedError(f"No visit method for {type(node).__name__}")

    def _resolve_obj_visit(self, obj):
        return self._resolve_type_visit(type(obj))

    def _resolve_type_visit(self, klass: type):
        method_name = f"{self.handler_name_prefix}{klass.__name__.lower()}"
        method = getattr(self.visit_handler, method_name, None)
        if method:
            return method
        return self._resolve_type_visit_recursive(klass)

    def _resolve_type_visit_recursive(self, klass: type):
        bases = klass.__bases__
        for base in bases:
            method = self._resolve_type_visit(base)
            if method:
                return method
        return getattr(self.visit_handler, "_generic_visit", self._visit_any)


class RuleExecutor:
    def execute(self, rule: Rule, context):
        context.errors = []
        visitor = TreeVisitor(self)
        visitor.visit(rule, context=context)

    def _visit_type_node(self, node, context):
        print(f"Visit node: {node} in context: {context}")

    def _visit_type_rule(self, rule: Rule, context):
        print(f"Visit rule: {rule} with context: {context}")
        try:
            rule.execute(context)
        except RuleError as err:
            context.errors.append(err)
            if err.stop_execution:
                raise StopIteration()
