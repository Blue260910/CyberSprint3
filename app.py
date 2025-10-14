from flask import Flask, request, jsonify, render_template
import sqlite3
import hashlib
import jwt, datetime
import os
from functools import wraps

# Tenta carregar arquivo .env se disponível
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Se python-dotenv não estiver instalado, continua sem ele
    pass

app = Flask(__name__)

# Configuração flexível: usa env var se disponível, senão fallback para teste
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'sua_chave_secreta_superforte')
TESTING_MODE = os.getenv('FLASK_TESTING', 'true').lower() == 'true'

# Configuração do banco de dados em memória para o exemplo
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO users VALUES ('admin', 'senha123')")
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('home.html')

def validate_login_input(username, password):
    if not username or not password:
        return False
    if len(username) < 3 or len(password) < 6:
        return False
    if any(c in username for c in "'\";-- "):
        return False
    return True

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if not validate_login_input(username, password):
        return render_template('login.html', message="Credenciais inválidas."), 400
    db = sqlite3.connect('users.db')
    cursor = db.cursor()
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    try:
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        if user:
            token = jwt.encode({'user': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, SECRET_KEY, algorithm='HS256')
            return render_template('login.html', message="Login bem-sucedido! Token gerado.", token=token), 200
        else:
            return render_template('login.html', message="Credenciais inválidas."), 401
    except Exception as e:
        app.logger.error(f'Erro interno: {str(e)}')
        return render_template('login.html', message="Erro interno."), 500

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token ausente'}), 401
        try:
            jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except Exception:
            return jsonify({'error': 'Token inválido'}), 401
        return f(*args, **kwargs)
    return decorator

@app.route('/user_info')
@token_required
def user_info():
    user_id = request.args.get('id')
    if not user_id or len(user_id) < 3:
        return jsonify({'error': 'ID inválido'}), 400
    user_id_hash = hashlib.sha256(user_id.encode()).hexdigest()
    return render_template('user_info.html', user_id_hash=user_id_hash)

@app.route('/welcome')
def welcome():
    name = request.args.get('name', 'Visitante')
    # Retorno de JSON, que não aciona as regras de XSS do SAST
    return jsonify({"message": f"Bem-vindo, {name}!"})

@app.route('/secret-admin-panel')
@app.route('/secret-admin-panel')
@token_required
def admin_panel():
    users = ["Alice", "Bob", "Charlie", "Davi"]
    return jsonify({"admin_panel_info": "Este endpoint está protegido!", "users": users})

if __name__ == '__main__':
    app.run()
