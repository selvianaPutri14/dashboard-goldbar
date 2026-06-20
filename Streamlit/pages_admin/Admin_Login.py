import streamlit as st
import sqlite3
from pathlib import Path

if st.session_state.get("admin_login", False):
    
    from Admin_Dashboard import show_dashboard

    show_dashboard()

    st.stop()

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Admin Login",
    page_icon="🔐",
    layout="centered"
)

# =====================================================
# BASE DIRECTORY
# =====================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent

DB_PATH = (
    BASE_DIR /
    "Database" /
    "goldbar.db"
)

# =====================================================
# DATABASE CONNECTION
# =====================================================
conn = sqlite3.connect(
    DB_PATH,
    check_same_thread=False
)

cursor = conn.cursor()

# =====================================================
# CREATE USERS TABLE
# =====================================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    nama TEXT,

    username TEXT UNIQUE,

    password TEXT,

    role TEXT
)
""")

conn.commit()

# =====================================================
# CREATE DEFAULT ADMIN
# =====================================================
cursor.execute(
    """
    SELECT *
    FROM users
    WHERE username=?
    """,
    ("admin",)
)

admin = cursor.fetchone()

if admin is None:

    cursor.execute(
        """
        INSERT INTO users
        (
            nama,
            username,
            password,
            role
        )
        VALUES
        (
            ?,
            ?,
            ?,
            ?
        )
        """,
        (
            "Administrator",
            "admin",
            "admin123",
            "admin"
        )
    )

    conn.commit()

# =====================================================
# SESSION
# =====================================================
if "admin_login" not in st.session_state:

    st.session_state.admin_login = False

# =====================================================
# HEADER
# =====================================================
st.title("🔐 Login Administrator")



# =====================================================
# FORM LOGIN
# =====================================================
username = st.text_input(
    "Username"
)

password = st.text_input(
    "Password",
    type="password"
)

# =====================================================
# LOGIN BUTTON
# =====================================================
if st.button(
    "Login",
    use_container_width=True
):

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE username=?
        AND password=?
        AND role='admin'
        """,
        (
            username,
            password
        )
    )

    admin = cursor.fetchone()

    if admin:

        st.session_state.admin_login = True

        st.session_state.admin_name = admin[1]

        st.success(
            "Login berhasil"
        )

        # Jika file ada di pages_admin
        st.session_state.admin_login = True
        st.rerun()

    else:

        st.error(
            "Username atau password salah"
        )

# =====================================================
# CEK USER DATABASE
# =====================================================
with st.expander(
    "🔍 Debug User Database"
):

    if st.button(
        "Tampilkan User"
    ):

        cursor.execute(
            """
            SELECT
                id,
                nama,
                username,
                password,
                role
            FROM users
            """
        )

        users = cursor.fetchall()

        st.dataframe(
            users,
            use_container_width=True
        )