from flask import Blueprint, make_response
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import datetime
from config import get_db_connection

unit_report_bp = Blueprint(
    "unit_report",
    __name__,
    url_prefix="/staff/session"
)

# -------------------------------------
# PDF CLASS
# -------------------------------------
class AttendancePDF(FPDF):
    def header(self):

        # 🔥 LOGO (TOP LEFT)
        self.image("static/images/logo.png", x=10, y=8, w=30)

        # move text right so it doesn't overlap logo
        self.set_xy(35, 10)

        self.set_font("Helvetica", "B", 12)
        self.cell(0, 5, "MULTIMEDIA UNIVERSITY",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_font("Helvetica", "", 8)
        self.cell(0, 5, "P.O BOX 15653-00503",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.cell(0, 5, "Telephone: +254 20 7252000, Email: info@mmu.ac.ke",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.ln(5)

        self.set_font("Helvetica", "BU", 10)
        self.cell(0, 10, "UNIT ATTENDANCE REPORT",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        

# -------------------------------------
# GET UNIT REPORT DATA
# -------------------------------------
def get_unit_report(assignment_id):

    conn = get_db_connection()
    cur = conn.cursor()

    # 1. UNIT INFO
    cur.execute("""
        SELECT 
            un.id,
            un.name,
            un.unit_code,
            c.name AS course_name
        FROM unit_assignments ua
        JOIN units un ON ua.unit_id = un.id
        JOIN course c ON ua.course_id = c.course_id
        WHERE ua.assignment_id = %s
    """, (assignment_id,))

    unit = cur.fetchone()

    unit_id = unit[0]
    unit_name = unit[1]
    unit_code = unit[2]
    course_name = unit[3]

    # 2. TOTAL CLASSES
    cur.execute("""
        SELECT COUNT(*)
        FROM class_session
        WHERE unit_assignment_id = %s
    """, (assignment_id,))

    total_classes = cur.fetchone()[0]

    # 3. STUDENT PERFORMANCE
    cur.execute("""
        SELECT 
            u.reg_no,
            u.name,
            COUNT(CASE WHEN a.status = 'present' THEN 1 END) AS attended

        FROM users u
        JOIN enrollments e ON e.student_id = u.id

        JOIN unit_assignments ua 
            ON ua.assignment_id = %s
            AND e.unit_id = ua.unit_id

        JOIN class_session cs 
            ON cs.unit_assignment_id = ua.assignment_id

        LEFT JOIN attendance a 
            ON a.student_id = u.id
            AND a.class_session_id = cs.id

        WHERE ua.assignment_id = %s

        GROUP BY u.id, u.reg_no, u.name
        ORDER BY u.name;
    """, (assignment_id, assignment_id))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    # 4. FORMAT DATA
    result = []

    for r in rows:
        attended = r[2] or 0
        percent = (attended / total_classes * 100) if total_classes > 0 else 0

        result.append({
            "reg_no": r[0],
            "name": r[1],
            "attended": attended,
            "percent": round(percent, 1)
        })

    return result, {
        "unit_id": unit_id,
        "unit_name": unit_name,
        "unit_code": unit_code,
        "course_name": course_name,
        "total_classes": total_classes
    }


# -------------------------------------
# ROUTE
# -------------------------------------
@unit_report_bp.route("/download-unit-report/<int:assignment_id>")
def download_unit_report(assignment_id):

    data, meta = get_unit_report(assignment_id)

    current_date = datetime.now().strftime("%d-%m-%Y")

    pdf = AttendancePDF()
    pdf.add_page()

    # HEADER DETAILS
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(95, 10, meta["unit_code"],
             new_x=XPos.RIGHT, new_y=YPos.TOP)

    pdf.cell(95, 10, current_date,
             align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.cell(0, 10, meta["unit_name"],
             align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, f"COURSE: {meta['course_name']}",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.cell(0, 7, f"TOTAL CLASSES: {meta['total_classes']}",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(5)

    # TABLE HEADER
    pdf.set_font("Helvetica", "B", 9)
    widths = [10, 50, 70, 30, 30]
    headers = ["NO", "REG-NO", "NAME", "ATTENDED", "PERCENT"]

    for i in range(len(headers)):
        pdf.cell(widths[i], 7, headers[i], border=1)
    pdf.ln()

    # TABLE BODY
    pdf.set_font("Helvetica", "", 9)

    for i, row in enumerate(data, start=1):
        pdf.cell(widths[0], 7, str(i), border=1)
        pdf.cell(widths[1], 7, row["reg_no"], border=1)
        pdf.cell(widths[2], 7, row["name"], border=1)
        pdf.cell(widths[3], 7, str(row["attended"]), border=1)

        percent_str = f"{row['percent']}%"
        pdf.cell(widths[4], 7, percent_str, border=1)
        pdf.ln()

    pdf_output = bytes(pdf.output())

    response = make_response(pdf_output)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = (
        f"attachment; filename=Unit_Report_{current_date}.pdf"
    )

    return response