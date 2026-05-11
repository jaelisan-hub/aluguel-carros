from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)

app.secret_key = '123456'

# LIBERAR IFRAME
@app.after_request
def after_request(response):

    response.headers['X-Frame-Options'] = 'ALLOWALL'

    return response

# CRIAR BANCO
conexao = sqlite3.connect('banco.db')

cursor = conexao.cursor()

# TABELA USUARIOS
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT,
    senha TEXT
)
''')

# TABELA CLIENTES
cursor.execute('''
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    telefone TEXT
)
''')

conexao.commit()

conexao.close()

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        usuario = request.form['usuario']
        senha = request.form['senha']

        conexao = sqlite3.connect('banco.db')

        cursor = conexao.cursor()

        cursor.execute(
            'SELECT * FROM usuarios WHERE usuario = ? AND senha = ?',
            (usuario, senha)
        )

        usuario_encontrado = cursor.fetchone()

        conexao.close()

        if usuario_encontrado:

            session['usuario'] = usuario

            return redirect('/')

    return render_template('login.html')

# CADASTRO
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():

    if request.method == 'POST':

        usuario = request.form['usuario']
        senha = request.form['senha']

        conexao = sqlite3.connect('banco.db')

        cursor = conexao.cursor()

        cursor.execute(
            'INSERT INTO usuarios (usuario, senha) VALUES (?, ?)',
            (usuario, senha)
        )

        conexao.commit()

        conexao.close()

        return redirect('/login')

    return render_template('cadastro.html')

 # HOME CLIENTES
@app.route('/', methods=['GET', 'POST'])
def home():

    if 'usuario' not in session:

        return redirect('/login')

    if request.method == 'POST':

        nome = request.form['nome']
        telefone = request.form['telefone']

        conexao = sqlite3.connect('banco.db')

        cursor = conexao.cursor()

        cursor.execute(
            'INSERT INTO clientes (nome, telefone) VALUES (?, ?)',
            (nome, telefone)
        )

        conexao.commit()

        conexao.close()

    conexao = sqlite3.connect('banco.db')

    cursor = conexao.cursor()

    cursor.execute('SELECT * FROM clientes')

    clientes = cursor.fetchall()

    conexao.close()

    return render_template(
        'index.html',
        clientes=clientes
    )

# LOGOUT
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)