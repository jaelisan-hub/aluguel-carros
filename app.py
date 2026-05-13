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

    # BUSCA CLIENTE
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