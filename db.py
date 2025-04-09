import sqlite3
import os
import streamlit as st
import zipfile
import requests

DB_ZIP_URL = st.secrets['databse']['db_zip_url']
ZIP_FILE = "trainer.zip"
DB_PATH = "trainer.db"

# Download and unzip the DB if not already present
if not os.path.exists(DB_PATH):
    # Download zip from Drive
    with open(ZIP_FILE, "wb") as f:
        f.write(requests.get(DB_ZIP_URL).content)

    # Extract the DB
    with zipfile.ZipFile(ZIP_FILE, "r") as zip_ref:
        zip_ref.extractall()

    # Optionally remove the zip to save space
    os.remove(ZIP_FILE)

@st.cache_resource
def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.commit()
    return conn
