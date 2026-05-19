import joblib
import os

MODEL_DIR = "models"
METRICS_PATH = os.path.join(MODEL_DIR, "metrics.pkl")

def cek_skor():
    if not os.path.exists(METRICS_PATH):
        print("\n[!] File metrics.pkl tidak ditemukan. Silakan latih model terlebih dahulu di web.")
        return

    # Load data metrik
    metrics = joblib.load(METRICS_PATH)

    print("\n" + "="*40)
    print("      LAPORAN AKURASI MODEL AI")
    print("="*40)

    for model_name, scores in metrics.items():
        print(f"\n> MODEL: {model_name}")
        print(f"  - Akurasi  : {scores['Accuracy']:.2%}")
        print(f"  - Presisi  : {scores['Precision']:.2%}")
        print(f"  - Recall   : {scores['Recall']:.2%}")
    
    print("\n" + "="*40)

if __name__ == "__main__":
    cek_skor()
