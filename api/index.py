from http.server import BaseHTTPRequestHandler
import json
import hashlib
from urllib.parse import urlparse, parse_qs

DATA_FILE = '/tmp/data.json'

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'admin_users': [{'username': 'admin', 'password': hashlib.sha256('admin123'.encode()).hexdigest()}], 'menu_items': []}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/admin-login':
            self.send_html_login()
        elif path == '/admin-dashboard.html':
            self.check_session_and_dashboard()
        elif path == '/admin-logout':
            self.send_response(302)
            self.send_header('Location', '/admin-login')
            self.end_headers()
        elif path == '/api/menu':
            self.send_json(load_data().get('menu_items', []))
        else:
            self.serve_static_file(path)
    
    def do_POST(self):
        if self.path == '/admin-login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode()
            params = parse_qs(post_data)
            username = params.get('username', [''])[0]
            password = params.get('password', [''])[0]
            
            hashed = hashlib.sha256(password.encode()).hexdigest()
            data = load_data()
            for admin in data['admin_users']:
                if admin['username'] == username and admin['password'] == hashed:
                    self.send_response(302)
                    self.send_header('Set-Cookie', 'admin_logged_in=true; Path=/')
                    self.send_header('Location', '/admin-dashboard.html')
                    self.end_headers()
                    return
            
            self.send_response(302)
            self.send_header('Location', '/admin-login?error=1')
            self.end_headers()
        
        elif self.path == '/api/menu':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode()
            item = json.loads(post_data)
            data = load_data()
            item['id'] = len(data.get('menu_items', [])) + 1
            if 'menu_items' not in data:
                data['menu_items'] = []
            data['menu_items'].append(item)
            save_data(data)
            self.send_json(item)
    
    def do_DELETE(self):
        if self.path.startswith('/api/menu/'):
            item_id = int(self.path.split('/')[-1])
            data = load_data()
            data['menu_items'] = [i for i in data.get('menu_items', []) if i.get('id') != item_id]
            save_data(data)
            self.send_json({'success': True})
    
    def check_session_and_dashboard(self):
        cookies = self.headers.get('Cookie', '')
        if 'admin_logged_in=true' not in cookies:
            self.send_response(302)
            self.send_header('Location', '/admin-login')
            self.end_headers()
            return
        self.send_html_dashboard()
    
    def send_html_login(self):
        error = 'error=1' in self.path
        html = f'''
        <!DOCTYPE html>
        <html>
        <head><title>Admin Login</title>
        <style>
            body{{background:#0a0a0a;font-family:Arial;display:flex;justify-content:center;align-items:center;height:100vh;}}
            .login{{background:#1a1a1a;padding:40px;border-radius:20px;border:1px solid #D4AF37;text-align:center;}}
            input{{display:block;width:100%;padding:12px;margin:10px 0;background:#0a0a0a;border:1px solid #D4AF37;border-radius:25px;color:white;}}
            button{{background:#D4AF37;color:#000;padding:12px 30px;border:none;border-radius:25px;cursor:pointer;font-weight:bold;}}
            h2{{color:#D4AF37;}}
            .error{{color:#ff4444;margin-bottom:10px;}}
        </style>
        </head>
        <body>
        <div class="login">
            <h2>KRUNCH ELITE Admin</h2>
            {'<p class="error">Invalid credentials</p>' if error else ''}
            <form method="POST">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
        </div>
        </body>
        </html>
        '''
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_html_dashboard(self):
        html = '''
        <!DOCTYPE html>
        <html>
        <head><title>Admin Dashboard</title>
        <style>
            body{background:#0a0a0a;font-family:Arial;color:white;padding:20px;}
            .header{background:#D4AF37;color:#000;padding:15px;border-radius:10px;margin-bottom:20px;}
            button{background:#D4AF37;color:#000;padding:10px 20px;border:none;border-radius:20px;cursor:pointer;margin:5px;}
            table{width:100%;border-collapse:collapse;margin-top:20px;}
            th,td{padding:12px;text-align:left;border-bottom:1px solid #333;}
            th{color:#D4AF37;}
        </style>
        </head>
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
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def serve_static_file(self, path):
        if path == '/' or path == '':
            path = '/index.html'
        try:
            with open('.' + path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            if path.endswith('.html'):
                self.send_header('Content-type', 'text/html')
            elif path.endswith('.css'):
                self.send_header('Content-type', 'text/css')
            elif path.endswith('.js'):
                self.send_header('Content-type', 'application/javascript')
            self.end_headers()
            self.wfile.write(content)
        except:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')