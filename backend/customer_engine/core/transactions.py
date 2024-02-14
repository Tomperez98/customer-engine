"""Transactions module."""
from __future__ import annotations

from lego_workflows.transactions import TransactionCommiter
from sqlalchemy import Connection, TextClause


class SqlAlchemyTransactionCommiter(TransactionCommiter[TextClause]):
    """Transaction commiter for sqlalchemy."""

    def __init__(self, conn: Connection) -> None:
        """Create a SqlAlchemy transaction commiter."""
        self.conn = conn

    def commit_transaction(self, state_changes: list[TextClause]) -> None:
        """Commit a set of text clause in a transaction."""
        for operation in state_changes:
            self.conn.execute(operation)
