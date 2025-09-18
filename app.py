from flask import Flask, request, jsonify
import sqlite3
import hashlib

app = Flask(__name__)

# Configuração do banco de dados em memória para o exemplo
def init_db():
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    cursor.execute("INSERT INTO users VALUES ('admin', 'senha123')")
    conn.commit()
    conn.close()
    
init_db()

@app.route('/')
def home():
    return "Bem-vindo à aplicação de teste de segurança! Este código deve passar na análise estática."

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    db = sqlite3.connect(':memory:')
    cursor = db.cursor()
    # Uso de consultas parametrizadas para evitar Injeção de SQL
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    try:
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        if user:
            return "Login bem-sucedido!", 200
        else:
            return "Credenciais inválidas.", 401
    except Exception as e:
        return str(e), 500

@app.route('/user_info')
def user_info():
    user_id = request.args.get('id')
    # Uso de hash seguro (sha256) em vez de MD5
    user_id_hash = hashlib.sha256(user_id.encode()).hexdigest()
    return f"Hash SHA-256 do ID do usuário: {user_id_hash}"

@app.route('/welcome')
def welcome():
    name = request.args.get('name', 'Visitante')
    # Retorno de JSON, que não aciona as regras de XSS do SAST
    return jsonify({"message": f"Bem-vindo, {name}!"})

@app.route('/secret-admin-panel')
def admin_panel():
    """
    VULNERABILIDADE DAST: Endpoint sem autenticação.
    O SAST não detecta, pois o código não tem falhas de sintaxe óbvias.
    O DAST, ao navegar pela aplicação, irá encontrar este endpoint exposto
    e o detectará como um problema de "Broken Access Control".
    """
    users = ["Alice", "Bob", "Charlie", "Davi"]
    return jsonify({"admin_panel_info": "Este endpoint deveria ser protegido!", "users": users})

if __name__ == '__main__':
    app.run()
