from flask import Blueprint, request, jsonify
from config import get_db_connection

class_session_bp = Blueprint('class_session', __name__)


# =========================
# 🟢 START SESSION
# =========================
@class_session_bp.route('/start-session', methods=['POST'])
def start_session():
    data = request.json

    assignment_id = data.get('assignment_id')
    lecturer_lat = data.get('lecturer_lat')
    lecturer_lng = data.get('lecturer_lng')

    # 🔒 proper validation
    if not assignment_id or lecturer_lat is None or lecturer_lng is None:
        return jsonify({"error": "Missing required data"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # 🔥 prevent multiple active sessions
        cur.execute("""
            SELECT id FROM class_session
            WHERE unit_assignment_id = %s
            AND status = 'active'
        """, (assignment_id,))

        existing = cur.fetchone()
        if existing:
            return jsonify({
                "message": "Session already active",
                "session_id": existing[0]
            }), 200

        # 🔥 create session
        cur.execute("""
            INSERT INTO class_session (
                unit_assignment_id,
                status,
                started_at,
                lecturer_lat,
                lecturer_lng
            )
            VALUES (%s, 'active', NOW(), %s, %s)
            RETURNING id
        """, (assignment_id, lecturer_lat, lecturer_lng))

        session_id = cur.fetchone()[0]

        # 🔥 mark all students absent
        cur.execute("""
            INSERT INTO attendance (student_id, class_session_id, status, method)
            SELECT 
                e.student_id,
                %s,
                'absent',
                'system'
            FROM enrollments e
            WHERE e.unit_id = (
                SELECT unit_id FROM unit_assignments WHERE assignment_id = %s
            )
            ON CONFLICT (student_id, class_session_id)
            DO NOTHING;
        """, (session_id, assignment_id))

        conn.commit()

        return jsonify({
            "message": "Session started",
            "session_id": session_id
        })

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()


# =========================
# 🔴 END SESSION
# =========================
@class_session_bp.route('/end-session', methods=['POST'])
def end_session():
    data = request.json
    session_id = data.get("session_id")

    if not session_id:
        return jsonify({"error": "session_id required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # 🔥 safe update (only if active)
        cur.execute("""
            UPDATE class_session
            SET status = 'ended',
                ended_at = NOW()
            WHERE id = %s
            AND status = 'active'
            RETURNING id
        """, (session_id,))

        updated = cur.fetchone()

        if not updated:
            return jsonify({
                "error": "Session not found or already ended"
            }), 400

        conn.commit()

        return jsonify({"message": "Session ended"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()


# =========================
# 🟡 GET CURRENT SESSION (OPTIONAL)
# =========================
@class_session_bp.route('/current-session/<int:assignment_id>', methods=['GET'])
def current_session(assignment_id):

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT id
            FROM class_session
            WHERE unit_assignment_id = %s
            AND status = 'active'
            ORDER BY started_at DESC
            LIMIT 1
        """, (assignment_id,))

        row = cur.fetchone()

        if row:
            return jsonify({
                "active": True,
                "session_id": row[0]
            })

        return jsonify({"active": False})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()


# =========================
# 🔵 GET ALL ACTIVE SESSIONS (CRITICAL FIX)
# =========================
@class_session_bp.route('/all-active-sessions', methods=['GET'])
def all_active_sessions():

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT id, unit_assignment_id
            FROM class_session
            WHERE status = 'active'
        """)

        rows = cur.fetchall()

        result = []
        for r in rows:
            result.append({
                "session_id": r[0],
                "assignment_id": r[1]
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()