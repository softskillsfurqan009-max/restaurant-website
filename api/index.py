from flask import Flask, request, jsonify, session, redirect
import json
import os
import hashlib

app = Flask(__name__, static_folder='..')
app.secret_key = 'secret-key-123'
app.config['SESSION_TYPE'] = 'filesystem'

DATA_FILE = '/tmp/data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        'admin': {'username': 'admin', 'password': hashlib.sha256('admin123'.encode()).hexdigest()},
        'menu_items': []
    }

@app.route('/')
def home():
    from flask import send_from_directory
    return send_from_directory('..', 'index.html')

@app.route('/<path:filename>')
def serve_file(filename):
    from flask import send_from_directory
    return send_from_directory('..', filename)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed = hashlib.sha256(password.encode()).hexdigest()
        
        data = load_data()
        if username == data['admin']['username'] and hashed == data['admin']['password']:
            session['admin'] = True
            return redirect('/admin-dashboard')
        
        return '<h3>Invalid!</h3><a href="/admin-login">Try again</a>'
    
    return '''
    <html>
    <head><title>Admin Login</title><style>
        body{background:#0a0a0a;display:flex;justify-content:center;align-items:center;height:100vh;font-family:Arial}
        .box{background:#1a1a1a;padding:40px;border-radius:20px;border:1px solid #D4AF37;text-align:center}
        input{padding:12px;margin:10px;background:#0a0a0a;border:1px solid #D4AF37;border-radius:25px;color:white}
        button{background:#D4AF37;padding:12px 30px;border:none;border-radius:25px;font-weight:bold;cursor:pointer}
        h2{color:#D4AF37}
    </style></head>
    <body>
    <div class="box">
        <h2>KRUNCH ELITE Admin</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Username"><br>
            <input type="password" name="password" placeholder="Password"><br><br>
            <button type="submit">Login</button>
        </form>
    </div>
    </body>
    </html>
    '''

@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect('/admin-login')
    
    return '''
    <html>
    <head><title>Admin Dashboard</title><style>
        body{background:#0a0a0a;font-family:Arial;color:white;padding:20px}
        .header{background:#D4AF37;color:#000;padding:15px;border-radius:10px}
        button{background:#D4AF37;padding:10px 20px;border:none;border-radius:20px;cursor:pointer;margin:5px}
        table{width:100%;border-collapse:collapse;margin-top:20px}
        th,td{padding:10px;text-align:left;border-bottom:1px solid #333}
        th{color:#D4AF37}
    </style></head>
    <body>
    <div class="header"><h2>Admin Dashboard</h2><p>Welcome! <a href="/admin-logout">Logout</a></p></div>
    <div><h3>Menu Items</h3><button onclick="addItem()">Add Item</button><div id="menuList"></div></div>
    <script>
        fetch('/api/menu').then(r=>r.json()).then(data=>{
            let html='<table><tr><th>ID</th><th>Name</th><th>Price</th><th>Action</th></tr>';
            data.forEach(item=>{html+=`<tr><td>${item.id}</td><td>${item.name}</td><td>$${item.price}</td><td><button onclick="deleteItem(${item.id})">Delete</button></td></tr>`});
            html+='</table>';
            document.getElementById('menuList').innerHTML=html;
        });
        function deleteItem(id){fetch('/api/menu/'+id,{method:'DELETE'}).then(()=>location.reload());}
        function addItem(){
            let name=prompt('Item name:');
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
    return jsonify(load_data()['menu_items'])

@app.route('/api/menu', methods=['POST'])
def add_menu():
    data = load_data()
    new = request.json
    new['id'] = len(data['menu_items']) + 1
    data['menu_items'].append(new)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)
    return jsonify(new)

@app.route('/api/menu/<int:item_id>', methods=['DELETE'])
def delete_menu(item_id):
    data = load_data()
    data['menu_items'] = [i for i in data['menu_items'] if i['id'] != item_id]
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)
    return jsonify({'ok': True})