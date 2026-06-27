import streamlit as st
import pandas as pd
import os
import time
import sqlite3
from pathlib import Path
from datetime import datetime

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Feedback GoldBar",
    page_icon="💬",
    layout="wide"
)

# ======================================================
# PATH PROJECT
# ======================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DB_PATH = (
    BASE_DIR /
    "Database" /
    "goldbar.db"
)

# ======================================================
# VALIDASI HARUS DARI EDUKASI FAQ
# ======================================================

if (
    "allow_feedback" not in st.session_state
    or st.session_state.allow_feedback is False
):

    st.warning(
        """
        ⚠️ Akses ditolak.

        Silakan buka halaman Edukasi FAQ terlebih dahulu
        kemudian klik tombol
        'Go to Feedback'.
        """
    )

    st.stop()

if st.session_state.allow_feedback is not True:

    st.warning(
        """
        ⚠️ Akses ditolak.

        Silakan buka halaman Edukasi FAQ terlebih dahulu
        kemudian klik tombol
        'Go to Feedback'.
        """
    )

    st.stop()

    # ======================================
    # FEEDBACK BERHASIL DIAKSES
    # ======================================

    st.session_state.allow_feedback = False
    

# ======================================================
# SIDEBAR
# ======================================================
def sidebar():

    with st.sidebar:

        st.markdown("---")

        st.markdown(
            "## 💬 Feedback Dashboard"
        )

        st.markdown("---")


# ======================================================
# MAIN
# ======================================================
def main():

    # ======================================================
    # SIDEBAR
    # ======================================================
    sidebar()

    # ======================================================
    # HEADER
    # ======================================================
    st.title("💬 Feedback")

    st.write(
        """
        Silakan memberikan masukan terhadap dashboard GoldBar
        untuk membantu meningkatkan kualitas sistem.
        """
    )

    # ======================================================
    # DATABASE
    # ======================================================

    DB_PATH = (
        BASE_DIR /
        "Database" /
        "goldbar.db"
    )

    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )

    cursor = conn.cursor()


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        timestamp TEXT,

        saran TEXT

    )
    """)

    conn.commit()

    
    # ======================================================
    # FORM FEEDBACK
    # ======================================================
    with st.form("feedback_form"):

 
        saran = st.text_area(
            "Umpan balik atau saran"
        )

        submit = st.form_submit_button(
            "Kirim Feedback"
        )

        # ======================================================
        # SUBMIT FEEDBACK
        # ======================================================
    if submit:
        # ========================================== 
        # VALIDASI FEEDBACK 
        # ==========================================
        if not saran.strip(): 
            st.warning( "⚠️ Umpan balik atau saran wajib diisi." ) 
        else: 
            try:

                timestamp = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                cursor.execute(
                    """
                    INSERT INTO feedback
                    (
                        timestamp,
                        saran
                    )
                    VALUES (?, ?)
                    """,
                    (
                        timestamp,
                        saran
                    )
                )

                conn.commit()

                
                # ==============================================
                # SUCCESS
                # ==============================================
                st.success(
                    "✅ Feedback berhasil disimpan!"
                )

                st.balloons()

                time.sleep(2)

                st.session_state.show_dashboard = False

                st.session_state.welcome_shown = False
                
                st.session_state.allow_analysis = False

                st.session_state.allow_prediction = False

                st.session_state.allow_faq = False

                st.session_state.allow_feedback = False

                conn.close()
                st.switch_page("Main.py")

            except Exception as e:

                st.error(
                    f"""
                    Terjadi error saat menyimpan data:
                    {e}
                    """
                )

    # ======================================================
    # FOOTER
    # ======================================================
    st.markdown("---")

    st.markdown("""
    ### 🚀 Terima Kasih Atas Umpan Balik Anda!

    Umpan balik atau saran dari pengguna sangat membantu pengembangan
    sistem GoldBar agar menjadi lebih baik, interaktif,
    dan bermanfaat untuk analisis investasi emas.
    """)

# ======================================================
# RUN APP
# ======================================================
if __name__ == "__main__":

    main()
