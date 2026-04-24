from flask import Blueprint, request, jsonify
from config import get_db_connection

restore_bp = Blueprint("restore_bp", __name__, url_prefix="/lecturer")

@restore_bp.route("/restore-student", methods=["POST"])
def restore_student():
    data = request.get_json()

    reg_no = data.get("reg_no")

    if not reg_no:
        return jsonify({
            "success": False,
            "message": "Registration number is required"
        }), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # 1. Find student
        cur.execute("""
            SELECT id FROM users
            WHERE reg_no = %s AND role = 'student'
        """, (reg_no,))

        user = cur.fetchone()

        if not user:
            return jsonify({
                "success": False,
                "message": "Student not found"
            }), 404

        student_id = user[0]

        # 2. Update device status to restored
        cur.execute("""
            UPDATE user_deviceinfo
            SET status = 'restored'
            WHERE user_id = %s
        """, (student_id,))

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Student access restored successfully"
        }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        cur.close()
        conn.close()