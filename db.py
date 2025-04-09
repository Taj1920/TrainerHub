import sqlite3
import os
import streamlit as st
import zipfile
import requests

DB_ZIP_URL = st.secrets['database']['db_zip_url']
ZIP_FILE = "trainer.zip"
DB_PATH = "trainer.db"

# Download and unzip the DB if not already present
if not os.path.exists(DB_PATH):
    try:
        response = requests.get(DB_ZIP_URL, stream=True)
        response.raise_for_status()

        # Save the zip file
        with open(ZIP_FILE, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Verify the downloaded file is a zip file
        if zipfile.is_zipfile(ZIP_FILE):
            with zipfile.ZipFile(ZIP_FILE, "r") as zip_ref:
                zip_ref.extractall()
            os.remove(ZIP_FILE)
        else:
            st.error("Downloaded file is not a valid zip archive.")
            os.remove(ZIP_FILE)
            st.stop()

    except requests.exceptions.RequestException as e:
        st.error(f"Error downloading the file: {e}")
        st.stop()
    except zipfile.BadZipFile:
        st.error("The file downloaded is not a valid zip file.")
        os.remove(ZIP_FILE)
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        st.stop()

@st.cache_resource
def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.commit()
    return conn
