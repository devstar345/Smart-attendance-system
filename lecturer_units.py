from flask import Blueprint, jsonify, session
from config import get_db_connection

lecturer_bp = Blueprint('lecturer_bp', __name__)

@lecturer_bp.route('/dashboard', methods=['GET'])
def get_my_units():
    lecturer_id = session.get("staff_id")  # 🔥 keep consistent

    if not lecturer_id:
        return jsonify({
            "success": False,
            "message": "Not logged in"
        }), 401

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        query = """
        SELECT 
    ua.assignment_id,
    un.unit_code,
    un.name AS unit_name,
    c.name AS course_name,

    COUNT(e.student_id) AS number_of_students

FROM unit_assignments ua

JOIN units un ON ua.unit_id = un.id
JOIN course c ON ua.course_id = c.course_id

LEFT JOIN enrollments e 
    ON e.unit_id = ua.unit_id   -- ✅ removed session restriction

WHERE ua.lecturer_id = %s

GROUP BY 
    ua.assignment_id,
    un.unit_code,
    un.name,
    c.name;
        """

        cur.execute(query, (lecturer_id,))
        rows = cur.fetchall()

        data = []
        for row in rows:
            data.append({
                "assignment_id": row[0],
                "unit_code": row[1],
                "unit_name": row[2],
                "course_name": row[3],
                "number_of_students": row[4]
            })

        return jsonify({
            "success": True,
            "data": data
        })

    except Exception as e:
        print("🔥 ERROR:", e)
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()