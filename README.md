# Expense Tracker MCP Server

A lightweight **Model Context Protocol (MCP)** server built with **FastMCP** and **SQLite** that enables AI assistants (like Claude Desktop) to track and manage personal expenses.

---

## ✨ Features

- **Add Expense:** Log an expense with date, amount, category, subcategory, and note.
- **List Expenses:** Filter and view expenses between specific dates (`YYYY-MM-DD`).
- **Update Expense:** Modify existing expense entries by date and note.
- **Delete Expense:** Remove specific expense records.
- **Summary:** Quickly calculate total spending and transaction count over a given date range.

---

## 🛠️ Tech Stack

- **Python** (>= 3.12)
- **FastMCP** (MCP Python framework)
- **SQLite3** (local embedded database)
- **uv** (fast Python package manager)

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/Pratik07065/Expense_Tracker_MCP.git
cd Expense_Tracker_MCP
```

### 2. Install dependencies
Using `uv`:
```bash
uv sync
```

Or using standard `pip`:
```bash
pip install -r requirements.txt
```

### 3. Test with MCP Inspector
You can test the server locally using the FastMCP web inspector:
```bash
uv run fastmcp dev inspector main.py
```

---

## 🤖 Claude Desktop Configuration

To connect this server to **Claude Desktop**, add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ExpenseTracker": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "fastmcp",
        "fastmcp",
        "run",
        "C:\\path\\to\\your\\main.py"
      ]
    }
  }
}
```

> **Note:** Replace `C:\path\to\your\main.py` with your actual file path.

---

## 💬 Example Prompts in Claude

Once connected, you can manage expenses using natural language:

- *"Add an expense of 250 for Food today with note 'Lunch at cafe'"*
- *"Show all my expenses from 2026-11-01 to 2026-11-04"*
- *"What was my total spending this week?"*
- *"Update the lunch expense on 2026-11-04 to 280"*
- *"Delete the expense on 2026-11-04 with note 'Lunch at cafe'"*

---

## 📄 License

MIT License

