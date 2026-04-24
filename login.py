from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash
from config import get_db_connection

login_bp = Blueprint('staff_login_bp', __name__)

@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}

    pf_no = data.get('pf_no')
    password = data.get('password')
    
    if not pf_no or not password:
        return jsonify({
            "success": False,
            "message": "pf_no and password are required"
        }), 400

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get user
        cur.execute(
            "SELECT id, password, name, email FROM users WHERE pf_no = %s",
            (pf_no,)
        )
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

        # Check password
        if not check_password_hash(hashed_password, password):
            return jsonify({
                "success": False,
                "message": "Invalid credentials"
            }), 401

        

        
        # Create session
        session['staff_id'] = user_id
        session['pf_no'] = pf_no
        session['staff_name'] = name
        session['email'] = email

        return jsonify({
            "success": True,
            "message": "Login successful",
            "name": name
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