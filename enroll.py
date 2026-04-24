from flask import Blueprint, request, jsonify, session
from config import get_db_connection
enroll_bp = Blueprint('enroll_bp', __name__)

@enroll_bp.route('/enroll', methods=['POST'])
def enroll_units():
    data = request.get_json()

    student_id = session.get("student_id")
    unit_ids = data.get("unit_ids")

    if not student_id:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    if not unit_ids:
        return jsonify({"success": False, "message": "No units selected"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # 🔥 STEP 1: GET ACTIVE SESSION
        cur.execute("""
            SELECT session_id 
            FROM academic_sessions 
            WHERE is_active = TRUE
            LIMIT 1
        """)
        result = cur.fetchone()

        if not result:
            return jsonify({
                "success": False,
                "message": "No active academic session found"
            }), 400

        session_id = result[0]

        # 🔥 STEP 2: INSERT ENROLLMENTS
        for unit_id in unit_ids:
            cur.execute("""
                INSERT INTO enrollments (student_id, unit_id, session_id)
                VALUES (%s, %s, %s)
                ON CONFLICT (student_id, unit_id, session_id) DO NOTHING
            """, (student_id, unit_id, session_id))

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Units registered successfully",
            "session_id": session_id
        })

    except Exception as e:
        conn.rollback()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        cur.close()
        conn.close()