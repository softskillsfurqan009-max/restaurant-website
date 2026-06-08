from flask import Flask, request, jsonify, session, redirect, url_for, send_from_directory
import json
import os
import hashlib

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'your-secret-key-here'
app.config['SESSION_TYPE'] = 'filesystem'

DATA_FILE = '/tmp/data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        'admin_users': [{'username': 'admin', 'password': hashlib.sha256('admin123'.encode()).hexdigest()}],
        'menu_items': []
    }

@app.route('/')
def home():
    return send_from_directory('..', 'index.html')

@app.route('/<path:filename>')
def serve_file(filename):
    return send_from_directory('..', filename)

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
                return redirect('/admin-dashboard.html')
        return '<h3>Invalid Credentials</h3><a href="/admin-login">Try Again</a>'
    
    # Return simple HTML login form
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Admin Login</title><style>
        body{background:#0a0a0a;font-family:Arial;display:flex;justify-content:center;align-items:center;height:100vh;}
        .login{background:#1a1a1a;padding:40px;border-radius:20px;border:1px solid #D4AF37;text-align:center;}
        input{display:block;width:100%;padding:12px;margin:10px 0;background:#0a0a0a;border:1px solid #D4AF37;border-radius:25px;color:white;}
        button{background:#D4AF37;color:#000;padding:12px 30px;border:none;border-radius:25px;cursor:pointer;font-weight:bold;}
        h2{color:#D4AF37;}
    </style></head>
    <body>
    <div class="login">
        <h2>KRUNCH ELITE Admin</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
    </div>
    </body>
    </html>
    '''

@app.route('/admin-dashboard.html')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect('/admin-login')
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Admin Dashboard</title><style>
        body{background:#0a0a0a;font-family:Arial;color:white;padding:20px;}
        .header{background:#D4AF37;color:#000;padding:15px;border-radius:10px;margin-bottom:20px;}
        button{background:#D4AF37;color:#000;padding:10px 20px;border:none;border-radius:20px;cursor:pointer;margin:5px;}
        table{width:100%;border-collapse:collapse;margin-top:20px;}
        th,td{padding:12px;text-align:left;border-bottom:1px solid #333;}
        th{color:#D4AF37;}
    </style></head>
    <body>
    <div class="header">
        <h2>KRUNCH ELITE - Admin Dashboard</h2>
        <p>Welcome Admin! <a href="/admin-logout">Logout</a></p>
    </div>
    <div>
        <h3>Menu Management</h3>
        <button onclick="addItem()">Add Menu Item</button>
        <div id="menuList"></div>
    </div>
    <script>
        fetch('/api/menu').then(r=>r.json()).then(data=>{
            let html='<table><tr><th>ID</th><th>Name</th><th>Price</th><th>Action</th></tr>';
            data.forEach(item=>{
                html+=`<tr><td>${item.id}</td><td>${item.name}</td><td>$${item.price}</td><td><button onclick="deleteItem(${item.id})">Delete</button></td></tr>`;
            });
            html+='</table>';
            document.getElementById('menuList').innerHTML=html;
        });
        function deleteItem(id){
            fetch('/api/menu/'+id,{method:'DELETE'}).then(()=>location.reload());
        }
        function addItem(){
            let name=prompt('Item Name:');
            let price=prompt('Price:');
            if(name && price){
                fetch('/api/menu',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:name,price:parseFloat(price)})}).then(()=>location.reload());
            }
        }
    </script>
    </body>
    </html>
    '''

@app.route('/admin-logout')
def admin_logout():
    session.clear()
    return redirect('/admin-login')

@app.route('/api/menu', methods=['GET'])
def get_menu():
    return jsonify(load_data().get('menu_items', []))

@app.route('/api/menu', methods=['POST'])
def add_menu():
    data = load_data()
    new_item = request.json
    new_item['id'] = len(data.get('menu_items', [])) + 1
    if 'menu_items' not in data:
        data['menu_items'] = []
    data['menu_items'].append(new_item)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)
    return jsonify(new_item)

@app.route('/api/menu/<int:item_id>', methods=['DELETE'])
def delete_menu(item_id):
    data = load_data()
    data['menu_items'] = [i for i in data.get('menu_items', []) if i.get('id') != item_id]
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)
    return jsonify({'success': True})

# This is for Vercel
app = app