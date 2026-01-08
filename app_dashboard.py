import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

# Konfigurasi Halaman (Industrial Dark Mode Style)
st.set_page_config(page_title="CIP-ENGINE Executive Dashboard", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #008080; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ CIP-ENGINE: Arsitektur Digital Twin & AI Predictive")
st.write("---")

# Sidebar untuk Skenario 1: Fleksibilitas M1
st.sidebar.header("⚙️ Kontrol Simulasi M1")
beta = st.sidebar.slider("Karakteristik Keausan (Parameter Beta)", 1.0, 3.5, 2.0, help="Geser untuk mengubah profil degradasi aset")
biaya_downtime = st.sidebar.number_input("Biaya Downtime per Hari (Juta IDR)", value=100)

# --- Logika Simulasi (Menghubungkan M1 ke M3 & M4) ---
days = np.arange(1, 366)
# Simulasi kurva degradasi berbasis Weibull (M1)
vibration = 0.8 + (days/100)**beta + np.random.normal(0, 0.05, len(days))
# Ambang batas bahaya (M3 logic)
threshold = 4.5
failure_day = np.where(vibration > threshold)[0][0] + 1 if any(vibration > threshold) else 365

# --- LAYOUT DASHBOARD ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Prediksi Degradasi & RUL (M3)")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(days, vibration, label="Prediksi Vibrasi M1", color='#008080', linewidth=2)
    ax.axhline(y=threshold, color='red', linestyle='--', label="Zona Kritis (Alarm)")
    
    # Highlight area degradasi
    ax.fill_between(days, vibration, threshold, where=(vibration > threshold), color='red', alpha=0.3)
    
    ax.set_xlabel("Hari Operasional (365 Hari)")
    ax.set_ylabel("Vibrasi (mm/s RMS)")
    ax.legend()
    ax.grid(alpha=0.2)
    st.pyplot(fig)
    
    st.info(f"💡 **Analisis M3:** Algoritma mendeteksi aset memasuki zona kritis pada **Hari ke-{failure_day}**.")

with col2:
    st.subheader("💰 Valuasi Risiko Ekonomi (M4)")
    # Kalkulasi dampak risiko berdasarkan pergeseran Beta
    total_risk = (365 - failure_day) * biaya_downtime
    st.metric(label="Potensi Kerugian Finansial", value=f"Rp {total_risk} Juta", delta=f"{beta} Beta Index")
    
    st.write("---")
    st.subheader("🛠️ Optimasi & Eksekusi (M5-M6)")
    st.write("Prioritas Intervensi: **TINGGI (Rank 1)**")
    
    # Skenario 3: Tombol Eksekusi M6
    if st.button("🚀 GENERATE WORK ORDER"):
        with st.spinner('Mengirim instruksi ke ERP lapangan...'):
            time.sleep(2)
            st.success("✅ SUCCESS: Work Order otomatis telah dikirim ke sistem ERP lapangan.")
            st.balloons()

# Menampilkan Gambar Hasil Eksperimen yang sudah ada di folder Sodaraku
st.write("---")
st.subheader("📁 Arsip Validasi Skenario (Data Folder)")
exp_col1, exp_col2, exp_col3 = st.columns(3)
with exp_col1:
    st.image("grafik_rul_standar_normal.png", caption="Skenario Normal")
with exp_col2:
    st.image("grafik_rul_ekstrem_atas_keras.png", caption="Skenario Beban Berat")
with exp_col3:
    st.image("grafik_rul_ekstrem_bawah_ideal.png", caption="Skenario Optimal")