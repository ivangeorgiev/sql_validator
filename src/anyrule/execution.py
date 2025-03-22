from typing import List
from .rule import Rule


class RuleExecutor:
    execute_children_list_context_attr = "execute_children_list"

    def execute(self, rule: Rule, context):
        rule(context)
        children = self._get_or_pop_children_to_execute(rule, context)
        for child in children:
            self.execute(child, context)

    def _get_or_pop_children_to_execute(self, rule: Rule, context) -> List[Rule]:
        """Pop children from context if available, otherwise return rule children."""
        if hasattr(context, self.execute_children_list_context_attr):
            children = getattr(context, self.execute_children_list_context_attr)
            delattr(context, self.execute_children_list_context_attr)
            return children
        return rule.children
