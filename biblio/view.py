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
        db = get_db()
        if "info" in request.form.keys():
            cod = int(request.form['cod'])
            posts =db.execute(
            'Select * FROM livros'
            ' WHERE cod_livro = ?',
            (cod,),
            ).fetchall()
            return redirect(url_for('info.livro'),code=307)
        elif "deletar" in request.form.keys():
            cod = int(request.form['cod'])
            db.execute("DELETE FROM livros WHERE cod_livro = ?",(cod,))
            db.commit()
            exemps = db.execute("SELECT cod_exemplar from exemplares WHERE cod_livro = ?",(cod,)).fetchall()
            for exemp in exemps:
                db.execute("DELETE FROM emprestimos WHERE cod_exemplar = ?",(exemp["cod_exemplar"],))
                db.commit()
            db.execute("DELETE FROM exemplares WHERE cod_livro = ?",(cod,))
            db.commit()
            posts = db.execute(
                'Select livros.cod_livro, tit_livro, nom_autor, num_volume, num_edicao, anoPublic, '
                '(select count(*) from exemplares where exemplares.cod_livro = livros.cod_livro) as QNT, '
                '(select sum(bool_disponivel) from exemplares where exemplares.cod_livro = livros.cod_livro) as DISP '
                'from livros '
                'ORDER BY tit_livro ASC'
            ).fetchall()
            db.commit()
        elif "btn_pesquisa" in request.form.keys():
            pesquisa = request.form['pesquisa']
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
        return render_template('view/livro.html', posts=posts)
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

