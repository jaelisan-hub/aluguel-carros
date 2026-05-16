from flask import Flask, render_template, request, redirect, session
import psycopg2

app = Flask(__name__)

app.secret_key = '123456'

# CONEXAO POSTGRESQL
DATABASE_URL = 'postgresql://locadora_v5d7_user:ZIa4dfq1MOZvXfNXCgW0UcmNZH0sFbMk@dpg-d815iijrjlhs73assr10-a.virginia-postgres.render.com/locadora_v5d7'


# =========================
# CONEXÃO BANCO
# =========================
def conectar():
    return psycopg2.connect(DATABASE_URL)


# LIBERAR IFRAME BLOGSPOT
@app.after_request
def after_request(response):
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    return response


# =========================
# CRIAR TABELAS
# =========================
conexao = conectar()
cursor = conexao.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(200),
    senha VARCHAR(200)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS clientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200),
    telefone VARCHAR(200)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS carros (
    id SERIAL PRIMARY KEY,
    modelo VARCHAR(200),
    marca VARCHAR(200),
    ano VARCHAR(200)
)
''')

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


# =========================
# LOGIN
# =========================
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        usuario = request.form['usuario']
        senha = request.form['senha']

        conexao = psycopg2.connect(DATABASE_URL)
        cursor = conexao.cursor()

        cursor.execute(
            "SELECT * FROM usuarios WHERE usuario=%s AND senha=%s",
            (usuario, senha)
        )

        usuario_encontrado = cursor.fetchone()

        if usuario_encontrado:
            session['usuario'] = usuario
            return redirect('/')

    return render_template('login.html')


# =========================
# CADASTRO
# =========================
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


# =========================
# CLIENTES
# =========================
@app.route('/', methods=['GET', 'POST'])
def home():

    if 'usuario' not in session:
        return redirect('/login')

    conexao = conectar()
    cursor = conexao.cursor()

    if request.method == 'POST':

        nome = request.form['nome']
        telefone = request.form['telefone']

        cursor.execute(
            'INSERT INTO clientes (nome, telefone) VALUES (%s, %s)',
            (nome, telefone)
        )

        conexao.commit()

    # 🔎 BUSCA CORRIGIDA (DENTRO DA FUNÇÃO)
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

    return render_template('index.html', clientes=clientes)


# =========================
# EXCLUIR CLIENTE
# =========================
@app.route('/excluir/<int:id>')
def excluir(id):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute('DELETE FROM clientes WHERE id = %s', (id,))

    conexao.commit()
    conexao.close()

    return redirect('/')


# =========================
# CARROS
# =========================
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

        cursor.execute(
            'INSERT INTO carros (modelo, marca, ano) VALUES (%s, %s, %s)',
            (modelo, marca, ano)
        )

        conexao.commit()

    # 🔎 BUSCA
    busca = request.args.get('busca')

    if busca:
        cursor.execute(
            "SELECT * FROM carros WHERE modelo ILIKE %s",
            ('%' + busca + '%',)
        )
    else:
        cursor.execute("SELECT * FROM carros")

    carros = cursor.fetchall()

    conexao.close()

    return render_template('carros.html', carros=carros)

# =========================
# EXCLUIR CARRO
# =========================
@app.route('/excluir_carro/<int:id>')
def excluir_carro(id):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute('DELETE FROM carros WHERE id = %s', (id,))

    conexao.commit()
    conexao.close()

    return redirect('/carros')


# =========================
# ALUGUEIS
# =========================
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
            INSERT INTO alugueis (cliente, carro, dias, diaria, total)
            VALUES (%s, %s, %s, %s, %s)
            ''',
            (cliente, carro, dias, diaria, total)
        )

        conexao.commit()

    # 🔎 BUSCA CORRIGIDA
    busca = request.args.get('busca')

    if busca:
        cursor.execute(
            "SELECT * FROM alugueis WHERE cliente ILIKE %s",
            ('%' + busca + '%',)
        )
    else:
        cursor.execute("SELECT * FROM alugueis")

    alugueis = cursor.fetchall()

    conexao.close()

    return render_template('alugueis.html', alugueis=alugueis)


# =========================
# EXCLUIR ALUGUEL
# =========================
@app.route('/excluir_aluguel/<int:id>')
def excluir_aluguel(id):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute('DELETE FROM alugueis WHERE id = %s', (id,))

    conexao.commit()
    conexao.close()

    return redirect('/alugueis')


# =========================
# LOGOUT
# =========================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# =========================
# FINANCEIRO
# =========================
@app.route('/financeiro')
def financeiro():

    if 'usuario' not in session:
        return redirect('/login')

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute('SELECT * FROM alugueis')
    alugueis = cursor.fetchall()

    cursor.execute('SELECT SUM(total::numeric) FROM alugueis')
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


# =========================
# 🟢 PAGAMENTO (NOVO - CORRIGIDO)
# =========================
@app.route("/pagamento")
def pagamento():

    valor = "A combinar"

    link_pagamento = "https://link-de-pagamento.com"

    return render_template(
        "pagamento.html",
        valor=valor,
        link_pagamento=link_pagamento
    )


# =========================
# START APP
# =========================
if __name__ == '__main__':
    app.run(debug=True)
