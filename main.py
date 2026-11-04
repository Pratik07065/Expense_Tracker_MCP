from fastmcp import FastMCP
from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "expenses.db"

mcp = FastMCP("ExpenseTracker")


def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        """)


init_db()


@mcp.tool()
def add_expense(date, amount, category, subcategory="", note=""):
    """Add a new expense entry to the database."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?,?,?,?,?)",
            (date, amount, category, subcategory, note),
        )
        return {"status": "ok", "id": cur.lastrowid}


@mcp.tool()
def list_expenses(start_date: str, end_date: str):
    """List all expenses between start_date and end_date (YYYY-MM-DD), oldest first."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            "SELECT id, date, amount, category, subcategory, note FROM expenses "
            "WHERE date BETWEEN ? AND ? ORDER BY date ASC, id ASC",
            (start_date, end_date),
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

@mcp.tool()
def update_expense(date: str, new_amount: float, new_category: str, new_subcategory: str = "", new_note: str = "", note: str = ""):
    """Update expenses on a date. If a note is given, only rows with that date AND note are updated."""
    query = "UPDATE expenses SET amount = ?, category = ?, subcategory = ?, note = ? WHERE date = ?"
    params = [new_amount, new_category, new_subcategory, new_note, date]

    if note:
        query += " AND note = ?"
        params.append(note)

    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(query, params)
        return {"status": "ok", "updated_rows": cur.rowcount}

@mcp.tool()
def delete_expense(date: str, note: str = ""):
    """Delete expenses on a date. If a note is given, only rows with that date AND note are deleted."""
    query = "DELETE FROM expenses WHERE date = ?"
    params = [date]

    if note:
        query += " AND note = ?"
        params.append(note)

    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(query, params)
        return {"status": "ok", "deleted_rows": cur.rowcount}

@mcp.tool()
def summary(start_date: str, end_date: str):
    """Get total amount and count of expenses between start_date and end_date (YYYY-MM-DD)."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            "SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM expenses "
            "WHERE date BETWEEN ? AND ?",
            (start_date, end_date),
        )
        count, total = cur.fetchone()
        return {"count": count, "total": round(total, 2)}


if __name__ == "__main__":
    mcp.run()