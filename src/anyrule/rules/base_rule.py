from .context import RuleContext


class BaseRule:
    def __init__(self, children=None):
        self._children = list(children) if children else []

    @property
    def children(self):
        return self._children

    def __call__(self, context: RuleContext):
        self.execute(context)
        self.execute_children(context)

    def execute(self, context: RuleContext):
        """Actual rule execution."""

    def execute_children(self, context: RuleContext):
        """Execute all children rules."""
        # TODO: Allow custom exception handling
        # TODO: Maybe capture StopIteration to stop iterating?
        for child in self.children:
            child(context)
