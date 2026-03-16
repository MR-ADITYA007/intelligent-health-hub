from fastapi import APIRouter, HTTPException
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

router = APIRouter(prefix="/api/doctors", tags=["Doctor Dashboard"])

def get_db_connection():
    return psycopg2.connect(DB_URL, cursor_factory=psycopg2.extras.RealDictCursor)

# ==========================================
# 1. FETCH APPROVED APPOINTMENTS FOR DOCTOR
# ==========================================
@router.get("/{doctor_id}/appointments")
def get_doctor_appointments(doctor_id: str):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # We only grab appointments that are 'confirmed' OR 'is_overbooked = TRUE'
        query = """
            SELECT 
                a.appointment_id, 
                CAST(a.appointment_time AS TEXT) as appointment_time, 
                a.status, 
                a.is_overbooked,
                COALESCE(p.full_name, 'Mock Patient ' || LEFT(CAST(a.patient_id AS TEXT), 4)) as patient_name,
                COALESCE(p.phone, 'No Phone') as phone
            FROM appointments a
            LEFT JOIN patient_profiles p ON a.patient_id = p.uid
            WHERE a.doctor_id = %s 
              AND (a.status = 'confirmed' OR a.is_overbooked = TRUE)
            ORDER BY a.appointment_time ASC;
        """
        cursor.execute(query, (doctor_id,))
        appointments = cursor.fetchall()
        
        return {"status": "success", "data": appointments}

    except Exception as e:
        print(f"🔥 Doctor DB Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch doctor appointments")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# ==========================================
# 2. MARK APPOINTMENT AS COMPLETED
# ==========================================
@router.put("/appointments/{appointment_id}/complete")
def complete_appointment(appointment_id: int):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "UPDATE appointments SET status = 'completed', is_overbooked = FALSE WHERE appointment_id = %s"
        cursor.execute(query, (appointment_id,))
        conn.commit()
        
        return {"status": "success", "message": "Appointment marked as completed!"}
    except Exception as e:
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail="Failed to complete appointment")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()