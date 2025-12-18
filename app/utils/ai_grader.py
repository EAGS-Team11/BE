import os
import json
import logging
from dotenv import load_dotenv
from decimal import Decimal

# --- PERUBAHAN 1: Ganti library Groq ke Google GenAI ---
from google import genai
from google.genai.errors import APIError 

# Konfigurasi Logging sederhana
logging.basicConfig(level=logging.INFO)

# Load env variables
load_dotenv()

class LLMGrader:
    """
    Penilai Esai Murni LLM menggunakan Gemini (gemini-2.5-flash)
    Menggunakan pola Singleton untuk memastikan inisialisasi API hanya sekali saat server startup.
    """
    _instance = None

    def __new__(cls):
        # Pola Singleton
        if cls._instance is None:
            cls._instance = super(LLMGrader, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # 1. Inisialisasi Kunci API dan Klien Gemini
        logging.info("🤖 [AI INIT] Memulai inisialisasi LLM Grader (Gemini)...")
        # --- PERUBAHAN 2: Ganti nama ENV key ---
        self.api_key = os.getenv("GEMINI_API_KEY") 
        
        # --- PERUBAHAN 3: Ganti model ke Gemini Flash (Gratis/Efisiensi Tinggi) ---
        self.llm_model = "gemini-2.5-flash" 
        self.client = None

        if self.api_key:
            try:
                # Inisialisasi Gemini client
                self.client = genai.Client(api_key=self.api_key)
                logging.info(f"✅ [AI INIT] Gemini Client loaded. Using {self.llm_model}")
            except Exception as e:
                logging.error(f"❌ [AI INIT] Gagal inisialisasi Gemini Client: {e}")
                self.api_key = None 
        else:
            logging.warning("⚠️ [AI INIT] GEMINI_API_KEY tidak ditemukan di .env. LLM Grader akan bekerja dalam Mode Offline/Dummy.")

    def _get_llm_score(self, soal: str, kunci: str, jawaban: str) -> tuple[float, str]:
        """Menghubungi Gemini API untuk mendapatkan skor (0-100) dan feedback."""
        
        if not self.api_key or not self.client:
            return 0.0, "⚠️ Layanan AI tidak aktif. API Key Gemini tidak ditemukan atau Client gagal diinisialisasi."

        prompt = f"""
        Anda adalah Dosen/Penguji Esai yang ketat. Nilai jawaban esai ini (skala 0-100). Fokus pada kualitas logika, struktur, kedalaman materi, dan relevansi terhadap kunci jawaban.
        SOAL: {soal}
        KUNCI JAWABAN: {kunci}
        JAWABAN MAHASISWA: {jawaban}
        
        Berikan output HANYA JSON. Pastikan JSON VALID.
        JSON FORMAT: {{"skor": <0-100>, "feedback": "<berikan feedback yang konstruktif, maksimum 3 kalimat>"}}
        """
        
        try:
            # --- PERUBAHAN 4: Ganti pemanggilan API Groq ke Gemini ---
            response = self.client.models.generate_content(
                model=self.llm_model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json", # Minta respons dalam format JSON
                    temperature=0.1
                )
            )

            # Karena kita meminta response_mime_type="application/json", 
            # response.text seharusnya sudah merupakan string JSON murni.
            content = response.text
            data = json.loads(content)
            
            # Sanitasi skor dan memastikan berada dalam range 0-100
            llm_score = float(data.get("skor", 0))
            llm_score = max(0.0, min(100.0, llm_score)) 
            
            return llm_score, data.get("feedback", "No feedback from LLM.")
            
        except APIError as e:
            logging.error(f"⚠️ Gemini API Error: {e}")
            return 0.0, f"Gagal terhubung ke AI Logika (Gemini API Error). Detail: {str(e)[:70]}..."
        except json.JSONDecodeError as e:
             logging.error(f"⚠️ JSON Parsing Error: {e}. Raw response: {response.text}")
             return 0.0, f"Gagal parsing JSON dari respons AI. Detail: {str(e)[:70]}..."
        except Exception as e:
            logging.error(f"⚠️ Unknown Error during Gemini call: {e}")
            return 0.0, f"Error tidak terduga saat pemanggilan AI. Detail: {str(e)[:70]}..."

    def grade_essay(self, soal: str, kunci_jawaban: str, jawaban_mahasiswa: str, max_score_dosen: float = 100.0):
        """Fungsi utama untuk penilaian 100% LLM."""
        
        # Validasi Jawaban
        if not jawaban_mahasiswa or len(jawaban_mahasiswa.strip()) < 5:
            return {
                "final_score": 0.0,
                "llm_score": 0.0,
                "feedback": "Jawaban kosong atau terlalu pendek.",
                "method": "Error"
            }

        # --- STEP 1: LOGICAL SCORE (LLM) ---
        llm_score, llm_feedback = self._get_llm_score(soal, kunci_jawaban, jawaban_mahasiswa)

        # Cek jika LLM gagal berfungsi
        if "⚠️ Layanan AI tidak aktif" in llm_feedback or "Gagal terhubung ke AI Logika" in llm_feedback or llm_score == 0.0 and "Gagal" in llm_feedback:
             return {
                "final_score": 0.0,
                "llm_score": 0.0,
                "feedback": llm_feedback,
                "method": "Error"
            }

        # --- STEP 2: FINAL CALCULATION (100% LLM) ---
        final_score_normalized = llm_score
        
        # Skala ulang ke Max Score Dosen
        final_score = (final_score_normalized / 100.0) * max_score_dosen

        return {
            "final_score": round(final_score, 2),
            "llm_score": round(llm_score, 2), # Skor 0-100 dari LLM
            "feedback": llm_feedback,
            # --- PERUBAHAN 5: Ganti nama method ---
            "method": "LLM Only (Gemini 2.5 Flash)" 
        }

# Inisiasi global var.
grader = LLMGrader()