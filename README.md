# sql_validator

The domain model:

```python
from types import SimpleNamespace
from typing import NamedTuple

class Buyer(NamedTuple):
    name: str
    age: int

class Item(NamedTuple):
    name: str
    price: float
    tags: list
```

Custom rules:

```python
from anyrule import Rule

class DenyRule(Rule):
    def __init__(self, reason):
        self.reason = reason
    
    def __call__(self, context):
        raise ValueError(f"Deny for reason: {self.reason}")
    
class SmileRule(Rule):
    def __call__(self, context):
        print("Smile")
```

Business rules and executor:

```python
from anyrule import RuleExecutor, IfEvalRule

if_rule = IfEvalRule("""("alchohol" in item.tags) and (buyer.age < 18)""")
then_rule = DenyRule("Underage")
else_rule = SmileRule()
if_rule.children += then_rule, else_rule

executor = RuleExecutor()
```

Let's execute for underage buyer:

```python
underage_buyer = Buyer(name="John", age=15)
item = Item(name="item", price=10, tags=["alchohol"])

context = SimpleNamespace(buyer=underage_buyer, item=item)
executor.execute(if_rule)
```


```python
class Action

```


```
If  user.age > 65
    Apply a 20% discount.

For each item in cart:
    If item.category == "Electronics":
        Apply a 10% discount.

Convert order.total currency to $ and store as order_total_usd.
If order.total > $200:
    Set shipping to "Free".
    Send a thank-you email.
```

