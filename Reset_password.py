from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash
from config import get_db_connection

lecturer_reset_bp = Blueprint("lecturer_reset_bp", __name__, url_prefix="/lecturer")


@lecturer_reset_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()

    lecturer_id = session.get("staff_id")

    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not lecturer_id:
        return jsonify({
            "success": False,
            "message": "Not logged in"
        }), 401

    if not old_password or not new_password:
        return jsonify({
            "success": False,
            "message": "All fields required"
        }), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # 1. Get lecturer password
        cur.execute("""
            SELECT password
            FROM users
            WHERE id = %s AND role = 'lecturer'
        """, (lecturer_id,))

        row = cur.fetchone()

        if not row:
            return jsonify({
                "success": False,
                "message": "Lecturer not found"
            }), 404

        current_hashed = row[0]

        # 2. Verify old password
        if not check_password_hash(current_hashed, old_password):
            return jsonify({
                "success": False,
                "message": "Old password is incorrect"
            }), 403

        # 3. Update password
        new_hashed = generate_password_hash(new_password)

        cur.execute("""
            UPDATE users
            SET password = %s
            WHERE id = %s AND role = 'lecturer'
        """, (new_hashed, lecturer_id))

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Password updated successfully"
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