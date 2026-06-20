import streamlit as st
import pandas as pd
import yfinance as yf
import sqlite3
from pathlib import Path
from datetime import datetime
import plotly.graph_objects as go

# ==================================================
# DATABASE
# ==================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent

DB_PATH = BASE_DIR / "Database" / "goldbar.db"

conn = sqlite3.connect(
    
    DB_PATH,
    check_same_thread=False
)

cursor = conn.cursor()

# ==================================================
# TABLE YAHOO FINANCE DATA
# ==================================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS yahoo_finance_data (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    symbol TEXT,

    datetime TEXT,

    open_price REAL,

    high_price REAL,

    low_price REAL,

    close_price REAL,

    volume REAL,

    source TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

# ==================================================
# TABLE ADMIN NOTES
# ==================================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS admin_notes (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    tanggal TEXT,

    catatan TEXT
)
""")

conn.commit()

# ==================================================
# TABLE FEEDBACK
# ==================================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS feedback (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    timestamp TEXT,

    saran TEXT
)
""")

conn.commit()

# ==================================================
# UPDATE YAHOO FINANCE TO DATABASE
# ==================================================
def update_yahoo_finance_data():

    try:

        gold = yf.Ticker("GC=F")

        df = gold.history(
            period="1mo"
        )

        if df.empty:

            return False

        df.reset_index(
            inplace=True
        )

        for _, row in df.iterrows():

            tanggal = str(
                row["Date"]
            )

            check = cursor.execute(
                """
                SELECT id
                FROM yahoo_finance_data
                WHERE datetime=?
                """,
                (tanggal,)
            ).fetchone()

            if check is None:

                cursor.execute(
                    """
                    INSERT INTO yahoo_finance_data
                    (
                        symbol,
                        datetime,
                        open_price,
                        high_price,
                        low_price,
                        close_price,
                        volume,
                        source
                    )
                    VALUES
                    (
                        ?,?,?,?,?,?,?,?
                    )
                    """,
                    (
                        "GC=F",
                        tanggal,
                        float(row["Open"]),
                        float(row["High"]),
                        float(row["Low"]),
                        float(row["Close"]),
                        float(row["Volume"]),
                        "Yahoo Finance"
                    )
                )

        conn.commit()

        return True

    except Exception as e:

        st.error(
            f"Update gagal: {e}"
        )

        return False

# ==================================================
# DASHBOARD ADMIN
# ==================================================
def show_dashboard():

    st.title("🛠️ Dashboard Administrator")

    menu = st.sidebar.radio(

        "Menu Admin",

        [

            "Dashboard",

            "Data Historis Harga Emas",

            "Riwayat Prediksi",

            "Feedback Pengguna",

            "Logout"

        ]
    )

    # ==========================================
    # DASHBOARD
    # ==========================================
    
    if menu == "Dashboard":
    
        update_yahoo_finance_data()

        st.subheader("Dashboard Admin")

        st.success("Monitoring Sistem GoldBar")
    
    # ==========================================
    # DATA HISTORIS HARGA EMAS
    # ==========================================
    elif menu == "Data Historis Harga Emas":

        st.subheader(
            "📈 Data Historis Harga Emas Yahoo Finance"
        )

        period = st.selectbox(

            "Pilih Periode",

            [

                "1mo",

                "3mo",

                "6mo",

                "1y",

                "2y",

                "5y"

            ]
        )

        try:

            # ======================================
            # DOWNLOAD YAHOO FINANCE
            # ======================================
            df = yf.download(

                "GC=F",

                period=period,

                progress=False,

                auto_adjust=False
            )

            if df.empty:

                st.warning(
                    "Data Yahoo Finance tidak tersedia"
                )

                return

            # ======================================
            # FIX MULTI INDEX
            # ======================================
            if isinstance(
                df.columns,
                pd.MultiIndex
            ):

                df.columns = (
                    df.columns
                    .get_level_values(0)
                )

            df.reset_index(
                inplace=True
            )

            # ======================================
            # GRAFIK
            # ======================================
            fig = go.Figure()

            fig.add_trace(

                go.Scatter(

                    x=df["Date"],

                    y=df["Close"],

                    mode="lines",

                    name="Harga Emas"
                )
            )

            fig.update_layout(

                title="Grafik Harga Emas Dunia",

                xaxis_title="Tanggal",

                yaxis_title="USD/OZ",

                template="plotly_dark",

                height=500
            )

            st.plotly_chart(

                fig,

                use_container_width=True
            )

            # ======================================
            # TABEL HISTORIS
            # ======================================
            st.markdown(
                "### Data Historis"
            )

            st.dataframe(

                df,

                use_container_width=True
            )

            # ======================================
            # DOWNLOAD CSV
            # ======================================
            st.download_button(

                "⬇ Download CSV",

                df.to_csv(
                    index=False
                ),

                "gold_history.csv",

                "text/csv"
            )

        except Exception as e:

            st.error(
                f"Error Yahoo Finance: {e}"
            )

        # ======================================
        # CATATAN ADMIN
        # ======================================
        st.markdown("---")

        st.subheader(
            "📝 Catatan Admin"
        )

        note = st.text_area(

            "Masukkan Catatan"
        )

        if st.button(
            "Simpan Catatan"
        ):

            if note.strip() != "":

                tanggal = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                cursor.execute(

                    """
                    INSERT INTO admin_notes
                    (
                        tanggal,
                        catatan
                    )
                    VALUES (?, ?)
                    """,

                    (
                        tanggal,
                        note
                    )
                )

                conn.commit()

                st.success(
                    "Catatan berhasil disimpan"
                )

            else:

                st.warning(
                    "Catatan tidak boleh kosong"
                )

        notes_df = pd.read_sql_query(

            """
            SELECT *
            FROM admin_notes
            ORDER BY id DESC
            """,

            conn
        )

        st.markdown(
            "### Riwayat Catatan"
        )

        st.dataframe(

            notes_df,

            use_container_width=True
        )

        # ==================================================
        # TABEL RIWAYAT PREDIKSI
        # ==================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS gold_predictions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            prediction_date TEXT,

            actual_price REAL,

            predicted_price REAL,

            difference REAL,

            model_name TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()

        # ==================================================
        # RIWAYAT PREDIKSI
        # ==================================================
    elif menu == "Riwayat Prediksi":

            st.subheader(
                "📈 Riwayat Prediksi Harga Emas"
            )

            pred_df = pd.read_sql_query(
                """
                SELECT *
                FROM gold_predictions
                ORDER BY id DESC
                """,
                conn
            )

            if pred_df.empty:

                st.warning(
                    "Belum ada data prediksi."
                )

            else:

                st.metric(
                    "Total Prediksi",
                    len(pred_df)
                )

                st.dataframe(
                    pred_df,
                    use_container_width=True
                )

                fig = go.Figure()

                fig.add_trace(
                    go.Scatter(
                        x=pred_df["prediction_date"],
                        y=pred_df["predicted_price"],
                        mode="lines+markers",
                        name="Prediksi"
                    )
                )

                fig.update_layout(
                    title="Grafik Riwayat Prediksi",
                    xaxis_title="Tanggal",
                    yaxis_title="Harga Prediksi",
                    height=500
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                if st.button(
                    "🗑 Hapus Semua Riwayat"
                ):

                    cursor.execute(
                        """
                        DELETE FROM gold_predictions
                        """
                    )

                    conn.commit()

                    st.success(
                        "Riwayat berhasil dihapus"
                    )

                    st.rerun()

    # ==========================================
    # FEEDBACK PENGGUNA
    # ==========================================
    elif menu == "Feedback Pengguna":

        st.subheader(
            "💬 Feedback Pengguna"
        )

        feedback_df = pd.read_sql_query(
            """
            SELECT *
            FROM feedback
            ORDER BY id DESC
            """,
            conn
        )

        if feedback_df.empty:

            st.warning(
                "Belum ada feedback dari pengguna."
            )

        else:

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "Total Feedback",
                    len(feedback_df)
                )

            with col2:

                st.metric(
                    "Feedback Terbaru",
                    feedback_df.iloc[0]["timestamp"]
                )

            st.markdown("---")

            st.dataframe(
                feedback_df,
                use_container_width=True
            )

            st.markdown("### 📩 Daftar Feedback")

            for _, row in feedback_df.iterrows():

                st.info(
                    f"""
                    🕒 {row['timestamp']}

                    💬 {row['saran']}
                    """
                )

            st.download_button(
                "⬇ Download Feedback CSV",
                feedback_df.to_csv(index=False),
                "feedback.csv",
                "text/csv"
            )

            if st.button(
                "🗑 Hapus Semua Feedback"
            ):

                cursor.execute(
                    """
                    DELETE FROM feedback
                    """
                )

                conn.commit()

                st.success(
                    "Semua feedback berhasil dihapus."
                )

                st.rerun()

    # ==========================================
    # FEEDBACK PENGGUNA
    # ==========================================
    elif menu == "Feedback Pengguna":

        st.subheader(
            "💬 Feedback Pengguna"
        )

        feedback_df = pd.read_sql_query(
            """
            SELECT *
            FROM feedback
            ORDER BY id DESC
            """,
            conn
        )

        if feedback_df.empty:

            st.warning(
                "Belum ada feedback dari pengguna."
            )

        else:

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "Total Feedback",
                    len(feedback_df)
                )

            with col2:

                st.metric(
                    "Feedback Terbaru",
                    feedback_df.iloc[0]["timestamp"]
                )

            st.markdown("---")

            st.dataframe(
                feedback_df,
                use_container_width=True
            )

            st.markdown("### 📩 Daftar Feedback")

            for _, row in feedback_df.iterrows():

                st.info(
                    f"""
                    🕒 {row['timestamp']}

                    💬 {row['saran']}
                    """
                )

            st.download_button(
                "⬇ Download Feedback CSV",
                feedback_df.to_csv(index=False),
                "feedback.csv",
                "text/csv"
            )

            if st.button(
                "🗑 Hapus Semua Feedback"
            ):

                cursor.execute(
                    """
                    DELETE FROM feedback
                    """
                )

                conn.commit()

                st.success(
                    "Semua feedback berhasil dihapus."
                )

                st.rerun()
    # ==========================================
    # LOGOUT
    # ==========================================
    elif menu == "Logout":

        st.session_state.admin_login = False

        st.rerun()