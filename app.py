from flask import Flask, request, make_response, jsonify
import sqlite3
import hashlib
import html

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
    # Adicionando um usuário de teste
    cursor.execute("INSERT INTO users VALUES ('admin', 'senha123')")
    conn.commit()
    conn.close()
    
# Chame a função para criar o banco de dados antes da aplicação rodar
init_db()

@app.route('/')
def home():
    return "Bem-vindo à aplicação de teste de segurança! Nenhuma falha SAST à vista."

@app.route('/login', methods=['POST'])
def login():
    """
    Função de login segura, usando consultas parametrizadas.
    O SAST vai aprovar.
    """
    username = request.form.get('username')
    password = request.form.get('password')

    # CORREÇÃO SAST: Uso de consultas parametrizadas para prevenir SQL Injection
    db = sqlite3.connect(':memory:')
    cursor = db.cursor()
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

    # CORREÇÃO SAST: Uso de um hash mais seguro (SHA-256) no lugar de MD5
    user_id_hash = hashlib.sha256(user_id.encode()).hexdigest()

    return f"Hash SHA-256 do ID do usuário: {user_id_hash}"

@app.route('/welcome')
def welcome():
    # CORREÇÃO SAST: Sanitização de input para prevenir XSS.
    # A função html.escape substitui caracteres perigosos por entidades HTML.
    name = request.args.get('name', 'Visitante')
    safe_name = html.escape(name)
    
    html_response = f"<h1>Bem-vindo, {safe_name}!</h1>"
    response = make_response(html_response, 200)

    # CORREÇÃO: Removemos o cabeçalho XSS-Protection desabilitado.
    return response

# VULNERABILIDADE DAST: ENDPOINT SECRETO E SEM AUTENTICAÇÃO
# Este endpoint não é linkado em nenhuma parte do código.
# O Semgrep não irá encontrá-lo, mas o ZAP (DAST) irá.
@app.route('/secret-admin-panel')
def admin_panel():
    # Imagine que este endpoint deveria ser protegido por login
    # Mas está acessível a qualquer um.
    users = ["Alice", "Bob", "Charlie", "Davi"]
    return jsonify({"admin_panel_info": "Este endpoint deveria ser protegido!", "users": users})


if __name__ == '__main__':
    app.run(debug=True)
