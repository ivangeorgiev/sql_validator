from anytree import Node, RenderTree

from executor import Context, RuleExecutor
from rules import ValidateAccessViewSql

sql_authorization = Node("SQL Authorization Rules")

def render_tree(node):
    for pre, _, node in RenderTree(node):
        print("%s%s" % (pre, node.name))

if __name__ == "__main__":
    sql_query = """
    SELECT u.name as uname, u.* FROM (SELECT name FROM users) u, orders WHERE users.id = orders.user_id;
    """
    # sql_query = """SELECT name FROM users u"""
    context = Context(query_text=sql_query)
    root_rule = ValidateAccessViewSql()
    executor = RuleExecutor()
    executor.execute(root_rule, context)
    print(context.errors)
    render_tree(root_rule)
