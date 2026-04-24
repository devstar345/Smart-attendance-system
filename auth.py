from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from config import get_db_connection

auth_bp = Blueprint('staff_auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}

    required_fields = ['name', 'email', 'pf_no', 'password', 'confirm_password']
    if not all(data.get(field) for field in required_fields):
        return jsonify({
            "success": False,
            "message": "All fields are required"
        }), 400

    name = data.get('name').strip()
    email = data.get('email').strip()
    pf_no = data.get('pf_no').strip()
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    # 🔥 FORCE ROLE FOR STAFF
    role = "lecturer"

    if password != confirm_password:
        return jsonify({
            "success": False,
            "message": "Passwords do not match"
        }), 400

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        conn.autocommit = False
        cur = conn.cursor()

        # Check duplicates
        check_sql = "SELECT id FROM users WHERE email = %s OR pf_no = %s"
        cur.execute(check_sql, (email, pf_no))

        if cur.fetchone():
            return jsonify({
                "success": False,
                "message": "Email or PF number already exists"
            }), 409

        hashed_password = generate_password_hash(password)

        # 🔥 INSERT WITH ROLE
        insert_sql = """
            INSERT INTO users (name, email, pf_no, password, role)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """

        cur.execute(insert_sql, (name, email, pf_no, hashed_password, role))
        user_id = cur.fetchone()[0]

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Staff registration successful",
            "data": {
                "user_id": user_id,
                "role": role
            }
        }), 201

    except Exception as e:
        if conn:
            conn.rollback()

        return jsonify({
            "success": False,
            "message": f"Registration error: {str(e)}"
        }), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()