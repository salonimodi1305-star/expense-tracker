import streamlit as st
import pandas as pd
import os
from datetime import datetime, date

# ── PAGE CONFIG ─────────────────────────────────────────────
st.set_page_config(page_title="Finance Tracker Pro 💰", layout="wide")

# ── 🎨 MODERN UI ────────────────────────────────────────────
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, #dfe9f3, #ffffff);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(to bottom, #141e30, #243b55);
    color: white;
}

/* Cards */
.card {
    padding: 25px;
    border-radius: 18px;
    background: linear-gradient(145deg, #ffffff, #f0f0f0);
    box-shadow: 8px 8px 20px #d1d1d1, -8px -8px 20px #ffffff;
    text-align: center;
}

/* Buttons */
.stButton>button {
    background: #243b55;
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ── FILES ──────────────────────────────────────────────────
EXP_FILE = "expenses.csv"
SAL_FILE = "salaries.csv"
USER_FILE = "users.csv"

# ── INIT FILES ─────────────────────────────────────────────
def init_files():
    if not os.path.exists(EXP_FILE):
        pd.DataFrame(columns=["id","name","amount","cat","date"]).to_csv(EXP_FILE,index=False)
    if not os.path.exists(SAL_FILE):
        pd.DataFrame(columns=["id","month","amount"]).to_csv(SAL_FILE,index=False)
    if not os.path.exists(USER_FILE):
        pd.DataFrame(columns=["username","password"]).to_csv(USER_FILE,index=False)

init_files()

# ── SAFE LOAD ──────────────────────────────────────────────
def safe_read(file):
    if os.path.exists(file) and os.path.getsize(file) > 0:
        try:
            return pd.read_csv(file).to_dict("records")
        except:
            return []
    return []

def load():
    return {
        "expenses": safe_read(EXP_FILE),
        "salaries": safe_read(SAL_FILE),
        "users": safe_read(USER_FILE)
    }

def save(db):
    pd.DataFrame(db["expenses"]).to_csv(EXP_FILE,index=False)
    pd.DataFrame(db["salaries"]).to_csv(SAL_FILE,index=False)
    pd.DataFrame(db["users"]).to_csv(USER_FILE,index=False)

# ── SESSION ────────────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None

# ── HELPERS ────────────────────────────────────────────────
def fmt(x):
    return f"₹{int(x):,}" if x else "₹0"

def cur_month():
    return date.today().strftime("%Y-%m")

CATS = ["Food","Transport","Shopping","Health","Entertainment","Utilities","Other"]

# ── LOGIN ──────────────────────────────────────────────────
def login():
    db = load()
    st.title("🔐 Login / Signup")

    tab1, tab2 = st.tabs(["Login","Signup"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            user = next((x for x in db["users"] if x["username"]==u and x["password"]==p),None)
            if user:
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        u = st.text_input("New Username")
        p = st.text_input("New Password", type="password")
        if st.button("Signup"):
            db["users"].append({"username":u,"password":p})
            save(db)
            st.success("Account created!")

if not st.session_state.user:
    login()
    st.stop()

# ── SIDEBAR ────────────────────────────────────────────────
st.sidebar.title(f"👋 {st.session_state.user}")

if st.sidebar.button("Logout"):
    st.session_state.user=None
    st.rerun()

page = st.sidebar.radio("Menu",["📊 Dashboard","💸 Expenses","💼 Salary","📈 Analytics"])

# ── LOAD DATA ──────────────────────────────────────────────
db = load()

# ── DASHBOARD ──────────────────────────────────────────────
if page=="📊 Dashboard":
    st.title("📊 Dashboard")

    cur = cur_month()

    m_exp = [e for e in db["expenses"] if str(e["date"]).startswith(cur)]
    m_sal = [s for s in db["salaries"] if s["month"]==cur]

    income = sum(float(s["amount"]) for s in m_sal)
    spent = sum(float(e["amount"]) for e in m_exp)
    saving = income - spent

    col1,col2,col3 = st.columns(3)

    col1.markdown(f"<div class='card'><h3>Income</h3><h2>{fmt(income)}</h2></div>",unsafe_allow_html=True)
    col2.markdown(f"<div class='card'><h3>Expense</h3><h2>{fmt(spent)}</h2></div>",unsafe_allow_html=True)
    col3.markdown(f"<div class='card'><h3>Saving</h3><h2>{fmt(saving)}</h2></div>",unsafe_allow_html=True)

    # 🎯 Budget Feature
    st.subheader("🎯 Monthly Budget")
    budget = st.number_input("Set Budget", value=5000)

    if spent > budget:
        st.error("⚠ Budget exceeded!")
    else:
        st.success(f"Remaining: {fmt(budget-spent)}")

# ── EXPENSES ───────────────────────────────────────────────
elif page=="💸 Expenses":
    st.title("💸 Add Expense")

    name = st.text_input("Description")
    amt = st.number_input("Amount",min_value=0.0)
    cat = st.selectbox("Category",CATS)

    if st.button("Add"):
        db["expenses"].append({
            "id":int(datetime.now().timestamp()*1000),
            "name":name,
            "amount":amt,
            "cat":cat,
            "date":date.today().strftime("%Y-%m-%d")
        })
        save(db)
        st.success("Added")
        st.rerun()

    if db["expenses"]:
        st.dataframe(pd.DataFrame(db["expenses"]))

# ── SALARY ─────────────────────────────────────────────────
elif page=="💼 Salary":
    st.title("💼 Salary")

    m = st.text_input("Month",value=cur_month())
    amt = st.number_input("Amount",min_value=0.0)

    if st.button("Save"):
        db["salaries"].append({
            "id":int(datetime.now().timestamp()*1000),
            "month":m,
            "amount":amt
        })
        save(db)
        st.success("Saved")
        st.rerun()

    st.dataframe(pd.DataFrame(db["salaries"]))

# ── 📈 ANALYTICS ───────────────────────────────────────────
elif page=="📈 Analytics":
    st.title("📈 Analytics")

    if not db["expenses"]:
        st.warning("No data available")
    else:
        df = pd.DataFrame(db["expenses"])
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.to_period("M")

        # 📊 Monthly Trend
        st.subheader("📊 Monthly Trend")
        trend = df.groupby("month")["amount"].sum()
        st.line_chart(trend)

        # 📊 Category chart
        st.subheader("📊 Category Breakdown")
        cat = df.groupby("cat")["amount"].sum()
        st.bar_chart(cat)
