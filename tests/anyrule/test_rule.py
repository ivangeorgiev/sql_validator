from anyrule import Rule


class TestRule:
    def test_should_use_class_name_as_name_if_not_set(self):
        rule = Rule()
        assert rule.name == "Rule"

    def test_should_use_specified_name(self):
        rule = Rule()
        rule.name = "Custom Name"
        assert rule.name == "Custom Name"
