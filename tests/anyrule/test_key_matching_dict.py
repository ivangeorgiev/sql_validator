from unittest.mock import Mock
import pytest
from anyrule.key_matching_dict import KeyMatchingDict, KeyMatchingResult


class TestKeyMatchingDict:
    def test_should_match_and_return_keymatchingresult_when_matching_key_exists(self):
        value = "value"
        kmd = KeyMatchingDict({"key {value}, {}": value})
        result = kmd.match("key 123, 456")
        assert isinstance(result, KeyMatchingResult)
        assert result.fixed == ("456",)
        assert result.named == {"value": "123"}
        assert result.value is value

    def test_should_raise_valueerror_when_no_key_matches(self):
        kmd = KeyMatchingDict({"key {value}": lambda value: f"Value is {value}"})
        with pytest.raises(KeyError):
            kmd.match("no match")


class TestKeyMatchingResult:
    def test_should_execute_callable_value_and_return_result(self):
        # GIVEN a KeyMatchingResult with a callable value
        fixed = (1, 2)
        named = {"a": 3}
        value = Mock()
        result_instance = KeyMatchingResult(fixed, named, value)
        # WHEN the callable value is executed
        actual = result_instance.execute_value()
        # THEN the value is called with the fixed and named arguments
        value.assert_called_with(*fixed, **named)
        # AND the return value is the result returned by the executable value
        assert actual is value.return_value

    def test_should_raise_valueerror_trying_to_execute_non_callable_value(self):
        result = KeyMatchingResult((), {}, "not callable")
        with pytest.raises(ValueError):
            result.execute_value()
