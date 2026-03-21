import streamlit as st
import matplotlib.pyplot as plt
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

# ── Helpers ────────────────────────────────────────────────────
def fmt(n):
    return "₹{:,}".format(int(round(abs(n))))

def cur_ym():
    return date.today().strftime("%Y-%m")

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

# ── Dashboard Data ─────────────────────────────────────────────
cur = cur_ym()
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

        st.success("Expense Saved! ✅")
        st.rerun()   # 🔥 FIX: refresh app instantly

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

        st.success("Salary Saved! ✅")
        st.rerun()   # 🔥 refresh

    if db["salaries"]:
        st.dataframe(pd.DataFrame(db["salaries"]))

# ── Charts ─────────────────────────────────────────────────────
elif page == "📈 Charts":
    st.title("📈 Charts")

    # 🔥 IMPORTANT: Reload latest data
    db = load()

    if not db["expenses"]:
        st.warning("No expense data available")
    else:
        df = pd.DataFrame(db["expenses"])

        # Fix data types
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

        # ── CATEGORY BAR CHART ─────────────────────
        st.subheader("Category-wise Expenses")

        cat_data = df.groupby("cat")["amount"].sum()
        st.bar_chart(cat_data)

        # ── PIE CHART ──────────────────────────────
        st.subheader("Expense Distribution")

        fig1, ax1 = plt.subplots()
        ax1.pie(cat_data, labels=cat_data.index, autopct="%1.1f%%")
        ax1.axis("equal")
        st.pyplot(fig1)

        # ── MONTHLY TREND ──────────────────────────
        st.subheader("Monthly Expense Trend")

        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.to_period("M").astype(str)

        month_data = df.groupby("month")["amount"].sum()

        fig2, ax2 = plt.subplots()
        month_data.plot(kind="line", marker="o", ax=ax2)

        st.pyplot(fig2)
