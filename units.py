from flask import Blueprint, jsonify, session
from config import get_db_connection

units_bp = Blueprint('units_bp', __name__)

@units_bp.route('/units', methods=['GET'])
def get_units_by_course():
    # 🔐 Get course_id from session
    course_id = session.get('course_id')

    if not course_id:
        return jsonify({
            "success": False,
            "message": "Course not found in session"
        }), 400

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        query = """
             SELECT 
        un.id AS unit_id,
        un.unit_code,
        un.name
    FROM course_units cu
    JOIN units un ON cu.unit_id = un.id
    WHERE cu.course_id = %s
        """

        cur.execute(query, (course_id,))
        units = cur.fetchall()

        return jsonify({
            "success": True,
            "data": [
                {
                    "unit_id": u[0],
                    "unit_code": u[1],
                    "name": u[2]
                } for u in units
            ]
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


@units_bp.route('/my-units', methods=['GET'])
def get_lecturer_units():
    # 🔐 Get staff_id from session
    staff_id = session.get('staff_id')

    if not staff_id:
        return jsonify({
            "success": False,
            "message": "Staff not logged in"
        }), 401

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        query = """
            SELECT 
                la.id AS assignment_id,
                u.unit_code,
                u.name AS unit_name,
                c.name AS course_name,
                COUNT(e.student_id) AS number_of_students
            FROM lecturer_assignments la
            JOIN units u ON la.unit_id = u.id
            JOIN courses c ON la.course_id = c.id
            LEFT JOIN enrollments e ON e.unit_id = la.unit_id 
                AND e.session_id = (SELECT id FROM academic_sessions WHERE is_active = TRUE LIMIT 1)
            WHERE la.lecturer_id = %s
            GROUP BY la.id, u.unit_code, u.name, c.name
        """

        cur.execute(query, (staff_id,))
        units = cur.fetchall()

        return jsonify({
            "success": True,
            "data": [
                {
                    "assignment_id": u[0],
                    "unit_code": u[1],
                    "unit_name": u[2],
                    "course_name": u[3],
                    "number_of_students": u[4]
                } for u in units
            ]
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