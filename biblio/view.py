import functools
import datetime as dt

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from biblio.db import get_db

bp = Blueprint('view', __name__, url_prefix='/view')

@bp.route('/livro', methods=('GET', 'POST'))
def livro():
    if request.method == 'POST':
        pesquisa = request.form['title']
        db = get_db()
        if pesquisa != "":
            pesquisa = "%"+pesquisa+"%"
            posts =db.execute(
                'Select livros.cod_livro, tit_livro, nom_autor, num_volume, num_edicao, anoPublic, '
                '(select count(*) from exemplares where exemplares.cod_livro = livros.cod_livro) as QNT, '
                '(select sum(bool_disponivel) from exemplares where exemplares.cod_livro = livros.cod_livro) as DISP '
                'from livros '
                ' WHERE tit_livro LIKE ? OR nom_autor LIKE ?'
                ' ORDER BY tit_livro ASC',
                (pesquisa,pesquisa),
                ).fetchall()
            db.commit()
        else:
            posts =db.execute(
                'Select livros.cod_livro, tit_livro, nom_autor, num_volume, num_edicao, anoPublic, '
                '(select count(*) from exemplares where exemplares.cod_livro = livros.cod_livro) as QNT, '
                '(select sum(bool_disponivel) from exemplares where exemplares.cod_livro = livros.cod_livro) as DISP '
                'from livros '
                ' ORDER BY tit_livro ASC',
                ).fetchall()
            db.commit()
    else:
        db = get_db()
        posts = db.execute(
            'Select livros.cod_livro, tit_livro, nom_autor, num_volume, num_edicao, anoPublic, '
            '(select count(*) from exemplares where exemplares.cod_livro = livros.cod_livro) as QNT, '
            '(select sum(bool_disponivel) from exemplares where exemplares.cod_livro = livros.cod_livro) as DISP '
            'from livros '
            'ORDER BY tit_livro ASC'
        ).fetchall()
        db.commit()
    return render_template('view/livro.html', posts=posts)


@bp.route('/cliente', methods=('GET', 'POST'))
def cliente():
    if request.method == 'POST':
        nome = request.form['title']
        db = get_db()
        if nome != "":
            nome = "%"+nome+"%"
            posts =db.execute(
                'Select * FROM clientes'
                ' WHERE nome_cliente LIKE ?'
                ' ORDER BY nome_cliente ASC',
                (nome,),
                ).fetchall()
            db.commit()
        else:
            posts =db.execute(
                'Select * FROM clientes'
                ' ORDER BY nome_cliente ASC',
                ).fetchall()
            db.commit()
    else:
        db = get_db()
        posts =db.execute(
                'Select * FROM clientes'
                ' ORDER BY nome_cliente ASC',
                ).fetchall()
        db.commit()
    return render_template('view/cliente.html', posts=posts)

@bp.route('/emprestimo', methods=('GET', 'POST'))
def emprestimo():
    if request.method == 'POST':
        pesquisa = request.form['title']
        db = get_db()
        if pesquisa != "":
            pesquisa = "%"+pesquisa+"%"
            posts =db.execute(
                'Select * '
                'FROM '
                    '(emprestimos LEFT JOIN '
                        '(exemplares LEFT JOIN livros on exemplares.cod_livro = livros.cod_livro) '
                    'on emprestimos.cod_exemplar = exemplares.cod_exemplar) '
                    'LEFT JOIN clientes on emprestimos.cod_cliente = clientes.cod_cliente '
                    'WHERE nome_cliente LIKE ? OR tit_livro LIKE ? OR nom_autor LIKE ?',(pesquisa,pesquisa,pesquisa),
                ).fetchall()
            db.commit()
        else:
            posts =db.execute(
                'Select * '
                'FROM '
                    '(emprestimos LEFT JOIN '
                        '(exemplares LEFT JOIN livros on exemplares.cod_livro = livros.cod_livro) '
                    'on emprestimos.cod_exemplar = exemplares.cod_exemplar) '
                    'LEFT JOIN clientes on emprestimos.cod_cliente = clientes.cod_cliente ',
                ).fetchall()
            db.commit()
    else:
        db = get_db()
        posts =db.execute(
                'Select * '
                'FROM '
                    '(emprestimos LEFT JOIN '
                        '(exemplares LEFT JOIN livros on exemplares.cod_livro = livros.cod_livro) '
                    'on emprestimos.cod_exemplar = exemplares.cod_exemplar) '
                    'LEFT JOIN clientes on emprestimos.cod_cliente = clientes.cod_cliente',
                ).fetchall()
        db.commit()
    return render_template('view/emprestimo.html', posts=posts)

