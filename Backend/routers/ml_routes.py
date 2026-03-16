from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

# Load database credentials
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

router = APIRouter(prefix="/api/ml", tags=["Machine Learning"])

# ==========================================
# 1. LOAD THE AI BRAIN ON STARTUP
# ==========================================
try:
    model = joblib.load('noshow_model.pkl')
    scaler = joblib.load('scaler.pkl')
    print("✅ AI Brain loaded successfully into FastAPI!")
except Exception as e:
    print(f"⚠️ Warning: ML models not found. Did you run train_model.py? Error: {e}")


def get_db_connection():
    return psycopg2.connect(DB_URL, cursor_factory=psycopg2.extras.RealDictCursor)


# ==========================================
# 2. WHAT REACT SENDS US
# ==========================================
class BookingData(BaseModel):
    lead_time_days: int # React only needs to send us how far away the appointment is!


# ==========================================
# 3. THE ULTIMATE PREDICTION ENDPOINT
# ==========================================
@router.post("/{uid}/predict-noshow")
def predict_noshow(uid: str, data: BookingData):
    conn = None
    cursor = None
    try:
        # --- PART A: FETCH REAL DATA FROM SUPABASE ---
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # The SQL Magic: Get Age, Distance, AND Count their previous ghostings all at once!
        # (Updated to use 'uid' instead of 'user_id' for Firebase compatibility)
        query = """
            SELECT 
                p.age, 
                p.distance_miles,
                (SELECT COUNT(*) FROM appointments a WHERE a.patient_id = p.uid AND a.status IN ('No-Show', 'no_show', 'No Show')) as previous_no_shows
            FROM patient_profiles p
            WHERE p.uid = %s;
        """
        cursor.execute(query, (uid,))
        db_data = cursor.fetchone()
        
        if not db_data:
            raise HTTPException(status_code=404, detail="Patient profile missing. Please update profile first.")
            
        age = db_data['age']
        distance_miles = db_data['distance_miles']
        previous_no_shows = db_data['previous_no_shows']
        
        # Extra safety check: Prevent the AI from crashing if they haven't filled out their profile
        if age is None or distance_miles is None:
            raise HTTPException(status_code=400, detail="Age and Distance must be filled in to predict no-shows.")

        # --- PART B: RUN THE MACHINE LEARNING MODEL ---
        # We arrange the 4 clues in the EXACT order the AI studied them
        patient_features = np.array([[
            age, 
            distance_miles, 
            data.lead_time_days, 
            previous_no_shows
        ]])
        
        # Scale the data so the math doesn't overflow
        patient_features_scaled = scaler.transform(patient_features)
        
        # Ask the AI for its prediction
        prediction = model.predict(patient_features_scaled)[0]
        probability = model.predict_proba(patient_features_scaled)[0]
        
        # Probability[0] is usually the chance of class 0 (No-Show)
        no_show_risk = probability[0] * 100 
        
        return {
            "patient_id": uid,
            "prediction": "Show-Up" if prediction == 1 else "No-Show",
            "no_show_risk_percentage": round(no_show_risk, 2),
            "data_used_by_ai": {
                "age": age,
                "distance": distance_miles,
                "lead_time": data.lead_time_days,
                "previous_ghosts": previous_no_shows
            },
            "recommendation": "Double-book this slot!" if prediction == 0 else "Normal booking."
        }
        
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Machine Learning Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()