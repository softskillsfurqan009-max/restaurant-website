from flask import Flask, request, jsonify, session, redirect, url_for, send_from_directory
import json
import os
import hashlib

app = Flask(__name__, static_folder='..')
app.secret_key = 'krunchelite-secret-key-2024'

DATA_FILE = '/tmp/data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        'admin_password': hashlib.sha256('admin123'.encode()).hexdigest(),
        'menu_items': []
    }

@app.route('/')
def index():
    return send_from_directory('..', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if path.endswith('.html'):
        return send_from_directory('..', path)
    return send_from_directory('..', path)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        hashed = hashlib.sha256(password.encode()).hexdigest()
        data = load_data()
        if hashed == data['admin_password']:
            session['admin'] = True
            return redirect('/admin-dashboard')
        return '<h3>Wrong Password! <a href="/admin-login">Try Again</a></h3>'
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Login - KRUNCH ELITE</title>
        <style>
            *{margin:0;padding:0;box-sizing:border-box;}
            body{
                background:#050505;
                font-family:Arial;
                display:flex;
                justify-content:center;
                align-items:center;
                height:100vh;
            }
            .login-box{
                background:#1A1A1A;
                padding:40px;
                border-radius:20px;
                border:2px solid #D4AF37;
                text-align:center;
                width:350px;
            }
            .logo{
                width:70px;
                height:70px;
                background:#D4AF37;
                border-radius:50%;
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:30px;
                font-weight:bold;
                color:#000;
                margin:0 auto 20px;
            }
            h2{color:#D4AF37;margin-bottom:20px;}
            input{
                width:100%;
                padding:12px;
                margin:10px 0;
                background:#0A0A0A;
                border:1px solid #D4AF37;
                border-radius:25px;
                color:white;
                font-size:16px;
            }
            button{
                width:100%;
                background:#D4AF37;
                color:#000;
                padding:12px;
                border:none;
                border-radius:25px;
                font-weight:bold;
                font-size:16px;
                cursor:pointer;
                margin-top:10px;
            }
            button:hover{background:#C5A028;}
        </style>
    </head>
    <body>
        <div class="login-box">
            <div class="logo">K</div>
            <h2>KRUNCH ELITE</h2>
            <form method="POST">
                <input type="password" name="password" placeholder="Admin Password" required>
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
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Dashboard - KRUNCH ELITE</title>
        <style>
            *{margin:0;padding:0;box-sizing:border-box;}
            body{
                background:#050505;
                font-family:Arial;
                color:white;
                padding:20px;
            }
            .header{
                background:#D4AF37;
                color:#000;
                padding:15px 20px;
                border-radius:10px;
                display:flex;
                justify-content:space-between;
                align-items:center;
                margin-bottom:30px;
            }
            .header a{color:#000;text-decoration:none;font-weight:bold;}
            .stats{
                display:grid;
                grid-template-columns:repeat(4,1fr);
                gap:20px;
                margin-bottom:30px;
            }
            .stat-card{
                background:#1A1A1A;
                padding:20px;
                border-radius:15px;
                border:1px solid #D4AF37;
                text-align:center;
            }
            .stat-card .number{font-size:32px;font-weight:bold;color:#D4AF37;}
            .section{
                background:#1A1A1A;
                padding:20px;
                border-radius:15px;
                border:1px solid #D4AF37;
            }
            .section h2{color:#D4AF37;margin-bottom:15px;}
            button{
                background:#D4AF37;
                color:#000;
                padding:8px 16px;
                border:none;
                border-radius:20px;
                cursor:pointer;
                margin:5px;
            }
            table{width:100%;border-collapse:collapse;}
            th,td{padding:12px;text-align:left;border-bottom:1px solid #333;}
            th{color:#D4AF37;}
            .btn-add{
                background:#D4AF37;
                padding:10px 20px;
                border-radius:25px;
                margin-bottom:15px;
                display:inline-block;
                cursor:pointer;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h2>KRUNCH ELITE - Admin Dashboard</h2>
            <a href="/admin-logout">Logout</a>
        </div>
        
        <div class="stats">
            <div class="stat-card"><div class="number" id="menuCount">0</div><div>Menu Items</div></div>
            <div class="stat-card"><div class="number" id="resCount">0</div><div>Reservations</div></div>
            <div class="stat-card"><div class="number" id="orderCount">0</div><div>Orders</div></div>
            <div class="stat-card"><div class="number" id="deliveryCount">0</div><div>Deliveries</div></div>
        </div>
        
        <div class="section">
            <h2>Menu Management</h2>
            <button class="btn-add" onclick="addMenuItem()">+ Add Menu Item</button>
            <div id="menuTable"></div>
        </div>
        
        <script>
            function loadStats(){
                fetch('/api/stats').then(r=>r.json()).then(d=>{
                    document.getElementById('menuCount').innerText=d.total_menu_items;
                });
            }
            
            function loadMenu(){
                fetch('/api/menu').then(r=>r.json()).then(items=>{
                    let html='<table><tr><th>ID</th><th>Name</th><th>Price</th><th>Action</th></tr>';
                    items.forEach(item=>{
                        html+=`<tr><td>${item.id}</td><td>${item.name}</td><td>$${item.price}</td><td><button onclick="deleteItem(${item.id})">Delete</button></td></tr>`;
                    });
                    html+='</table>';
                    document.getElementById('menuTable').innerHTML=html;
                    loadStats();
                });
            }
            
            function addMenuItem(){
                let name=prompt('Enter item name:');
                let price=prompt('Enter price:');
                if(name && price){
                    fetch('/api/menu',{
                        method:'POST',
                        headers:{'Content-Type':'application/json'},
                        body:JSON.stringify({name:name,price:parseFloat(price)})
                    }).then(()=>loadMenu());
                }
            }
            
            function deleteItem(id){
                if(confirm('Delete this item?')){
                    fetch('/api/menu/'+id,{method:'DELETE'}).then(()=>loadMenu());
                }
            }
            
            loadMenu();
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
    data = load_data()
    return jsonify(data.get('menu_items', []))

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

@app.route('/api/stats', methods=['GET'])
def get_stats():
    data = load_data()
    return jsonify({
        'total_menu_items': len(data.get('menu_items', []))
    })

# This is required for Vercel
app = app