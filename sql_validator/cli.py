import click
from anytree import RenderTree
from rules import ValidateAccessViewSql

@click.group()
def cli():
    """A CLI application to render rules."""
    pass

@cli.command()
def render_rules():
    """Render rules."""
    rule = ValidateAccessViewSql()
    for pre, _, node in RenderTree(rule):
        print(f"{pre}{node.name}")


def read_query_from_stdin():
    """Read query from standard input."""
    return click.get_text_stream('stdin').read().strip()

def retrieve_query(ctx):
    """Custom validation to ensure only one input method is used."""
    query = ctx.params.get("query")
    query_file = ctx.params.get("query_file")

    # Count the number of input methods provided
    input_methods = [method for method in [query, query_file] if method]
    if len(input_methods) > 1:
        raise click.BadParameter("You can only provide one of --query, --query-file, or stdin.")

    if query:
        return query
    elif query_file:
        try:
            with open(query_file, "r") as f:
                return f.read()
        except FileNotFoundError:
            raise click.BadParameter(f"File not found: {query_file}")
    else:
        return read_query_from_stdin()

@cli.command()
@click.option("--use-case-id", type=str, required=True, help="Use case ID that needs to run the query")
@click.option("--requesting-user", type=str, required=True, help="Requesting user")
@click.option("--query", help="The query to validate.")
@click.option("--query-file", type=click.Path(exists=False), help="Path to a file containing the query.")
def validate_authorization(use_case_id, requesting_user, query, query_file):
    """Validate authorization"""

    query = retrieve_query(click.get_current_context())
    print(query)

if __name__ == "__main__":
    cli()
