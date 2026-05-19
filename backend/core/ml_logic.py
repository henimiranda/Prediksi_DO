import streamlit as st
import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

import psycopg2
from sqlalchemy import create_engine

TABLE_NAME = "mahasiswa"

def _db_get(key, default=""):
    """Baca config dari st.secrets (Cloud) atau os.environ (Lokal)."""
    try:
        val = st.secrets.get(key, None)
        if val is not None:
            return str(val)
    except Exception:
        pass
    return os.environ.get(key, default)

def get_connection():
    """Buat koneksi psycopg2 langsung dari st.secrets."""
    return psycopg2.connect(
        host=_db_get("DB_HOST", "localhost"),
        database=_db_get("DB_NAME", "prediksi_do"),
        user=_db_get("DB_USER", "postgres"),
        password=_db_get("DB_PASSWORD", ""),
        port=_db_get("DB_PORT", "5432"),
        sslmode="require",
        connect_timeout=10
    )

def get_db_engine():
    """Buat SQLAlchemy engine dari st.secrets."""
    h = _db_get("DB_HOST", "localhost")
    d = _db_get("DB_NAME", "prediksi_do")
    u = _db_get("DB_USER", "postgres")
    p = _db_get("DB_PASSWORD", "")
    port = _db_get("DB_PORT", "5432")
    url = f"postgresql+psycopg2://{u}:{p}@{h}:{port}/{d}?sslmode=require"
    return create_engine(url)


DATA_PATH = "backend/data/data_mahasiswa_v2.csv"
MODEL_DIR = "models"
FEATURE_COLS = ['Angkatan','Semester','IPK','SKS_Lulus','Mengulang','Absensi','Status_Pembayaran']
TARGET_COL   = 'Status_DO'

def load_from_db():
    engine = get_db_engine()
    if engine is None: return None
    try:
        df = pd.read_sql_table(TABLE_NAME, engine)
        col_map = {'nim':'NIM','angkatan':'Angkatan','semester':'Semester','ipk':'IPK',
                   'sks_lulus':'SKS_Lulus','mengulang':'Mengulang','absensi':'Absensi',
                   'status_pembayaran':'Status_Pembayaran','status_do':'Status_DO'}
        df = df.rename(columns=col_map)
        for dc in ['id','created_at']:
            if dc in df.columns: df = df.drop(columns=[dc])
        return df
    except: return None

def save_to_db(df):
    engine = get_db_engine()
    if engine is None: return False
    try:
        col_map = {'NIM':'nim','Angkatan':'angkatan','Semester':'semester','IPK':'ipk',
                   'SKS_Lulus':'sks_lulus','Mengulang':'mengulang','Absensi':'absensi',
                   'Status_Pembayaran':'status_pembayaran','Status_DO':'status_do'}
        ds = df.rename(columns=col_map)
        vc = ['nim','angkatan','semester','ipk','sks_lulus','mengulang','absensi','status_pembayaran','status_do']
        ds = ds[[c for c in vc if c in ds.columns]]
        ds.to_sql(TABLE_NAME, engine, if_exists='replace', index=False)
        return True
    except: return False

def save_prediction_to_db(data_list):
    conn = get_connection()
    if conn is None: return False
    try:
        cur = conn.cursor()
        for d in data_list:
            cur.execute("""INSERT INTO hasil_prediksi
                (nim,angkatan,semester,ipk,sks_lulus,mengulang,absensi,status_pembayaran,
                 risiko_persen,status_risiko,model_ai,tipe_prediksi)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (str(d.get('nim','')),int(d.get('angkatan',0)),int(d.get('semester',0)),
                 float(d.get('ipk',0)),int(d.get('sks_lulus',0)),int(d.get('mengulang',0)),
                 float(d.get('absensi',0)),int(d.get('status_pembayaran',0)),
                 float(d.get('risiko_persen',0)),str(d.get('status_risiko','')),
                 str(d.get('model_ai','')),str(d.get('tipe_prediksi','individu'))))
        conn.commit(); cur.close(); conn.close()
        return True
    except: return False

def load_prediction_history():
    engine = get_db_engine()
    if engine is None: return None
    try: return pd.read_sql("SELECT * FROM hasil_prediksi ORDER BY tanggal_prediksi DESC", engine)
    except: return None

class MLEngine:
    def _load_df(self):
        df = load_from_db()
        if df is not None and len(df)>0: return df
        if not os.path.exists(DATA_PATH): return pd.DataFrame(columns=FEATURE_COLS+[TARGET_COL])
        df = pd.read_csv(DATA_PATH, sep=None, engine='python')
        col_map = {}
        for c in df.columns:
            cl = c.lower().strip()
            if cl in ['sks_lulus','total_sks_lulus','skslulus']: col_map[c]='SKS_Lulus'
            elif cl in ['mengulang','jumlah_mengulang']: col_map[c]='Mengulang'
            elif cl in ['absensi','absensi_persen']: col_map[c]='Absensi'
            elif cl in ['status_pembayaran','status_bayar']: col_map[c]='Status_Pembayaran'
            elif cl in ['semester','semester_saat_ini']: col_map[c]='Semester'
            elif cl=='status_do': col_map[c]='Status_DO'
        return df.rename(columns=col_map)

    def train(self):
        if not os.path.exists(DATA_PATH): return None
        df = self._load_df()
        
        for col in FEATURE_COLS:
            if col not in df.columns: df[col]=0
        if TARGET_COL not in df.columns: return None
        
        X, y = df[FEATURE_COLS], df[TARGET_COL]

        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        xgb = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)

        from sklearn.model_selection import cross_validate, cross_val_predict
        from sklearn.metrics import confusion_matrix
        scoring = ['accuracy', 'precision', 'recall', 'f1']
        metrics = {}
        for name, mdl in [("Random Forest", rf), ("XGBoost", xgb)]:
            # 1. Metrik Dasar (Akurasi, Presisi, Recall, F1)
            cv_results = cross_validate(mdl, X, y, cv=10, scoring=scoring)
            
            # 2. Confusion Matrix
            y_pred = cross_val_predict(mdl, X, y, cv=10)
            cm = confusion_matrix(y, y_pred).tolist()
            
            metrics[name] = {
                "Accuracy":  cv_results['test_accuracy'].mean(),
                "Precision": cv_results['test_precision'].mean(),
                "Recall":    cv_results['test_recall'].mean(),
                "F1-Score":  cv_results['test_f1'].mean(),
                "ConfusionMatrix": cm
            }
            mdl.fit(X, y)

        os.makedirs(MODEL_DIR, exist_ok=True)
        joblib.dump(rf, f"{MODEL_DIR}/rf_model.pkl")
        joblib.dump(xgb, f"{MODEL_DIR}/xgb_model.pkl")
        joblib.dump(metrics, f"{MODEL_DIR}/metrics.pkl")
        
        return metrics

    def _model_is_valid(self, mt):
        path = f"{MODEL_DIR}/{'xgb' if mt=='XGBoost' else 'rf'}_model.pkl"
        if not os.path.exists(path): return False
        try:
            mdl = joblib.load(path)
            b = getattr(mdl,'get_booster',None)
            sc = b().feature_names if b else list(mdl.feature_names_in_)
            return list(sc)==FEATURE_COLS
        except: return False

    def predict(self, row_dict, model_type="XGBoost"):
        if not self._model_is_valid(model_type):
            for f in ['rf_model.pkl','xgb_model.pkl','metrics.pkl']:
                fp=f"{MODEL_DIR}/{f}"
                if os.path.exists(fp): os.remove(fp)
            return None
        path = f"{MODEL_DIR}/{'xgb' if model_type=='XGBoost' else 'rf'}_model.pkl"
        mdl = joblib.load(path)
        return mdl.predict_proba(pd.DataFrame([row_dict])[FEATURE_COLS])[:,1][0]

    def predict_batch(self, df_input, model_type="XGBoost"):
        if not self._model_is_valid(model_type):
            for f in ['rf_model.pkl','xgb_model.pkl','metrics.pkl']:
                fp=f"{MODEL_DIR}/{f}"
                if os.path.exists(fp): os.remove(fp)
            return None
        path = f"{MODEL_DIR}/{'xgb' if model_type=='XGBoost' else 'rf'}_model.pkl"
        mdl = joblib.load(path)
        df = self._load_df_from_input(df_input)
        return mdl.predict_proba(df[FEATURE_COLS])[:,1]

    def _load_df_from_input(self, df):
        col_map = {}
        for c in df.columns:
            cl = c.lower().strip()
            if cl in ['sks_lulus','total_sks_lulus','skslulus']: col_map[c]='SKS_Lulus'
            elif cl in ['mengulang','jumlah_mengulang']: col_map[c]='Mengulang'
            elif cl in ['absensi','absensi_persen']: col_map[c]='Absensi'
            elif cl in ['status_pembayaran','status_bayar']: col_map[c]='Status_Pembayaran'
            elif cl in ['semester','semester_saat_ini']: col_map[c]='Semester'
        df = df.rename(columns=col_map)
        for col in FEATURE_COLS:
            if col not in df.columns: df[col]=0
        return df
