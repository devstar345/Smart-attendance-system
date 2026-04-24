from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash
from config import get_db_connection

login_bp = Blueprint('student_login_bp', __name__)


@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}

    reg_no = data.get('reg_no')
    password = data.get('password')
    visitor_id = data.get('visitorId')

    if not reg_no or not password or not visitor_id:
        return jsonify({
            "success": False,
            "message": "reg_no, password and visitorId are required"
        }), 400

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # =========================
        # GET USER
        # =========================
        cur.execute("""
            SELECT id, password, name, email, role, course_id 
            FROM users 
            WHERE reg_no = %s
        """, (reg_no,))

        user = cur.fetchone()

        if not user:
            return jsonify({
                "success": False,
                "message": "Invalid credentials"
            }), 401

        user_id = user[0]
        hashed_password = user[1]
        name = user[2]
        email = user[3]
        role = user[4]
        course_id = user[5]

        # =========================
        # CHECK PASSWORD
        # =========================
        if not check_password_hash(hashed_password, password):
            return jsonify({
                "success": False,
                "message": "Invalid credentials"
            }), 401

        # =========================
        # CHECK DEVICE
        # =========================
        cur.execute("""
            SELECT id, visitor_id, status
            FROM user_deviceinfo
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (user_id,))

        device = cur.fetchone()

        # =========================
        # CASE 1: NO DEVICE FOUND
        # =========================
        if not device:
            cur.execute("""
                INSERT INTO user_deviceinfo (user_id, visitor_id, status)
                VALUES (%s, %s, NULL)
            """, (user_id, visitor_id))

            conn.commit()

        else:
            device_id, db_visitor, status = device

            # =========================
            # CASE 2: SAME DEVICE → LOGIN
            # =========================
            if db_visitor == visitor_id:
                pass

            # =========================
            # CASE 3: RESTORED DEVICE → UPDATE + LOGIN
            # =========================
            elif status == "restored":
                cur.execute("""
                    UPDATE user_deviceinfo
                    SET visitor_id = %s,
                        status = NULL
                    WHERE id = %s
                """, (visitor_id, device_id))

                conn.commit()

            # =========================
            # CASE 4: NOT ALLOWED
            # =========================
            else:
                return jsonify({
                    "success": False,
                    "message": "Device not recognised"
                }), 403

        # =========================
        # CREATE SESSION
        # =========================
        session['student_id'] = user_id
        session['reg_no'] = reg_no
        session['student_name'] = name
        session['email'] = email
        session['course_id'] = course_id
        session['role'] = role

        return jsonify({
            "success": True,
            "message": "Login successful",
            "name": name,
            "email": email
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()