from flask import Flask, render_template, request, redirect, session
import psycopg2
import os

app = Flask(__name__)

app.secret_key = '123456'


# CONEXAO
DATABASE_URL = os.getenv('DATABASE_URL')


def conectar():
    return psycopg2.connect(DATABASE_URL)


# CRIAR TABELA CLIENTES
conexao = conectar()

cursor = conexao.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS clientes (

    id SERIAL PRIMARY KEY,
    nome VARCHAR(200),
    telefone VARCHAR(200)

)
''')

conexao.commit()

conexao.close()


# LOGIN
@app.route('/login')
def login():

    session['usuario'] = 'admin'

    return redirect('/')


# CLIENTES
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

    busca = request.args.get('busca')

    if busca:

        cursor.execute(
            "SELECT * FROM clientes WHERE nome ILIKE %s",
            ('%' + busca + '%',)
        )

    else:

        cursor.execute(
            'SELECT * FROM clientes'
        )

    clientes = cursor.fetchall()

    conexao.close()

    return render_template(
        'index.html',
        clientes=clientes
    )


# EXCLUIR
@app.route('/excluir/<int:id>')
def excluir(id):

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute(
        'DELETE FROM clientes WHERE id = %s',
        (id,)
    )

    conexao.commit()

    conexao.close()

    return redirect('/')


if __name__ == '__main__':

    app.run(debug=True)