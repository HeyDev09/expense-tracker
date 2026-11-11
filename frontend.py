# frontend.py - Streamlit dashboard for the Expense Tracker
# Run with (in a second terminal, while the backend is running):
#   streamlit run frontend.py

from datetime import date

import pandas as pd
import requests
import streamlit as st

API = "http://127.0.0.1:8000"          # address of the FastAPI backend

st.set_page_config(page_title="Expense Tracker", layout="wide")
st.title("Personal Expense Tracker")

# ---------- Add an expense (sends POST) ----------
with st.sidebar:
    st.header("Add expense")
    with st.form("add_form", clear_on_submit=True):
        amount = st.number_input("Amount (Rs)", min_value=0.0, step=10.0)
        category = st.selectbox("Category", ["Food", "Travel", "Rent", "Shopping", "Other"])
        when = st.date_input("Date", value=date.today())
        note = st.text_input("Note (optional)")
        submitted = st.form_submit_button("Add")

    if submitted:
        payload = {"amount": amount, "category": category,
                   "date": when.isoformat(), "note": note}
        res = requests.post(f"{API}/expenses", json=payload)
        if res.status_code == 201:
            st.success("Expense added")
        else:
            st.error(f"Error {res.status_code}: {res.json()['detail']}")

# ---------- Show all expenses (sends GET) ----------
expenses = requests.get(f"{API}/expenses").json()

if not expenses:
    st.info("No expenses yet. Add one from the sidebar.")
    st.stop()

df = pd.DataFrame(expenses)
st.metric("Total spent", f"Rs {df['amount'].sum():,.0f}")
st.subheader("All expenses")
st.dataframe(df, use_container_width=True, hide_index=True)

# ---------- Delete an expense (sends DELETE) ----------
col1, col2 = st.columns([1, 3])
with col1:
    del_id = st.number_input("Expense ID to delete", min_value=1, step=1)
    if st.button("Delete"):
        res = requests.delete(f"{API}/expenses/{int(del_id)}")
        if res.status_code == 200:
            st.success(res.json()["message"])
            st.rerun()
        else:
            st.error(res.json()["detail"])

# ---------- Charts from the summary endpoints ----------
left, right = st.columns(2)
with left:
    st.subheader("Spending by category")
    cat = pd.DataFrame(requests.get(f"{API}/summary/category").json())
    st.bar_chart(cat, x="category", y="total")
with right:
    st.subheader("Spending by month")
    mon = pd.DataFrame(requests.get(f"{API}/summary/monthly").json())
    st.bar_chart(mon, x="month", y="total")
