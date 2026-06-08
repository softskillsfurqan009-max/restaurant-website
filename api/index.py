from flask import Flask, request, jsonify, render_template, session, redirect, url_for, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime
import hashlib

app = Flask(__name__, 
           template_folder='../templates',
           static_folder='../static')
app.secret_key = 'krunchelite-secret-key-2024'
app.config['SESSION_TYPE'] = 'filesystem'
CORS(app)

# File-based storage (Vercel's /tmp directory works)
DATA_FILE = '/tmp/data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'menu_items': [],
        'reservations': [],
        'deliveries': [],
        'orders': [],
        'admin_users': [{'username': 'admin', 'password_hash': hashlib.sha256('admin123'.encode()).hexdigest()}],
        'next_ids': {'menu': 1, 'reservation': 1, 'delivery': 1, 'order': 1}
    }

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str, ensure_ascii=False)

def check_password(password, stored_hash):
    return hashlib.sha256(password.encode()).hexdigest() == stored_hash

def check_admin_login():
    return session.get('admin_logged_in', False)

# ============= STATIC FILES =============
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>.html')
def serve_html(filename):
    return send_from_directory('.', f'{filename}.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

# ============= ADMIN AUTH =============
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        data = load_data()
        for admin in data['admin_users']:
            if admin['username'] == username and check_password(password, admin['password_hash']):
                session['admin_logged_in'] = True
                session['admin_username'] = username
                return redirect('/admin/dashboard')
        
        return render_template('admin_login.html', error='Invalid credentials')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not check_admin_login():
        return redirect('/admin-login')
    return render_template('admin_dashboard.html')

@app.route('/admin-logout')
def admin_logout():
    session.clear()
    return redirect('/admin-login')

# ============= API ROUTES =============
@app.route('/api/menu', methods=['GET'])
def get_menu():
    return jsonify(load_data()['menu_items'])

@app.route('/api/reservations', methods=['GET'])
def get_reservations():
    return jsonify(load_data()['reservations'])

@app.route('/api/deliveries', methods=['GET'])
def get_deliveries():
    return jsonify(load_data()['deliveries'])

@app.route('/api/orders', methods=['GET'])
def get_orders():
    return jsonify(load_data()['orders'])

@app.route('/api/stats', methods=['GET'])
def get_stats():
    data = load_data()
    return jsonify({
        'total_menu_items': len(data['menu_items']),
        'total_reservations': len(data['reservations']),
        'total_deliveries': len(data['deliveries']),
        'total_orders': len(data['orders']),
        'total_revenue': 0
    })

# Vercel requires this
app = app