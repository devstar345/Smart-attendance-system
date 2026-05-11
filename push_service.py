import os
import json
import logging
import base64
from pywebpush import webpush, WebPushException
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    Encoding,
    PrivateFormat,
    NoEncryption,
)
from cryptography.hazmat.backends import default_backend
from config import get_db_connection

logger = logging.getLogger(__name__)


def _normalize_private_key(private_key: str) -> str:
    if private_key.strip().startswith("-----BEGIN"):
        key_bytes = private_key.encode("utf-8")
        key = load_pem_private_key(key_bytes, password=None, backend=default_backend())
        der = key.private_bytes(
            encoding=Encoding.DER,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption(),
        )
        return base64.urlsafe_b64encode(der).decode("utf-8").rstrip("=")
    return private_key


# ---------------------------
# VAPID CONFIG
# ---------------------------
def get_vapid_config():
    print("🔑 Checking VAPID keys...")

    private_key = os.getenv("VAPID_PRIVATE_KEY")
    public_key = os.getenv("VAPID_PUBLIC_KEY")

    if private_key:
        private_key = private_key.strip()
        if private_key.startswith('"') and private_key.endswith('"'):
            private_key = private_key[1:-1]
        private_key = private_key.replace('\\n', '\n')
        private_key = _normalize_private_key(private_key)

    if public_key:
        public_key = public_key.strip()
        if public_key.startswith('"') and public_key.endswith('"'):
            public_key = public_key[1:-1]

    if not private_key or not public_key:
        print("❌ VAPID MISSING")
        raise RuntimeError("VAPID keys missing")

    print("✅ VAPID OK")

    claims = {
        "sub": f"mailto:{os.getenv('VAPID_CLAIM_EMAIL', 'admin@example.com')}"
    }

    return private_key, public_key, claims


def get_vapid_public_key():
    _, public_key, _ = get_vapid_config()
    return public_key


# ---------------------------
# SINGLE PUSH
# ---------------------------
def send_web_push(subscription_info, payload):
    private_key, _, claims = get_vapid_config()

    if isinstance(payload, dict):
        payload = json.dumps(payload)

    print("📤 Sending push →", subscription_info.get("endpoint"))

    try:
        webpush(
            subscription_info=subscription_info,
            data=payload,
            vapid_private_key=private_key,
            vapid_claims=claims,
            timeout=10
        )

        print("✅ PUSH SUCCESS")

    except WebPushException as exc:
        print("❌ PUSH FAILED")

        status = exc.response.status_code if exc.response else None
        print("Status:", status)

        if exc.response:
            print("Body:", exc.response.text)

        raise


# ---------------------------
# MULTI PUSH
# ---------------------------
def send_push_notifications_to_students(student_ids, payload):

    print("🚀 PUSH START")
    print("Students input:", student_ids)

    if not student_ids:
        print("❌ NO STUDENTS → STOP")
        return 0

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT endpoint, p256dh, auth
            FROM push_subscriptions
            WHERE student_id = ANY(%s)
            """,
            (student_ids,)
        )

        subscriptions = cur.fetchall()

        print("📦 Subscriptions found:", len(subscriptions))

        if not subscriptions:
            print("❌ NO SUBSCRIPTIONS IN DB")
            return 0

        success = 0

        for endpoint, p256dh, auth in subscriptions:

            if not endpoint or not p256dh or not auth:
                print("⚠️ Invalid subscription skipped")
                continue

            sub = {
                "endpoint": endpoint,
                "keys": {
                    "p256dh": p256dh,
                    "auth": auth
                }
            }

            try:
                send_web_push(sub, payload)
                success += 1

            except WebPushException as exc:
                status_code = exc.response.status_code if exc.response else None
                body = exc.response.text if exc.response else ''
                print("❌ ERROR SENDING:", exc)
                print("Status:", status_code)
                print("Body:", body)

                if status_code in (404, 410) or 'unsubscribed' in body.lower() or 'expired' in body.lower():
                    print("🗑️ Removing expired subscription:", endpoint)
                    cur.execute(
                        "DELETE FROM push_subscriptions WHERE endpoint = %s",
                        (endpoint,)
                    )
                    conn.commit()

            except Exception as e:
                print("❌ ERROR SENDING:", e)

        print("🎯 PUSH SENT:", success)

        return success

    finally:
        cur.close()
        conn.close()


# ---------------------------
# ASSIGNMENT PUSH
# ---------------------------
def send_assignment_push_notifications(assignment_id, session_id, unit_name, lecturer_name):

    print("🚀 ASSIGNMENT PUSH START")
    print("Assignment:", assignment_id)

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT DISTINCT e.student_id
            FROM enrollments e
            JOIN unit_assignments ua
                ON ua.unit_id = e.unit_id
            WHERE ua.assignment_id = %s
            """,
            (assignment_id,)
        )

        student_ids = [r[0] for r in cur.fetchall()]

        print("👨‍🎓 Students:", student_ids)

    finally:
        cur.close()
        conn.close()

    payload = {
        "title": f"Class started: {unit_name}",
        "body": f"{lecturer_name} started attendance for {unit_name}",
        "data": {
            "url": f"/student/markAttendance?session_id={session_id}",
            "session_id": session_id
        },
        "tag": f"lesson-{session_id}"
    }

    return send_push_notifications_to_students(student_ids, payload)