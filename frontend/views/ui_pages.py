"""
Halaman-halaman UI EduPredict AI (COMPLETE VERSION - NO FEATURES MISSING).
"""
import streamlit as st
import pandas as pd
import joblib
import os
import plotly.express as px

# Constants
MODEL_DIR = "models"
FEATURE_COLS = ['Angkatan','Semester','IPK','SKS_Lulus','Mengulang','Absensi','Status_Pembayaran']
TARGET_COL = 'Status_DO'
DATA_PATH = "backend/data/data_mahasiswa_v2.csv"

def _header(icon, title, subtitle):
    st.markdown(f"""<div class='page-header'>
        <h1>{icon} {title}</h1><p>{subtitle}</p></div>""", unsafe_allow_html=True)

def _metric(val, label, color="white"):
    return f"<div class='metric-card'><div class='metric-value' style='color:{color}'>{val}</div><div class='metric-label'>{label}</div></div>"

def show_metrics_block(key=""):
    if not os.path.exists(f"{MODEL_DIR}/metrics.pkl"):
        st.info("⚠️ Model belum dilatih.")
        return
    metrics = joblib.load(f"{MODEL_DIR}/metrics.pkl")
    df_m = pd.DataFrame(metrics).T.reset_index().rename(columns={"index":"Model"})

    models = df_m['Model'].tolist()
    is_identical = False
    if len(models) == 2:
        r0 = df_m.iloc[0]; r1 = df_m.iloc[1]
        is_identical = (abs(r0['Accuracy'] - r1['Accuracy']) < 1e-6 and
                        abs(r0['Precision'] - r1['Precision']) < 1e-6 and
                        abs(r0['Recall'] - r1['Recall']) < 1e-6)

    if is_identical:
        st.markdown("#### 🏆 Skor Performa AI (Identik)")
        st.info("💡 Hasil analisis **Random Forest** & **XGBoost** menunjukkan skor yang **sama**.")
        row = df_m.iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(_metric(f"{row['Accuracy']:.1%}", "Akurasi", "#818cf8"), unsafe_allow_html=True)
        c2.markdown(_metric(f"{row['Precision']:.1%}", "Presisi", "#c084fc"), unsafe_allow_html=True)
        c3.markdown(_metric(f"{row['Recall']:.1%}", "Recall", "#f472b6"), unsafe_allow_html=True)
        f1_val = row.get('F1-Score', (2 * row['Precision'] * row['Recall']) / (row['Precision'] + row['Recall']) if (row['Precision'] + row['Recall']) > 0 else 0)
        c4.markdown(_metric(f"{f1_val:.1%}", "F1-Score", "#fb7185"), unsafe_allow_html=True)
        
        # Tampilkan Confusion Matrix jika tersedia
        cm = row.get('ConfusionMatrix', None)
        if cm is not None and len(cm) == 2:
            st.markdown("<br>##### 📊 Confusion Matrix (Identik)", unsafe_allow_html=True)
            st.markdown(f"""
            <table style='width:100%; border-collapse: collapse; text-align:center; color:white; border: 1px solid rgba(255,255,255,0.1); margin-top:0.5rem;'>
              <tr style='background:rgba(255,255,255,0.05); font-weight:bold;'>
                <th style='padding:10px; border: 1px solid rgba(255,255,255,0.1);'>Aktual \ Prediksi</th>
                <th style='padding:10px; border: 1px solid rgba(255,255,255,0.1);'>Aktif (0)</th>
                <th style='padding:10px; border: 1px solid rgba(255,255,255,0.1);'>Drop Out (1)</th>
              </tr>
              <tr>
                <td style='padding:10px; font-weight:bold; background:rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1);'>Aktual Aktif (0)</td>
                <td style='padding:10px; background:rgba(16,185,129,0.15); color:#10b981; border: 1px solid rgba(255,255,255,0.1); font-weight:bold;'>TN: {cm[0][0]} (True Neg)</td>
                <td style='padding:10px; background:rgba(244,63,94,0.15); color:#f43f5e; border: 1px solid rgba(255,255,255,0.1);'>FP: {cm[0][1]} (False Pos)</td>
              </tr>
              <tr>
                <td style='padding:10px; font-weight:bold; background:rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1);'>Aktual DO (1)</td>
                <td style='padding:10px; background:rgba(244,63,94,0.15); color:#f43f5e; border: 1px solid rgba(255,255,255,0.1);'>FN: {cm[1][0]} (False Neg)</td>
                <td style='padding:10px; background:rgba(16,185,129,0.15); color:#10b981; border: 1px solid rgba(255,255,255,0.1); font-weight:bold;'>TP: {cm[1][1]} (True Pos)</td>
              </tr>
            </table>
            """, unsafe_allow_html=True)
    else:
        st.markdown("#### 🏆 Perbandingan Model AI")
        for _, row in df_m.iterrows():
            st.markdown(f"**🤖 {row['Model']}**")
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(_metric(f"{row['Accuracy']:.1%}", "Akurasi", "#818cf8"), unsafe_allow_html=True)
            c2.markdown(_metric(f"{row['Precision']:.1%}", "Presisi", "#c084fc"), unsafe_allow_html=True)
            c3.markdown(_metric(f"{row['Recall']:.1%}", "Recall", "#f472b6"), unsafe_allow_html=True)
            f1_val = row.get('F1-Score', (2 * row['Precision'] * row['Recall']) / (row['Precision'] + row['Recall']) if (row['Precision'] + row['Recall']) > 0 else 0)
            c4.markdown(_metric(f"{f1_val:.1%}", "F1-Score", "#fb7185"), unsafe_allow_html=True)
            
            cm = row.get('ConfusionMatrix', None)
            if cm is not None and len(cm) == 2:
                st.markdown(f"<div style='margin-top:0.5rem;'><b>📊 Confusion Matrix ({row['Model']})</b></div>", unsafe_allow_html=True)
                st.markdown(f"""
                <table style='width:100%; border-collapse: collapse; text-align:center; color:white; border: 1px solid rgba(255,255,255,0.1); margin-top:0.3rem; margin-bottom: 1rem;'>
                  <tr style='background:rgba(255,255,255,0.05); font-weight:bold;'>
                    <th style='padding:10px; border: 1px solid rgba(255,255,255,0.1);'>Aktual \ Prediksi</th>
                    <th style='padding:10px; border: 1px solid rgba(255,255,255,0.1);'>Aktif (0)</th>
                    <th style='padding:10px; border: 1px solid rgba(255,255,255,0.1);'>Drop Out (1)</th>
                  </tr>
                  <tr>
                    <td style='padding:10px; font-weight:bold; background:rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1);'>Aktual Aktif (0)</td>
                    <td style='padding:10px; background:rgba(16,185,129,0.15); color:#10b981; border: 1px solid rgba(255,255,255,0.1); font-weight:bold;'>TN: {cm[0][0]} (True Neg)</td>
                    <td style='padding:10px; background:rgba(244,63,94,0.15); color:#f43f5e; border: 1px solid rgba(255,255,255,0.1);'>FP: {cm[0][1]} (False Pos)</td>
                  </tr>
                  <tr>
                    <td style='padding:10px; font-weight:bold; background:rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1);'>Aktual DO (1)</td>
                    <td style='padding:10px; background:rgba(244,63,94,0.15); color:#f43f5e; border: 1px solid rgba(255,255,255,0.1);'>FN: {cm[1][0]} (False Neg)</td>
                    <td style='padding:10px; background:rgba(16,185,129,0.15); color:#10b981; border: 1px solid rgba(255,255,255,0.1); font-weight:bold;'>TP: {cm[1][1]} (True Pos)</td>
                  </tr>
                </table>
                """, unsafe_allow_html=True)

def page_dashboard(load_from_db, DB_AVAILABLE):
    _header("📊","Dashboard","Ringkasan data dan statistik mahasiswa")
    df = load_from_db()
    if df is None or len(df)==0:
        if os.path.exists(DATA_PATH): df = pd.read_csv(DATA_PATH, sep=None, engine='python')
        else: df = None
    if df is None or len(df)==0:
        st.warning("⚠️ Dataset belum tersedia.")
        return

    if TARGET_COL not in df.columns: df[TARGET_COL] = 0
    src = "🐘 PostgreSQL" if DB_AVAILABLE else "📄 CSV"
    st.caption(f"Sumber data: {src}")

    total = len(df); total_do = int(df[TARGET_COL].sum()); avg_ipk = df['IPK'].mean() if 'IPK' in df.columns else 0
    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(_metric(f"{total:,}","Total Mahasiswa"), unsafe_allow_html=True)
    c2.markdown(_metric(f"{total_do:,}","Potensi DO","#f43f5e"), unsafe_allow_html=True)
    c3.markdown(_metric(f"{total-total_do:,}","Aman","#10b981"), unsafe_allow_html=True)
    c4.markdown(_metric(f"{avg_ipk:.2f}","Rata-rata IPK","#818cf8"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("<div class='section-card'><h5>🔘 Distribusi Status</h5>", unsafe_allow_html=True)
        fig = px.pie(df, names=TARGET_COL, hole=0.65, color_discrete_sequence=['#10b981','#f43f5e'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False, margin=dict(t=0,b=0,l=0,r=0), height=280)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_r:
        st.markdown("<div class='section-card'><h5>📈 Distribusi per Angkatan</h5>", unsafe_allow_html=True)
        if 'Angkatan' in df.columns:
            fig2 = px.histogram(df, x='Angkatan', color=TARGET_COL, barmode='group',
                                color_discrete_map={0:'#818cf8',1:'#f43f5e'})
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               font_color="white", showlegend=True, margin=dict(t=10,b=10,l=10,r=10), height=280)
            st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

def page_data(engine, load_from_db, save_to_db, DB_AVAILABLE):
    _header("📋","Data & Pelatihan","Kelola dataset dan latih model AI")
    df_db = load_from_db()
    if df_db is None or len(df_db)==0:
        if os.path.exists(DATA_PATH): df_db = pd.read_csv(DATA_PATH, sep=None, engine='python')
        else: df_db = None

    if df_db is not None and len(df_db)>0:
        st.dataframe(df_db, use_container_width=True, height=280)
    else: st.info("Belum ada dataset.")

    st.markdown("---")
    cp1, cp2 = st.columns(2)
    with cp1:
        st.markdown("#### 📂 Update Dataset")
        up = st.file_uploader("Upload CSV", type="csv")
        if up:
            # Cegah loop dengan mengecek jika file sudah diproses
            if 'last_uploaded' not in st.session_state or st.session_state.last_uploaded != up.name:
                with open(DATA_PATH,"wb") as f: f.write(up.getbuffer())
                df_up = pd.read_csv(DATA_PATH, sep=None, engine='python')
                if DB_AVAILABLE: save_to_db(df_up)
                st.session_state.last_uploaded = up.name
                st.success("✅ Dataset diperbarui!")
                st.rerun()
    with cp2:
        st.markdown("#### 🚀 Latih Ulang AI")
        if st.button("🔁 RE-TRAIN AI ENGINE", use_container_width=True):
            with st.spinner("🔄 Sedang melatih ulang mesin AI..."):
                try:
                    engine.train()
                    st.success("✅ AI berhasil dilatih dengan metrik baru!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Gagal melatih model: {str(e)}")

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    show_metrics_block("data")
    st.markdown("</div>", unsafe_allow_html=True)

def page_predict(engine, save_prediction_to_db):
    _header("🧠","Prediksi Individu","Analisis risiko DO satu mahasiswa")
    with st.form("individu_form"):
        c1, c2 = st.columns(2)
        with c1:
            angkatan = st.selectbox("Angkatan",[2020,2021,2022,2023,2024,2025])
            semester = st.number_input("Semester",1,14,4)
            ipk = st.number_input("IPK",0.0,4.0,3.0,0.01)
            sks = st.number_input("SKS Lulus",0,160,60)
        with c2:
            mengulang = st.number_input("Mata Kuliah Diulang",0,30,0)
            absensi = st.slider("Kehadiran (%)",0,100,85)
            bayar = st.selectbox("Status Pembayaran",["LUNAS (1)","BELUM (0)"])
            model_p = st.radio("Model AI",["XGBoost","Random Forest"],horizontal=True)
        submitted = st.form_submit_button("🚀 JALANKAN ANALISIS", use_container_width=True)

    if submitted:
        bv = 1 if "LUNAS" in bayar else 0
        row = {'Angkatan':angkatan,'Semester':semester,'IPK':ipk,'SKS_Lulus':sks,
               'Mengulang':mengulang,'Absensi':absensi,'Status_Pembayaran':bv}
        prob = engine.predict(row, model_p)
        if prob is not None:
            color = "#f43f5e" if prob>0.7 else "#f59e0b" if prob>0.4 else "#10b981"
            label = "🔴 BAHAYA" if prob>0.7 else "🟡 WASPADA" if prob>0.4 else "🟢 AMAN"
            try:
                save_prediction_to_db([{'nim':'-','angkatan':angkatan,'semester':semester,'ipk':ipk,
                    'sks_lulus':sks,'mengulang':mengulang,'absensi':absensi,'status_pembayaran':bv,
                    'risiko_persen':round(prob*100,1),'status_risiko':label,'model_ai':model_p,'tipe_prediksi':'individu'}])
            except Exception:
                pass  # Prediksi tetap tampil meski simpan DB gagal

            _,mid,_ = st.columns([1,2,1])
            with mid:
                st.markdown(f"""<div class='result-card' style='border:2px solid {color}'>
                    <div class='result-pct' style='color:{color}'>{prob*100:.1f}%</div>
                    <div class='result-label' style='color:{color}'>{label}</div>
                    <div class='result-sub'>Risiko Drop Out</div></div>""", unsafe_allow_html=True)
                
                st.markdown("#### 🔍 Analisis Detail Faktor")
                target_sks = semester * 18
                sks_ratio = sks / target_sks if target_sks > 0 else 1.0
                factors = []
                if ipk < 2.0: factors.append(("❌", "IPK Rendah", f"{ipk:.2f} (Dibawah standar 2.0)", "#f43f5e"))
                elif ipk < 2.75: factors.append(("⚠️", "IPK Cukup", f"{ipk:.2f} (Perlu ditingkatkan)", "#f59e0b"))
                else: factors.append(("✅", "IPK Baik", f"{ipk:.2f} (Memenuhi standar)", "#10b981"))
                if absensi < 75: factors.append(("❌", "Absensi Rendah", f"{absensi}% (Min. 75%)", "#f43f5e"))
                elif absensi < 85: factors.append(("⚠️", "Absensi Cukup", f"{absensi}%", "#f59e0b"))
                else: factors.append(("✅", "Absensi Bagus", f"{absensi}%", "#10b981"))
                if sks_ratio < 0.6: factors.append(("❌", "Progres SKS Lambat", f"{sks} SKS (Ketinggalan jauh)", "#f43f5e"))
                elif sks_ratio < 0.85: factors.append(("⚠️", "Progres SKS Cukup", f"{sks} SKS", "#f59e0b"))
                else: factors.append(("✅", "Progres SKS Lancar", f"{sks} SKS", "#10b981"))
                if bv == 0: factors.append(("❌", "Status Keuangan", "Belum Lunas", "#f43f5e"))
                else: factors.append(("✅", "Status Keuangan", "Lunas", "#10b981"))
                if mengulang > 3: factors.append(("❌", "Beban Studi Berat", f"{mengulang} MK Diulang", "#f43f5e"))
                elif mengulang > 0: factors.append(("⚠️", "Ada Pengulangan", f"{mengulang} MK Diulang", "#f59e0b"))
                else: factors.append(("✅", "Beban Studi Ringan", "Tidak ada MK diulang", "#10b981"))

                f_col1, f_col2 = st.columns(2)
                for i, (icon, title, desc, color_f) in enumerate(factors):
                    target_col = f_col1 if i % 2 == 0 else f_col2
                    target_col.markdown(f"""
                        <div style='background:rgba(255,255,255,0.03); padding:1rem; border-radius:1rem; border-left:4px solid {color_f}; margin-bottom:0.5rem;'>
                            <div style='font-size:0.8rem; color:#94a3b8; font-weight:600;'>{icon} {title.upper()}</div>
                            <div style='font-size:0.95rem; color:white; margin-top:0.2rem;'>{desc}</div>
                        </div>
                    """, unsafe_allow_html=True)
        else: st.error("❌ Model belum dilatih!")

def page_batch(engine, save_prediction_to_db):
    _header("📂","Prediksi Batch","Upload CSV untuk prediksi massal")
    
    # Template CSV untuk didownload
    template_data = "NIM,Angkatan,Semester,IPK,SKS_Lulus,Mengulang,Absensi,Status_Pembayaran\n12345678,2022,4,3.25,80,0,95.0,1\n87654321,2021,6,2.80,110,2,82.5,0\n"
    st.download_button(
        label="📥 Download Template CSV",
        data=template_data,
        file_name="template_prediksi_batch.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    with st.form("batch_form"):
        bf = st.file_uploader("📁 Upload CSV Mahasiswa", type="csv")
        bm = st.selectbox("Model AI",["XGBoost","Random Forest"])
        bs = st.form_submit_button("🚀 EKSEKUSI PREDIKSI MASSAL", use_container_width=True)

    if bs and bf:
        df_b = pd.read_csv(bf, sep=None, engine='python')
        probs = engine.predict_batch(df_b, bm)
        if probs is not None:
            df_b['Risiko (%)']=[ f"{x*100:.1f}%" for x in probs]
            df_b['Status']=["🔴 BAHAYA" if x>0.7 else "🟡 WASPADA" if x>0.4 else "🟢 AMAN" for x in probs]
            st.dataframe(df_b, use_container_width=True)
            recs = []
            for idx,row in df_b.iterrows():
                p=probs[idx]; sl="🔴 BAHAYA" if p>0.7 else "🟡 WASPADA" if p>0.4 else "🟢 AMAN"
                recs.append({'nim':str(row.get('NIM',row.get('nim','-'))),'angkatan':int(row.get('Angkatan',row.get('angkatan',0))),
                    'semester':int(row.get('Semester',row.get('semester',0))),'ipk':float(row.get('IPK',row.get('ipk',0))),
                    'sks_lulus':int(row.get('SKS_Lulus',row.get('sks_lulus',0))),'mengulang':int(row.get('Mengulang',row.get('mengulang',0))),
                    'absensi':float(row.get('Absensi',row.get('absensi',0))),'status_pembayaran':int(row.get('Status_Pembayaran',row.get('status_pembayaran',0))),
                    'risiko_persen':round(p*100,1),'status_risiko':sl,'model_ai':bm,'tipe_prediksi':'batch'})
            try:
                save_prediction_to_db(recs)
                st.success(f"✅ {len(recs)} hasil prediksi selesai!")
            except Exception:
                st.success(f"✅ {len(recs)} hasil prediksi selesai!")
            st.download_button("📥 DOWNLOAD HASIL",df_b.to_csv(index=False).encode('utf-8'),"Hasil_Prediksi.csv","text/csv")

def page_history(load_prediction_history, DB_AVAILABLE):
    _header("📜","Riwayat Prediksi","Semua hasil prediksi yang tersimpan")
    df_h = load_prediction_history()
    if df_h is not None and len(df_h)>0:
        # CLEANING DATA FOR FILTERS
        df_h['tipe_prediksi'] = df_h['tipe_prediksi'].str.strip()
        df_h['model_ai'] = df_h['model_ai'].str.strip()

        # FILTERS
        cf1, cf2 = st.columns(2)
        with cf1: tf = st.selectbox("Filter Tipe", ["Semua"] + sorted(df_h['tipe_prediksi'].unique().tolist()))
        with cf2: mf = st.selectbox("Filter Model", ["Semua"] + sorted(df_h['model_ai'].unique().tolist()))
        
        if tf!="Semua": df_h = df_h[df_h['tipe_prediksi']==tf]
        if mf!="Semua": df_h = df_h[df_h['model_ai']==mf]

        # METRICS
        tp = len(df_h)
        nb = len(df_h[df_h['risiko_persen']>70])
        nw = len(df_h[(df_h['risiko_persen']>40)&(df_h['risiko_persen']<=70)])
        na = len(df_h[df_h['risiko_persen']<=40])

        c1,c2,c3,c4=st.columns(4)
        c1.markdown(_metric(f"{tp:,}","Total Prediksi"), unsafe_allow_html=True)
        c2.markdown(_metric(nb,"🔴 Bahaya","#f43f5e"), unsafe_allow_html=True)
        c3.markdown(_metric(nw,"🟡 Waspada","#f59e0b"), unsafe_allow_html=True)
        c4.markdown(_metric(na,"🟢 Aman","#10b981"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Penataan kolom
        display_cols = {
            'nim': 'NIM',
            'angkatan': 'Angkatan',
            'semester': 'Semester',
            'ipk': 'IPK',
            'sks_lulus': 'SKS Lulus',
            'mengulang': 'Mengulang',
            'absensi': 'Absensi (%)',
            'status_pembayaran': 'Bayar',
            'risiko_persen': 'Risiko (%)',
            'status_risiko': 'Status',
            'model_ai': 'Model',
            'tipe_prediksi': 'Tipe',
            'tanggal_prediksi': 'Tanggal'
        }
        cols_to_use = [c for c in display_cols.keys() if c in df_h.columns]
        df_display = df_h[cols_to_use].copy()
        
        if 'status_pembayaran' in df_display.columns:
            df_display['status_pembayaran'] = df_display['status_pembayaran'].map({1: 'Lunas', 0: 'Belum'})
            
        df_display = df_display.rename(columns=display_cols)
        
        st.dataframe(df_display, use_container_width=True, height=400)
        st.download_button("📥 DOWNLOAD RIWAYAT",df_h.to_csv(index=False).encode('utf-8'),"Riwayat_Prediksi.csv","text/csv")
        
        st.markdown("---")
        if st.button("🗑️ Hapus Semua Riwayat"):
            try:
                from backend.core.ml_logic import get_connection, load_prediction_history
                conn=get_connection(); cur=conn.cursor()
                cur.execute("TRUNCATE TABLE hasil_prediksi RESTART IDENTITY")
                conn.commit(); cur.close(); conn.close()
                load_prediction_history.clear()  # Clear cache after deleting history
                st.success("✅ Riwayat dihapus!"); st.rerun()
            except Exception as e:
                st.error(f"Gagal menghapus: {e}")
    else: st.info("💭 Belum ada riwayat.")

def page_user_management(get_all_users, update_user_auth):
    _header("👥", "Manajemen Pengguna", "Kelola hak akses pengguna, berikan akses admin, atau kunci pengguna")
    
    users = get_all_users()
    
    # Kolom pencarian email
    search_query = st.text_input("🔍 Cari Email Pengguna", placeholder="Ketik email untuk mencari...", label_visibility="collapsed")
    
    if search_query:
        users = [u for u in users if search_query.lower().strip() in u["email"].lower()]
        
    if not users:
        st.info("ℹ️ Tidak ada pengguna terdaftar yang sesuai pencarian.")
        return
        
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    
    # Judul kolom tabel (Tanpa kolom Tindakan/Action)
    col_em, col_ro, col_lo = st.columns([4, 3, 3])
    col_em.markdown("**Email**")
    col_ro.markdown("**Peran (Admin)**")
    col_lo.markdown("**Status Akses**")
    st.markdown("<hr style='margin: 0.5rem 0 1rem 0; border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    for u in users:
        u_email = u["email"]
        u_is_admin = u["is_admin"]
        u_is_locked = u["is_locked"]
        
        # Super admin (owner atau akun yang sedang login) tidak bisa diubah statusnya
        is_protected = (u_email == "henimiranda9@gmail.com" or u_email == st.session_state.get("user_email"))
        
        col_em_val, col_ro_val, col_lo_val = st.columns([4, 3, 3])
        
        # Kolom Email (Tanpa emoji mahkota/crown)
        if u_is_admin:
            col_em_val.markdown(f"**{u_email}**")
        else:
            col_em_val.markdown(u_email)
            
        if is_protected:
            # Tanpa emoji perisai/shield
            col_ro_val.markdown("Super Admin")
            col_lo_val.markdown("Aktif")
        else:
            # Dropdown Peran (Tanpa emoji)
            role_opts = ["Admin", "Regular User"]
            role_idx = 0 if u_is_admin else 1
            role_sel = col_ro_val.selectbox(
                f"Peran_{u_email}",
                options=role_opts,
                index=role_idx,
                key=f"role_{u_email}",
                label_visibility="collapsed"
            )
            
            # Dropdown Kunci (Tanpa emoji gembok/lock)
            lock_opts = ["Aktif", "Terkunci"]
            lock_idx = 1 if u_is_locked else 0
            lock_sel = col_lo_val.selectbox(
                f"Status_{u_email}",
                options=lock_opts,
                index=lock_idx,
                key=f"lock_{u_email}",
                label_visibility="collapsed"
            )
            
            # Cek perubahan untuk auto-save langsung
            new_is_admin = (role_sel == "Admin")
            new_is_locked = (lock_sel == "Terkunci")
            
            if new_is_admin != u_is_admin or new_is_locked != u_is_locked:
                if update_user_auth(u_email, new_is_admin, new_is_locked):
                    st.toast(f"✅ Akses {u_email} berhasil diperbarui!")
                    st.rerun()
                else:
                    st.error("Gagal memperbarui database!")
                
        st.markdown("<hr style='margin: 0.8rem 0; border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)
