from dataclasses import dataclass
from parse import parse


@dataclass(frozen=True)
class KeyMatchingResult:
    fixed: tuple
    named: dict
    value: object

    def execute_value(self):
        """Execute the value if it is callable or rises ValueError."""
        if not callable(self.value):
            raise ValueError("Value is not callable")
        return self.value(*self.fixed, **self.named)


class KeyMatchingDict(dict):
    def match(self, input) -> KeyMatchingResult:
        """Returns the value for the key that matches the input or raises KeyError."""
        for key, value in self.items():
            parse_result = parse(key, input)
            if parse_result:
                result = KeyMatchingResult(
                    parse_result.fixed, parse_result.named, value
                )
                return result
        raise KeyError(f"No key matches the input: {input}")
