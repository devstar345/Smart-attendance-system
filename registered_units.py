from flask import Blueprint, jsonify, session
from config import get_db_connection

student_dashboard_bp = Blueprint(
    "student_dashboard",
    __name__,
    url_prefix="/student"
)

@student_dashboard_bp.route("/my-units", methods=["GET"])
def my_units():
    student_id = session.get("student_id")

    if not student_id:
        return jsonify({"error": "Not logged in"}), 401

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            un.id AS unit_id,
            un.name AS unit_name,
            un.unit_code,

            COUNT(DISTINCT cs.id) AS total_classes,

            COUNT(DISTINCT CASE 
                WHEN a.status = 'present' THEN cs.id 
            END) AS attended,

            ROUND(
                (
                    COUNT(DISTINCT CASE 
                        WHEN a.status = 'present' THEN cs.id 
                    END)::numeric
                    /
                    NULLIF(COUNT(DISTINCT cs.id), 0)
                ) * 100, 
                1
            ) AS percentage

        FROM enrollments e

        JOIN units un ON e.unit_id = un.id
        JOIN unit_assignments ua ON ua.unit_id = un.id

        LEFT JOIN class_session cs 
            ON cs.unit_assignment_id = ua.assignment_id

        LEFT JOIN attendance a 
            ON a.student_id = e.student_id
            AND a.class_session_id = cs.id

        WHERE e.student_id = %s

        GROUP BY un.id, un.name, un.unit_code
        ORDER BY un.name;
    """, (student_id,))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "unit_name": r[1],
            "unit_code": r[2],
            "percentage": float(r[5] or 0)
        })

    return jsonify(result)