import abc

from anytree import NodeMixin


class Rule(abc.ABC):
    @abc.abstractmethod
    def execute(self, context):
        raise NotImplementedError

    def __str__(self):
        name = getattr(self, "name", "<unnamed>")
        repr = f"{type(self).__name__}('{name}')"
        return repr


class RuleNode(Rule, NodeMixin):
    name: str

    def __init__(self, parent=None, name=None):
        self.parent = parent
        self.name = name or getattr(self, "name", None) or type(self).__name__
        self._build()

    def _build(self):
        """Allow inhriting classes to perform some build, e.g. initialize children nodes."""
