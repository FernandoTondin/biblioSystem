import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from biblio.db import get_db

bp = Blueprint('info', __name__, url_prefix='/info')

@bp.route('/livro', methods=('GET', 'POST'))
def livro():
    if request.method == 'GET':
        cod = int(request.args.get('cod'))
        print(type(cod))
        print(cod)
        db = get_db()
        posts =db.execute(
            'Select * FROM livros'
            ' WHERE cod_livro = ?',
            (cod,),
            ).fetchall()
        return render_template('info/livro.html', posts=posts)
    if request.method == 'POST':
        cod = request.form['cod']
        titulo = request.form['livro']
        autor = request.form['autor']
        volume = request.form['volume']
        edicao = request.form['edicao']
        publicacao = request.form['anoPublicacao']
        db = get_db()
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
                db.execute(
                    'UPDATE livros'
                    ' SET tit_livro = ?, nom_autor = ?, num_volume = ?, num_edicao = ?, anoPublic = ?'
                    ' WHERE cod_livro = ?;',
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
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        end = request.form['descEnderecoCliente']
        db = get_db()
        error = None

        if not nome:
            error = 'nome is required.'
        elif not cpf:
            error = 'cpf is required.'
        elif not end:
            error = 'endereco is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO clientes (nome_cliente, CPF, dsc_endereco_cliente) VALUES (?, ?, ?)",
                    (nome, cpf, end),
                )
                db.commit()
            except db.IntegrityError:
                error = f"livro {nome} is already registered."
            else:
                return redirect(url_for("home"))

        flash(error)

    return render_template('info/cliente.html')