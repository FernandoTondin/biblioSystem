import functools
import datetime as dt

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from biblio.db import get_db,get_cursor

bp = Blueprint('view', __name__, url_prefix='/view')

@bp.route('/livro', methods=('GET', 'POST'))
def livro():
    db = get_db()
    cur = get_cursor()
    if request.method == 'POST':
        if "info" in request.form.keys():
            cod = int(request.form['cod'])
            cur.execute(
            'Select * FROM livros'
            ' WHERE cod_livro = %s',
            (cod,),
            )
            posts =cur.fetchall()
            return redirect(url_for('info.livro'),code=307)
        elif "emprestar" in request.form.keys():
            cod = int(request.form['cod'])
            cur.execute(
            'Select * FROM livros'
            ' WHERE cod_livro = %s',
            (cod,),
            )
            posts =cur.fetchall()
            return redirect(url_for('info.livro'),code=307)
        elif "deletar" in request.form.keys():
            cod = int(request.form['cod'])
            cur.execute("DELETE FROM livros WHERE cod_livro = %s",(cod,))
            db.commit()
            exemps = db.execute("SELECT cod_exemplar from exemplares WHERE cod_livro = %s",(cod,)).fetchall()
            for exemp in exemps:
                cur.execute("DELETE FROM emprestimos WHERE cod_exemplar = %s",(exemp["cod_exemplar"],))
                db.commit()
            cur.execute("DELETE FROM exemplares WHERE cod_livro = %s",(cod,))
            db.commit()
            cur.execute(
                'Select livros.cod_livro, tit_livro, nom_autor, num_volume, num_edicao, anoPublic, '
                '(select count(*) from exemplares where exemplares.cod_livro = livros.cod_livro) as QNT, '
                '(select sum(bool_disponivel) from exemplares where exemplares.cod_livro = livros.cod_livro) as DISP '
                'from livros '
                'ORDER BY tit_livro ASC'
            )
            posts = cur.fetchall()
            db.commit()
        elif "btn_pesquisa" in request.form.keys():
            pesquisa = request.form['pesquisa']
            pesquisa = "%"+pesquisa+"%"
            cur.execute(
                'Select livros.cod_livro, tit_livro, nom_autor, num_volume, num_edicao, anoPublic, '
                '(select count(*) from exemplares where exemplares.cod_livro = livros.cod_livro) as QNT, '
                '(select sum(bool_disponivel) from exemplares where exemplares.cod_livro = livros.cod_livro) as DISP '
                'from livros '
                ' WHERE tit_livro LIKE %s OR nom_autor LIKE %s'
                ' ORDER BY tit_livro ASC',
                (pesquisa,pesquisa),
                )
            posts =cur.fetchall()
            db.commit()
        else:
            posts =db.execute(
                'Select livros.cod_livro, tit_livro, nom_autor, num_volume, num_edicao, anoPublic, '
                '(select count(*) from exemplares where exemplares.cod_livro = livros.cod_livro) as QNT, '
                '(select sum(bool_disponivel) from exemplares where exemplares.cod_livro = livros.cod_livro) as DISP '
                'from livros '
                ' ORDER BY tit_livro ASC',
                )
            posts =cur.fetchall()
            db.commit()
        return render_template('view/livro.html', posts=posts)
    else:
        cur.execute(
            'Select livros.cod_livro, tit_livro, nom_autor, num_volume, num_edicao, anoPublic, '
            '(select count(*) from exemplares where exemplares.cod_livro = livros.cod_livro) as QNT, '
            '(select sum(bool_disponivel) from exemplares where exemplares.cod_livro = livros.cod_livro) as DISP '
            'from livros '
            'ORDER BY tit_livro ASC'
        )
        posts =cur.fetchall()
        print(posts)

        db.commit()
    return render_template('view/livro.html', posts=posts)


@bp.route('/cliente', methods=('GET', 'POST'))
def cliente():
    db = get_db()
    cur = get_cursor()
    if request.method == 'POST':
        if "info" in request.form.keys():
            cod = int(request.form['cod'])
            cur.execute(
            'Select * FROM clientes'
            ' WHERE cod_cliente = %s',
            (cod,),
            )
            posts = cur.fetchall()
            return redirect(url_for('info.cliente'),code=307)
        else:
            nome = request.form['title']
            if nome != "":
                nome = "%"+nome+"%"
                cur.execute(
                    'Select * FROM clientes'
                    ' WHERE nome_cliente LIKE %s'
                    ' ORDER BY nome_cliente ASC',
                    (nome,),
                    )
                posts = cur.fetchall()
                db.commit()
            else:
                cur.execute(
                    'Select * FROM clientes'
                    ' ORDER BY nome_cliente ASC',
                    )
                posts = cur.fetchall()
                db.commit()
    else:
        cur.execute(
                'Select * FROM clientes'
                ' ORDER BY nome_cliente ASC',
                )
        posts = cur.fetchall()
        db.commit()
    return render_template('view/cliente.html', posts=posts)

@bp.route('/emprestimo', methods=('GET', 'POST'))
def emprestimo():
    db = get_db()
    cur = get_cursor()
    if request.method == 'POST':
        pesquisa = request.form['title']
        if pesquisa != "":
            pesquisa = "%"+pesquisa+"%"
            cur.execute(
                'Select * '
                'FROM '
                    '(emprestimos LEFT JOIN '
                        '(exemplares LEFT JOIN livros on exemplares.cod_livro = livros.cod_livro) '
                    'on emprestimos.cod_exemplar = exemplares.cod_exemplar) '
                    'LEFT JOIN clientes on emprestimos.cod_cliente = clientes.cod_cliente '
                    'WHERE nome_cliente LIKE %s OR tit_livro LIKE %s OR nom_autor LIKE %s',(pesquisa,pesquisa,pesquisa),
                )
            posts = cur.fetchall()
            db.commit()
        else:
            cur.execute(
                'Select * '
                'FROM '
                    '(emprestimos LEFT JOIN '
                        '(exemplares LEFT JOIN livros on exemplares.cod_livro = livros.cod_livro) '
                    'on emprestimos.cod_exemplar = exemplares.cod_exemplar) '
                    'LEFT JOIN clientes on emprestimos.cod_cliente = clientes.cod_cliente ',
                )
            posts = cur.fetchall()
            db.commit()
    else:
        cur.execute(
                'Select * '
                'FROM '
                    '(emprestimos LEFT JOIN '
                        '(exemplares LEFT JOIN livros on exemplares.cod_livro = livros.cod_livro) '
                    'on emprestimos.cod_exemplar = exemplares.cod_exemplar) '
                    'LEFT JOIN clientes on emprestimos.cod_cliente = clientes.cod_cliente',
                )
        posts = cur.fetchall()
        db.commit()
    return render_template('view/emprestimo.html', posts=posts)

