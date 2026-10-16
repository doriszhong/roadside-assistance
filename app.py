from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from database import get_db, init_db
from functools import wraps
import os, hashlib, secrets, datetime

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(32))
CORS(app, supports_credentials=True)

init_db()

# ─── Auth Helpers ────────────────────────────────────────────────────────────

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "Unauthorized"}), 401
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM sessions WHERE token=%s AND expires_at > NOW()", (token,))
        sess = cursor.fetchone()
        conn.close()
        if not sess:
            return jsonify({"error": "Invalid or expired token"}), 401
        request.user_id = sess["user_id"]
        request.user_role = sess["role"]
        return f(*args, **kwargs)
    return decorated

def require_role(role):
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated(*args, **kwargs):
            if request.user_role != role:
                return jsonify({"error": "Forbidden"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

# ─── Pages ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/mechanic')
def mechanic_portal():
    return render_template('mechanic.html')

@app.route('/admin')
def admin_portal():
    return render_template('admin.html')

# ─── Auth API ─────────────────────────────────────────────────────────────────

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')  # user | mechanic
    phone = data.get('phone', '')

    if not all([name, email, password]):
        return jsonify({"error": "All fields required"}), 400
    if role not in ['user', 'mechanic']:
        return jsonify({"error": "Invalid role"}), 400

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "Email already registered"}), 409

    pw_hash = hash_password(password)
    cursor.execute(
        "INSERT INTO users (name, email, password_hash, role, phone) VALUES (%s,%s,%s,%s,%s)",
        (name, email, pw_hash, role, phone)
    )
    user_id = cursor.lastrowid

    # If mechanic, create mechanic profile
    if role == 'mechanic':
        specialty = data.get('specialty', 'General')
        cursor.execute(
            "INSERT INTO mechanics (user_id, specialty, is_available) VALUES (%s,%s,1)",
            (user_id, specialty)
        )

    conn.commit()
    conn.close()
    return jsonify({"message": "Registered successfully"}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email=%s AND password_hash=%s", (email, hash_password(password)))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return jsonify({"error": "Invalid credentials"}), 401

    token = secrets.token_hex(32)
    expires = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    cursor.execute(
        "INSERT INTO sessions (user_id, token, role, expires_at) VALUES (%s,%s,%s,%s)",
        (user['id'], token, user['role'], expires)
    )
    conn.commit()
    conn.close()
    return jsonify({
        "token": token,
        "user": {"id": user['id'], "name": user['name'], "role": user['role'], "email": user['email']}
    })

@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE token=%s", (token,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Logged out"})

@app.route('/api/auth/me', methods=['GET'])
@require_auth
def me():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email, role, phone, created_at FROM users WHERE id=%s", (request.user_id,))
    user = cursor.fetchone()
    conn.close()
    return jsonify(user)

# ─── SOS / Requests API ───────────────────────────────────────────────────────

@app.route('/api/sos', methods=['POST'])
@require_auth
def trigger_sos():
    data = request.json
    lat = data.get('lat')
    lon = data.get('lon')
    issue_type = data.get('issue_type', 'General')
    description = data.get('description', '')

    if not all([lat, lon]):
        return jsonify({"error": "Location required"}), 400

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # Find nearest available mechanic
    cursor.execute("""
        SELECT m.id, m.user_id, u.name, m.latitude, m.longitude,
               (6371 * ACOS(
                   COS(RADIANS(%s)) * COS(RADIANS(m.latitude)) *
                   COS(RADIANS(m.longitude) - RADIANS(%s)) +
                   SIN(RADIANS(%s)) * SIN(RADIANS(m.latitude))
               )) AS distance
        FROM mechanics m
        JOIN users u ON m.user_id = u.id
        WHERE m.is_available = 1 AND m.latitude IS NOT NULL
        ORDER BY distance ASC
        LIMIT 1
    """, (lat, lon, lat))
    nearest = cursor.fetchone()

    mechanic_id = nearest['id'] if nearest else None
    est_time = round(nearest['distance'] * 3, 0) if nearest else None  # ~3 min/km

    cursor.execute("""
        INSERT INTO sos_requests (user_id, latitude, longitude, issue_type, description, mechanic_id, estimated_arrival)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (request.user_id, lat, lon, issue_type, description, mechanic_id, est_time))
    request_id = cursor.lastrowid

    # Mark mechanic busy
    if mechanic_id:
        cursor.execute("UPDATE mechanics SET is_available=0 WHERE id=%s", (mechanic_id,))

    conn.commit()

    # Fetch created request
    cursor.execute("SELECT * FROM sos_requests WHERE id=%s", (request_id,))
    req = cursor.fetchone()
    conn.close()

    return jsonify({
        "status": "success",
        "request_id": request_id,
        "mechanic_assigned": nearest['name'] if nearest else None,
        "estimated_arrival_minutes": est_time,
        "message": f"Mechanic {nearest['name']} is on the way!" if nearest else "No mechanic available nearby. Please try again."
    })

@app.route('/api/requests', methods=['GET'])
@require_auth
def get_requests():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.user_role == 'admin':
        cursor.execute("""
            SELECT r.*, u.name as user_name, u.phone as user_phone,
                   mu.name as mechanic_name
            FROM sos_requests r
            JOIN users u ON r.user_id = u.id
            LEFT JOIN mechanics m ON r.mechanic_id = m.id
            LEFT JOIN users mu ON m.user_id = mu.id
            ORDER BY r.created_at DESC
            LIMIT 100
        """)
    elif request.user_role == 'mechanic':
        cursor.execute("SELECT id FROM mechanics WHERE user_id=%s", (request.user_id,))
        mech = cursor.fetchone()
        if not mech:
            conn.close()
            return jsonify([])
        cursor.execute("""
            SELECT r.*, u.name as user_name, u.phone as user_phone
            FROM sos_requests r
            JOIN users u ON r.user_id = u.id
            WHERE r.mechanic_id=%s
            ORDER BY r.created_at DESC
        """, (mech['id'],))
    else:
        cursor.execute("""
            SELECT r.*, mu.name as mechanic_name
            FROM sos_requests r
            LEFT JOIN mechanics m ON r.mechanic_id = m.id
            LEFT JOIN users mu ON m.user_id = mu.id
            WHERE r.user_id=%s
            ORDER BY r.created_at DESC
        """, (request.user_id,))

    rows = cursor.fetchall()
    conn.close()
    # Convert datetime objects
    for r in rows:
        for k, v in r.items():
            if isinstance(v, datetime.datetime):
                r[k] = v.isoformat()
    return jsonify(rows)

@app.route('/api/requests/<int:req_id>/status', methods=['PATCH'])
@require_auth
def update_request_status(req_id):
    data = request.json
    status = data.get('status')
    if status not in ['searching', 'dispatched', 'completed', 'cancelled']:
        return jsonify({"error": "Invalid status"}), 400

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sos_requests WHERE id=%s", (req_id,))
    req = cursor.fetchone()
    if not req:
        conn.close()
        return jsonify({"error": "Not found"}), 404

    cursor.execute("UPDATE sos_requests SET status=%s WHERE id=%s", (status, req_id))

    # If completed/cancelled, free the mechanic
    if status in ['completed', 'cancelled'] and req['mechanic_id']:
        cursor.execute("UPDATE mechanics SET is_available=1 WHERE id=%s", (req['mechanic_id'],))

    conn.commit()
    conn.close()
    return jsonify({"message": "Updated"})

# ─── Mechanics API ────────────────────────────────────────────────────────────

@app.route('/api/mechanics', methods=['GET'])
@require_auth
def get_mechanics():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT m.id, u.name, u.phone, u.email, m.specialty, m.is_available,
               m.latitude, m.longitude, m.rating, m.total_jobs, m.created_at
        FROM mechanics m JOIN users u ON m.user_id = u.id
        ORDER BY m.rating DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    for r in rows:
        for k, v in r.items():
            if isinstance(v, datetime.datetime):
                r[k] = v.isoformat()
    return jsonify(rows)

@app.route('/api/mechanics/location', methods=['POST'])
@require_auth
def update_mechanic_location():
    data = request.json
    lat, lon = data.get('lat'), data.get('lon')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE mechanics SET latitude=%s, longitude=%s WHERE user_id=%s",
        (lat, lon, request.user_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Location updated"})

@app.route('/api/mechanics/availability', methods=['PATCH'])
@require_auth
def toggle_availability():
    data = request.json
    available = data.get('available', True)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE mechanics SET is_available=%s WHERE user_id=%s",
        (1 if available else 0, request.user_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Availability updated"})

# ─── Ratings API ──────────────────────────────────────────────────────────────

@app.route('/api/ratings', methods=['POST'])
@require_auth
def submit_rating():
    data = request.json
    request_id = data.get('request_id')
    rating = data.get('rating')  # 1-5
    review = data.get('review', '')

    if not request_id or not rating or not (1 <= int(rating) <= 5):
        return jsonify({"error": "Invalid rating data"}), 400

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT mechanic_id FROM sos_requests WHERE id=%s AND user_id=%s AND status='completed'",
                   (request_id, request.user_id))
    req = cursor.fetchone()
    if not req:
        conn.close()
        return jsonify({"error": "Cannot rate this request"}), 403

    cursor.execute(
        "INSERT INTO ratings (request_id, mechanic_id, user_id, rating, review) VALUES (%s,%s,%s,%s,%s)",
        (request_id, req['mechanic_id'], request.user_id, rating, review)
    )

    # Update mechanic average rating
    cursor.execute(
        "UPDATE mechanics SET rating=(SELECT AVG(rating) FROM ratings WHERE mechanic_id=%s), total_jobs=total_jobs+1 WHERE id=%s",
        (req['mechanic_id'], req['mechanic_id'])
    )

    conn.commit()
    conn.close()
    return jsonify({"message": "Rating submitted"})

# ─── Stats / Admin API ────────────────────────────────────────────────────────

@app.route('/api/admin/stats', methods=['GET'])
@require_role('admin')
def admin_stats():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) as total FROM sos_requests")
    total = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as cnt FROM sos_requests WHERE status='completed'")
    completed = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) as cnt FROM sos_requests WHERE status='searching'")
    active = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE role='user'")
    users = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) as cnt FROM mechanics WHERE is_available=1")
    available_mechs = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) as cnt FROM mechanics")
    total_mechs = cursor.fetchone()['cnt']

    cursor.execute("SELECT AVG(rating) as avg FROM ratings")
    avg_rating = cursor.fetchone()['avg'] or 0

    cursor.execute("""
        SELECT DATE(created_at) as day, COUNT(*) as cnt
        FROM sos_requests
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        GROUP BY DATE(created_at)
        ORDER BY day
    """)
    weekly = cursor.fetchall()
    for w in weekly:
        if isinstance(w.get('day'), datetime.date):
            w['day'] = w['day'].isoformat()

    cursor.execute("""
        SELECT issue_type, COUNT(*) as cnt
        FROM sos_requests
        GROUP BY issue_type
        ORDER BY cnt DESC
    """)
    by_issue = cursor.fetchall()

    conn.close()
    return jsonify({
        "total_requests": total,
        "completed": completed,
        "active": active,
        "total_users": users,
        "available_mechanics": available_mechs,
        "total_mechanics": total_mechs,
        "avg_rating": round(float(avg_rating), 2),
        "weekly_requests": weekly,
        "by_issue_type": by_issue
    })

@app.route('/api/admin/users', methods=['GET'])
@require_role('admin')
def admin_users():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email, role, phone, created_at FROM users ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    for r in rows:
        for k, v in r.items():
            if isinstance(v, datetime.datetime):
                r[k] = v.isoformat()
    return jsonify(rows)

@app.route('/api/admin/users/<int:uid>', methods=['DELETE'])
@require_role('admin')
def delete_user(uid):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=%s", (uid,))
    conn.commit()
    conn.close()
    return jsonify({"message": "User deleted"})

# ─── Notifications (simple polling) ──────────────────────────────────────────

@app.route('/api/notifications', methods=['GET'])
@require_auth
def get_notifications():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM notifications WHERE user_id=%s ORDER BY created_at DESC LIMIT 20",
        (request.user_id,)
    )
    rows = cursor.fetchall()
    # Mark as read
    cursor.execute("UPDATE notifications SET is_read=1 WHERE user_id=%s AND is_read=0", (request.user_id,))
    conn.commit()
    conn.close()
    for r in rows:
        for k, v in r.items():
            if isinstance(v, datetime.datetime):
                r[k] = v.isoformat()
    return jsonify(rows)

@app.route('/api/notifications/unread-count', methods=['GET'])
@require_auth
def unread_count():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as cnt FROM notifications WHERE user_id=%s AND is_read=0", (request.user_id,))
    cnt = cursor.fetchone()['cnt']
    conn.close()
    return jsonify({"count": cnt})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
