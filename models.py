import pandas as pd
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import date
import calendar

@dataclass
class Expense:
    """
    Represents a single expense record.
    """
    amount: float
    date: str
    description: str
    category: str
    user_id: int
    id: Optional[int] = None

class BudgetAnalyzer:
    """
    Responsible for analyzing collections of Expense objects.
    Provides methods to calculate totals, category breakdowns, and time-series data.
    """
    def __init__(self, expenses: List[Expense]):
        self.expenses = expenses
        # Convert to pandas dataframe for easier analysis if there is data
        if self.expenses:
            self.df = pd.DataFrame([vars(e) for e in self.expenses])
            self.df['date_obj'] = pd.to_datetime(self.df['date'])
        else:
            self.df = pd.DataFrame(columns=['id', 'amount', 'date', 'description', 'category', 'date_obj'])

    def get_total_expenses(self) -> float:
        """Returns the sum of all expenses."""
        if self.df.empty:
            return 0.0
        return float(self.df['amount'].sum())

    def get_expenses_by_category(self) -> pd.DataFrame:
        """Returns a DataFrame grouped by category and sum of amount."""
        if self.df.empty:
            return pd.DataFrame(columns=['category', 'amount'])
        
        grouped = self.df.groupby('category')['amount'].sum().reset_index()
        # Sort descending by amount
        grouped = grouped.sort_values(by='amount', ascending=False)
        return grouped

    def get_expenses_over_time(self) -> pd.DataFrame:
        """Returns a DataFrame grouped by date and sum of amount."""
        if self.df.empty:
            return pd.DataFrame(columns=['date', 'amount'])
        
        grouped = self.df.groupby('date')['amount'].sum().reset_index()
        grouped['date_obj'] = pd.to_datetime(grouped['date'])
        grouped = grouped.sort_values(by='date_obj')
        # Drop date_obj before returning to keep it clean
        return grouped[['date', 'amount']]

    def is_over_budget(self, monthly_budget: float) -> bool:
        """Checks if current expenses exceed the given budget."""
        return self.get_total_expenses() > monthly_budget
    
    def get_budget_status_percentage(self, monthly_budget: float) -> float:
        """Returns percentage of budget used."""
        if monthly_budget <= 0:
            return 0.0
        return (self.get_total_expenses() / monthly_budget) * 100

    def get_daily_average_this_month(self) -> float:
        """Returns the average daily spending for the current month."""
        if self.df.empty:
            return 0.0
            
        today = date.today()
        # Filter for current month's expenses
        current_month_df = self.df[(self.df['date_obj'].dt.month == today.month) & (self.df['date_obj'].dt.year == today.year)]
        
        if current_month_df.empty:
            return 0.0
            
        total_this_month = float(current_month_df['amount'].sum())
        return total_this_month / today.day
        
    def get_projected_spending(self) -> float:
        """Projects the total spending for the current month based on current burn rate."""
        today = date.today()
        daily_avg = self.get_daily_average_this_month()
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        return daily_avg * days_in_month
