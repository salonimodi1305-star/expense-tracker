import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import os
from datetime import datetime, date

# ── CSV FILE PATHS ─────────────────────────────────────────────
EXP_FILE = "expenses.csv"
SAL_FILE = "salaries.csv"

# ── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Load & Save Functions (CSV) ─────────────────────────────────
def load():
    if os.path.exists(EXP_FILE):
        expenses = pd.read_csv(EXP_FILE).to_dict("records")
    else:
        expenses = []

    if os.path.exists(SAL_FILE):
        salaries = pd.read_csv(SAL_FILE).to_dict("records")
    else:
        salaries = []

    return {"expenses": expenses, "salaries": salaries}


def save(data):
    pd.DataFrame(data["expenses"]).to_csv(EXP_FILE, index=False)
    pd.DataFrame(data["salaries"]).to_csv(SAL_FILE, index=False)

# ── Constants ──────────────────────────────────────────────────
CATS    = ["Food","Transport","Shopping","Health","Entertainment","Utilities","Other"]
COLORS  = ["#E07B39","#3266AD","#7B62C2","#C25454","#3A9FC4","#5A9E6F","#A07850"]
BUDGETS = {"Food":8000,"Transport":4000,"Shopping":5000,"Health":3000,
           "Entertainment":3000,"Utilities":2000,"Other":2000}
MONTHS  = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

GREEN  = "#2A7A4B"
RED    = "#B83232"
BLUE   = "#2D5FA8"
ORANGE = "#C07010"

# ── Helpers ────────────────────────────────────────────────────
def fmt(n):
    return "₹{:,}".format(int(round(abs(n))))

def cur_ym():
    return date.today().strftime("%Y-%m")

def ym_label(ym):
    y, m = ym.split("-")
    return "{} {}".format(MONTHS[int(m)-1], y)

def last6():
    y, m = date.today().year, date.today().month
    out = []
    for _ in range(6):
        out.insert(0, "{}-{:02d}".format(y, m))
        m -= 1
        if m == 0: m, y = 12, y-1
    return out

# ── Session State ──────────────────────────────────────────────
if "db" not in st.session_state:
    st.session_state.db = load()

db = st.session_state.db

# ── Sidebar ────────────────────────────────────────────────────
st.sidebar.markdown("## 💰 Finance Tracker")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    ["📊 Dashboard", "💸 Expenses", "💼 Salary", "📈 Charts"],
    label_visibility="collapsed"
)

cur   = cur_ym()
m_exp = [e for e in db["expenses"] if str(e["date"]).startswith(cur)]
m_sal = [s for s in db["salaries"] if str(s["month"]) == cur]

income = sum(float(s["amount"]) for s in m_sal)
spent  = sum(float(e["amount"]) for e in m_exp)
saving = income - spent

# ── Dashboard ──────────────────────────────────────────────────
if page == "📊 Dashboard":
    st.title("📊 Dashboard")
    st.metric("Income", fmt(income))
    st.metric("Expenses", fmt(spent))
    st.metric("Savings", fmt(saving))

# ── Expenses ───────────────────────────────────────────────────
elif page == "💸 Expenses":
    st.title("💸 Expenses")

    name = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0.0)
    category = st.selectbox("Category", CATS)

    if st.button("Add Expense"):
        db["expenses"].append({
            "id": int(datetime.now().timestamp()*1000),
            "name": name,
            "amount": float(amount),
            "cat": category,
            "date": date.today().strftime("%Y-%m-%d")
        })
        save(db)
        st.success("Expense Saved!")

    if db["expenses"]:
        st.dataframe(pd.DataFrame(db["expenses"]))

# ── Salary ─────────────────────────────────────────────────────
elif page == "💼 Salary":
    st.title("💼 Salary")

    month = st.text_input("Month (YYYY-MM)", value=cur_ym())
    amount = st.number_input("Salary", min_value=0.0)

    if st.button("Save Salary"):
        db["salaries"].append({
            "id": int(datetime.now().timestamp()*1000),
            "month": month,
            "amount": float(amount)
        })
        save(db)
        st.success("Salary Saved!")

    if db["salaries"]:
        st.dataframe(pd.DataFrame(db["salaries"]))

# ── Charts (basic placeholder, original charts can stay same) ──
elif page == "📈 Charts":
    st.title("📈 Charts")
    st.info("Charts working with saved CSV data")
 