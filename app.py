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
                st.experimental_rerun()
            else:
                st.error("Invalid credentials. Please try again.")

# Main App Logic

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        login_page()
        return

    st.title("📊 Samhita Sync – Exploratory Data Analysis")
    st.markdown("**Developed by Manikanta Damacharla**")

    st.success(f"👋 Welcome, {st.session_state['user']} (Role: {st.session_state['role']}, Logged in at {st.session_state['login_time']})")

    if st.button("Logout"):
        st.session_state.clear()
        st.experimental_rerun()

    if st.session_state['role'] == 'admin':
        st.markdown("### 🔐 Admin Panel: Login History")
        if os.path.exists(LOGIN_LOG_FILE):
            log_df = pd.read_csv(LOGIN_LOG_FILE)
            st.dataframe(log_df, use_container_width=True)
            csv = log_df.to_csv(index=False)
            st.download_button("📤 Download Login Log", csv, "login_log.csv", mime="text/csv")
        else:
            st.info("No login records found.")

    if st.session_state['role'] in ['admin', 'analyst']:
        uploaded_file = st.sidebar.file_uploader("Upload a dataset", type=["csv", "xlsx", "xls", "json", "parquet", "tsv", "txt", "pkl"])

        if uploaded_file:
            def load_data(file):
                try:
                    file_name = file.name
                    file_content = file.read()
                    file_extension = file_name.lower().split('.')[-1]
                    file_obj = io.BytesIO(file_content)

                    if file_extension == 'csv':
                        for enc in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                            try:
                                file_obj.seek(0)
                                return pd.read_csv(file_obj, encoding=enc, low_memory=False)
                            except UnicodeDecodeError:
                                continue
                        raise ValueError("CSV decoding failed.")
                    elif file_extension in ['xlsx', 'xls']:
                        return pd.read_excel(file_obj)
                    elif file_extension == 'json':
                        return pd.read_json(file_obj)
                    elif file_extension == 'parquet':
                        return pd.read_parquet(file_obj)
                    elif file_extension == 'tsv':
                        return pd.read_csv(file_obj, sep='	', low_memory=False)
                    elif file_extension == 'txt':
                        file_obj.seek(0)
                        sample = file_obj.read(1024).decode('utf-8', errors='ignore')
                        file_obj.seek(0)
                        if '	' in sample:
                            return pd.read_csv(file_obj, sep='	', low_memory=False)
                        elif ';' in sample:
                            return pd.read_csv(file_obj, sep=';', low_memory=False)
                        elif '|' in sample:
                            return pd.read_csv(file_obj, sep='|', low_memory=False)
                        else:
                            return pd.read_csv(file_obj, low_memory=False)
                    elif file_extension == 'pkl':
                        return pd.read_pickle(file_obj)
                    else:
                        st.error(f"Unsupported file format: .{file_extension}")
                        return None
                except Exception as e:
                    st.error(f"Error loading file: {str(e)}")
                    return None

            df = load_data(uploaded_file)
            if df is not None:
                st.markdown("## 📋 Dataset Overview")
                col1, col2, col3, col4 = st.columns(4)
                with col1: st.metric("Rows", f"{df.shape[0]:,}")
                with col2: st.metric("Columns", f"{df.shape[1]:,}")
                with col3: st.metric("Memory", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
                with col4: st.metric("Duplicates", f"{df.duplicated().sum():,}")

                st.markdown("### 🔍 Column Summary")
                summary = pd.DataFrame({
                    "Column": df.columns,
                    "Type": [str(df[col].dtype) for col in df.columns],
                    "Non-Null": df.notnull().sum().values,
                    "Null %": df.isnull().mean().round(2).mul(100).values,
                    "Unique": df.nunique().values
                })
                st.dataframe(summary)

                st.markdown("### 🔬 Descriptive Stats")
                st.dataframe(df.describe(include='all'), use_container_width=True)

                st.markdown("### 🧪 Data Quality Checks")
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Missing Values")
                    missing_df = df.isnull().sum()
                    if missing_df.sum() == 0:
                        st.success("No missing values found.")
                    else:
                        miss_df = pd.DataFrame({"Column": missing_df.index, "Missing": missing_df.values})
                        miss_df = miss_df[miss_df.Missing > 0]
                        st.dataframe(miss_df)
                with col2:
                    st.subheader("Constant Columns")
                    const = [col for col in df.columns if df[col].nunique() <= 1]
                    if const:
                        st.warning(f"{len(const)} constant columns: {', '.join(const)}")
                    else:
                        st.success("No constant columns found.")
            else:
                st.warning("Please upload a valid dataset.")
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
