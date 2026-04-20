import os
import bcrypt
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from models import Expense, Goal

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

class DBGoal(Base):
    __tablename__ = 'goals'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    goal_name = Column(String, nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)

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

    def update_password(self, username: str, new_password: str) -> bool:
        """Updates the password for an existing user. Returns True if successful, False if user not found."""
        with self.Session() as session:
            user = session.query(DBUser).filter_by(username=username).first()
            if not user:
                return False
                
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
            user.password_hash = hashed
            session.commit()
            return True

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

    def add_goal(self, goal: Goal) -> None:
        """Inserts a new goal record belonging to a specific user"""
        with self.Session() as session:
            db_goal = DBGoal(
                user_id=goal.user_id,
                goal_name=goal.name,
                target_amount=goal.target_amount,
                current_amount=goal.current_amount
            )
            session.add(db_goal)
            session.commit()

    def get_all_goals(self, user_id: int) -> List[Goal]:
        """Retrieves all goals ensuring isolation to the requesting user_id."""
        with self.Session() as session:
            rows = session.query(DBGoal).filter_by(user_id=user_id).all()
            goals = []
            for row in rows:
                goals.append(
                    Goal(
                        id=row.id,
                        user_id=row.user_id,
                        name=row.goal_name,
                        target_amount=row.target_amount,
                        current_amount=row.current_amount
                    )
                )
            return goals

    def add_funds_to_goal(self, goal_id: int, user_id: int, amount: float) -> None:
        """Adds funds to an existing goal safely."""
        with self.Session() as session:
            goal = session.query(DBGoal).filter_by(id=goal_id, user_id=user_id).first()
            if goal:
                goal.current_amount += amount
                session.commit()
