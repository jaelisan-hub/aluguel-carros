from flask import Flask, render_template, request, redirect, session
import psycopg2
import os

app = Flask(__name__)

app.secret_key = 'locadora123'


# LIBERAR IFRAME BLOGSPOT
@app.after_request
def after_request(response):

    response.headers['X-Frame-Options'] = 'ALLOWALL'

    return response


# CONEXAO POSTGRESQL
DATABASE_URL = os.environ.get('DATABASE_URL')


# CONECTAR
def conectar():

    return psycopg2.connect(DATABASE_URL)


# CRIAR TABELAS
conexao = conectar()

cursor = conexao.cursor()


# USUARIOS
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (

    id SERIAL PRIMARY KEY,
    usuario VARCHAR(200),
    senha VARCHAR(200)

)
''')


# CLIENTES
cursor.execute('''
CREATE TABLE IF NOT EXISTS clientes (

    id SERIAL PRIMARY KEY,
    nome VARCHAR(200),
    telefone VARCHAR(200)

)
''')


# CARROS
cursor.execute('''
CREATE TABLE IF NOT EXISTS carros (

    id SERIAL PRIMARY KEY,
    modelo VARCHAR(200),
    marca VARCHAR(200),
    ano VARCHAR(200),
    valor VARCHAR(200)

)
''')


# ALUGUEIS
cursor.execute('''
CREATE TABLE IF NOT EXISTS alugueis (

    id SERIAL PRIMARY KEY,
    cliente VARCHAR(200),
    carro VARCHAR(200),
    dias VARCHAR(200),
    diaria VARCHAR(200),
    total VARCHAR(200)

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

        conexao = conectar()

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

        conexao = conectar()

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

    conexao = conectar()

    cursor = conexao.cursor()

    # CADASTRAR CLIENTE
    if request.method == 'POST':

        nome = request.form['nome']
        telefone = request.form['telefone']

        cursor.execute(
            'INSERT INTO clientes (nome, telefone) VALUES (%s, %s)',
            (nome, telefone)
        )

        conexao.commit()

    # BUSCA
    busca = request.args.get('busca')

    if busca:

        cursor.execute(
            "SELECT * FROM clientes WHERE nome ILIKE %s",
            ('%' + busca + '%',)
        )

    else:

        cursor.execute('SELECT * FROM clientes')

    clientes = cursor.fetchall()

    conexao.close()

    return render_template(
        'index.html',
        clientes=clientes
    )


# EXCLUIR CLIENTE
@app.route('/excluir/<int:id>')
def excluir(id):

    if 'usuario' not in session:
        return redirect('/login')

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute(
        'DELETE FROM clientes WHERE id = %s',
        (id,)
    )

    conexao.commit()

    conexao.close()

    return redirect('/')


# CARROS
@app.route('/carros', methods=['GET', 'POST'])
def carros():

    if 'usuario' not in session:
        return redirect('/login')

    conexao = conectar()

    cursor = conexao.cursor()

    if request.method == 'POST':

        modelo = request.form['modelo']
        marca = request.form['marca']
        ano = request.form['ano']
        valor = request.form['valor']

        cursor.execute(
            '''
            INSERT INTO carros
            (modelo, marca, ano, valor)

            VALUES (%s, %s, %s, %s)
            ''',
            (modelo, marca, ano, valor)
        )

        conexao.commit()

    cursor.execute('SELECT * FROM carros')

    carros = cursor.fetchall()

    conexao.close()

    return render_template(
        'carros.html',
        carros=carros
    )


# EXCLUIR CARRO
@app.route('/excluir_carro/<int:id>')
def excluir_carro(id):

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute(
        'DELETE FROM carros WHERE id = %s',
        (id,)
    )

    conexao.commit()

    conexao.close()

    return redirect('/carros')


# ALUGUEIS
@app.route('/alugueis', methods=['GET', 'POST'])
def alugueis():

    if 'usuario' not in session:
        return redirect('/login')

    conexao = conectar()

    cursor = conexao.cursor()

    if request.method == 'POST':

        cliente = request.form['cliente']
        carro = request.form['carro']
        dias = int(request.form['dias'])
        diaria = float(request.form['diaria'])

        total = dias * diaria

        cursor.execute(
            '''
            INSERT INTO alugueis
            (cliente, carro, dias, diaria, total)

            VALUES (%s, %s, %s, %s, %s)
            ''',
            (cliente, carro, dias, diaria, total)
        )

        conexao.commit()

    cursor.execute('SELECT * FROM alugueis')

    alugueis = cursor.fetchall()

    conexao.close()

    return render_template(
        'alugueis.html',
        alugueis=alugueis
    )


# EXCLUIR ALUGUEL
@app.route('/excluir_aluguel/<int:id>')
def excluir_aluguel(id):

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute(
        'DELETE FROM alugueis WHERE id = %s',
        (id,)
    )

    conexao.commit()

    conexao.close()

    return redirect('/alugueis')


# FINANCEIRO
@app.route('/financeiro')
def financeiro():

    if 'usuario' not in session:
        return redirect('/login')

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute('SELECT * FROM alugueis')

    alugueis = cursor.fetchall()

    cursor.execute(
        'SELECT SUM(total::numeric) FROM alugueis'
    )

    resultado = cursor.fetchone()

    total = resultado[0]

    if total is None:
        total = 0

    conexao.close()

    return render_template(
        'financeiro.html',
        alugueis=alugueis,
        total=total
    )


if __name__ == '__main__':

    app.run(debug=True)