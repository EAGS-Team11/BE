import os
import joblib
import json
import numpy as np
import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from xgboost import XGBRegressor
import openai
from dotenv import load_dotenv

# Load env variables untuk memastikan OPENROUTER_API_KEY tersedia
load_dotenv()

# --- Definisi Model Deep Learning (Placeholder jika pakai PyTorch) ---
class MyModel(torch.nn.Module):
    def __init__(self, input_dim=384, hidden_dim=128, output_dim=1):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, output_dim)
        
    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        return self.fc2(x)

class HybridGrader:
    _instance = None

    def __new__(cls):
        # Singleton Pattern: Memastikan hanya ada 1 instance grader di memori
        if cls._instance is None:
            cls._instance = super(HybridGrader, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        print("🤖 [AI INIT] Memulai inisialisasi Hybrid Grader...")
        self.encoder = None
        self.model = None
        self.model_type = "dummy"
        self.model_max_score = 100.0 # Default fallback (0-100)
        # Mengambil kunci dari environment variable yang sudah dimuat oleh load_dotenv()
        self.api_key = os.getenv("OPENROUTER_API_KEY")

        # 1. Load SBERT (Wajib untuk embedding)
        try:
            # Menggunakan model kecil agar hemat RAM server
            self.encoder = SentenceTransformer("paraphrase-MiniLM-L6-v2")
            print("✅ [AI INIT] SBERT Model loaded.")
        except Exception as e:
            # Jika ini gagal, server masih bisa start, tapi grading teknis akan error/skip
            print(f"❌ [AI INIT] Gagal load SBERT (pastikan koneksi dan requirements.txt sudah diinstal): {e}")

        # 2. Load Trained Model (.pkl / .pth)
        # --- MODIFIKASI: Target folder dan filename sesuai instruksi user ---
        # ASUMSI: Script dijalankan dari folder 'BE'. Path relatif ke model adalah 'app/models/'
        model_dir = os.path.join(os.getcwd(), "app", "models")
        target_filename = "eXtreme_Gradient_Boosting_(XGBoost).pkl"
        
        try:
            # Path Absolut yang sedang dicari
            model_path = os.path.join(model_dir, target_filename)
            print(f"🔍 [AI INIT] Mencoba load model dari path absolut: {model_path}")
            
            if os.path.exists(model_path):
                loaded_data = joblib.load(model_path)
                
                # Handle jika joblib save dictionary atau langsung object model
                self.model = loaded_data.get('model', loaded_data) if isinstance(loaded_data, dict) else loaded_data
                self.model_type = "ml"
                print(f"✅ [AI INIT] ML Model loaded: {target_filename}")
            
            if self.model is None or self.model_type == "dummy":
                # Fallback ke Dummy Model jika file asli tidak ketemu atau gagal dimuat
                print("⚠️ [AI INIT] Model fisik tidak ditemukan di path yang ditentukan. Menggunakan DUMMY Mode (hanya similarity dan LLM).")
                # Fitting dummy data agar tidak error saat predict, jika dipanggil
                self.model = XGBRegressor()
                self.model.fit(np.random.rand(5, 384), np.random.rand(5) * 10)
                
        except Exception as e:
            print(f"❌ [AI INIT] Error loading ML Model. Menggunakan DUMMY Mode: {e}")
            self.model = None
            self.model_type = "dummy"


    def _get_llm_score(self, soal: str, kunci: str, jawaban: str) -> tuple[float, str]:
        """Hitung skor logika menggunakan OpenRouter/OpenAI"""
        if not self.api_key:
            return 0.0, "⚠️ API Key OpenRouter tidak ditemukan di .env"

        try:
            # Implementasi pemanggilan API OpenRouter
            client = openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
            )
            
            prompt = f"""
            Sebagai Dosen, nilai jawaban esai ini (skala 0-100). Fokus pada kualitas logika, struktur, dan kedalaman materi.
            SOAL: {soal}
            KUNCI: {kunci}
            JAWABAN MHS: {jawaban}
            
            Berikan output HANYA JSON: {{"skor": <0-100>, "feedback": "<singkat, maksimum 3 kalimat>"}}
            """
            
            # Menggunakan model yang ringan dan efisien
            response = client.chat.completions.create(
                model="mistralai/mistral-7b-instruct:free",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            return float(data.get("skor", 0)), data.get("feedback", "No feedback from LLM.")
            
        except Exception as e:
            print(f"⚠️ LLM Error (periksa koneksi atau API Key): {e}")
            return 0.0, "Gagal terhubung ke AI Logika (Mode Offline/Error Koneksi)"

    def grade_essay(self, soal: str, kunci_jawaban: str, jawaban_mahasiswa: str, max_score_dosen: float = 100.0):
        """Fungsi utama yang dipanggil oleh Router/API"""
        
        # Validasi Input dan SBERT check
        if not jawaban_mahasiswa or not self.encoder:
            # Fallback jika SBERT gagal dimuat, atau jawaban kosong
            if self.api_key and self.encoder: # If SBERT is the only failure but API key is present, use LLM
                llm_score, llm_feedback = self._get_llm_score(soal, kunci_jawaban, jawaban_mahasiswa)
                method_used = "LLM Only"
                technical_score = 0.0
                final_score_normalized = llm_score
                feedback = llm_feedback + " (Technical check skipped: SBERT failed to load.)"
            elif not jawaban_mahasiswa:
                method_used = "Error"
                technical_score = 0.0
                llm_score = 0.0
                final_score_normalized = 0.0
                feedback = "Jawaban kosong."
            else:
                method_used = "Error"
                technical_score = 0.0
                llm_score = 0.0
                final_score_normalized = 0.0
                feedback = "Jawaban kosong atau Model AI tidak siap."

            final_score = (final_score_normalized / 100.0) * max_score_dosen
            return {
                "final_score": round(final_score, 2),
                "technical_score": round(technical_score, 2),
                "llm_score": round(llm_score, 2),
                "feedback": feedback,
                "method": method_used
            }


        # --- STEP 1: TECHNICAL SCORE (Embedding + ML) ---
        emb_mhs = self.encoder.encode([jawaban_mahasiswa])
        emb_kunci = self.encoder.encode([kunci_jawaban])
        
        # 1. Similarity (always calculated)
        similarity = cosine_similarity(emb_mhs, emb_kunci)[0][0]
        
        # 2. Model Prediction
        score_tech_raw = 0.0
        if self.model and self.model_type == "ml":
            try:
                raw_pred = self.model.predict(emb_mhs)[0]
                # Normalisasi
                score_tech_raw = (float(raw_pred) / self.model_max_score) * 100
            except:
                # Fallback ke similarity murni jika prediksi gagal
                score_tech_raw = similarity * 100 
        else:
            # Gunakan similarity jika model dummy/gagal
            score_tech_raw = similarity * 100 
        
        technical_score = max(0.0, min(100.0, score_tech_raw))

        # --- STEP 2: LOGICAL SCORE (LLM) ---
        llm_score, llm_feedback = self._get_llm_score(soal, kunci_jawaban, jawaban_mahasiswa)

        # --- STEP 3: HYBRID CALCULATION (50:50) ---
        # Final score is a 50/50 blend of technical content (ML/SBERT) and logical depth (LLM)
        final_score_normalized = (technical_score * 0.5) + (llm_score * 0.5)
        
        # Skala ulang ke Max Score Dosen
        final_score = (final_score_normalized / 100.0) * max_score_dosen

        return {
            "final_score": round(final_score, 2),
            "technical_score": round(technical_score, 2),
            "llm_score": round(llm_score, 2),
            "feedback": llm_feedback,
            "method": "Hybrid 50-50"
        }

# Inisiasi global var. Baris ini HARUS berhasil dieksekusi agar 'grader' tersedia.
# Catatan: Grader akan mencoba memuat model saat inisiasi ini.
grader = HybridGrader()