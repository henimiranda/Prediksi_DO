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
        c1, c2, c3 = st.columns(3)
        c1.markdown(_metric(f"{row['Accuracy']:.1%}", "Akurasi", "#818cf8"), unsafe_allow_html=True)
        c2.markdown(_metric(f"{row['Precision']:.1%}", "Presisi", "#c084fc"), unsafe_allow_html=True)
        c3.markdown(_metric(f"{row['Recall']:.1%}", "Recall", "#f472b6"), unsafe_allow_html=True)
    else:
        st.markdown("#### 🏆 Perbandingan Model AI")
        for _, row in df_m.iterrows():
            st.markdown(f"**🤖 {row['Model']}**")
            c1, c2, c3 = st.columns(3)
            c1.markdown(_metric(f"{row['Accuracy']:.1%}", "Akurasi"), unsafe_allow_html=True)
            c2.markdown(_metric(f"{row['Precision']:.1%}", "Presisi"), unsafe_allow_html=True)
            c3.markdown(_metric(f"{row['Recall']:.1%}", "Recall"), unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

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
            save_prediction_to_db([{'nim':'-','angkatan':angkatan,'semester':semester,'ipk':ipk,
                'sks_lulus':sks,'mengulang':mengulang,'absensi':absensi,'status_pembayaran':bv,
                'risiko_persen':round(prob*100,1),'status_risiko':label,'model_ai':model_p,'tipe_prediksi':'individu'}])

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
            save_prediction_to_db(recs)
            st.success(f"✅ {len(recs)} hasil tersimpan!")
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
        st.dataframe(df_h, use_container_width=True, height=400)
        st.download_button("📥 DOWNLOAD RIWAYAT",df_h.to_csv(index=False).encode('utf-8'),"Riwayat_Prediksi.csv","text/csv")
        
        st.markdown("---")
        if st.button("🗑️ Hapus Semua Riwayat"):
            from config.database import get_connection
            conn=get_connection(); cur=conn.cursor()
            cur.execute("TRUNCATE TABLE hasil_prediksi RESTART IDENTITY")
            conn.commit(); cur.close(); conn.close()
            st.success("✅ Riwayat dihapus!"); st.rerun()
    else: st.info("💭 Belum ada riwayat.")
