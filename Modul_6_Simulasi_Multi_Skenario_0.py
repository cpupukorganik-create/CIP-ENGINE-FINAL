import pandas as pd
import numpy as np
from scipy.stats import weibull_min
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import random

# ==============================================================================
# 0. KONSTANTA GLOBAL (SAMA SEPERTI MODUL 1)
# ==============================================================================
TOTAL_HARI_SIMULASI = 1095  # 3 Tahun
N_ASET = 5  
ASSET_NAMES = [f'ASET_FT_{i+1}' for i in range(N_ASET)]

# Tabel untuk menyimpan hasil akhir semua skenario
FINAL_RESULTS_COMPARISON = []

# ==============================================================================
# 1. PARAMETER SKENARIO MULTI-SKENARIO
# ==============================================================================

# Definisikan parameter yang akan diuji untuk setiap skenario
SCENARIOS = {
    'EKSTREM_BAWAH_IDEAL': {
        'WEIBULL_BETA': 4.5,      # Beta Tinggi: Wear-out lambat
        'MTBF_RANGE': (400, 500), # MTBF Tinggi
        'DEGRADATION_FACTOR': 3.0 # Kenaikan sinyal lambat
    },
    'STANDAR_NORMAL': {
        'WEIBULL_BETA': 3.5,      # Beta Sedang
        'MTBF_RANGE': (250, 350), # MTBF Sedang
        'DEGRADATION_FACTOR': 5.0 # Kenaikan sinyal normal
    },
    'EKSTREM_ATAS_KERAS': {
        'WEIBULL_BETA': 2.0,      # Beta Rendah: Wear-out cepat
        'MTBF_RANGE': (150, 200), # MTBF Rendah
        'DEGRADATION_FACTOR': 8.0 # Kenaikan sinyal cepat
    }
}

# ==============================================================================
# 2. FUNGSI INTI MODUL (Integrasi Modul 1 s/d 5)
# ==============================================================================

def run_single_scenario(scenario_name, params):
    """
    Fungsi ini menjalankan seluruh proses Modul 1 sampai 5 untuk satu skenario.
    """
    print(f"\n========================================================")
    print(f"       >>> MENGINISIASI SKENARIO: {scenario_name} <<<       ")
    print(f"========================================================")

    # --- SIMULASI MODUL 1 (Generator Data) ---
    print(" [1] Modul 1: Membangkitkan data sintetis...")
    
    # Menghasilkan Data Statis (MTBF disesuaikan dengan skenario)
    static_data = {
        'AssetID': ASSET_NAMES,
        'Biaya_COF': np.random.randint(80000000, 150000000, N_ASET),
        'Rata2_MTBF_Historis': np.random.randint(params['MTBF_RANGE'][0], params['MTBF_RANGE'][1], N_ASET)
    }
    static_df = pd.DataFrame(static_data)

    # Menghasilkan Data Kegagalan (Weibull Beta disesuaikan)
    historical_data = []
    for _, row in static_df.iterrows():
        alpha = row['Rata2_MTBF_Historis'] / 0.9 
        failure_times = weibull_min.rvs(params['WEIBULL_BETA'], loc=0, scale=alpha, size=5)
        for t in failure_times:
            if t < TOTAL_HARI_SIMULASI:
                historical_data.append({'AssetID': row['AssetID'], 'Tanggal_Kejadian': pd.to_datetime('2022-01-01') + pd.Timedelta(days=int(t)), 'Biaya_COF': row['Biaya_COF'], 'Downtime_Hari': random.randint(5, 10)})
    historical_df = pd.DataFrame(historical_data).sort_values('Tanggal_Kejadian').reset_index(drop=True)

    # Menghasilkan Data Sensor (Faktor Degradasi disesuaikan)
    sensor_data = []
    failure_points = historical_df.copy()
    start_date = pd.to_datetime('2022-01-01')
    
    for hari in range(1, TOTAL_HARI_SIMULASI + 1):
        current_date = start_date + pd.Timedelta(days=hari)
        for asset_id in ASSET_NAMES:
            getaran_base = np.random.normal(loc=5.0, scale=0.5) 
            future_failures = failure_points[
                (failure_points['AssetID'] == asset_id) & (failure_points['Tanggal_Kejadian'] > current_date) &
                (failure_points['Tanggal_Kejadian'] <= current_date + pd.Timedelta(days=30))
            ]
            if not future_failures.empty:
                days_to_failure = (future_failures['Tanggal_Kejadian'].iloc[0] - current_date).days
                if days_to_failure > 0:
                    # Menggunakan Faktor Degradasi Skenario
                    degradation_factor = params['DEGRADATION_FACTOR'] * np.exp(-(days_to_failure / 15)) 
                    getaran_base += degradation_factor  
            sensor_data.append({'Tanggal_Waktu': current_date, 'AssetID': asset_id, 'Getaran_RMS': max(getaran_base, 0), 'Suhu_Bearing_C': np.random.normal(loc=60, scale=1.5)})
    sensor_df = pd.DataFrame(sensor_data)

    # --- MODUL 2 (FMECA) - Hanya untuk penentuan fokus kritis (tidak diulang per skenario) ---
    # FMECA hasilnya cenderung statis. Kita asumsikan aset kritis teridentifikasi.

    # --- MODUL 3 (Prediktif RUL) ---
    print(" [2] Modul 3: Melatih model prediksi RUL...")
    
    # Pre-processing: Hitung RUL (logika Modul 3)
    def calculate_rul(sensor_df, historical_df):
        df = sensor_df.copy(); df['RUL'] = 9999 
        for asset_id in df['AssetID'].unique():
            asset_failures = historical_df[historical_df['AssetID'] == asset_id].sort_values('Tanggal_Kejadian')
            asset_data = df[df['AssetID'] == asset_id].copy()
            for i in range(len(asset_failures)):
                failure_date = asset_failures.iloc[i]['Tanggal_Kejadian']
                start_date = failure_date - pd.Timedelta(days=60)
                mask = (asset_data['Tanggal_Waktu'] >= start_date) & (asset_data['Tanggal_Waktu'] <= failure_date)
                rul_values = (failure_date - asset_data.loc[mask, 'Tanggal_Waktu']).dt.days
                asset_data.loc[mask, 'RUL'] = np.minimum(asset_data.loc[mask, 'RUL'], rul_values)
            df.loc[df['AssetID'] == asset_id, 'RUL'] = asset_data['RUL']
        return df[df['RUL'] < 9999].reset_index(drop=True)

    df_rul_calculated = calculate_rul(sensor_df, historical_df)
    
    # Pelatihan Model (logika Modul 3)
    features = ['Getaran_RMS', 'Suhu_Bearing_C'] 
    if df_rul_calculated.empty: # Cek jika tidak ada kegagalan yang cukup terdeteksi
        print("   [Peringatan]: Tidak cukup data RUL untuk dilatih. Melewati skenario ini.")
        return None 
        
    X = df_rul_calculated[features]; Y = df_rul_calculated['RUL']
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
    model = LinearRegression(); model.fit(X_train, Y_train)
    Y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(Y_test, Y_pred)); r2 = r2_score(Y_test, Y_pred)
    
    # --- MODUL 4 (Decision Maker) ---
    print(" [3] Modul 4: Menghitung Risiko Dinamis dan Keputusan...")
    
    # Simulasi Decision Input (membuat DataFrame yang menggabungkan Prediksi RUL)
    df_decision_data = pd.DataFrame({
        'RUL_Aktual_Hari': Y_test.reset_index(drop=True),
        'RUL_Prediksi_Hari': Y_pred.round(2)
    })
    
    # Hanya mengambil 1 aset kritis dan merata-ratakan COF-nya
    COF_IDR_AVG = static_df['Biaya_COF'].mean() 
    k_sensitivity = 0.15 
    
    df_decision_data['POF_Prediksi'] = np.exp(-k_sensitivity * df_decision_data['RUL_Prediksi_Hari']) 
    df_decision_data['Risk_Score_IDR'] = df_decision_data['POF_Prediksi'] * COF_IDR_AVG

    # --- MODUL 5 (Analisis Gap) ---
    print(" [4] Modul 5: Melakukan Analisis Gap dan Validasi...")
    
    # Validasi Akurasi (Hasil RMSE dan R2) sudah didapat dari Modul 3.
    
    # Analisis Gap
    baseline_cost = historical_df['Biaya_COF'].sum()
    baseline_total_downtime = historical_df['Downtime_Hari'].sum()
    total_time = 365 * 3 * N_ASET 
    baseline_availability = (total_time - baseline_total_downtime) / total_time
    
    # Biaya Digital RBM (Dianggap konstan per aset)
    PM_COST_PER_ASSET = 25000000 
    SENSOR_COST_PER_ASSET = 5000000
    digital_total_cost = (PM_COST_PER_ASSET + SENSOR_COST_PER_ASSET) * N_ASET
    digital_total_downtime = 2 * N_ASET # Asumsi PM butuh 2 hari/aset
    digital_availability = (total_time - digital_total_downtime) / total_time
    
    gap_cost_saving = baseline_cost - digital_total_cost
    
    # Menyimpan hasil skenario ini
    return {
        'Skenario': scenario_name,
        'Beta_Weibull': params['WEIBULL_BETA'],
        'RUL_RMSE': rmse,
        'R2_Score': r2,
        'Penghematan_IDR_Juta': gap_cost_saving / 1000000,
        'Penghematan_Persen': (gap_cost_saving / baseline_cost) * 100 if baseline_cost > 0 else 0,
        'Peningkatan_Availability_Persen': (digital_availability - baseline_availability) * 100
    }

# ==============================================================================
# 3. EKSEKUSI UTAMA ORCHESTRATOR
# ==============================================================================

if __name__ == '__main__':
    
    # Loop melalui semua skenario yang telah didefinisikan
    for name, params in SCENARIOS.items():
        result = run_single_scenario(name, params)
        if result:
            FINAL_RESULTS_COMPARISON.append(result)

    print("\n\n========================================================")
    print("         >>> LAPORAN AKHIR SIMULASI ROBUSTNESS <<<        ")
    print("========================================================\n")
    
    final_df = pd.DataFrame(FINAL_RESULTS_COMPARISON)
    
    # Format output untuk Bab 4 dan Jurnal
    print(final_df.to_markdown(index=False, floatfmt=".2f"))
    
    # --- INTERPRETASI FINAL ---
    print("\n[INTERPRETASI MODUL 6]:")
    print("1. RUL_RMSE (Error Prediksi) harus konsisten rendah di semua skenario untuk membuktikan model bersifat ROBUST.")
    print("2. Penghematan Persen harus TERTINGGI pada skenario EKSTREM ATAS (Operasi Keras) karena di sinilah RBM Digital paling efektif mencegah kegagalan yang mahal.")