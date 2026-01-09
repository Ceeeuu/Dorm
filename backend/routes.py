import os
import random
import html
import time
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models import db, User, Report, ReportLike
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, UserMixin

# --- Flask app & config ---
app = Flask(__name__, static_folder='static', static_url_path='')
# 使用環境變數設定 SECRET_KEY（避免硬編碼）
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change_this_in_prod')
DATABASE_PATH = os.environ.get('DATABASE_URI', 'sqlite:///dormwatch.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# session cookie 強化
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
# 若要在真實 HTTPS 環境，設 SESSION_COOKIE_SECURE=True（預設在本地開發設 False）
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'

# 只允許本機端 origin（開發用）
CORS(app, resources={r"/*": {"origins": ["http://localhost:5000", "http://127.0.0.1:5000"]}})

# init db & login
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Simple user adapter for Flask-Login (UserMixin)
class LoginUser(UserMixin):
    def __init__(self, user: User):
        self.id = user.id
        self.username = user.username

@login_manager.user_loader
def load_user(user_id):
    u = User.query.get(int(user_id))
    if not u:
        return None
    return LoginUser(u)

with app.app_context():
    db.create_all()

# Simple in-memory rate limiter (per IP)
_rate_limit_store = {}
def is_rate_limited(key, limit=5, per=60):
    now = time.time()
    lst = _rate_limit_store.get(key, [])
    # keep only recent
    lst = [t for t in lst if now - t < per]
    if len(lst) >= limit:
        _rate_limit_store[key] = lst
        return True
    lst.append(now)
    _rate_limit_store[key] = lst
    return False

# Nickname pools (server side)
adjs = ["瘋狂的","可愛的","懶惰的","勇敢的","神秘的","悄悄的"]
animals = ["水獺","貓咪","狐狸","刺蝟","貓頭鷹","兔子"]

# --- Routes ---

# Serve SPA index
@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

# Register
@app.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400
    if len(username) > 80 or len(password) < 6:
        return jsonify({'error': 'invalid username or password length'}), 400
    # check existing
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'username taken'}), 400
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'registered successfully'}), 201

# Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'invalid credentials'}), 401
    login_user(LoginUser(user))
    return jsonify({'message': 'logged in', 'username': user.username})

# Logout
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'logged out'})

# Submit report (anonymous allowed)
@app.route('/report', methods=['POST'])
def add_report():
    ip = request.remote_addr or 'unknown'
    if is_rate_limited(f"report:{ip}", limit=5, per=60):
        return jsonify({'error': 'rate limit exceeded'}), 429

    data = request.json or {}
    room = (data.get('room') or '').strip()
    content = (data.get('content') or '').strip()

    # basic input validation
    if not room or not content:
        return jsonify({'error': 'room and content required'}), 400
    if len(room) > 20 or len(content) > 1000:
        return jsonify({'error': 'input too long'}), 400

    # server-side nickname (prevent client spoof)
    nickname = random.choice(adjs) + random.choice(animals)

    new_report = Report(
        room=room,
        content=content,
        nickname=nickname
    )
    db.session.add(new_report)
    db.session.commit()

    # When returning, escape content to avoid stored-XSS
    return jsonify({
        'id': new_report.id,
        'room': html.escape(new_report.room),
        'content': html.escape(new_report.content),
        'nickname': html.escape(new_report.nickname),
        'likes': new_report.likes
    }), 201

# Get reports (anonymous readable)
@app.route('/reports', methods=['GET'])
def get_reports():
    reports = Report.query.order_by(Report.created_at.desc()).all()
    result = []
    for r in reports:
        result.append({
            'id': r.id,
            'content': html.escape(r.content),
            'room': html.escape(r.room),
            'nickname': html.escape(r.nickname),
            'likes': r.likes
        })
    return jsonify(result)

# Like a report (requires login) - prevents duplicate like per user
@app.route('/report/<int:report_id>/like', methods=['POST'])
@login_required
def like_report(report_id):
    ip = request.remote_addr or 'unknown'
    if is_rate_limited(f"like:{ip}", limit=10, per=60):
        return jsonify({'error': 'rate limit exceeded'}), 429

    report = Report.query.get_or_404(report_id)
    # prevent duplicate likes by same user
    existing = ReportLike.query.filter_by(user_id=int(current_user.id), report_id=report.id).first()
    if existing:
        return jsonify({'error': 'already liked'}), 400

    like = ReportLike(user_id=int(current_user.id), report_id=report.id)
    report.likes = report.likes + 1
    db.session.add(like)
    db.session.commit()
    return jsonify({'likes': report.likes})

# Get current user
@app.route('/me', methods=['GET'])
def me():
    if current_user.is_authenticated:
        return jsonify({'authenticated': True, 'username': current_user.username})
    return jsonify({'authenticated': False})
