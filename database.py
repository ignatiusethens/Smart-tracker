import sqlite3
from typing import List
from models import Expense

class DatabaseManager:
    """
    Manages SQLite database connections and operations.
    Handles data persistence for the Expense Tracker.
    """
    def __init__(self, db_path: str = "expenses.db"):
        self.db_path = db_path
        self._create_tables()

    def _get_connection(self):
        """Returns a connection to the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self):
        """Initializes the database schema if it doesn't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    date TEXT NOT NULL,
                    description TEXT,
                    category TEXT NOT NULL
                )
            ''')
            conn.commit()

    def add_expense(self, expense: Expense) -> None:
        """Inserts a new expense record into the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO expenses (amount, date, description, category)
                VALUES (?, ?, ?, ?)
            ''', (expense.amount, expense.date, expense.description, expense.category))
            conn.commit()

    def get_all_expenses(self) -> List[Expense]:
        """Retrieves all expenses from the database and returns them as Expense objects."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM expenses ORDER BY date DESC, id DESC')
            rows = cursor.fetchall()
            
            expenses = []
            for row in rows:
                expenses.append(
                    Expense(
                        id=row['id'],
                        amount=row['amount'],
                        date=row['date'],
                        description=row['description'],
                        category=row['category']
                    )
                )
            return expenses

    def delete_expense(self, expense_id: int) -> None:
        """Deletes an expense given its ID (useful for future features)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
            conn.commit()
