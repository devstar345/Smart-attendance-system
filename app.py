import os
from dotenv import load_dotenv
from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from config import get_db_connection

# Student blueprints
from student_restAPI.auth import auth_bp as student_auth_bp
from student_restAPI.devices import devices_bp
from student_restAPI.login import login_bp as student_login_bp
from student_restAPI.forgotPassword import forgot_password_bp, init_forgot_password
from student_restAPI.units import units_bp
from student_restAPI.enroll import enroll_bp
from student_restAPI.active_lesson import active_lessons_bp
from student_restAPI.registered_units import student_dashboard_bp
from student_restAPI.Reset_password import reset_bp




# Staff blueprints
from staff_restApi.auth import auth_bp as staff_auth_bp
from staff_restApi.login import login_bp as staff_login_bp
from staff_restApi.forgotPassword import forgot_password_bp as staff_forgot_password_bp, init_staff_forgot_password
from staff_restApi.lecturer_units import lecturer_bp
from staff_restApi.class_session import class_session_bp as staff_session_bp
from staff_restApi.view_attendance import view_attendance_bp
from staff_restApi.unit_report import unit_report_bp
from staff_restApi.restore_student import restore_bp
from staff_restApi.Reset_password import lecturer_reset_bp




# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')


# --- Mail Configuration ---
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv('MAIL_USERNAME')
app.config["MAIL_PASSWORD"] = os.getenv('MAIL_PASSWORD')
app.config["MAIL_DEFAULT_SENDER"] = os.getenv('MAIL_DEFAULT_SENDER')


# --- Register Blueprints ---
app.register_blueprint(student_auth_bp, url_prefix='/student/auth')
app.register_blueprint(devices_bp, url_prefix='/student/devices')
app.register_blueprint(student_login_bp, url_prefix='/student/login')
app.register_blueprint(forgot_password_bp, url_prefix='/student')
app.register_blueprint(units_bp, url_prefix='/api')
app.register_blueprint(enroll_bp, url_prefix="/api")
app.register_blueprint(active_lessons_bp, url_prefix='/student')
app.register_blueprint(student_dashboard_bp, url_prefix='/student')
app.register_blueprint(reset_bp, url_prefix='/student')

app.register_blueprint(staff_auth_bp, url_prefix='/staff/auth')
app.register_blueprint(staff_login_bp, url_prefix='/staff/login')
app.register_blueprint(staff_forgot_password_bp, url_prefix='/staff')
app.register_blueprint(lecturer_bp, url_prefix="/api")
app.register_blueprint(staff_session_bp, url_prefix='/staff/session')
app.register_blueprint(view_attendance_bp, url_prefix='/staff/session')
app.register_blueprint(unit_report_bp, url_prefix='/staff/session')
app.register_blueprint(restore_bp)
app.register_blueprint(lecturer_reset_bp)


# --- Initialize Password Reset ---
init_forgot_password(app)
init_staff_forgot_password(app)


# --- Helper Functions (AUTH GUARDS) ---
def student_required():
    return 'student_id' in session

def staff_required():
    return 'staff_id' in session


# --- Home ---
@app.route('/')
def home():
    return 'Flask app is running...'


# =========================
# STUDENT ROUTES
# =========================

@app.route('/student/login')
def student_login_page():
    return render_template('student_portal/login.html')


@app.route('/student/register')
def register_page():
    return render_template('student_portal/sign_up.html')


@app.route('/student/forgot_password')
def student_forgot_password_page():
    return render_template('student_portal/forgot_password.html')


@app.route('/student/dashboard')
def student_dashboard():
    if not student_required():
        return redirect(url_for('student_login_page'))

    return render_template(
        'student_portal/dashboard.html',
        name=session.get('student_name')
    )


@app.route('/student/myProfile')
def student_myProfile():
    if not student_required():
        return redirect(url_for('student_login_page'))

    return render_template(
        'student_portal/myProfile.html',
        name=session.get('student_name'),
        reg_no=session.get('reg_no'),
        email=session.get('email')
    )


@app.route('/student/Register_units')
def student_register_units():
    if not student_required():
        return redirect(url_for('student_login_page'))

    return render_template(
        'student_portal/Register_units.html',
        name=session.get('student_name'),
        reg_no=session.get('reg_no'),
        email=session.get('email')
    )
@app.route('/student/markAttendance')
def student_mark_attendance():
    if not student_required():
        return redirect(url_for('student_login_page'))

    session_id = request.args.get('session_id')

    return render_template(
        'student_portal/markAttendance.html',
        name=session.get('student_name'),
        reg_no=session.get('reg_no'),
        email=session.get('email'),
        session_id=session_id
    )
@app.route('/student/Reset_password')
def student_reset_password():
    if not student_required():
        return redirect(url_for('student_login_page'))

    session_id = request.args.get('session_id')

    return render_template(
        'student_portal/Reset_password.html',
        name=session.get('student_name'),
        reg_no=session.get('reg_no'),
        email=session.get('email'),
        session_id=session_id
    )
@app.route('/student/viewAttendance')
def student_view_attendance():
    if not student_required():
        return redirect(url_for('student_login_page'))

    session_id = request.args.get('session_id')

    return render_template(
        'student_portal/ViewAttendance.html',
        name=session.get('student_name'),
        reg_no=session.get('reg_no'),
        email=session.get('email'),
        session_id=session_id
    )

@app.route('/student/logout')
def student_logout():
    session.clear()
    return redirect(url_for('student_login_page'))

@app.route('/student/session-info/<int:session_id>')
def get_session_info(session_id):
    if not student_required():
        return jsonify({"error": "Not logged in"}), 401

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        query = """
        SELECT 
            cs.start_time,
            u.name AS unit_name,
            u.code AS unit_code
        FROM class_sessions cs
        JOIN units u ON cs.unit_id = u.id
        WHERE cs.id = %s
        """

        cur.execute(query, (session_id,))
        result = cur.fetchone()

        if not result:
            return jsonify({"error": "Session not found"}), 404

        data = {
            "date": result[0].isoformat() if result[0] else None,
            "unit_name": result[1],
            "unit_code": result[2]
        }

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# =========================
# STAFF ROUTES
# =========================

@app.route('/staff/login')
def staff_login_page():
    return render_template('staff_portal/login.html')


@app.route('/staff/register')
def staff_register_page():
    return render_template('staff_portal/sign_up.html')


@app.route('/staff/forgot_password')
def staff_forgot_password_page():
    return render_template('staff_portal/forgot_password.html')


@app.route('/staff/dashboard')
def staff_dashboard():
    if not staff_required():
        return redirect(url_for('staff_login_page'))

    return render_template(
        'staff_portal/dashboard.html',
        name=session.get('staff_name')
    )


@app.route('/staff/myProfile')
def staff_myProfile():
    if not staff_required():
        return redirect(url_for('staff_login_page'))

    return render_template(
        'staff_portal/myProfile.html',
        name=session.get('staff_name'),
        pf_no=session.get('pf_no'),
        email=session.get('email')
    )

@app.route('/staff/manage_students')
def staff_manage_students():
    if not staff_required():
        return redirect(url_for('staff_login_page'))

    return render_template(
        'staff_portal/manage_students.html',
        name=session.get('staff_name'),
        pf_no=session.get('pf_no'),
        email=session.get('email')
    )
@app.route('/staff/viewAttendance')
def staff_view_attendance():
    if not staff_required():
        return redirect(url_for('staff_login_page'))

    return render_template(
        'staff_portal/viewAttendance.html',
        name=session.get('staff_name'),
        pf_no=session.get('pf_no'),
        email=session.get('email')
    )
@app.route('/staff/Reset_password')
def staff_reset_password():
    if not staff_required():
        return redirect(url_for('staff_login_page'))

    session_id = request.args.get('session_id')

    return render_template(
        'staff_portal/Reset_password.html',
        name=session.get('staff_name'),
        pf_no=session.get('pf_no'),
        email=session.get('email'),
        session_id=session_id
    )


@app.route('/staff/logout')
def staff_logout():
    session.clear()
    return redirect(url_for('staff_login_page'))


# =========================
# TEST DATABASE CONNECTION
# =========================

@app.route('/test-db')
def test_db():
    try:
        conn = get_db_connection()
        conn.close()
        return 'Database connection successful!'
    except Exception as e:
        return f'Database connection failed: {str(e)}'


# --- Run App ---
if __name__ == '__main__':
    app.run(debug=True)