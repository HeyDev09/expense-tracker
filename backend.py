# backend.py - FastAPI backend for the Expense Tracker
# Run with:  uvicorn backend:app --reload
# Then open: http://127.0.0.1:8000/docs  (auto-generated API page)

import sqlite3
from datetime import date

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Expense Tracker API")
DB_FILE = "expenses.db"


# ---------- Database helpers ----------
def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row      # rows behave like dicts: row["amount"]
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                amount   REAL    NOT NULL,
                category TEXT    NOT NULL,
                date     TEXT    NOT NULL,   -- stored as YYYY-MM-DD
                note     TEXT
            )
        """)


init_db()


# ---------- Pydantic model: the shape of valid input ----------
class ExpenseIn(BaseModel):
    amount: float = Field(gt=0)               # must be greater than 0
    category: str = Field(min_length=1)       # cannot be empty
    date: date                                # must be a real date
    note: str = ""                            # optional


# ---------- CRUD endpoints ----------
@app.post("/expenses", status_code=201)                 # CREATE
def add_expense(exp: ExpenseIn):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO expenses (amount, category, date, note) VALUES (?, ?, ?, ?)",
            (exp.amount, exp.category, exp.date.isoformat(), exp.note),
        )
        return {"id": cur.lastrowid, **exp.model_dump(mode="json")}


@app.get("/expenses")                                   # READ all
def list_expenses(category: str | None = None):
    with get_conn() as conn:
        if category:
            rows = conn.execute(
                "SELECT * FROM expenses WHERE category = ? ORDER BY date DESC", (category,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM expenses ORDER BY date DESC").fetchall()
        return [dict(r) for r in rows]


@app.get("/expenses/{expense_id}")                      # READ one
def get_expense(expense_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return dict(row)


@app.put("/expenses/{expense_id}")                      # UPDATE
def update_expense(expense_id: int, exp: ExpenseIn):
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE expenses SET amount = ?, category = ?, date = ?, note = ? WHERE id = ?",
            (exp.amount, exp.category, exp.date.isoformat(), exp.note, expense_id),
        )
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"id": expense_id, **exp.model_dump(mode="json")}


@app.delete("/expenses/{expense_id}")                   # DELETE
def delete_expense(expense_id: int):
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": f"Expense {expense_id} deleted"}


# ---------- Summary endpoints (SQL GROUP BY) ----------
@app.get("/summary/category")
def summary_by_category():
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT category, SUM(amount) AS total
            FROM expenses
            GROUP BY category
            ORDER BY total DESC
        """).fetchall()
    return [dict(r) for r in rows]


@app.get("/summary/monthly")
def summary_by_month():
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT strftime('%Y-%m', date) AS month, SUM(amount) AS total
            FROM expenses
            GROUP BY month
            ORDER BY month
        """).fetchall()
    return [dict(r) for r in rows]
