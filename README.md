# Smart Student Expense Tracker 🎓

A modern, fast, and interactive web application designed to help university students manage their limited income and prevent overspending. Built using Python, Streamlit, and SQLite.

## Features
- **Clean UI**: A rich, premium, dark-mode design with metrics micro-animations.
- **Budget Alerts**: Visual warnings when your expenses approach or exceed your tailored monthly budget.
- **Categorized Logging**: Log your expenses by category (e.g., Food, Transport, Rent, Academics).
- **Interactive Dashboards**: Deep insights via Plotly's Pie and Bar charts for spending trends.
- **OOP Architecture**: Strict separation of Streamlit UI logic, Database persistent storage logic, and Business calculation logic for robust scalability and maintainability.

## Project Structure
- `models.py`: Data classes (`Expense`) and analysis models (`BudgetAnalyzer`) utilizing OOP.
- `database.py`: The `DatabaseManager` handles all SQLite bindings and data migrations abstraction.
- `main_app.py`: The frontend application interface leveraging `streamlit`.

## How to Run Locally

1. **Clone the repository or navigate to this folder:**
   ```bash
   cd "Smart Student Expense Tracker"
   ```

2. **(Optional) Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Streamlit Application:**
   ```bash
   streamlit run main_app.py
   ```

5. **Interact:** The application will open automatically in your browser (usually `http://localhost:8501`). Start inputting expenses via the sidebar!

## PostgreSQL Production Ready
By default, the application will create a local `expenses.db` SQLite database inside this folder.
To scale up automatically using a real cloud database (like Neon or Supabase), simply set the `DATABASE_URL` environment variable or add it to `.streamlit/secrets.toml`:

```bash
export DATABASE_URL="postgresql://user:password@host/dbname"
```
The python backend automatically converts and connects via `SQLAlchemy`.

