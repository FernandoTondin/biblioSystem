import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from biblio.db import get_db,get_cursor

bp = Blueprint('info', __name__, url_prefix='/info')

@bp.route('/livro', methods=('GET', 'POST'))
def livro():
    db = get_db()
    cur = get_cursor()
    
    if request.method == 'POST':
        if "info" in request.form.keys():

            cod = request.form['cod']
            cur.execute(
                'Select * FROM livros'
                ' WHERE cod_livro = %s',
                (cod,),
                )
            posts = cur.fetchall()
            return render_template('info/livro.html', posts=posts)
        
        if "enviar" in request.form.keys():
            cod = request.form['cod']
            titulo = request.form['livro']
            autor = request.form['autor']
            volume = request.form['volume']
            edicao = request.form['edicao']
            publicacao = request.form['anoPublicacao']
            error = None

            if not titulo:
                error = 'titulo is required.'
            elif not autor:
                error = 'autor is required.'
            elif not volume:
                error = 'volume is required.'
            elif not edicao:
                error = 'edicao is required.'
            elif not publicacao:
                error = 'publicacao is required.'

            if error is None:
                try:
                    cur.execute(
                        'UPDATE livros'
                        ' SET tit_livro = %s, nom_autor = %s, num_volume = %s, num_edicao = %s, anoPublic = %s'
                        ' WHERE cod_livro = %s;',
                        (titulo, autor, volume, edicao,publicacao,cod),
                    )
                    db.commit()
                except db.IntegrityError:
                    error = f"livro {titulo} is already registered."
                else:
                    return redirect(url_for("view.livro"))

            flash(error)
        
    return render_template('info/livro.html')

@bp.route('/cliente', methods=('GET', 'POST'))
def cliente():
    db = get_db()
    cur = get_cursor()
    print(request.form.keys())
    if request.method == 'POST':
        if "info" in request.form.keys():
            cod = request.form['cod']
            cur.execute(
                'Select * FROM clientes'
                ' WHERE cod_cliente = %s',
                (cod,),
                )
            posts = cur.fetchall()
            return render_template('info/cliente.html', posts=posts)

        if "enviar" in request.form.keys():
            cod = request.form['cod']
            nome = request.form['nome']
            cpf = request.form['cpf']
            end = request.form['descEnderecoCliente']
            error = None

            if not nome:
                error = 'nome is required.'
            elif not cpf:
                error = 'cpf is required.'
            elif not end:
                error = 'endereco is required.'

            if error is None:
                try:
                    cur.execute(
                        'UPDATE clientes '
                        'SET nome_cliente = %s, CPF= %s, dsc_endereco_cliente= %s '
                        'WHERE cod_cliente = %s;',(nome, cpf, end,cod)
                    )
                    db.commit()
                except Exception as e: 
                    print("excecao")
                    print(e)
                    error = f"{e}"
                else:
                    return redirect(url_for("view.cliente"))

            flash(error)

    return render_template('info/cliente.html')