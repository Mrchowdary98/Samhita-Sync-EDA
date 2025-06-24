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
                <h1 style='color: #004080;'>🔗 Samhita Sync</h1>
                <p style='font-size: 18px;'>
                    The Ultimate No-Code EDA Assistant
                </p>
                <ul style='font-size: 16px; line-height: 1.6;'>
                    <li>📊 Descriptive Statistics</li>
                    <li>🔍 Data Quality Assessment</li>
                    <li>📈 Visualizations</li>
                    <li>🛠️ Feature Engineering</li>
                    <li>📅 Time Series & Statistical Tests</li>
                </ul>
                <br><strong>Developed by Manikanta Damacharla</strong>
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

    # Admin panel to view login logs
    if st.session_state['role'] == 'admin':
        st.markdown("### 🔐 Admin Panel: Login History")
        if os.path.exists(LOGIN_LOG_FILE):
            log_df = pd.read_csv(LOGIN_LOG_FILE)
            st.dataframe(log_df, use_container_width=True)
            csv = log_df.to_csv(index=False)
            st.download_button("📤 Download Login Log", csv, "login_log.csv", mime="text/csv")
        else:
            st.info("No login records found.")

    uploaded_file = st.sidebar.file_uploader("Upload a dataset", type=["csv", "xlsx", "xls", "json", "parquet"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        st.write("### Sample Preview")
        st.dataframe(df.head())

        st.write("### Basic Stats")
        st.write(df.describe())
    else:
        st.info("Please upload a dataset to get started.")

    # Footer
    st.markdown("""
        <hr style="margin-top: 2rem;"/>
        <center style="font-size: 15px; color: gray;">
            © 2025 Samhita Sync — Developed by Manikanta Damacharla
        </center>
    """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
