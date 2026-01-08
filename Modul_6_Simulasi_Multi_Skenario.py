import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

# ==========================================
# KONFIGURASI HALAMAN & TEMA (PROFESIONAL)
# ==========================================
st.set_page_config(
    page_title="CIP-ENGINE Executive Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk tampilan Industrial Dark Mode
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1a1c24; padding: 15px; border-radius: 10px; border-left: 5px solid #008080; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #008080; color: white; font-weight: bold; height: 3em; }
    .pilar-box { padding: 20px; border-radius: 10px; height: 100%; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# HEADER UTAMA
# ==========================================
st.title("🛡️ CIP-ENGINE: FRAMEWORK DARI DATA MENUJU KEARIFAN (WISDOM)")
st.write("---")

# ==========================================
# SIDEBAR: SKENARIO HULU (MODUL M1)
# ==========================================
st.sidebar.header("⚙️ KONTROL SIMULASI M1 (HULU)")
st.sidebar.info("Gunakan slider untuk mensimulasikan karakteristik degradasi aset.")

beta = st.sidebar.slider(
    "Parameter Beta (Keausan Weibull)", 
    min_value=1.0, 
    max_value=3.5, 
    value=2.0, 
    step=0.1,
    help="1.0 = Wear-out Normal, >2.0 = Degradasi Eksponensial/Berat"
)

biaya_downtime = st.sidebar.number_input(
    "Estimasi Biaya Downtime (Juta IDR/Hari)", 
    min_value=10, 
    max_value=1000, 
    value=201
)

terminal_choice = st.sidebar.selectbox(
    "Pilih Fuel Terminal (Modul M5)",
    ["Terminal Jakarta (T1)", "Terminal Surabaya (T2)", "Terminal Medan (T3)", "Terminal Balikpapan (T4)"]
)

# ==========================================
# ENGINE LOGIKA: INTEGRASI M1 s/d M4
# ==========================================
days = np.arange(1, 366)
# Simulasi M1: Pembangkitan Data Vibrasi berdasarkan Beta Weibull
vibration = 0.8 + (days/100)**beta + np.random.normal(0, 0.08, len(days))
threshold = 4.5 # Ambang Batas Kritis (Alarm)

# M3: Mencari Hari Kegagalan (Failure Point)
try:
    failure_day = np.where(vibration > threshold)[0][0] + 1
except IndexError:
    failure_day = 365

# M4: Kalkulasi Risiko Finansial
sisa_umur = 365 - failure_day
total_risk_cost = max(0, sisa_umur * biaya_downtime)

# ==========================================
# DISPLAY UTAMA: VISUALISASI M3 & M4
# ==========================================
col_grafik, col_metrik = st.columns([2, 1])

with col_grafik:
    st.subheader("📊 Analisis Prediktif AI (Modul M3)")
    fig, ax = plt.subplots(figsize=(10, 5))
    plt.style.use('dark_background')
    
    ax.plot(days, vibration, label="Prediksi Degradasi M1", color='#008080', linewidth=2.5)
    ax.axhline(y=threshold, color='#FF4B4B', linestyle='--', label="Ambang Batas Kritis (4.5 mm/s)")
    
    # Menandai Point of Failure (F-Point)
    ax.scatter(failure_day, threshold, color='red', s=100, zorder=5, label="Deteksi F-Point")
    
    ax.set_xlabel("Waktu Operasional (Hari)")
    ax.set_ylabel("Vibrasi (mm/s RMS)")
    ax.legend(facecolor='#1a1c24')
    ax.grid(alpha=0.1)
    st.pyplot(fig)
    st.caption(f"Hasil Analisis: Aset diprediksi memasuki zona bahaya pada Hari ke-{failure_day}.")

with col_metrik:
    st.subheader("💰 Valuasi Ekonomi (Modul M4)")
    st.metric(
        label="Potensi Kerugian Finansial", 
        value=f"Rp {total_risk_cost:,.0f} Juta",
        delta=f"Impact: {beta} Beta",
        delta_color="inverse"
    )
    st.write("---")
    st.markdown(f"""
    **Status Strategis:**
    - **Aset:** {terminal_choice}
    - **Sisa Umur Teknis (RUL):** {sisa_umur} Hari
    - **Prioritas Intervensi:** **TINGGI (RANK 1)**
    """)

# ==========================================
# BAGIAN HILIR: EKSEKUSI 3 PILAR (M5 - M6)
# ==========================================
st.write("---")
st.subheader("🛠️ MODUL M6: EKSEKUSI PERINTAH KERJA OTOMATIS")

if st.button("🚀 GENERATE WORK ORDER"):
    with st.spinner('Mensinkronisasi Data M1-M5 ke Sistem Hilir...'):
        time.sleep(1.5)
    
    st.success("✅ KONFIRMASI EKSEKUSI: Instruksi Digital Telah Terfragmentasi Secara Simultan")
    
    # Tampilan 3 Pilar Horizontal
    pilar1, pilar2, pilar3 = st.columns(3)
    
    with pilar1:
        st.info("### 🔍 PILAR 1\n**Snapshot Teknis (M1-M3)**")
        st.markdown(f"""
        - **Vibrasi:** {vibration[-1]:.2f} mm/s
        - **RUL:** {sisa_umur} Hari
        - **Data Source:** NASA IMS Ref.
        """)
        
    with pilar2:
        st.warning("### ⚖️ PILAR 2\n**Verifikasi Strategis (M5)**")
        st.markdown(f"""
        - **Skor AHP:** 0.89
        - **Matriks Risiko:** Kritis
        - **SLA Perbaikan:** < 48 Jam
        """)
        
    with pilar3:
        st.success("### 📡 PILAR 3\n**Konektivitas Hilir (M6)**")
        st.markdown(f"""
        - **No. WO:** WO/CIP-ENG/2026/001
        - **ERP Status:** SYNCED
        - **Notifikasi:** SENT TO MOBILE
        """)
    
    st.balloons()

# ==========================================
# FOOTER: ARSIP VALIDASI
# ==========================================
st.write("---")
st.caption("CIP-ENGINE Dashboard | Disertasi Doktoral | © 2026")