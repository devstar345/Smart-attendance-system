from flask import Blueprint, request, url_for
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash
from config import get_db_connection

forgot_password_bp = Blueprint('staff_forgot_password_bp', __name__)

# Get mail and serializer from current app
mail = None
s = None

def init_staff_forgot_password(app):
    global mail, s
    mail = Mail(app)
    s = URLSafeTimedSerializer(app.config["SECRET_KEY"])


# --- 1. Request Password Reset ---
@forgot_password_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json() or {}
    email = data.get("email")

    if not email:
        return {"success": False, "message": "Email is required"}, 400

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if user exists
        cur.execute("SELECT id, name FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

        if not user:
            return {"success": False, "message": "Email not found"}, 404

        username = user[1]

        # Generate token
        token = s.dumps(email, salt="password-reset-salt")
        reset_link = url_for("staff_forgot_password.reset_password", token=token, _external=True)

        # Send email
        msg = Message(
            subject="Password Reset Request",
            recipients=[email]
        )
        msg.body = f"""
Hello {username},

Click the link below to reset your password:
{reset_link}

This link will expire in 30 minutes.
"""
        mail.send(msg)

        return {"success": True, "message": "Password reset link sent to email"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# --- 2. Reset Password ---
@forgot_password_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        email = s.loads(token, salt="password-reset-salt", max_age=1800)
    except:
        return "Invalid or expired token", 400

    if request.method == "GET":
        # Show the reset password form
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Reset Password</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .container {{ max-width: 400px; margin: 0 auto; }}
                input {{ width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box; }}
                button {{ background: #007bff; color: white; padding: 10px; border: none; width: 100%; cursor: pointer; }}
                .message {{ margin: 10px 0; padding: 10px; border-radius: 4px; }}
                .success {{ background: #d4edda; color: #155724; }}
                .error {{ background: #f8d7da; color: #721c24; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Reset Your Password</h2>
                <form method="POST">
                    <input type="password" name="password" placeholder="Enter new password" required minlength="8">
                    <button type="submit">Reset Password</button>
                </form>
            </div>
        </body>
        </html>
        """

    # Handle POST request
    new_password = request.form.get("password")

    if not new_password:
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Reset Password</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .container {{ max-width: 400px; margin: 0 auto; }}
                .error {{ background: #f8d7da; color: #721c24; padding: 10px; border-radius: 4px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error">Password is required</div>
                <a href="{request.url}">Try again</a>
            </div>
        </body>
        </html>
        """, 400

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        conn.autocommit = False
        cur = conn.cursor()

        # Update password
        hashed_password = generate_password_hash(new_password)

        cur.execute(
            "UPDATE users SET password = %s WHERE email = %s",
            (hashed_password, email)
        )

        if cur.rowcount == 0:
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Reset Password</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .container {{ max-width: 400px; margin: 0 auto; }}
                    .error {{ background: #f8d7da; color: #721c24; padding: 10px; border-radius: 4px; margin: 10px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="error">User not found</div>
                </div>
            </body>
            </html>
            """, 404

        conn.commit()

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Password Reset Successful</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .container {{ max-width: 400px; margin: 0 auto; }}
                .success {{ background: #d4edda; color: #155724; padding: 10px; border-radius: 4px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success">Password reset successful! You can now log in with your new password.</div>
                <a href="/staff/login">Go to Staff Login</a>
            </div>
        </body>
        </html>
        """

    except Exception as e:
        if conn:
            conn.rollback()

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Reset Password Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .container {{ max-width: 400px; margin: 0 auto; }}
                .error {{ background: #f8d7da; color: #721c24; padding: 10px; border-radius: 4px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error">Error: {str(e)}</div>
                <a href="{request.url}">Try again</a>
            </div>
        </body>
        </html>
        """, 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
