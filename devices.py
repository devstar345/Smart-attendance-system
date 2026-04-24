from flask import Blueprint, request, jsonify
from config import get_db_connection

devices_bp = Blueprint('devices_bp', __name__)

@devices_bp.route('/register', methods=['POST'])
def register_device():
    data = request.get_json() or {}

    # Required fields
    user_id = data.get('user_id')
    visitor_id = data.get('visitorId')

    if not user_id or not visitor_id:
        return jsonify({
            "success": False,
            "message": "user_id and visitorId are required"
        }), 400

    user_agent = data.get('userAgent')
    platform = data.get('platform')
    language = data.get('language')
    screen_resolution = data.get('screenResolution')
    timezone = data.get('timezone')
    device_memory = data.get('deviceMemory')
    hardware_concurrency = data.get('hardwareConcurrency')

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        conn.autocommit = False
        cur = conn.cursor()

        # Check if user exists
        cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cur.fetchone():
            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        # Prevent duplicate device per user
        cur.execute(
            "SELECT id FROM user_deviceInfo WHERE user_id = %s AND visitor_id = %s",
            (user_id, visitor_id)
        )

        if cur.fetchone():
            return jsonify({
                "success": False,
                "message": "Device already registered for this user"
            }), 409

        # Insert device info
        insert_sql = """
            INSERT INTO user_deviceInfo 
            (user_id, visitor_id, user_agent, platform, language, screen_resolution, timezone, device_memory, hardware_concurrency)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cur.execute(insert_sql, (
            user_id,
            visitor_id,
            user_agent,
            platform,
            language,
            screen_resolution,
            timezone,
            device_memory,
            hardware_concurrency
        ))

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Device information saved successfully"
        }), 201

    except Exception as e:
        if conn:
            conn.rollback()

        return jsonify({
            "success": False,
            "message": f"Device registration error: {str(e)}"
        }), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()