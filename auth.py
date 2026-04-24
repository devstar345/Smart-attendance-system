from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from config import get_db_connection

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}

    # Validate required fields
    required_fields = ['name', 'email', 'reg_no', 'password', 'confirm_password']
    if not all(data.get(field) for field in required_fields):
        return jsonify({
            "success": False,
            "message": "All fields are required"
        }), 400

    name = data.get('name').strip()
    email = data.get('email').strip()
    reg_no = data.get('reg_no').strip().upper()  # 🔥 normalize
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    # 🔥 FORCE ROLE
    role = "student"

    # 🔥 DETERMINE COURSE FROM REG NO
    if reg_no.startswith("ENG"):
        course_id = 1  # Electrical Engineering
    elif reg_no.startswith("CS"):
        course_id = 2  # Computer Science
    else:
        return jsonify({
            "success": False,
            "message": "Invalid registration number format (must start with ENG or CS)"
        }), 400

    # Validate password match
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
        check_sql = "SELECT id FROM users WHERE email = %s OR reg_no = %s"
        cur.execute(check_sql, (email, reg_no))

        if cur.fetchone():
            return jsonify({
                "success": False,
                "message": "Email or registration number already exists"
            }), 409

        # Hash password
        hashed_password = generate_password_hash(password)

        # 🔥 INSERT WITH COURSE ID
        insert_sql = """
            INSERT INTO users (name, email, reg_no, password, role, course_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """

        cur.execute(insert_sql, (name, email, reg_no, hashed_password, role, course_id))
        user_id = cur.fetchone()[0]

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Registration successful",
            "data": {
                "user_id": user_id,
                "role": role,
                "course_id": course_id
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