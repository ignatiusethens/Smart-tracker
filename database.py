import os
import bcrypt
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from models import Expense

Base = declarative_base()

class DBUser(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

class DBExpense(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(String, nullable=False)
    description = Column(String)
    category = Column(String, nullable=False)

class DatabaseManager:
    """
    Manages SQLAlchemy database connections and operations.
    Seamlessly works traversing local SQLite (`sqlite:///...`) 
    and production cloud PostgreSQL databases.
    """
    def __init__(self):
        # Use DATABASE_URL if in production environment, otherwise local SQLite
        db_url = os.environ.get("DATABASE_URL", "sqlite:///expenses.db")
        # Handle SQLAlchemy 1.4+ Heroku deprecation format if needed
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
            
        connect_args = {"check_same_thread": False} if "sqlite" in db_url else {}
        self.engine = create_engine(db_url, connect_args=connect_args)
        
        # Initialize schema
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def create_user(self, username: str, password: str) -> bool:
        """Creates a new user. Returns True if successful, False if username already exists."""
        with self.Session() as session:
            existing = session.query(DBUser).filter_by(username=username).first()
            if existing:
                return False
                
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            new_user = DBUser(username=username, password_hash=hashed)
            session.add(new_user)
            session.commit()
            return True

    def verify_user(self, username: str, password: str) -> Optional[int]:
        """Verifies login credentials. Returns the user_id if successful, None otherwise."""
        with self.Session() as session:
            user = session.query(DBUser).filter_by(username=username).first()
            if not user:
                return None
            
            if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                return user.id
            return None

    def add_expense(self, expense: Expense) -> None:
        """Inserts a new expense record belonging to a specific user"""
        with self.Session() as session:
            db_exp = DBExpense(
                user_id=expense.user_id,
                amount=expense.amount,
                date=expense.date,
                description=expense.description,
                category=expense.category
            )
            session.add(db_exp)
            session.commit()

    def get_all_expenses(self, user_id: int) -> List[Expense]:
        """Retrieves all expenses ensuring isolation to the requesting user_id."""
        with self.Session() as session:
            rows = session.query(DBExpense).filter_by(user_id=user_id).order_by(DBExpense.date.desc(), DBExpense.id.desc()).all()
            
            expenses = []
            for row in rows:
                expenses.append(
                    Expense(
                        id=row.id,
                        user_id=row.user_id,
                        amount=row.amount,
                        date=row.date,
                        description=row.description,
                        category=row.category
                    )
                )
            return expenses

    def delete_expense(self, expense_id: int, user_id: int) -> None:
        """Deletes an expense, checking for ownership safety (user_id match)."""
        with self.Session() as session:
            session.query(DBExpense).filter_by(id=expense_id, user_id=user_id).delete()
            session.commit()
