import streamlit as st
import pandas as pd
import os
from datetime import datetime, date

# ── CONFIG ────────────────────────────────────────────────
st.set_page_config(page_title="Finance Tracker Pro 💰", layout="wide")

# ── 🎨 NEW GRAPHICAL UI ───────────────────────────────────
st.markdown("""
<style>

/* 🌈 BACKGROUND */
.stApp {
    background: linear-gradient(135deg, #74ebd5, #ACB6E5);
    background-attachment: fixed;
}

/* ✨ EMOJI BACKGROUND */
.stApp::before {
    content: "💰 📊 💸 📈 💵 💳 🪙 💼";
    position: fixed;
    font-size: 70px;
    opacity: 0.07;
    top: 25%;
    left: 10%;
    transform: rotate(-15deg);
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: linear-gradient(to bottom, #141e30, #243b55);
    color: white;
}

/* ✨ METRIC CARDS */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.75);
    padding: 18px;
    border-radius: 15px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.15);
}

/* BUTTONS */
.stButton>button {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border-radius: 12px;
    font-weight: bold;
}

/* TABLE */
.stDataFrame {
    background: rgba(255,255,255,0.85);
    border-radius: 10px;
}

/* HEADINGS */
h1, h2, h3 {
    color: #1f2a44;
}

</style>
""", unsafe_allow_html=True)

# ── FILES ────────────────────────────────────────────────
EXP_FILE = "expenses.csv"
SAL_FILE = "salaries.csv"
USER_FILE = "users.csv"

# ── INIT FILES ───────────────────────────────────────────
def init_files():
    if not os.path.exists(EXP_FILE):
        pd.DataFrame(columns=["id","name","amount","cat","date"]).to_csv(EXP_FILE,index=False)
    if not os.path.exists(SAL_FILE):
        pd.DataFrame(columns=["id","month","amount"]).to_csv(SAL_FILE,index=False)
    if not os.path.exists(USER_FILE):
        pd.DataFrame(columns=["username","password"]).to_csv(USER_FILE,index=False)

init_files()

# ── SAFE LOAD ────────────────────────────────────────────
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

# ── SESSION ──────────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None

# ── HELPERS ──────────────────────────────────────────────
def fmt(x):
    return f"₹{int(x):,}" if x else "₹0"

def cur_month():
    return date.today().strftime("%Y-%m")

CATS = ["Food","Transport","Shopping","Health","Entertainment","Utilities","Other"]

# ── LOGIN ────────────────────────────────────────────────
def login():
    db = load()
    st.title("🔐 Login / Signup 💼")

    tab1, tab2 = st.tabs(["🔑 Login","🆕 Signup"])

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

# ── SIDEBAR ──────────────────────────────────────────────
st.sidebar.title(f"👋 Welcome {st.session_state.user} 💰")

if st.sidebar.button("🚪 Logout"):
    st.session_state.user = None
    st.rerun()

page = st.sidebar.radio("📌 Menu",["📊 Dashboard","💸 Expenses","💼 Salary","📈 Analytics"])

# ── LOAD DATA ────────────────────────────────────────────
db = load()

# ── DASHBOARD ────────────────────────────────────────────
if page=="📊 Dashboard":
    st.title("📊 Finance Dashboard 💰✨")

    cur = cur_month()

    df_exp = pd.DataFrame(db["expenses"])
    df_sal = pd.DataFrame(db["salaries"])

    if not df_exp.empty:
        df_exp["date"] = pd.to_datetime(df_exp["date"], errors="coerce")
        df_exp = df_exp[df_exp["date"].dt.strftime("%Y-%m") == cur]

    if not df_sal.empty:
        df_sal = df_sal[df_sal["month"] == cur]

    income = df_sal["amount"].astype(float).sum() if not df_sal.empty else 0
    spent = df_exp["amount"].astype(float).sum() if not df_exp.empty else 0
    saving = income - spent

    col1,col2,col3 = st.columns(3)
    col1.metric("💰 Income", fmt(income))
    col2.metric("💸 Expenses", fmt(spent))
    col3.metric("💎 Savings", fmt(saving))

    st.subheader("🎯 Monthly Budget")
    budget = st.number_input("Set Budget", value=5000)

    if spent > budget:
        st.error("⚠ Budget Exceeded!")
    else:
        st.success(f"Remaining: {fmt(budget-spent)}")

# ── EXPENSES ─────────────────────────────────────────────
elif page=="💸 Expenses":
    st.title("💸 Expense Manager")

    name = st.text_input("Description")
    amt = st.number_input("Amount",min_value=0.0)
    cat = st.selectbox("Category",CATS)

    if st.button("➕ Add Expense"):
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

    df = pd.DataFrame(db["expenses"])

    if not df.empty:
        st.dataframe(df)

        st.subheader("✏ Edit Expense")
        eid = st.selectbox("Select ID", df["id"])
        exp = next(e for e in db["expenses"] if e["id"]==eid)

        new_name = st.text_input("Edit Name", exp["name"])
        new_amt = st.number_input("Edit Amount", value=float(exp["amount"]))
        new_cat = st.selectbox("Edit Category", CATS, index=CATS.index(exp["cat"]))

        if st.button("Update Expense"):
            exp["name"] = new_name
            exp["amount"] = new_amt
            exp["cat"] = new_cat
            save(db)
            st.success("Updated")
            st.rerun()

        st.subheader("🗑 Delete Expense")
        did = st.selectbox("Delete ID", df["id"], key="del")

        if st.button("Delete Expense"):
            db["expenses"] = [e for e in db["expenses"] if e["id"]!=did]
            save(db)
            st.success("Deleted")
            st.rerun()

# ── SALARY ───────────────────────────────────────────────
elif page=="💼 Salary":
    st.title("💼 Salary Manager")

    month = st.text_input("Month", value=cur_month())
    amt = st.number_input("Amount", min_value=0.0)

    if st.button("➕ Add Salary"):
        db["salaries"].append({
            "id":int(datetime.now().timestamp()*1000),
            "month":month,
            "amount":amt
        })
        save(db)
        st.success("Saved")
        st.rerun()

    df = pd.DataFrame(db["salaries"])

    if not df.empty:
        st.dataframe(df)

        sid = st.selectbox("Edit Salary ID", df["id"])
        sal = next(s for s in db["salaries"] if s["id"]==sid)

        new_amt = st.number_input("Edit Amount", value=float(sal["amount"]))

        if st.button("Update Salary"):
            sal["amount"] = new_amt
            save(db)
            st.success("Updated")
            st.rerun()

        did = st.selectbox("Delete Salary ID", df["id"], key="sdel")

        if st.button("Delete Salary"):
            db["salaries"] = [s for s in db["salaries"] if s["id"]!=did]
            save(db)
            st.success("Deleted")
            st.rerun()

# ── ANALYTICS ────────────────────────────────────────────
elif page=="📈 Analytics":
    st.title("📈 Analytics Dashboard")

    df = pd.DataFrame(db["expenses"])

    if df.empty:
        st.warning("No data")
    else:
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.to_period("M")

        st.subheader("📊 Monthly Trend")
        st.line_chart(df.groupby("month")["amount"].sum())

        st.subheader("📊 Category Breakdown")
        st.bar_chart(df.groupby("cat")["amount"].sum())
