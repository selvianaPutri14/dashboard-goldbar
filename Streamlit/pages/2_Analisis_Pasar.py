import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import yfinance as yf
from newsapi import NewsApiClient


# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Analisis Pasar",
    page_icon="📊",
    layout="wide"
)

# ======================================================
# VALIDASI AKSES ANALISIS PASAR
# ======================================================

if "allow_analysis" not in st.session_state:

    st.error(
        """
        🚫 Akses ditolak.

        Silakan buka halaman Main terlebih dahulu
        kemudian klik tombol
        'Go to Analisis Pasar'

        """
    )

    st.stop()

if st.session_state.allow_analysis is not True:

    st.error(
        """
        🚫 Akses ditolak.

        Silakan buka halaman Main terlebih dahulu
        kemudian klik tombol "Go to Analisis Pasar".
        """
    )

    st.stop()

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False


# ======================================================
# DOWNLOAD VADER
# ======================================================
nltk.download('vader_lexicon')

# ======================================================
# SIDEBAR
# ======================================================
def sidebar():

    with st.sidebar:


        st.markdown("---")

        st.markdown(
            "## 📊 Analisis Pasar"
        )

        st.markdown("---")


# ======================================================
# MAIN PROGRAM
# ======================================================
def main():

    # ======================================================
    # SIDEBAR
    # ======================================================
    sidebar()

    # ======================================================
    # HEADER
    # ======================================================
    st.title(
        "📊 Analisis Pasar & Wawasan Historis"
    )

    st.write(
        """
        Eksplorasi tren harga emas dan wawasan berbasis data historis 
        Yahoo Finance.
        """
    )

    try:

        # ======================================================
        # FILTER DATA
        # ======================================================
        st.subheader("Filter Data")

        min_year = 2021
        max_year = 2026

        year_range = st.slider(
            "Pilih rentang tahun:",
            min_year,
            max_year,
            (2020, max_year)
        )

        # ======================================================
        # YAHOO FINANCE
        # ======================================================
        gold = yf.Ticker("GC=F")

        yahoo_df = gold.history(
            start="2021-06-01",
            end="2026-12-31"
        )

        # ======================================================
        # VALIDASI
        # ======================================================
        if yahoo_df.empty:

            st.error(
                "Data Yahoo Finance tidak tersedia."
            )

            return

        # ======================================================
        # RESET INDEX
        # ======================================================
        yahoo_df = yahoo_df.reset_index()

        # ======================================================
        # DATETIME
        # ======================================================
        yahoo_df['Date'] = pd.to_datetime(
            yahoo_df['Date']
        )

        # ======================================================
        # FILTER YEAR
        # ======================================================
        filtered_df = yahoo_df[
            (
                yahoo_df['Date'].dt.year >= year_range[0]
            ) &
            (
                yahoo_df['Date'].dt.year <= year_range[1]
            )
        ]

        # ======================================================
        # METRICS
        # ======================================================
        st.subheader(
            "📌 Pengukuran Harga Emas Realtime Yahoo Finance"
        )

        latest_close = filtered_df['Close'].iloc[-1]

        latest_open = filtered_df['Open'].iloc[-1]

        latest_high = filtered_df['High'].iloc[-1]

        latest_low = filtered_df['Low'].iloc[-1]

        previous_close = filtered_df['Close'].iloc[-2]

        change_percent = (
            (
                latest_close - previous_close
            ) / previous_close
        ) * 100

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:

            st.metric(
                "Harga Saat Ini",
                f"${latest_close:.2f}"
            )

        with col2:

            st.metric(
                "Harga Open",
                f"${latest_open:.2f}"
            )

        with col3:

            st.metric(
                "Harga Tertinggi",
                f"${latest_high:.2f}"
            )

        with col4:

            st.metric(
                "Harga Terendah",
                f"${latest_low:.2f}"
            )

        with col5:

            st.metric(
                "Perubahan",
                f"{change_percent:.2f}%"
            )

        # ======================================================
        # GRAFIK HARGA EMAS
        # ======================================================
        st.subheader(
            "Tren Harga Emas (Close)"
        )

        st.subheader("Tren Harga Emas (Close)")

        chart_df = filtered_df.set_index("Date")

        st.line_chart(chart_df["Close"])

        # ======================================================
        # GRAFIK VOLUME
        # ======================================================
        st.subheader(
            "Volume Perdagangan Emas Berjangka"
        )

        st.subheader("Volume Perdagangan Emas Berjangka")

        st.line_chart(chart_df["Volume"])

        # ======================================================
        # BERITA EMAS DARI NEWSAPI
        # ======================================================

        st.subheader(
            "📰 Berita Emas Terkini"
        )

        API_KEY = "484cf61f9630489789fba0776ebbcaee"

        newsapi = NewsApiClient(
            api_key=API_KEY
        )

        try:

            news = newsapi.get_everything(
                q='("gold price" OR "gold market" OR "gold trading" OR "gold futures" OR bullion)',
                language="en",
                sort_by="publishedAt",
                page_size=50
            )

            articles = news["articles"]

            if len(articles) == 0:

                st.warning(
                    "Tidak ada berita ditemukan."
                )

            else:

                news_df = pd.DataFrame([
                    {
                        "title": article["title"],
                        "source": article["source"]["name"],
                        "published": article["publishedAt"]
                    }
                    for article in articles
                ])

                st.dataframe(
                    news_df,
                    use_container_width=True
                )

                # ==========================================
                # WORD CLOUD
                # ==========================================

                st.subheader(
                    "☁️ Word Cloud Berita Emas"
                )

                text = " ".join(
                    news_df["title"]
                    .dropna()
                    .astype(str)
                )

                wordcloud = WordCloud(
                    width=1200,
                    height=600,
                    background_color="white"
                ).generate(text)

                fig_wc, ax = plt.subplots(
                    figsize=(14,6)
                )

                ax.imshow(
                    wordcloud,
                    interpolation="bilinear"
                )

                ax.axis("off")

                st.pyplot(fig_wc)

                # ==========================================
                # SENTIMENT ANALYSIS
                # ==========================================

                st.subheader(
                    "📊 Sentimen Berita Emas"
                )

                analyzer = (
                    SentimentIntensityAnalyzer()
                )

                sentiments = []

                for title in news_df["title"]:

                    score = analyzer.polarity_scores(
                        str(title)
                    )

                    if score["compound"] >= 0.05:

                        sentiments.append(
                            "Positif"
                        )

                    elif score["compound"] <= -0.05:

                        sentiments.append(
                            "Negatif"
                        )

                    else:

                        sentiments.append(
                            "Netral"
                        )

                news_df["sentiment"] = sentiments

                sentiment_count = (
                    news_df["sentiment"]
                    .value_counts()
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "Positif",
                        sentiment_count.get(
                            "Positif",
                            0
                        )
                    )

                with col2:

                    st.metric(
                        "Netral",
                        sentiment_count.get(
                            "Netral",
                            0
                        )
                    )

                with col3:

                    st.metric(
                        "Negatif",
                        sentiment_count.get(
                            "Negatif",
                            0
                        )
                    )

                fig_sent, ax = plt.subplots(
                    figsize=(2,2)
                )

                ax.pie(
                    sentiment_count.values,
                    labels=sentiment_count.index,
                    autopct="%1.1f%%",
                    startangle=90
                )

                ax.set_title(
                    "Distribusi Sentimen Berita Emas"
                )

                st.pyplot(fig_sent)

                # ======================================================
                # ANALISIS PASAR SELESAI
                # ======================================================
                st.session_state.analysis_done = True

                # ======================================================
                # TOMBOL MENUJU HALAMAN PREDIKSI HARGA
                # ======================================================
                st.markdown("---")

                st.subheader(
                    "📈 Prediksi Harga Emas"
                )

                st.info(
                    """
                    Analisis pasar telah selesai dilakukan.

                    Anda dapat melanjutkan ke halaman
                    Prediksi Harga untuk memperoleh
                    estimasi harga emas beberapa hari
                    ke depan menggunakan model
                    Deep Learning GRU.
                    """
                )

            # Analisis selesai
            st.session_state.analysis_done = True

            # ======================================================
            # TOMBOL MENUJU HALAMAN PREDIKSI HARGA
            # ======================================================

            st.markdown("---")

            col1, col2, col3 = st.columns([1,2,1])

            with col2:

                if st.button(
                    "📈 Go to Prediksi Harga",
                    use_container_width=True,
                    type="primary"
                ):
                    st.session_state.allow_prediction = True
                    st.session_state.allow_analysis = False

                    st.switch_page(
                        "pages/3_Prediksi_Harga.py"
                    )
        except Exception as e:

            st.error(
                f"Gagal mengambil berita: {e}"
            )

    except Exception as e:

        st.error(
            f"Error memuat data: {str(e)}"
        )

# ======================================================
# RUN PROGRAM
# ======================================================
if __name__ == "__main__":

    main()