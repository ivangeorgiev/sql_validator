import sqlparse
from executor.exceptions import RuleError
from executor.rule import RuleNode
from sqlparse.sql import Identifier, IdentifierList, Statement
import sqlglot
from sqlglot import exp

ATTR_QUERY_TEXT = "query_text"
ATTR_SQL = "sql"
ATTR_FIELDS = "fields"


class ParseSql(RuleNode):
    query_text_attr = ATTR_QUERY_TEXT
    sql_attr = ATTR_SQL

    def execute(self, context):
        query_text = getattr(context, self.query_text_attr)
        parsed_sql = sqlglot.parse_one(query_text)
        setattr(context, self.sql_attr, parsed_sql)

    def _build(self):
        super()._build()
        AllowOnlySelectStatement(parent=self)
        ExtractFields(parent=self)

class ExtractFields(RuleNode):
    sql_attr = ATTR_SQL
    fields_attr = ATTR_FIELDS

    def execute(self, context):
        sql = getattr(context, self.sql_attr)
        fields = self._extract_physical_fields(sql)
        setattr(context, self.fields_attr, fields)

    @staticmethod
    def _extract_physical_fields(parsed):
        """Extract fully qualified physical field names from a SQL SELECT statement."""

        alias_to_table = {}
        fields = []

        def _register_table_alias(node):
            """Resolve table aliases and populate the alias_to_table dictionary."""
            if isinstance(node, exp.Table):
                if node.alias:
                    alias_to_table[node.alias] = node.name
                else:
                    alias_to_table[node.name] = node.name

        def _extract_fields(node):
            """Recursively extract fields from the AST, resolving aliases."""
            if isinstance(node, exp.Column):
                fields.append(node)
            elif isinstance(node, exp.Table):
                # Resolve table aliases
                _register_table_alias(node)
            elif isinstance(node, exp.Alias):
                # Skip aliases, but process their children
                _extract_fields(node.this)
            elif isinstance(node, exp.CTE):
                # Process CTEs and resolve their aliases
                _register_table_alias(node)
                _extract_fields(node.this)
            else:
                if hasattr(node, "args"):
                    for child in node.args.values():
                        if isinstance(child, (list, tuple)):
                            for item in child:
                                _extract_fields(item)
                        elif child:
                            _extract_fields(child)

        def _resolve_table_name(table_alias):
            table_name = alias_to_table.get(table_alias, table_alias)
            if table_name in alias_to_table and table_name != table_alias:
                table_name = _resolve_table_name(table_name)
            return table_name


        def _resolve_field_name(node):
            table_alias = node.table
            table_name = alias_to_table.get(table_alias, table_alias)
            if table_name and node.name:
                return f"{table_name}.{node.name}"
            return node.name

        _extract_fields(parsed)
        field_names = [_resolve_field_name(field) for field in fields]
        return field_names

    @staticmethod
    def _extract_fully_qualified_fields(parsed):
        fields = []

        def _extract_fields(node):
            """Recursively extract fields from the AST."""
            if isinstance(node, exp.Column):
                # Extract fully qualified field name
                field_parts = []
                if node.table:
                    field_parts.append(node.table)
                if node.name:
                    field_parts.append(node.name)
                if field_parts:
                    fields.append(".".join(field_parts))
            elif isinstance(node, exp.Alias):
                # Skip aliases, but process their children
                _extract_fields(node.this)
            else:
                # Recursively process child nodes
                if hasattr(node, "args"):
                    for child in node.args.values():
                        if isinstance(child, (list, tuple)):
                            for item in child:
                                _extract_fields(item)
                        elif child:
                            _extract_fields(child)

        # Start traversing the AST
        _extract_fields(parsed)

        return fields


def get_statement(sql):
    for token in sql.tokens:
        if isinstance(token, Statement):
            return token
    return None


def get_identifiers_list(sql):
    for token in sql.tokens:
        if isinstance(token, IdentifierList):
            return list(token.get_identifiers())
    return None


class AllowOnlySelectStatement(RuleNode):
    sql_attr = ATTR_SQL

    def execute(self, context):
        sql = getattr(context, self.sql_attr)
        if not isinstance(sql, exp.Select):
            raise RuleError("Only SELECT statement is supported", stop_execution=True)


class WildcardIdentifierIsNotAllowed(RuleNode):
    sql_attr = ATTR_SQL

    def execute(self, context):
        sql = getattr(context, self.sql_attr)
        identifiers = get_identifiers_list(sql)
        has_wildcard = any(x.value == "*" or x.is_wildcard() for x in identifiers)
        if has_wildcard:
            raise RuleError(
                "Wilidcard identifiers are not allowed.", stop_execution=True
            )


class ValidateAccessViewSql(RuleNode):
    def execute(self, context):
        """Nothing to execute in this rule"""

    def _build(self):
        ParseSql(parent=self)
        # WildcardIdentifierIsNotAllowed(parent=self)
