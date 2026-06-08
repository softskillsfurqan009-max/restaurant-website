from flask import Flask, request, jsonify, session, redirect, url_for, send_from_directory
import json
import os
import hashlib
from functools import wraps

app = Flask(__name__, static_folder='..', template_folder='..')
app.secret_key = 'krunchelite-secret-key-2024'

DATA_FILE = '/tmp/data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        'admin_users': [{'username': 'admin', 'password': hashlib.sha256('admin123'.encode()).hexdigest()}],
        'menu_items': [
            {'id': 1, 'name': 'Gold Label Wagyu Burger', 'category': 'Burgers', 'price': 18.99, 'image_url': 'https://images.pexels.com/photos/1633578/pexels-photo-1633578.jpeg', 'description': 'Black truffle, wagyu beef'},
            {'id': 2, 'name': 'Crispy Zinger Deluxe', 'category': 'Burgers', 'price': 13.99, 'image_url': 'https://images.pexels.com/photos/2983101/pexels-photo-2983101.jpeg', 'description': 'Spicy buttermilk chicken'},
            {'id': 3, 'name': 'Truffle Mushroom Pizza', 'category': 'Pizza', 'price': 19.99, 'image_url': 'https://images.pexels.com/photos/825661/pexels-photo-825661.jpeg', 'description': 'Porcini, truffle oil, mozzarella'}
        ],
        'reservations': [],
        'orders': [],
        'deliveries': []
    }

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/admin-login')
        return f(*args, **kwargs)
    return decorated_function

# ============= STATIC FILES =============
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>.html')
def serve_html(filename):
    return send_from_directory('.', f'{filename}.html')

# ============= ADMIN LOGIN =============
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed = hashlib.sha256(password.encode()).hexdigest()
        
        data = load_data()
        for admin in data['admin_users']:
            if admin['username'] == username and admin['password'] == hashed:
                session['logged_in'] = True
                return redirect('/admin-dashboard')
        return render_template_string(LOGIN_HTML, error='Invalid credentials')
    
    return render_template_string(LOGIN_HTML)

# ============= ADMIN DASHBOARD =============
@app.route('/admin-dashboard')
@login_required
def admin_dashboard():
    return render_template_string(DASHBOARD_HTML)

# ============= ADMIN LOGOUT =============
@app.route('/admin-logout')
def admin_logout():
    session.clear()
    return redirect('/admin-login')

# ============= API ROUTES =============
@app.route('/api/menu', methods=['GET'])
def get_menu():
    data = load_data()
    return jsonify(data['menu_items'])

@app.route('/api/menu', methods=['POST'])
@login_required
def add_menu_item():
    data = load_data()
    new_item = request.json
    new_item['id'] = max([i['id'] for i in data['menu_items']] + [0]) + 1
    data['menu_items'].append(new_item)
    save_data(data)
    return jsonify(new_item)

@app.route('/api/menu/<int:item_id>', methods=['DELETE'])
@login_required
def delete_menu_item(item_id):
    data = load_data()
    data['menu_items'] = [i for i in data['menu_items'] if i['id'] != item_id]
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/reservations', methods=['GET'])
@login_required
def get_reservations():
    data = load_data()
    return jsonify(data['reservations'])

@app.route('/api/orders', methods=['GET'])
@login_required
def get_orders():
    data = load_data()
    return jsonify(data['orders'])

@app.route('/api/deliveries', methods=['GET'])
@login_required
def get_deliveries():
    data = load_data()
    return jsonify(data['deliveries'])

@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    data = load_data()
    return jsonify({
        'total_menu_items': len(data['menu_items']),
        'total_reservations': len(data['reservations']),
        'total_orders': len(data['orders']),
        'total_deliveries': len(data['deliveries']),
        'total_revenue': 0
    })

# ============= HTML TEMPLATES =============
LOGIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Login - KRUNCH ELITE</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #050505, #1a1a1a);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .login-container {
            background: rgba(20,20,20,0.95);
            padding: 3rem;
            border-radius: 40px;
            border: 2px solid #D4AF37;
            width: 100%;
            max-width: 450px;
            text-align: center;
        }
        .logo-icon {
            width: 80px;
            height: 80px;
            background: #D4AF37;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5rem;
            font-weight: bold;
            color: #050505;
            margin: 0 auto 1.5rem;
        }
        h2 { color: #D4AF37; margin-bottom: 0.5rem; }
        .input-group { margin-bottom: 1.5rem; text-align: left; }
        .input-group input {
            width: 100%;
            padding: 15px 20px;
            background: rgba(10,10,10,0.95);
            border: 1px solid #D4AF37;
            border-radius: 30px;
            color: white;
            font-size: 1rem;
        }
        button {
            width: 100%;
            background: #D4AF37;
            color: #050505;
            padding: 14px;
            border: none;
            border-radius: 30px;
            font-weight: bold;
            font-size: 1rem;
            cursor: pointer;
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(212,175,55,0.4); }
        .error { color: #ff4444; margin-top: 1rem; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo-icon">K</div>
        <h2>Admin Login</h2>
        <p style="color: #B0B0B0; margin-bottom: 2rem;">KRUNCH ELITE Dashboard</p>
        <form method="POST">
            <div class="input-group">
                <input type="text" name="username" placeholder="Username" required>
            </div>
            <div class="input-group">
                <input type="password" name="password" placeholder="Password" required>
            </div>
            <button type="submit">Login to Dashboard</button>
            {% if error %}
                <p class="error">{{ error }}</p>
            {% endif %}
        </form>
    </div>
</body>
</html>
'''

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard - KRUNCH ELITE</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0A0A0A; color: white; }
        .sidebar { position: fixed; left: 0; top: 0; width: 260px; height: 100%; background: #0F0F0F; border-right: 1px solid #D4AF37; padding: 2rem 1rem; overflow-y: auto; }
        .sidebar .logo-icon { width: 60px; height: 60px; background: #D4AF37; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; margin: 0 auto 1rem; color: #050505; font-weight: bold; }
        .sidebar nav a { display: flex; align-items: center; gap: 12px; padding: 12px 20px; color: #B0B0B0; text-decoration: none; border-radius: 12px; margin-bottom: 8px; cursor: pointer; }
        .sidebar nav a:hover, .sidebar nav a.active { background: rgba(212,175,55,0.1); color: #D4AF37; }
        .main-content { margin-left: 260px; padding: 2rem; }
        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; margin-bottom: 2rem; }
        .stat-card { background: rgba(20,20,20,0.9); border-radius: 24px; padding: 1.5rem; border: 1px solid #D4AF37; text-align: center; }
        .stat-card i { font-size: 2rem; color: #D4AF37; }
        .stat-card .number { font-size: 2rem; font-weight: 800; }
        .section { background: rgba(20,20,20,0.8); border-radius: 28px; padding: 1.5rem; border: 1px solid #D4AF37; overflow-x: auto; }
        .section h2 { color: #D4AF37; margin-bottom: 1rem; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid rgba(212,175,55,0.2); }
        th { color: #D4AF37; }
        button { background: #D4AF37; color: #050505; border: none; padding: 6px 15px; border-radius: 20px; cursor: pointer; margin: 0 3px; }
        .btn-add { background: #D4AF37; padding: 10px 20px; border-radius: 30px; margin-bottom: 1rem; cursor: pointer; font-weight: bold; border: none; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); justify-content: center; align-items: center; z-index: 1000; }
        .modal-content { background: #1A1A1A; border-radius: 28px; padding: 2rem; width: 90%; max-width: 500px; border: 2px solid #D4AF37; }
        .modal-content input, .modal-content select { width: 100%; padding: 12px; margin: 10px 0; background: #0A0A0A; border: 1px solid #D4AF37; border-radius: 20px; color: white; }
        @media (max-width: 768px) { .sidebar { width: 70px; } .sidebar span { display: none; } .main-content { margin-left: 70px; } .stats-grid { grid-template-columns: repeat(2,1fr); } }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body>
    <div class="sidebar">
        <div class="logo-icon">K</div>
        <nav>
            <a class="active" data-tab="dashboard"><i class="fas fa-chart-line"></i> <span>Dashboard</span></a>
            <a data-tab="menu"><i class="fas fa-utensils"></i> <span>Menu</span></a>
            <a data-tab="reservations"><i class="fas fa-calendar-check"></i> <span>Reservations</span></a>
            <a data-tab="deliveries"><i class="fas fa-truck"></i> <span>Deliveries</span></a>
            <a data-tab="orders"><i class="fas fa-shopping-cart"></i> <span>Orders</span></a>
            <a href="/admin-logout"><i class="fas fa-sign-out-alt"></i> <span>Logout</span></a>
        </nav>
    </div>
    <div class="main-content" id="mainContent"></div>
    <div id="menuModal" class="modal"><div class="modal-content"><h3 style="color:#D4AF37;">Add Menu Item</h3>
        <input type="text" id="itemName" placeholder="Item Name">
        <select id="itemCategory"><option>Burgers</option><option>Pizza</option><option>Crispy Chicken</option></select>
        <input type="number" id="itemPrice" placeholder="Price">
        <input type="text" id="itemDesc" placeholder="Description">
        <input type="text" id="itemImage" placeholder="Image URL">
        <button onclick="addMenuItem()">Add</button><button onclick="closeModal('menuModal')">Cancel</button>
    </div></div>
    <script>
        function loadDashboard(){fetch('/api/stats').then(r=>r.json()).then(d=>{document.getElementById('mainContent').innerHTML='<div class="stats-grid"><div class="stat-card"><i class="fas fa-hamburger"></i><div class="number">'+d.total_menu_items+'</div><div>Menu Items</div></div><div class="stat-card"><i class="fas fa-calendar"></i><div class="number">'+d.total_reservations+'</div><div>Reservations</div></div><div class="stat-card"><i class="fas fa-truck"></i><div class="number">'+d.total_deliveries+'</div><div>Deliveries</div></div><div class="stat-card"><i class="fas fa-shopping-cart"></i><div class="number">'+d.total_orders+'</div><div>Orders</div></div></div><div class="section"><h2>Dashboard</h2><p>Welcome to KRUNCH ELITE Admin Panel</p></div>'})}
        function loadMenu(){fetch('/api/menu').then(r=>r.json()).then(i=>{let h='<div><button class="btn-add" onclick="openModal(\'menuModal\')">+ Add Item</button></div><div class="section"><h2>Menu Items</h2><table><thead><tr><th>Image</th><th>Name</th><th>Category</th><th>Price</th><th>Action</th></tr></thead><tbody>';i.forEach(item=>{h+='<tr><td><img src="'+item.image_url+'" width="40" style="border-radius:10px"></td><td>'+item.name+'</td><td>'+item.category+'</td><td>$'+item.price+'</td><td><button onclick="deleteItem('+item.id+')">Delete</button></td></tr>'});h+='</tbody></table></div>';document.getElementById('mainContent').innerHTML=h})}
        function loadReservations(){fetch('/api/reservations').then(r=>r.json()).then(i=>{let h='<div class="section"><h2>Reservations</h2><table><thead><tr><th>Name</th><th>Date</th><th>Time</th><th>Guests</th></tr></thead><tbody>';i.forEach(item=>{h+='<tr><td>'+item.customer_name+'</td><td>'+item.reservation_date+'</td><td>'+item.reservation_time+'</td><td>'+item.guests+'</td></tr>'});h+='</tbody></table></div>';document.getElementById('mainContent').innerHTML=h})}
        function loadDeliveries(){fetch('/api/deliveries').then(r=>r.json()).then(i=>{let h='<div class="section"><h2>Deliveries</h2><table><thead><tr><th>Name</th><th>Phone</th><th>Address</th></tr></thead><tbody>';i.forEach(item=>{h+='<tr><td>'+item.full_name+'</td><td>'+item.phone+'</td><td>'+(item.address||'').substring(0,30)+'...</td></tr>'});h+='</tbody></table></div>';document.getElementById('mainContent').innerHTML=h})}
        function loadOrders(){fetch('/api/orders').then(r=>r.json()).then(i=>{let h='<div class="section"><h2>Orders</h2><table><thead><tr><th>Customer</th><th>Items</th><th>Total</th></tr></thead><tbody>';i.forEach(item=>{h+='<tr><td>'+item.customer_name+'</td><td>'+(item.items||'').substring(0,30)+'...</td><td>$'+item.total_amount+'</td></tr>'});h+='</tbody></table></div>';document.getElementById('mainContent').innerHTML=h})}
        function addMenuItem(){let item={name:document.getElementById('itemName').value,category:document.getElementById('itemCategory').value,price:parseFloat(document.getElementById('itemPrice').value),description:document.getElementById('itemDesc').value,image_url:document.getElementById('itemImage').value};fetch('/api/menu',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(item)}).then(()=>{closeModal('menuModal');loadMenu()})}
        function deleteItem(id){if(confirm('Delete this item?')){fetch('/api/menu/'+id,{method:'DELETE'}).then(()=>loadMenu())}}
        function openModal(id){document.getElementById(id).style.display='flex'}
        function closeModal(id){document.getElementById(id).style.display='none'}
        document.querySelectorAll('.sidebar nav a').forEach(link=>{link.onclick=(e)=>{e.preventDefault();document.querySelectorAll('.sidebar nav a').forEach(l=>l.classList.remove('active'));link.classList.add('active');let tab=link.dataset.tab;if(tab=='dashboard')loadDashboard();else if(tab=='menu')loadMenu();else if(tab=='reservations')loadReservations();else if(tab=='deliveries')loadDeliveries();else if(tab=='orders')loadOrders()}})
        loadDashboard();
    </script>
</body>
</html>
'''

def render_template_string(template, **kwargs):
    from flask import render_template_string as flask_render
    return flask_render(template, **kwargs)

if __name__ == '__main__':
    app.run()