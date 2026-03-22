import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import os
from datetime import datetime, date

# ── FILE PATHS ─────────────────────────────────────────────
EXP_FILE = "expenses.csv"
SAL_FILE = "salaries.csv"
USER_FILE = "users.csv"

# ── PAGE CONFIG ────────────────────────────────────────────
st.set_page_config(page_title="Finance Tracker", page_icon="💰", layout="wide")

# ── LOAD / SAVE ────────────────────────────────────────────
def load():
    expenses = pd.read_csv(EXP_FILE).to_dict("records") if os.path.exists(EXP_FILE) else []
    salaries = pd.read_csv(SAL_FILE).to_dict("records") if os.path.exists(SAL_FILE) else []
    users = pd.read_csv(USER_FILE).to_dict("records") if os.path.exists(USER_FILE) else []
    return {"expenses": expenses, "salaries": salaries, "users": users}

def save(data):
    pd.DataFrame(data["expenses"]).to_csv(EXP_FILE, index=False)
    pd.DataFrame(data["salaries"]).to_csv(SAL_FILE, index=False)
    pd.DataFrame(data["users"]).to_csv(USER_FILE, index=False)

# ── INIT SESSION ───────────────────────────────────────────
if "db" not in st.session_state:
    st.session_state.db = load()

if "user" not in st.session_state:
    st.session_state.user = None

db = st.session_state.db

# ── HELPERS ────────────────────────────────────────────────
def fmt(n):
    return "₹{:,}".format(int(round(abs(n))))

def cur_ym():
    return date.today().strftime("%Y-%m")

CATS = ["Food", "Transport", "Shopping", "Health", "Entertainment", "Utilities", "Other"]

# ── AUTH SYSTEM ────────────────────────────────────────────
def login_page():
    st.title("🔐 Login / Signup")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    # LOGIN
    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            user = next((x for x in db["users"] if x["username"] == u and x["password"] == p), None)
            if user:
                st.session_state.user = u
                st.success("Login successful ✅")
                st.rerun()
            else:
                st.error("Invalid credentials")

    # SIGNUP
    with tab2:
        new_u = st.text_input("New Username")
        new_p = st.text_input("New Password", type="password")

        if st.button("Signup"):
            if any(x["username"] == new_u for x in db["users"]):
                st.warning("User already exists")
            else:
                db["users"].append({"username": new_u, "password": new_p})
                save(db)
                st.success("Account created! Now login.")

# ── IF NOT LOGGED IN ───────────────────────────────────────
if not st.session_state.user:
    login_page()
    st.stop()

# ── SIDEBAR ────────────────────────────────────────────────
st.sidebar.title(f"👋 {st.session_state.user}")
if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()

page = st.sidebar.radio("Navigate", ["📊 Dashboard", "💸 Expenses", "💼 Salary", "📈 Charts"])

# ── DASHBOARD DATA ─────────────────────────────────────────
cur = cur_ym()
m_exp = [e for e in db["expenses"] if str(e["date"]).startswith(cur)]
m_sal = [s for s in db["salaries"] if str(s["month"]) == cur]

income = sum(float(s["amount"]) for s in m_sal)
spent = sum(float(e["amount"]) for e in m_exp)
saving = income - spent

# ── DASHBOARD ──────────────────────────────────────────────
if page == "📊 Dashboard":
    st.title("📊 Dashboard")

    c1, c2, c3 = st.columns(3)
    c1.metric("Income", fmt(income))
    c2.metric("Expenses", fmt(spent))
    c3.metric("Savings", fmt(saving))

# ── EXPENSES ───────────────────────────────────────────────
elif page == "💸 Expenses":
    st.title("💸 Expenses")

    # ADD
    st.subheader("➕ Add Expense")
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
        st.success("Added ✅")
        st.rerun()

    # DISPLAY
    if db["expenses"]:
        df = pd.DataFrame(db["expenses"])
        st.dataframe(df, use_container_width=True)

        # EDIT
        st.subheader("✏ Edit Expense")
        edit_id = st.selectbox("Select ID", df["id"])

        exp = next(e for e in db["expenses"] if e["id"] == edit_id)

        new_name = st.text_input("Edit Name", value=exp["name"])
        new_amount = st.number_input("Edit Amount", value=float(exp["amount"]))
        new_cat = st.selectbox("Edit Category", CATS, index=CATS.index(exp["cat"]))

        if st.button("Update Expense"):
            exp["name"] = new_name
            exp["amount"] = new_amount
            exp["cat"] = new_cat
            save(db)
            st.success("Updated ✅")
            st.rerun()

        # DELETE
        st.subheader("🗑 Delete Expense")
        del_id = st.selectbox("Delete ID", df["id"], key="delete")

        if st.button("Delete Expense"):
            db["expenses"] = [e for e in db["expenses"] if e["id"] != del_id]
            save(db)
            st.success("Deleted ✅")
            st.rerun()

        # DOWNLOAD
        st.download_button(
            "⬇ Download CSV",
            data=pd.DataFrame(db["expenses"]).to_csv(index=False),
            file_name="expenses.csv",
            mime="text/csv"
        )

# ── SALARY ─────────────────────────────────────────────────
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
        st.success("Saved ✅")
        st.rerun()

    if db["salaries"]:
        st.dataframe(pd.DataFrame(db["salaries"]), use_container_width=True)

# ── CHARTS ─────────────────────────────────────────────────
elif page == "📈 Charts":
    st.title("📈 Charts")

    db = load()

    if not db["expenses"]:
        st.warning("No data")
    else:
        df = pd.DataFrame(db["expenses"])
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

        st.subheader("Category-wise")
        st.bar_chart(df.groupby("cat")["amount"].sum())

        st.subheader("Distribution")
        fig1, ax1 = plt.subplots()
        cat = df.groupby("cat")["amount"].sum()
        ax1.pie(cat, labels=cat.index, autopct="%1.1f%%")
        ax1.axis("equal")
        st.pyplot(fig1)

        st.subheader("Monthly Trend")
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.to_period("M").astype(str)
        month = df.groupby("month")["amount"].sum()

        fig2, ax2 = plt.subplots()
        month.plot(marker="o", ax=ax2)
        st.pyplot(fig2)
