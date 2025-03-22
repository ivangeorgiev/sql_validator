from anyrule import Rule, RuleRenderer


class TestRuleRenderer:
    def test_should_render_rule_tree(self):
        rule = Rule()
        child = Rule()
        child.parent = rule
        renderer = RuleRenderer(rule)
        assert list(tuple(line) for line in renderer) == [
            ("", "", rule),
            ("└── ", "    ", child),
        ]
