import streamlit as st
import pandas as pd
import numpy as np
import tensorflow as tf
import joblib
import plotly.express as px
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import os
from pathlib import Path
from datetime import datetime, timedelta
import yfinance as yf
import sqlite3

# =================================================
# DATABASE
# =================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent

DB_PATH = BASE_DIR / "Database" / "goldbar.db"

# Buat folder jika belum ada
DB_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

conn = sqlite3.connect(
    str(DB_PATH),
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS gold_predictions (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    prediction_date TEXT,

    horizon INTEGER,

    current_price REAL,

    predicted_price REAL,

    percentage_change REAL,

    model_name TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

# =================================================
# VALIDASI HARUS DARI ANALISIS PASAR
# =================================================

if "allow_prediction" not in st.session_state:

    st.warning(
        """
        ⚠️Akses ditolak.

        Silakan buka halaman Analisis Pasar terlebih dahulu
        kemudian klik tombol
        'Go to Prediksi Harga'.
        """
    )

    st.stop()

if st.session_state.allow_prediction is not True:

    st.warning(
        """
     ⚠️Akses ditolak.

        Silakan buka halaman Analisis Pasar terlebih dahulu
        kemudian klik tombol
        'Go to Prediksi Harga'.
        """
    )

    st.stop()


# ======================================================
# SIDEBAR
# ======================================================
def sidebar():

    with st.sidebar:


        st.markdown("---")

        st.markdown(
            "## 📈 Prediksi Harga Emas"
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

    st.title("📈 Prediksi Harga Emas")
    st.write(
    "Gunakan model Deep Learning GRU untuk memprediksi harga emas jangka pendek berdasarkan hasil analisis sebelumnya."
)

    # Inisialisasi session state untuk horizon
    if 'horizon' not in st.session_state:
        st.session_state.horizon = 7

    # Load model dan scaler
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    model_path = BASE_DIR / 'Model' / 'best_model_gru.h5'
    scaler_path = BASE_DIR / 'Model' / 'scaler_close_gru.pkl'

    try:
        if not os.path.exists(model_path):
            st.error(f"File model tidak ditemukan: {model_path}")
            return
        if not os.path.exists(scaler_path):
            st.error(f"File scaler tidak ditemukan: {scaler_path}")
            return
        
        model = tf.keras.models.load_model(
            model_path,
            custom_objects={
                'mse': tf.keras.losses.MeanSquaredError(),
                'mean_squared_error': tf.keras.losses.MeanSquaredError()
            }
        )
        
        scaler = joblib.load(scaler_path)
        # =================================================
        # DATA HISTORIS YAHOO FINANCE
        # =================================================
        gold = yf.Ticker("GC=F")

        df = gold.history(
            period="5y",
            interval="1d",
            auto_adjust=False
        )

        if df.empty:
            st.error("Data Yahoo Finance gagal dimuat.")
            return

        df.reset_index(inplace=True)

        df.rename(
            columns={
                "Date": "timestamp",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume"
            },
            inplace=True
        )

        timestamp_col = "timestamp"
        
        if timestamp_col is None:
            st.error("Kolom 'timestamp' tidak ditemukan di data.")
            return
        
        if 'close' not in df.columns:
            st.error("Kolom 'close' tidak ditemukan di data.")
            return

        try:
            df[timestamp_col] = pd.to_datetime(df[timestamp_col])
        except Exception as e:
            st.error(f"Error saat mengonversi kolom {timestamp_col} ke datetime: {str(e)}")
            return

        close_prices = df['close'].values
        last_date = df[timestamp_col].iloc[-1]

        # =============================================
        # KURS USD -> IDR REALTIME
        # =============================================

        usd_idr = yf.Ticker("IDR=X")

        kurs_df = usd_idr.history(
            period="5d",
            interval="1d"
        )

        kurs_idr = float(
            kurs_df["Close"].iloc[-1]
        )

        # Evaluasi model
        st.subheader("Performa Model")
        WINDOW = 20
        close_scaled = scaler.transform(close_prices.reshape(-1, 1))
        X, y = [], []
        for i in range(len(close_scaled) - WINDOW):
            X.append(close_scaled[i:i + WINDOW])
            y.append(close_scaled[i + WINDOW])
        X = np.array(X).reshape(-1, WINDOW, 1)
        y = np.array(y).flatten()
        
        total = len(X)
        val_end = int(total * 0.85)
        X_test = X[val_end:]
        y_test = y[val_end:]
        
        y_pred_s = model.predict(X_test, verbose=0).flatten()
        y_test_true = scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()
        y_pred_true = scaler.inverse_transform(y_pred_s.reshape(-1, 1)).flatten()

        # ==========================================
        # ANALISIS TREN GRU
        # ==========================================

        trend_window = WINDOW

        recent_pred = y_pred_true[-trend_window:]

        pred_slope = np.polyfit(
            np.arange(len(recent_pred)),
            recent_pred,
            1
        )[0]

        trend_direction = (
            "📉 Turun"
            if pred_slope < 0
            else "📈 Naik"
        )
        
        rmse = np.sqrt(mean_squared_error(y_test_true, y_pred_true))
        mae = mean_absolute_error(y_test_true, y_pred_true)
        mape = np.mean(np.abs((y_test_true - y_pred_true) / y_test_true)) * 100
        r2 = r2_score(y_test_true, y_pred_true)
        
        metrics_df = pd.DataFrame({
            'Metrik': ['RMSE', 'MAE', 'MAPE', 'R2'],
            'Nilai': [rmse, mae, mape, r2]
        })
        # Format nilai ke dua angka di belakang koma tanpa pembulatan
        def format_trunc(val):
            return f"{int(val * 100) / 100:.2f}"

        metrics_df['Nilai'] = metrics_df['Nilai'].apply(format_trunc)

        fig_metrics = px.bar(metrics_df, x='Metrik', y='Nilai', 
                   labels={'Nilai': 'Nilai Metrik'},
                   text_auto=True,
                   color='Metrik',
                   color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
        fig_metrics.update_traces(textposition='outside')
        st.plotly_chart(fig_metrics, use_container_width=True)

        # ==========================================
        # GRAFIK AKTUAL VS PREDIKSI
        # ==========================================

        st.subheader(
            "📈 Perbandingan Harga Asli vs Prediksi GRU"
        )

        # Ambil tanggal yang sesuai dengan data test
        test_start_idx = len(df) - len(y_test_true)

        compare_df = pd.DataFrame({

            "Tanggal":
                df[timestamp_col]
                .iloc[test_start_idx:]
                .values,

            "Harga Asli":
                y_test_true,

            "Prediksi GRU":
                y_pred_true
        })

        fig_compare = px.line(

            compare_df,

            x="Tanggal",

            y=[
                "Harga Asli",
                "Prediksi GRU"
            ],

            title=
            "Perbandingan Harga Asli dan Prediksi GRU"
        )

        fig_compare.update_layout(

            hovermode="x unified",

            height=500,

            legend_title="Keterangan"
        )

        fig_compare.update_traces(
            line=dict(width=2)
        )

        st.plotly_chart(
            fig_compare,
            use_container_width=True
        )

        # Pilih mode prediksi
        st.subheader("Pilih Mode Prediksi")
        mode = st.radio("Pilih cara menentukan horizon prediksi:", 
                      ("Custom via Slider", "Preset", "Pilih Tanggal"))

        if mode == "Custom via Slider":
            st.session_state.horizon = st.slider("Pilih horizon prediksi (hari):", 
                                              1, 21, st.session_state.horizon)
        elif mode == "Preset":
            st.write("Pilih preset horizon:")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("3 Hari"):
                    st.session_state.horizon = 3
            with col2:
                if st.button("7 Hari"):
                    st.session_state.horizon = 7
            with col3:
                if st.button("14 Hari"):
                    st.session_state.horizon = 14
            with col4:
                if st.button("21 Hari"):
                    st.session_state.horizon = 21
        else:
            st.write(f"Tanggal terakhir data Yahoo Finance: {last_date.strftime('%Y-%m-%d')}")
            selected_date = st.date_input(
                

            "📅 Pilih Tanggal Prediksi",

            value=last_date.date() + timedelta(days=7),

            min_value=last_date.date() + timedelta(days=1),

            max_value=last_date.date() + timedelta(days=21)
        )
            horizon = (selected_date - last_date.date()).days
            if horizon <= 0:
                st.error("Tanggal yang dipilih harus setelah tanggal terakhir di data Yahoo Finance!")
                return
            st.session_state.horizon = horizon

        st.write(f"Horizon yang dipilih: {st.session_state.horizon} hari")

        # =============================================
        # FILTER TAMPILAN HARGA
        # =============================================

        st.markdown("---")
        st.subheader("📈 Harga Emas Realtime Yahoo Finance")

        col1, col2, col3 = st.columns(3)

        with col1:
            asset = st.selectbox(
                "Aset",
                ["Gold"]
            )

        with col2:
            currency = st.selectbox(
                "Mata Uang",
                ["USD", "IDR"]
            )

        with col3:
            unit = st.selectbox(
                "Satuan",
                ["oz", "gr"]
            )

        if st.button("Dapatkan Prediksi"):
            horizon = st.session_state.horizon
            if len(close_prices) < WINDOW:
                st.error(f"Data tidak cukup untuk prediksi (minimum {WINDOW} hari).")
                return
            last_sequence = close_prices[-WINDOW:]
            last_sequence_scaled = scaler.transform(last_sequence.reshape(-1, 1))
            X = last_sequence_scaled.reshape(1, WINDOW, 1)

            predictions = []
            current_sequence = X.copy()
            for _ in range(horizon):
                pred = model.predict(current_sequence, verbose=0)
                predictions.append(pred[0, 0])
                current_sequence = np.roll(current_sequence, -1)
                current_sequence[0, -1, 0] = pred

            predictions = scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()
            predictions = np.maximum(predictions, 0)

            last_close = close_prices[-1]
            last_pred = predictions[-1]
            percent_change = ((last_pred - last_close) / last_close) * 100

            # =============================================
            # SIMPAN RIWAYAT PREDIKSI
            # =============================================

            cursor.execute(
                """
                INSERT INTO gold_predictions
                (
                    prediction_date,
                    horizon,
                    current_price,
                    predicted_price,
                    percentage_change,
                    model_name
                )
                VALUES
                (
                    ?,?,?,?,?,?
                )
                """,
                (
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    horizon,
                    float(last_close),
                    float(last_pred),
                    float(percent_change),
                    "GRU"
                )
            )

            conn.commit()
            
            st.subheader("Perubahan Harga Prediksi")
            st.metric(
                label="Perubahan Harga (%)",
                value=f"{percent_change:.2f}%",
                delta=f"{percent_change:.2f}% {'naik' if percent_change >= 0 else 'turun'}"
            )

            future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), 
                                       periods=horizon, freq='D')
            pred_df = pd.DataFrame({
                'Tanggal': future_dates,
                'Prediksi Harga (USD)': predictions
            })
            # st.write("**Tabel Prediksi Harga**")
            # st.dataframe(pred_df)

            # =====================================================
            # DATA HISTORIS
            # =====================================================
            last_30_days = close_prices[-30:]
            historical_df = pd.DataFrame({
                "Tanggal": df[timestamp_col].tail(30).values,
                "Harga": last_30_days,
                "Tipe": "Historis"
            })

            # =====================================================
            # DATA PREDIKSI
            # =====================================================
            prediction_df = pd.DataFrame({
                "Tanggal": future_dates,
                "Harga": predictions,
                "Tipe": "Prediksi"
            })

            # =====================================================
            # GABUNGKAN DATA
            # =====================================================
            plot_df = pd.concat(
                [historical_df, prediction_df],
                ignore_index=True
            )

            # =============================================
            # KONVERSI SATUAN
            # =============================================

            plot_df["USD_OZ"] = plot_df["Harga"]

            plot_df["USD_GR"] = (
                plot_df["Harga"] / 31.1035
            )

            plot_df["IDR_OZ"] = (
                plot_df["Harga"] * kurs_idr
            )

            plot_df["IDR_GR"] = (
                plot_df["Harga"] * kurs_idr
            ) / 31.1035

            # =============================================
            # SESUAIKAN TAMPILAN BERDASARKAN DROPDOWN
            # =============================================

            if currency == "USD" and unit == "oz":

                plot_df["display_price"] = plot_df["USD_OZ"]
                y_title = "Harga Emas (USD/oz)"
                prefix = "$"

            elif currency == "USD" and unit == "gr":

                plot_df["display_price"] = plot_df["USD_GR"]
                y_title = "Harga Emas (USD/gr)"
                prefix = "$"

            elif currency == "IDR" and unit == "oz":

                plot_df["display_price"] = plot_df["IDR_OZ"]
                y_title = "Harga Emas (IDR/oz)"
                prefix = "Rp "

            else:

                plot_df["display_price"] = plot_df["IDR_GR"]
                y_title = "Harga Emas (IDR/gr)"
                prefix = "Rp "

            st.subheader("Grafik Prediksi vs Historis")

            fig = px.line(
                plot_df,
                x="Tanggal",
                y="display_price",
                color="Tipe",
                markers=True,
                title=f"Prediksi {horizon} Hari vs Harga Historis"
            )

            # =====================================================
            # FORMAT TAMPILAN
            # =====================================================
            fig.update_layout(
                hovermode="x unified",
                legend_title="Tipe Data",
                xaxis_title="Tanggal",
                yaxis_title=y_title,
                height=550
            )

            # Format tanggal
            fig.update_xaxes(
                tickformat="%d-%b-%Y"
            )

            # Format harga USD
            if currency == "USD":
    
                fig.update_yaxes(
                    tickprefix="$ ",
                    tickformat=",.2f",
                    separatethousands=True
                )

            else:

                fig.update_yaxes(
                    tickprefix="Rp ",
                    tickformat=",.0f",
                    separatethousands=True
                )

            # Pertebal garis tanpa mengubah warna
            # =============================================
            # HOVER SESUAI PILIHAN USER
            # =============================================

            if currency == "USD" and unit == "oz":

                hover_template = (
                    "<b>%{x}</b><br><br>"
                    "Harga : $%{y:,.2f}/oz"
                    "<extra></extra>"
                )

            elif currency == "USD" and unit == "gr":

                hover_template = (
                    "<b>%{x}</b><br><br>"
                    "Harga : $%{y:,.2f}/gr"
                    "<extra></extra>"
                )

            elif currency == "IDR" and unit == "oz":

                hover_template = (
                    "<b>%{x}</b><br><br>"
                    "Harga : Rp%{y:,.0f}/oz"
                    "<extra></extra>"
                )

            else:

                hover_template = (
                    "<b>%{x}</b><br><br>"
                    "Harga : Rp%{y:,.0f}/gr"
                    "<extra></extra>"
                )

            fig.update_traces(
                line=dict(width=3),
                hovertemplate=hover_template
            )
                        

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            # =============================================
            # REKOMENDASI BELI EMAS
            # =============================================
            st.markdown("---")
            st.subheader("📢 Rekomendasi Investasi Emas")

            # =============================================
            # SESUAIKAN MATA UANG DAN SATUAN
            # =============================================

            if currency == "USD" and unit == "oz":

                current_price = last_close
                predicted_price = last_pred

                simbol = "$"
                satuan = "oz"

            elif currency == "USD" and unit == "gr":

                current_price = last_close / 31.1035
                predicted_price = last_pred / 31.1035

                simbol = "$"
                satuan = "gr"

            elif currency == "IDR" and unit == "oz":

                current_price = last_close * kurs_idr
                predicted_price = last_pred * kurs_idr

                simbol = "Rp"
                satuan = "oz"

            else:

                current_price = (
                    last_close * kurs_idr
                ) / 31.1035

                predicted_price = (
                    last_pred * kurs_idr
                ) / 31.1035

                simbol = "Rp"
                satuan = "gr"

            st.write(
                f"Harga saat ini : {simbol} {current_price:,.2f}/{satuan}"
            )

            st.write(
                f"Harga prediksi : {simbol} {predicted_price:,.2f}/{satuan}"
            )

            if predicted_price < current_price:

                selisih = current_price - predicted_price

                persen = (
                    selisih / current_price
                ) * 100

                st.success(
                    f"""
            ### ✅ Waktu Membeli Emas
           **Harga Saat Ini :**
            {simbol} {current_price:,.2f}/{satuan}

            **Harga Prediksi :**
            {simbol} {predicted_price:,.2f}/{satuan}

            **Potensi Penurunan :** {persen:.2f}%

            Harga emas diperkirakan turun sebesar
            **{simbol} {selisih:,.2f}/{satuan}** sehingga dapat menjadi
            peluang yang baik untuk melakukan pembelian.
            """
                )

            elif predicted_price > current_price:
    
                selisih = (
                    predicted_price - current_price
                )

                persen = (
                    selisih / current_price
                ) * 100

                st.warning(
                    f"""
            ### ⚠️ Belum Saatnya Membeli Emas

            **Harga Saat Ini :**
            {simbol} {current_price:,.2f}/{satuan}

            **Harga Prediksi :**
            {simbol} {predicted_price:,.2f}/{satuan}

            **Potensi Kenaikan :**
            {persen:.2f}%

            Harga emas diperkirakan naik sebesar
            **{simbol} {selisih:,.2f}/{satuan}**

            sehingga harga beli menjadi lebih mahal.

            Disarankan menunggu koreksi harga terlebih dahulu.
            """
                )
            else:
    
                st.info(
                    f"""
            ### ℹ️ Harga Emas Relatif Stabil

            **Harga Saat Ini :**
            {simbol} {current_price:,.2f}

            **Harga Prediksi :**
            {simbol} {predicted_price:,.2f}

            Perubahan harga tidak signifikan sehingga
            investor dapat mempertimbangkan keputusan
            berdasarkan strategi masing-masing.
            """
                )

    
        # ======================================================
        # ANALISIS PASAR SELESAI
        # ======================================================
        st.session_state.analysis_done = True

        # ======================================================
        # TOMBOL MENUJU HALAMAN EDUKASI FAQ
        # ======================================================
        st.markdown("---")

        st.subheader(
                    "📚 Edukasi FAQ"
                )

        st.info(
                    """
                    Prediksi Harga telah selesai dilakukan.

                    Anda dapat melanjutkan ke halaman
                    Edukasi FAQ untuk informasi tentang investasi emas sebagai aset safe-haven,
                    penjelasan model GRU yang dilatih dengan data Yahoo Finance, dan FAQ
        
                    """
                )

        # Prediksi selesai
        st.session_state.analysis_done = True

        # ======================================================
        # TOMBOL MENUJU HALAMAN EDUKASI FAQ
        # ======================================================

        st.markdown("---")

        col1, col2, col3 = st.columns([1,2,1])

        with col2:

                if st.button(
                    "📚 Go to Edukasi FAQ",
                    use_container_width=True,
                    type="primary"
                ):
                    st.session_state.allow_faq = True
                    st.session_state.allow_prediction = False

                    st.switch_page(
                        "pages/4_Edukasi_FAQ.py"
                    )

    except Exception as e:
        st.error(f"Error memuat data atau model: {str(e)}")
        st.write(f"Silakan cek file di {model_path}, dan {scaler_path}")

if __name__ == "__main__":
    main()
