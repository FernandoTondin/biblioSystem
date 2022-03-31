import functools
import datetime as dt

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from biblio.db import get_db

bp = Blueprint('cadastro', __name__, url_prefix='/cadastro')

@bp.route('/livro', methods=('GET', 'POST'))
def livro():
    if request.method == 'POST':
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
                    "INSERT INTO livros (tit_livro, nom_autor,num_volume,num_edicao,anoPublic) VALUES (?, ?, ?, ?, ?)",
                    (titulo, autor, volume, edicao,publicacao),
                )
                db.commit()
                db.execute('INSERT INTO exemplares (cod_livro,num_exemplar,bool_disponivel)'
                ' SELECT cod_livro,0 as num_exemplar,1 as bool_disponivel FROM livros'
                ' WHERE tit_livro=? AND num_volume=? AND num_edicao=?',
                (titulo, volume, edicao))
                db.commit()
            except db.IntegrityError:
                error = f"livro {titulo} is already registered."
            else:
                return redirect(url_for("home"))

        flash(error)

    return render_template('cadastro/livro.html')

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
                error = f"cliente {nome} is already registered."
            else:
                return redirect(url_for("home"))

        flash(error)

    return render_template('cadastro/cliente.html')

@bp.route('/emprestimo', methods=('GET', 'POST'))
def emprestimo():
    if request.method == 'POST':
        cdExemplar = request.form['cdExemplar']
        cdCliente = request.form['cdCliente']
        db = get_db()
        data = dt.date.today()
        dataemp = data.strftime("%Y-%m-%d")
        prazo = data + dt.timedelta(5)
        prazoemp = prazo.strftime("%Y-%m-%d")
        error = None

        if not cdExemplar:
            error = 'cdExemplar is required.'
        elif not cdCliente:
            error = 'cdExemplar is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO emprestimos (cod_exemplar, cod_cliente, data_emp, prazo_devol) VALUES (?, ?, ?, ?)",
                    (cdExemplar, cdCliente, dataemp, prazoemp),
                )
                db.commit()
            except db.IntegrityError:
                error = f"livro {cdExemplar} is already registered."
        else:
            return redirect(url_for("home"))

        flash(error)

    return render_template('cadastro/emprestimo.html')

@bp.route('/exemplar', methods=('GET', 'POST'))
def exemplar():
    if request.method == 'POST':
        cod_livro = request.form['cod_livro']
        num_exemplar = request.form['num_exemplar']
        desc_local = request.form['desc_local']
        db = get_db()
        error = None

        if not cod_livro:
            error = 'cdExemplar is required.'
        elif not num_exemplar:
            error = 'num_exemplar is required.'
        elif not desc_local:
            error = 'desc_local is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO emprestimos (cod_exemplar, cod_cliente, data_emp) VALUES (?, ?, ?)",
                    (cod_livro, num_exemplar, desc_local),
                )
                db.commit()
            except db.IntegrityError:
                error = f"livro {num_exemplar} is already registered."
            else:
                return redirect(url_for("home"))

        flash(error)

    return render_template('cadastro/exemplar.html')