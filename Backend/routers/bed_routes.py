from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_db_connection 

router = APIRouter()

# 1. Matches the integer ID from your database!
class BedAllocationRequest(BaseModel):
    bed_id: int
    patient_id: int

# 2. GET Route (Maps your DB columns to what React expects)
@router.get("/api/beds/status")
def get_bed_status():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # We rename the columns on-the-fly so the React frontend understands them
        cursor.execute("""
            SELECT 
                bed_id AS id, 
                ward_type AS ward, 
                is_occupied AS occupied, 
                current_patient_id AS patient 
            FROM beds 
            ORDER BY bed_id;
        """)
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# 3. POST Route: Person 2's ACID Concurrency Lock
@router.post("/api/beds/allocate")
def allocate_bed(request: BedAllocationRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # PESSIMISTIC LOCKING: NOWAIT prevents two nurses from booking the same bed
        cursor.execute("""
            SELECT bed_id FROM beds 
            WHERE bed_id = %s AND is_occupied = FALSE 
            FOR UPDATE NOWAIT; 
        """, (request.bed_id,))
        
        available_bed = cursor.fetchone()
        
        if not available_bed:
            conn.rollback()
            raise HTTPException(status_code=404, detail="Bed is already occupied or locked by another admin!")

        # Update using current_patient_id (int4) exactly like your schema
        cursor.execute("""
            UPDATE beds 
            SET is_occupied = TRUE, current_patient_id = %s 
            WHERE bed_id = %s;
        """, (request.patient_id, request.bed_id))

        conn.commit()
        return {"message": "Bed allocated successfully", "bed_id": request.bed_id}
        
    except Exception as e:
        conn.rollback() 
        # Handle lock collision
        if hasattr(e, 'pgcode') and e.pgcode == '55P03':
            raise HTTPException(status_code=409, detail="Database Lock: Another nurse is booking this exact bed right now!")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# 4. POST Route: Release Bed
@router.post("/api/beds/release/{bed_id}")
def release_bed(bed_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE beds 
            SET is_occupied = FALSE, current_patient_id = NULL 
            WHERE bed_id = %s;
        """, (bed_id,))
        conn.commit()
        return {"message": "Bed released successfully."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()