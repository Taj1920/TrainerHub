import sqlite3
import os
import streamlit as st
import requests

DB_FILE_URL = st.secrets['database']['db_file_url']
DB_PATH = "trainer.db"

# Download DB directly if not exists
if not os.path.exists(DB_PATH):
    try:
        response = requests.get(DB_FILE_URL)
        if response.status_code == 200:
            with open(DB_PATH, "wb") as f:
                f.write(response.content)
        else:
            st.error("Failed to download DB file.")
            st.stop()
    except Exception as e:
        st.error(f"Error downloading DB: {e}")
        st.stop()

@st.cache_resource
def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.commit()
    return conn
