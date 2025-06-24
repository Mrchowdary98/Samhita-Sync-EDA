import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from scipy import stats
from sklearn.preprocessing import LabelEncoder
import io
import base64
from datetime import datetime
import csv
import os

warnings.filterwarnings('ignore')

# Page config
st.set_page_config(
    page_title="Samhita Sync",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply dark/light mode CSS
mode = st.sidebar.radio("Theme", ["Light", "Dark"])
if mode == "Dark":
    st.markdown("""
        <style>
        body {
            background-color: #1e1e1e;
            color: white;
        }
        .stApp {
            background-color: #1e1e1e;
        }
        </style>
    """, unsafe_allow_html=True)

# Save login log
LOGIN_LOG_FILE = "login_log.csv"
USER_CREDENTIALS = {
    "dmkc1998@gmail.com": {"password": "Mani$@1998", "role": "admin"},
    "dmkcanalyst1@samhitasync.com": {"password": "Samhita@sync123", "role": "analyst"},
    "dmkcguest@samhitasync.com": {"password": "Samhita$sync@guest", "role": "viewer"}
}

def log_login_event(user_email):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = [user_email, now, USER_CREDENTIALS[user_email]['role']]
    file_exists = os.path.isfile(LOGIN_LOG_FILE)
    with open(LOGIN_LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Username", "Login Time", "Role"])
        writer.writerow(entry)

# Data loader function

def load_data(file):
    try:
        file_name = file.name
        file_extension = file_name.split(".")[-1].lower()
        file_content = file.read()
        file_obj = io.BytesIO(file_content)

        if file_extension == "csv":
            for enc in ["utf-8", "latin-1", "cp1252", "iso-8859-1"]:
                try:
                    file_obj.seek(0)
                    return pd.read_csv(file_obj, encoding=enc, low_memory=False)
                except UnicodeDecodeError:
                    continue
            raise ValueError("CSV decoding failed.")

        elif file_extension in ["xlsx", "xls"]:
            return pd.read_excel(file_obj)
        elif file_extension == "json":
            return pd.read_json(file_obj)
        elif file_extension == "parquet":
            return pd.read_parquet(file_obj)
        elif file_extension == "tsv":
            return pd.read_csv(file_obj, sep="\t")
        elif file_extension == "txt":
            return pd.read_csv(file_obj, sep=None, engine="python")
        elif file_extension == "pkl":
            return pd.read_pickle(file_obj)
        else:
            st.error(f"Unsupported file format: .{file_extension}")
            return None
    except Exception as e:
        st.error(f"❌ Failed to load file: {str(e)}")
        return None

# Login Page Function
def login_page():
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("""
            <div style='padding: 2rem;'>
                <h1 style='color: #004080; font-size: 3rem;'>📊 Samhita Sync</h1>
                <p style='font-size: 18px;'>Developed by <strong>Manikanta Damacharla</strong></p>
                <br>
                <ul style='font-size: 18px; line-height: 1.8;'>
                    <li>✅ Deep profiling</li>
                    <li>✅ Feature engineering</li>
                    <li>✅ Statistical tests</li>
                    <li>✅ Time series analysis</li>
                    <li>✅ Visualizations & insights</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 🔐 Login to Samhita Sync")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login = st.button("Login")
        if login:
            if username in USER_CREDENTIALS and password == USER_CREDENTIALS[username]["password"]:
                st.session_state['logged_in'] = True
                st.session_state['user'] = username
                st.session_state['role'] = USER_CREDENTIALS[username]['role']
                st.session_state['login_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_login_event(username)
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")

# Main App Logic

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        login_page()
        return

    st.title("🔍 Advanced EDA Tool")
    st.markdown("Upload your dataset and explore insights using the toggle menu on the left.")

    if st.session_state['role'] == 'admin':
        st.markdown("### 🔐 Admin Panel: Login History")
        if os.path.exists(LOGIN_LOG_FILE):
            log_df = pd.read_csv(LOGIN_LOG_FILE)
            st.dataframe(log_df, use_container_width=True)
            csv = log_df.to_csv(index=False)
            st.download_button("📤 Download Login Log", csv, "login_log.csv", mime="text/csv")
        else:
            st.info("No login records found.")

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

    if st.session_state['role'] in ['admin', 'analyst']:
        st.sidebar.header("📁 Upload Dataset")
        uploaded_file = st.sidebar.file_uploader("Choose a file", type=["csv", "xlsx", "xls", "json", "parquet", "tsv", "txt", "pkl"])

        st.sidebar.header("🧪 Analysis Options")
        show_basic = st.sidebar.checkbox("📋 Basic Information", True)
        show_quality = st.sidebar.checkbox("🔍 Data Quality Assessment", True)
        show_summary = st.sidebar.checkbox("📊 Statistical Summary")
        show_ts = st.sidebar.checkbox("📅 Time Series Analysis")
        show_vis = st.sidebar.checkbox("📈 Visualizations")
        show_auto = st.sidebar.checkbox("💡 Automated insights")
        show_tests = st.sidebar.checkbox("🧪 Statistical Tests")
        show_fe = st.sidebar.checkbox("🛠 Feature Engineering")

        if uploaded_file:
            if st.sidebar.button("🔁 Refresh Data"):
                st.rerun()

            df = load_data(uploaded_file)
            if df is None:
                return

            st.success(f"✅ Loaded `{uploaded_file.name}`")

            if show_basic:
                st.markdown("### 📋 Dataset Overview")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Rows", df.shape[0])
                col2.metric("Columns", df.shape[1])
                col3.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
                col4.metric("Duplicate Rows", df.duplicated().sum())

                st.markdown("### 📊 Column Information")
                info_df = pd.DataFrame({
                    "Column": df.columns,
                    "Data Type": df.dtypes.astype(str),
                    "Non-Null Count": df.notnull().sum(),
                    "Null Count": df.isnull().sum(),
                    "Null %": df.isnull().mean().round(2) * 100,
                    "Unique Values": df.nunique(),
                    "Memory (KB)": df.memory_usage(deep=True) / 1024
                }).reset_index(drop=True)
                st.dataframe(info_df, use_container_width=True)

            if show_quality:
                st.markdown("### 🔍 Data Quality Assessment")
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Missing Values Analysis")
                    if df.isnull().sum().sum() == 0:
                        st.success("No missing values found!")
                    else:
                        st.dataframe(df.isnull().sum().reset_index().rename(columns={0: "Missing Count"}))
                with col2:
                    st.subheader("Data Quality Issues")
                    outliers = []
                    for col in df.select_dtypes(include=np.number):
                        Q1 = df[col].quantile(0.25)
                        Q3 = df[col].quantile(0.75)
                        IQR = Q3 - Q1
                        count = ((df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)).sum()
                        if count > 0:
                            outliers.append(f"{col} ({count} outliers)")
                    if outliers:
                        st.warning("🟡 Columns with outliers:")
                        st.markdown(", ".join(outliers[:5]) + ("..." if len(outliers) > 5 else ""))
                    else:
                        st.success("No major outlier issues.")

            if show_tests:
                st.markdown("### 🧪 Statistical Tests")
                numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
                if len(numeric_cols) >= 2:
                    col1 = st.selectbox("Select first numeric column:", numeric_cols)
                    col2 = st.selectbox("Select second numeric column:", [c for c in numeric_cols if c != col1])

                    if st.button("Run Pearson Correlation Test"):
                        corr, pval = stats.pearsonr(df[col1].dropna(), df[col2].dropna())
                        st.info(f"Pearson Correlation Coefficient between `{col1}` and `{col2}`: **{corr:.4f}**")
                        st.info(f"P-value: **{pval:.4e}**")

    elif st.session_state['role'] == 'viewer':
        st.info("👀 You are logged in as a Viewer. Dataset upload and analysis are restricted.")

    # Footer
    st.markdown("""
        <hr style="margin-top: 2rem;"/>
        <center style="font-size: 15px; color: gray;">
            © 2025 Samhita Sync — Developed by Manikanta Damacharla
        </center>
    """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
