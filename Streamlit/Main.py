import streamlit as st
from pathlib import Path
import time
import pandas as pd
import os
import yfinance as yf
import plotly.express as px
import sqlite3
from datetime import datetime
import plotly.graph_objects as go


# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="GoldBar",
    page_icon="🥇",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# BASE DIRECTORY
# ==========================================
BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# DATABASE
# ==========================================
DATABASE_DIR = BASE_DIR / "Database"

DATABASE_DIR.mkdir(exist_ok=True)

DB_PATH = DATABASE_DIR / "goldbar.db"

conn = sqlite3.connect(
    DB_PATH,
    check_same_thread=False
)

cursor = conn.cursor()

# ==========================================
# CREATE TABLE USERS
# ==========================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

# ==========================================
# CREATE TABLE LOGIN HISTORY
# ==========================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS login_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    role TEXT,
    login_time TEXT
)
""")

# ==========================================
# CREATE TABLE ACTIVITY LOGS
# ==========================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    aktivitas TEXT,
    halaman TEXT,
    waktu TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()


# ==========================================
# SESSION STATE
# ==========================================
if "show_dashboard" not in st.session_state:
    st.session_state.show_dashboard = False


if "welcome_shown" not in st.session_state:
    st.session_state.welcome_shown = False


# ==========================================
# SIDEBAR
# ==========================================

# ==========================================
# SIDEBAR
# ==========================================
def render_sidebar():

    with st.sidebar:

        st.markdown(
            """
            ### GoldBar

            Dashboard Analisis Harga Emas
            Realtime Yahoo Finance
            """
        )

        st.markdown("---")

# ==========================================
# LANDING PAGE
# ==========================================
def landing_page():

    placeholder = st.empty()

    with placeholder.container():

        image_path = (
            BASE_DIR /
            "assets" /
            "image" /
            "goldbar.png"
        )

        if os.path.exists(image_path):

            st.image(
                image_path,
                use_container_width=True
            )

        st.title(
            "GoldBar :blue[Navigasi Cerdas Investasi Emas Anda]"
        )

        st.subheader(
            "Prediksi Harga Emas Berbasis Deep Learning"
        )

        st.markdown("""
        **GoldBar** membantu investor memahami tren harga emas dan membuat keputusan berbasis data di tengah volatilitas pasar global.

        Dengan visualisasi realtime dan data historis Yahoo Finance, GoldBar memberikan pengalaman analisis investasi emas yang modern dan interaktif.
        """)

        col1, col2, col3 = st.columns([1, 0.7, 1])

        with col2:

            if st.button(
                "🚀 Go to Dashboard",
                use_container_width=True
            ):

                st.session_state.show_dashboard = True

                st.rerun()

    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# DOWNLOAD FUNCTION
# ==========================================
def download_data(symbol, period, interval):

    for attempt in range(3):

        try:

            data = yf.download(
                symbol,
                period=period,
                interval=interval,
                auto_adjust=True,
                progress=False,
                timeout=30,
                threads=False
            )

            if not data.empty:

                return data

        except Exception as e:

            print(
                f"Download gagal {symbol}: {e}"
            )

        time.sleep(2)

    return pd.DataFrame()

# ==========================================
# DASHBOARD
# ==========================================
def dashboard():

    render_sidebar()

    if not st.session_state.welcome_shown:

        st.toast(
            "Selamat datang di GoldBar! 🎉"
        )

        st.session_state.welcome_shown = True

    st.title(
        "🥇 GoldBar: Navigasi Cerdas Investasi Emas Anda"
    )

    st.subheader(
        "Welcome to Dashboard! 🚀"
    )

    st.markdown("""
    **GoldBar** membantu investor memahami tren harga emas dan membuat keputusan berbasis data di tengah volatilitas pasar global.
    """)

    try:

        # =====================================================
        # GET GOLD DATA
        # =====================================================
        gold = yf.Ticker("GC=F")

        # =====================================================
        # DASHBOARD HEADER
        # =====================================================

        st.markdown(
            "## 📈 Harga Emas Realtime Yahoo Finance"
        )


        # =====================================================
        # FILTER TOP BAR
        # =====================================================
        top_col1, top_col2, top_col3 = st.columns([1, 1, 1])

        with top_col1:

            gold_type = st.selectbox(
                "",
                [
                    "Gold"
                ],
                label_visibility="collapsed"
            )

        with top_col2:

            currency = st.selectbox(
                "",
                [
                    "USD",
                    "IDR"
                ],
                label_visibility="collapsed"
            )

        with top_col3:

            unit = st.selectbox(
                "",
                [
                    "oz",
                    "gr"
                ],
                label_visibility="collapsed"
            )

        # =====================================================
        # PERIOD FILTER
        # =====================================================
        period_option = st.selectbox(
            "Pilih Periode Data",
            (
                "1mo",
                "3mo",
                "6mo",
                "1y",
                "2y",
                "5y"
            )
        )

        # =====================================================
        # LOAD GOLD DATA
        # =====================================================
        df = gold.history(
            period=period_option,
        interval="1d"
)

        # =====================================================
        # VALIDASI DATA
        # =====================================================
        if df.empty:

            st.warning(
                "Data harga emas tidak tersedia."
            )

            st.stop()

        # =====================================================
        # RESET INDEX    
        # =====================================================
        df.reset_index(inplace=True)
        df["Date"] = pd.to_datetime(
         df["Date"]
            ).dt.strftime("%Y-%m-%d")

        # =====================================================
        # GET USD TO IDR
        # =====================================================
        usd_idr = yf.Ticker("IDR=X")

        kurs_df = usd_idr.history(period="1d")

        # =====================================================
        # VALIDASI KURS
        # =====================================================
        if kurs_df.empty:

            st.warning(
                "Data kurs IDR tidak tersedia."
            )

            st.stop()

        kurs = kurs_df["Close"].iloc[-1]

        # =====================================================
        # CONVERT UNIT
        # 1 TROY OUNCE = 31.1035 GRAM
        # =====================================================
        if unit == "gr":

            df["Close"] = (
                df["Close"] / 31.1035
            )

            df["Open"] = (
                df["Open"] / 31.1035
            )

            df["High"] = (
                df["High"] / 31.1035
            )

            df["Low"] = (
                df["Low"] / 31.1035
            )

        # =====================================================
        # CONVERT CURRENCY
        # =====================================================
        if currency == "IDR":

            df["Close"] = (
                df["Close"] * kurs
            )

            df["Open"] = (
                df["Open"] * kurs
            )

            df["High"] = (
                df["High"] * kurs
            )

            df["Low"] = (
                df["Low"] * kurs
            )

        # =====================================================
        # GET PRICE
        # =====================================================
        latest_price = df["Close"].iloc[-1]

        previous_price = df["Close"].iloc[-2]

        price_change = (
            (
                latest_price - previous_price
            ) / previous_price
        ) * 100

        # =====================================================
        # FORMAT PRICE
        # =====================================================
        if currency == "USD":

            formatted_price = (
                f"${latest_price:,.2f}"
            )

        else:

            formatted_price = (
                f"Rp{latest_price:,.0f}"
            )

        # =====================================================
        # PRICE DISPLAY
        # =====================================================
        price_color = (
            "green"
            if price_change >= 0
            else "red"
        )

        st.markdown(
            f"""
            <h1 style='
                color:{price_color};
                font-size:48px;
                margin-bottom:0;
            '>
                {formatted_price}
            </h1>

            <h3 style='
                color:{price_color};
                margin-top:0;
            '>
                {price_change:.2f}%
            </h3>
            """,
            unsafe_allow_html=True
        )

        # =====================================================
        # CHART
        # =====================================================
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(

                x=df["Date"],

                y=df["Close"],

                mode="lines",

                name="Harga Emas",

                line=dict(
                    width=3
                )
            )
        )

        fig.update_layout(

            title=f"""
            Grafik Harga Emas
            ({currency}/{unit})
            """,

            xaxis_title="Tanggal",

            yaxis_title=f"""
            Harga ({currency}/{unit})
            """,

            template="plotly_dark",

            height=500
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # =====================================================
        # HISTORICAL TABLE
        # =====================================================
        st.markdown(
            "## 📄 Data Historis Harga Emas"
        )

        historical_df = df[
            [
                "Date",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume"
            ]
        ].copy()

        # =====================================================
        # FORMAT TABLE
        # =====================================================
        for col in [
            "Open",
            "High",
            "Low",
            "Close"
        ]:

            if currency == "USD":

                historical_df[col] = historical_df[
                    col
                ].apply(
                    lambda x:
                    f"${x:,.2f}"
                )

            else:

                historical_df[col] = historical_df[
                    col
                ].apply(
                    lambda x:
                    f"Rp{x:,.0f}"
                )

        # =====================================================
        # SHOW TABLE
        # =====================================================
        st.dataframe(
            historical_df,
            use_container_width=True
        )

        # ======================================================
        # MAIN SELESAI
        # ======================================================
        st.session_state.analysis_done = True

        # ======================================================
        # TOMBOL MENUJU HALAMAN ANALISIS PASAR
        # ======================================================
        st.markdown("---")

        st.subheader(
                    "📊 Analisis Pasar"
                )

        st.info(
                    """
                    Main telah selesai dilakukan.

                    Anda dapat melanjutkan ke halaman
                    Analisis Pasar untuk analisis tren harga emas dan berita emas terkini
                    menggunakan model
                    Deep Learning GRU.
                    """
                )

        # Analisis selesai
        st.session_state.analysis_done = True

        # ======================================================
        # TOMBOL MENUJU HALAMAN ANALISIS PASAR
        # ======================================================

        st.markdown("---")

        col1, col2, col3 = st.columns([1,2,1])

        with col2:

                if st.button(
                    "📊  Go to Analisis Pasar",
                    use_container_width=True,
                    type="primary"
                ):
                    st.session_state.allow_analysis = True

                    st.switch_page(
                        "pages/2_Analisis_Pasar.py"
                    )

    except Exception as e:

        st.error(
            f"Gagal mengambil data realtime: {e}"
        )


# ==========================================
# MAIN
# ==========================================
def main():

    if not st.session_state.show_dashboard:

        landing_page()

    else:

        dashboard()

# ==========================================
# RUN APP
# ==========================================
if __name__ == "__main__":

    main()