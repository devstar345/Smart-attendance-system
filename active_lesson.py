from flask import Blueprint, jsonify, session, request
from config import get_db_connection
from functools import wraps

active_lessons_bp = Blueprint('active_lessons', __name__)


# 🔐 Protect routes
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "student_id" not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return wrapper


# 🟢 ACTIVE LESSONS
@active_lessons_bp.route('/active-lessons', methods=['GET'])
@login_required
def active_lessons():
    student_id = session.get("student_id")

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT 
                cs.id AS session_id,
                ua.assignment_id,
                u.name AS unit_name,
                l.name AS lecturer_name,
                cs.started_at
            FROM enrollments e
            JOIN unit_assignments ua 
                ON ua.unit_id = e.unit_id
                AND ua.session_id = e.session_id
            JOIN class_session cs
                ON cs.unit_assignment_id = ua.assignment_id
            JOIN units u 
                ON u.id = ua.unit_id
            JOIN users l 
                ON l.id = ua.lecturer_id
            WHERE e.student_id = %s
              AND cs.status = 'active'
        """, (student_id,))

        rows = cur.fetchall()

        lessons = [
            {
                "session_id": r[0],
                "assignment_id": r[1],
                "unit_name": r[2],
                "lecturer_name": r[3],
                "started_at": r[4]
            }
            for r in rows
        ]

        return jsonify(lessons)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()


# 🟡 SESSION INFO
@active_lessons_bp.route('/session-info/<int:session_id>', methods=['GET'])
@login_required
def session_info(session_id):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
           SELECT 
    u.name AS unit_name,
    u.unit_code AS unit_code,
    cs.started_at
FROM class_session cs
JOIN unit_assignments ua 
    ON ua.assignment_id = cs.unit_assignment_id
JOIN units u 
    ON u.id = ua.unit_id
WHERE cs.id = %s
        """, (session_id,))

        row = cur.fetchone()

        if not row:
            return jsonify({"error": "Session not found"}), 404

        return jsonify({
            "unit_name": row[0],
            "unit_code": row[1],
            "date": row[2]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()





@active_lessons_bp.route("/verify-gps", methods=["POST"])
@login_required
def verify_gps():
    data = request.json

    student_lat = data.get("lat")
    student_lng = data.get("lng")
    session_id = data.get("session_id")

    if student_lat is None or student_lng is None or not session_id:
        return jsonify({"error": "Missing required data"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # 🔍 Get lecturer location from active session
        cur.execute("""
            SELECT lecturer_lat, lecturer_lng
            FROM class_session
            WHERE id = %s AND status = 'active'
        """, (session_id,))

        row = cur.fetchone()

        if not row:
            return jsonify({"error": "Session not active"}), 400

        lecturer_lat, lecturer_lng = row

        # =========================
        # 📏 DISTANCE CALCULATION
        # =========================
        # simple approximation (works fine for small distances)
        distance = ((student_lat - lecturer_lat) ** 2 + 
                    (student_lng - lecturer_lng) ** 2) ** 0.5

        # 🔥 threshold (tune this)
        MAX_DISTANCE = 0.001  # ~100m approx

        if distance > MAX_DISTANCE:
            return jsonify({"error": "You are not in class"}), 403

        return jsonify({"message": "GPS verified"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

# 🟢 MARK ATTENDANCE (FIXED LOGIC)
@active_lessons_bp.route('/mark-attendance', methods=['POST'])
@login_required
def mark_attendance():
    student_id = session.get("student_id")
    data = request.json

    session_id = data.get("session_id")

    if not session_id:
        return jsonify({"error": "Session ID required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # 🔍 check current attendance status
        cur.execute("""
            SELECT status FROM attendance
            WHERE student_id = %s
            AND class_session_id = %s
        """, (student_id, session_id))

        row = cur.fetchone()

        if row:
            current_status = row[0]

            # ❌ only block if already present
            if current_status == 'present':
                return jsonify({"message": "Already marked"}), 200

            # 🔥 update absent → present
            cur.execute("""
                UPDATE attendance
                SET status = 'present',
                    method = 'manual'
                WHERE student_id = %s
                AND class_session_id = %s
                AND status != 'present'
            """, (student_id, session_id))

            conn.commit()

            return jsonify({"message": "Attendance updated to PRESENT"}), 200

        else:
            # 🟢 fallback (rare case)
            cur.execute("""
                INSERT INTO attendance (
                    student_id,
                    class_session_id,
                    status,
                    method
                )
                VALUES (%s, %s, 'present', 'manual')
            """, (student_id, session_id))

            conn.commit()

            return jsonify({"message": "Attendance marked successfully"}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()
       