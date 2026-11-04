from fastmcp import FastMCP
from pathlib import Path
import aiosqlite
import sqlite3
import os
import tempfile


def get_db_path() -> Path:
    if custom_path := os.getenv("EXPENSES_DB_PATH"):
        path = Path(custom_path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    local_path = Path(__file__).resolve().parent / "expenses.db"
    try:
        test_file = local_path.parent / ".write_test"
        test_file.touch()
        test_file.unlink()
        return local_path
    except (PermissionError, OSError):
        return Path(tempfile.gettempdir()) / "expenses.db"


DB_PATH = get_db_path()

mcp = FastMCP("ExpenseTracker")


def init_db():
    try:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
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
    except Exception as e:
        print(f"Database initialization error: {e}")
        raise


init_db()


@mcp.tool()
async def add_expense(date, amount, category, subcategory="", note=""):
    """Add a new expense entry to the database."""
    try:
        async with aiosqlite.connect(DB_PATH) as c:
            cur = await c.execute(
                "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?,?,?,?,?)",
                (date, amount, category, subcategory, note),
            )
            await c.commit()
            return {"status": "ok", "id": cur.lastrowid}
    except Exception as e:
        return {"status": "error", "message": f"Error adding expense: {str(e)}"}


@mcp.tool()
async def list_expenses(start_date: str, end_date: str):
    """List all expenses between start_date and end_date (YYYY-MM-DD), oldest first."""
    try:
        async with aiosqlite.connect(DB_PATH) as c:
            cur = await c.execute(
                "SELECT id, date, amount, category, subcategory, note FROM expenses "
                "WHERE date BETWEEN ? AND ? ORDER BY date ASC, id ASC",
                (start_date, end_date),
            )
            cols = [d[0] for d in cur.description]
            rows = await cur.fetchall()
            return [dict(zip(cols, r)) for r in rows]
    except Exception as e:
        return {"status": "error", "message": f"Error listing expenses: {str(e)}"}


@mcp.tool()
async def update_expense(date: str, new_amount: float, new_category: str, new_subcategory: str = "", new_note: str = "", note: str = ""):
    """Update expenses on a date. If a note is given, only rows with that date AND note are updated."""
    try:
        query = "UPDATE expenses SET amount = ?, category = ?, subcategory = ?, note = ? WHERE date = ?"
        params = [new_amount, new_category, new_subcategory, new_note, date]

        if note:
            query += " AND note = ?"
            params.append(note)

        async with aiosqlite.connect(DB_PATH) as c:
            cur = await c.execute(query, params)
            await c.commit()
            return {"status": "ok", "updated_rows": cur.rowcount}
    except Exception as e:
        return {"status": "error", "message": f"Error updating expense: {str(e)}"}


@mcp.tool()
async def delete_expense(date: str, note: str = ""):
    """Delete expenses on a date. If a note is given, only rows with that date AND note are deleted."""
    try:
        query = "DELETE FROM expenses WHERE date = ?"
        params = [date]

        if note:
            query += " AND note = ?"
            params.append(note)

        async with aiosqlite.connect(DB_PATH) as c:
            cur = await c.execute(query, params)
            await c.commit()
            return {"status": "ok", "deleted_rows": cur.rowcount}
    except Exception as e:
        return {"status": "error", "message": f"Error deleting expense: {str(e)}"}


@mcp.tool()
async def summary(start_date: str, end_date: str):
    """Get total amount and count of expenses between start_date and end_date (YYYY-MM-DD)."""
    try:
        async with aiosqlite.connect(DB_PATH) as c:
            cur = await c.execute(
                "SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM expenses "
                "WHERE date BETWEEN ? AND ?",
                (start_date, end_date),
            )
            row = await cur.fetchone()
            count, total = row[0], row[1]
            return {"count": count, "total": round(total, 2)}
    except Exception as e:
        return {"status": "error", "message": f"Error calculating summary: {str(e)}"}


if __name__ == "__main__":
    mcp.run(transport="http" , host="0.0.0.0", port=8000 )
