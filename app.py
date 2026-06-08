from flask import Flask, request, jsonify, render_template, session, redirect, url_for, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime
import hashlib

app = Flask(__name__)
app.secret_key = 'krunchelite-secret-key-2024'
CORS(app)

# File-based storage
DATA_FILE = 'data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    # Initial data with sample menu items
    return {
        'menu_items': [
            {'id': 1, 'name': 'Gold Label Wagyu Burger', 'category': 'Burgers', 'price': 18.99, 'description': 'Black truffle, wagyu beef, edible gold', 'image_url': 'https://images.pexels.com/photos/1633578/pexels-photo-1633578.jpeg', 'calories': '850 cal', 'prep_time': '15 min', 'spicy_level': 'Medium', 'is_bestseller': True},
            {'id': 2, 'name': 'Crispy Zinger Deluxe', 'category': 'Burgers', 'price': 13.99, 'description': 'Spicy buttermilk chicken, signature sauce', 'image_url': 'https://images.pexels.com/photos/2983101/pexels-photo-2983101.jpeg', 'calories': '720 cal', 'prep_time': '12 min', 'spicy_level': 'Hot', 'is_bestseller': False},
            {'id': 3, 'name': 'Truffle Mushroom Pizza', 'category': 'Pizza', 'price': 19.99, 'description': 'Porcini, truffle oil, fresh mozzarella', 'image_url': 'https://images.pexels.com/photos/825661/pexels-photo-825661.jpeg', 'calories': '980 cal', 'prep_time': '20 min', 'spicy_level': 'No', 'is_bestseller': True},
            {'id': 4, 'name': 'Elite Fried Chicken (10pc)', 'category': 'Crispy Chicken', 'price': 21.99, 'description': 'Secret recipe, double fried, ultra crispy', 'image_url': 'https://images.pexels.com/photos/6065572/pexels-photo-6065572.jpeg', 'calories': '1250 cal', 'prep_time': '20 min', 'spicy_level': 'Mild', 'is_bestseller': True},
            {'id': 5, 'name': 'Parmesan Truffle Fries', 'category': 'Fries & Sides', 'price': 8.99, 'description': 'Fresh parmesan, rosemary, truffle oil', 'image_url': 'https://images.pexels.com/photos/1583884/pexels-photo-1583884.jpeg', 'calories': '450 cal', 'prep_time': '8 min', 'spicy_level': 'No', 'is_bestseller': True},
            {'id': 6, 'name': 'Lamb Shawarma Plate', 'category': 'Shawarma & Wraps', 'price': 17.99, 'description': 'Slow roasted lamb, tahini sauce, pickles', 'image_url': 'https://images.pexels.com/photos/6287764/pexels-photo-6287764.jpeg', 'calories': '750 cal', 'prep_time': '15 min', 'spicy_level': 'Medium', 'is_bestseller': True}
        ],
        'reservations': [],
        'deliveries': [],
        'orders': [],
        'admin_users': [{'username': 'admin', 'password_hash': hashlib.sha256('admin123'.encode()).hexdigest()}],
        'next_ids': {'menu': 7, 'reservation': 1, 'delivery': 1, 'order': 1}
    }

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str, ensure_ascii=False)

def check_password(password, stored_hash):
    return hashlib.sha256(password.encode()).hexdigest() == stored_hash

def check_admin_login():
    return session.get('admin_logged_in', False)

# ============= ADMIN AUTH ROUTES =============
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

@app.route('/admin-logout')
def admin_logout():
    session.clear()
    return redirect('/admin-login')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not check_admin_login():
        return redirect('/admin-login')
    return render_template('admin_dashboard.html')

# ============= MENU MANAGEMENT API =============
@app.route('/api/menu', methods=['GET'])
def get_menu():
    data = load_data()
    return jsonify(data['menu_items'])

@app.route('/api/menu', methods=['POST'])
def add_menu_item():
    if not check_admin_login():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = load_data()
    new_item = request.json
    new_item['id'] = data['next_ids']['menu']
    data['next_ids']['menu'] += 1
    data['menu_items'].append(new_item)
    save_data(data)
    return jsonify(new_item)

@app.route('/api/menu/<int:item_id>', methods=['PUT'])
def update_menu_item(item_id):
    if not check_admin_login():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = load_data()
    updates = request.json
    for item in data['menu_items']:
        if item['id'] == item_id:
            item.update(updates)
            break
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/menu/<int:item_id>', methods=['DELETE'])
def delete_menu_item(item_id):
    if not check_admin_login():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = load_data()
    data['menu_items'] = [item for item in data['menu_items'] if item.get('id') != item_id]
    save_data(data)
    return jsonify({'success': True})

# ============= RESERVATION API =============
@app.route('/api/reservations', methods=['GET'])
def get_reservations():
    if not check_admin_login():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = load_data()
    return jsonify(data['reservations'])

@app.route('/api/reservations', methods=['POST'])
def create_reservation():
    data = load_data()
    new_res = request.json
    new_res['id'] = data['next_ids']['reservation']
    new_res['created_at'] = datetime.now().isoformat()
    new_res['status'] = 'pending'
    data['next_ids']['reservation'] += 1
    data['reservations'].append(new_res)
    save_data(data)
    return jsonify(new_res)

@app.route('/api/reservations/<int:res_id>/status', methods=['PUT'])
def update_reservation_status(res_id):
    if not check_admin_login():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = load_data()
    new_status = request.json.get('status')
    for res in data['reservations']:
        if res.get('id') == res_id:
            res['status'] = new_status
            break
    save_data(data)
    return jsonify({'success': True})

# ============= DELIVERY API =============
@app.route('/api/deliveries', methods=['GET'])
def get_deliveries():
    if not check_admin_login():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = load_data()
    return jsonify(data['deliveries'])

@app.route('/api/deliveries', methods=['POST'])
def register_delivery():
    data = load_data()
    new_del = request.json
    new_del['id'] = data['next_ids']['delivery']
    new_del['registered_at'] = datetime.now().isoformat()
    new_del['status'] = 'active'
    data['next_ids']['delivery'] += 1
    data['deliveries'].append(new_del)
    save_data(data)
    return jsonify(new_del)

@app.route('/api/deliveries/<int:del_id>/status', methods=['PUT'])
def update_delivery_status(del_id):
    if not check_admin_login():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = load_data()
    new_status = request.json.get('status')
    for delivery in data['deliveries']:
        if delivery.get('id') == del_id:
            delivery['status'] = new_status
            break
    save_data(data)
    return jsonify({'success': True})

# ============= ORDERS API =============
@app.route('/api/orders', methods=['GET'])
def get_orders():
    if not check_admin_login():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = load_data()
    return jsonify(data['orders'])

@app.route('/api/orders', methods=['POST'])
def create_order():
    data = load_data()
    new_order = request.json
    new_order['id'] = data['next_ids']['order']
    new_order['created_at'] = datetime.now().isoformat()
    new_order['status'] = 'pending'
    data['next_ids']['order'] += 1
    data['orders'].append(new_order)
    save_data(data)
    return jsonify(new_order)

@app.route('/api/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    if not check_admin_login():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = load_data()
    new_status = request.json.get('status')
    for order in data['orders']:
        if order.get('id') == order_id:
            order['status'] = new_status
            break
    save_data(data)
    return jsonify({'success': True})

# ============= STATISTICS API =============
@app.route('/api/stats', methods=['GET'])
def get_stats():
    if not check_admin_login():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = load_data()
    total_revenue = sum([order.get('total_amount', 0) for order in data['orders']])
    
    return jsonify({
        'total_menu_items': len(data['menu_items']),
        'total_reservations': len(data['reservations']),
        'total_deliveries': len(data['deliveries']),
        'total_orders': len(data['orders']),
        'total_revenue': total_revenue
    })

# ============= SERVE FRONTEND FILES =============
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 KRUNCH ELITE Backend Server Starting...")
    print("=" * 60)
    print("📍 Frontend URL: http://localhost:5000/")
    print("🔐 Admin Login: http://localhost:5000/admin-login")
    print("👤 Username: admin")
    print("🔑 Password: admin123")
    print("=" * 60)
    print("✅ Server is running! Press Ctrl+C to stop")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)