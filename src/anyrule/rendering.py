from anytree import RenderTree


class RuleRenderer:
    """Render the rule tree.

    Example:
    >>> rule = Rule()
    >>> child = Rule()
    >>> child.parent = rule
    >>> renderer = RuleTreeRenderer(rule)
    >>> for pre, _, node in renderer:
    ...     print(f"{pre}{node.name}")
    Rule
    └── Rule

    """

    def __init__(self, rule):
        self.rule = rule

    def __iter__(self):
        return iter(RenderTree(self.rule))
