from flask import Flask, render_template, request, redirect, session
import psycopg2
import os

app = Flask(__name__)

app.secret_key = '123456'

# LIBERAR IFRAME
@app.after_request
def after_request(response):

    response.headers['X-Frame-Options'] = 'ALLOWALL'

    return response

# CONEXAO POSTGRESQL
DATABASE_URL = os.environ.get('DATABASE_URL')

conexao = psycopg2.connect(DATABASE_URL)

cursor = conexao.cursor()

# TABELA CLIENTES
cursor.execute('''
CREATE TABLE IF NOT EXISTS clientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200),
    telefone VARCHAR(200)
)
''')

# TABELA CARROS
cursor.execute('''
CREATE TABLE IF NOT EXISTS carros (
    id SERIAL PRIMARY KEY,
    modelo VARCHAR(200),
    marca VARCHAR(200),
    ano VARCHAR(200)
)
''')

# TABELA ALUGUEIS
cursor.execute('''
CREATE TABLE IF NOT EXISTS alugueis (
    id SERIAL PRIMARY KEY,
    cliente VARCHAR(200),
    carro VARCHAR(200),
    dias VARCHAR(200)
)
''')

# TABELA USUARIOS
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(200),
    senha VARCHAR(200)
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

        conexao = psycopg2.connect(DATABASE_URL)

        cursor = conexao.cursor()

        cursor.execute(
            'SELECT * FROM usuarios WHERE usuario = %s AND senha = %s',
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

        conexao = psycopg2.connect(DATABASE_URL)

        cursor = conexao.cursor()

        cursor.execute(
            'INSERT INTO usuarios (usuario, senha) VALUES (%s, %s)',
            (usuario, senha)
        )

        conexao.commit()

        conexao.close()

        return redirect('/login')

    return render_template('cadastro.html')

# LOGOUT
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')

# CLIENTES
@app.route('/', methods=['GET', 'POST'])
def home():

    if 'usuario' not in session:

        return redirect('/login')

    if request.method == 'POST':

        nome = request.form['nome']
        telefone = request.form['telefone']

        conexao = psycopg2.connect(DATABASE_URL)

        cursor = conexao.cursor()

        cursor.execute(
            'INSERT INTO clientes (nome, telefone) VALUES (%s, %s)',
            (nome, telefone)
        )

        conexao.commit()

        conexao.close()

    conexao = psycopg2.connect(DATABASE_URL)

    cursor = conexao.cursor()

    cursor.execute('SELECT * FROM clientes')

    clientes = cursor.fetchall()

    conexao.close()

    return render_template(
        'index.html',
        clientes=clientes
    )

if __name__ == '__main__':
    app.run(debug=True)