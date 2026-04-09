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

@dataclass
class Goal:
    """
    Represents a sinking fund target goal.
    """
    name: str
    target_amount: float
    current_amount: float
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

    def get_safe_daily_limit(self, monthly_budget: float) -> float:
        """Calculates safe daily spending amount based on remaining budget and days."""
        today = date.today()
        total_spent = self.get_total_expenses()
        remaining_budget = max(0, monthly_budget - total_spent)
        
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        days_left = max(1, days_in_month - today.day + 1)
        
        return remaining_budget / days_left

class InsightsEngine:
    """
    Synthesizes raw financial data from the BudgetAnalyzer into conversational 
    paragraphs and actionable recommendations.
    """
    def __init__(self, analyzer: BudgetAnalyzer, monthly_budget: float):
        self.analyzer = analyzer
        self.monthly_budget = monthly_budget
        
    def get_financial_translation(self) -> str:
        spent = self.analyzer.get_total_expenses()
        rem = max(0, self.monthly_budget - spent)
        burn = self.analyzer.get_projected_spending()
        safe_daily = self.analyzer.get_safe_daily_limit(self.monthly_budget)
        
        today = date.today()
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        days_left = max(1, days_in_month - today.day + 1)
        
        if burn > self.monthly_budget:
            # Over or projecting to over
            avg = self.analyzer.get_daily_average_this_month()
            if avg > 0:
                run_out_days = int(rem / avg) if rem > 0 else 0
                run_out_str = f"run out of money in {run_out_days} days"
            else:
                run_out_str = "exceed your budget soon"
            projection_str = run_out_str
        else:
            surplus = self.monthly_budget - burn
            projection_str = f"end the month with a surplus of Ksh {surplus:,.0f}"
            
        return f"You have spent Ksh {spent:,.0f} so far this month, leaving you with Ksh {rem:,.0f}. Based on your current spending habits, you are projected to {projection_str}. This means your strict daily safe-to-spend limit is currently Ksh {safe_daily:,.0f}."
        
    def get_actionable_recommendation(self) -> dict:
        burn = self.analyzer.get_projected_spending()
        pct = self.analyzer.get_budget_status_percentage(self.monthly_budget)
        
        today = date.today()
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        days_left = days_in_month - today.day + 1
        
        if burn > self.monthly_budget:
            # Condition A
            cat_df = self.analyzer.get_expenses_by_category()
            if not cat_df.empty:
                top_cat = cat_df.iloc[0]['category']
            else:
                top_cat = "various things"
            return {
                'type': 'danger',
                'msg': f"⚠️ **Recommendation:** You are spending too fast. You have spent heavily on **{top_cat}**. Try to purposefully pause or minimize spending in this category for the next week to bring your daily average back into alignment."
            }
        elif pct > 80 and days_left >= 7:
            # Condition B
            return {
                'type': 'warning',
                'msg': f"⚠️ **Recommendation:** Your budget utilization is sitting heavily at {pct:.1f}% with {days_left} days still remaining. Strictly adhere to your safe-to-spend daily limit to avoid falling into deficit."
            }
        else:
            # Condition C
            surplus = self.monthly_budget - burn
            amt_to_save = surplus * 0.25 # Suggested save is 25% of the run-rate surplus
            if amt_to_save < 100:
                amt_to_save = 100
                
            return {
                'type': 'success',
                'msg': f"✅ **Recommendation:** You are well under budget and projecting perfectly! Consider taking Ksh {amt_to_save:,.0f} from your remaining balance right now and routing it toward one of your Sinking Funds."
            }
