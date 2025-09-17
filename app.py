import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Vulnerabilidade de Exposição de Dados Sensíveis
# Dados de API Keys ou senhas embutidos no código.
API_KEY = "sua_chave_secreta_aqui"

# Função para inicializar o banco de dados
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Vulnerabilidade: SQL Injection
@app.route('/user_search')
def user_search():
    username = request.args.get('username')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"
    print(f"Executing query: {query}")
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

# Vulnerabilidade: Cross-Site Scripting (XSS)
@app.route('/hello')
def hello_xss():
    name = request.args.get('name', 'World')
    
    html = f"<h1>Hello, {name}!</h1>"
    return render_template_string(html)

# Vulnerabilidade: Uso de senha em plain text)
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password') 
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "User registered successfully."})


if __name__ == '__main__':
    init_db()
    # Vulnerabilidade: Servidor de desenvolvimento em produção.
    app.run(host='0.0.0.0', port=8080)
