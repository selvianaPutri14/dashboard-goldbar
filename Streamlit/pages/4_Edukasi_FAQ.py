import streamlit as st

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Edukasi FAQ",
    page_icon="📚",
    layout="wide"
)

# ======================================================
# VALIDASI HARUS DARI PREDIKSI HARGA
# ======================================================

if "allow_faq" not in st.session_state:

    st.error(
        """
        🚫 Akses ditolak.

        Silakan buka halaman Prediksi Harga terlebih dahulu
        kemudian klik tombol
        'Go to Edukasi FAQ'.
        """
    )


    st.stop()

if st.session_state.allow_faq is not True:

    st.error(
        """
        🚫 Akses ditolak.

        Silakan buka halaman Prediksi Harga terlebih dahulu
        kemudian klik tombol
        'Go to Edukasi FAQ'.
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
            "## 📚 Edukasi FAQ"
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
    st.title("📚 Edukasi & FAQ")

    st.write(
        """
        Pelajari dasar investasi emas, cara kerja sistem
        prediksi GoldBar, dan berbagai pertanyaan umum
        mengenai analisis harga emas.
        """
    )

    # ======================================================
    # CONTENT
    # ======================================================
    st.markdown("""
    ### Tentang Investasi Emas

    Emas adalah aset safe-haven yang populer di tengah 
    ketidakpastian ekonomi. Harga emas global melonjak 
    karena beberapa faktor seperti kebijakan tarif AS dan aksi beli bank sentral.

    ### Bagaimana GoldBar Bekerja?

    Kami menggunakan model **GRU (Gated Recurrent Unit)**, 
    sebuah algoritma Deep Learning, untuk memprediksi 
    harga emas berdasarkan data historis sejak tahun 2021. 

    Model ini dilatih menggunakan data realtime dan 
    historis dari Yahoo Finance untuk menghasilkan 
    prediksi harga emas jangka pendek secara interaktif.

    ### FAQ

    #### 1. Seberapa akurat prediksi kami?

    Akurasi prediksi tergantung pada volatilitas pasar 
    dan kualitas data. Model kami dievaluasi menggunakan 
    metrik seperti:

    - MAE (Mean Absolute Error)
    - RMSE (Root Mean Squared Error)
    - MAPE (Mean Absolute Percentage Error)
    - R² Score

    untuk memastikan kualitas model prediksi.

    #### 2. Apa batasan model ini?

    - Ketidakpastian ekonomi global dapat memengaruhi akurasi.
    - Prediksi jangka pendek (1–21 hari) lebih stabil dibandingkan jangka panjang.
    - Model ini merupakan sistem pendukung keputusan dan bukan pengganti saran keuangan profesional.

    #### 3. Bagaimana cara terbaik berinvestasi emas?

    - Pantau tren harga emas secara berkala.
    - Analisis sentimen pasar dan berita global.
    - Gunakan strategi diversifikasi portofolio.
    - Investasikan sesuai profil risiko masing-masing.

    #### 4. Apa itu Yahoo Finance?

    Yahoo Finance adalah platform data keuangan global 
    yang menyediakan informasi realtime pasar saham, 
    komoditas, mata uang, dan logam mulia seperti emas.

    #### 5. Mengapa harga emas selalu berubah?

    Harga emas dipengaruhi oleh:

    - Inflasi
    - Nilai tukar dolar AS
    - Suku bunga
    - Kondisi geopolitik
    - Permintaan pasar global
    - Kebijakan bank sentral

    #### 6. Apa keuntungan menggunakan GoldBar?

    - Visualisasi harga emas realtime
    - Prediksi berbasis AI Deep Learning
    - Analisis historis interaktif
    - Dashboard modern dan mudah digunakan
    """)

    # ======================================================
    # EDUKASI FAQ SELESAI
    # ======================================================
    st.session_state.analysis_done = True

        # ======================================================
        # TOMBOL MENUJU HALAMAN FEEDBACK
        # ======================================================
    st.markdown("---")

    st.subheader(
                    "💬 Feedback"
                )

    st.info(
                    """
                    Edukasi FAQ telah selesai dilakukan.

                    Anda dapat melanjutkan ke halaman
                    Feedback untuk memberikan masukan terhadap 
                    dashboard GoldBar untuk membantu meningkatkan kualitas sistem.
        
                    """
                )

        # Edukasi FAQ selesai
    st.session_state.analysis_done = True

        # ======================================================
        # TOMBOL MENUJU HALAMAN FEEDBACK
        # ======================================================

    st.markdown("---")

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

                if st.button(
                    "💬 Go to Feedback",
                    use_container_width=True,
                    type="primary"
                ):
                    
                    st.session_state.allow_feedback = True
                    st.session_state.allow_faq = False

                    st.switch_page(
                        "pages/5_Feedback.py"
                    )
                    

# ======================================================
# RUN APP
# ======================================================
if __name__ == "__main__":

    main()
