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
            return redirect(url_for('cadastro.emprestimo'),code=307)
        elif "reservar" in request.form.keys():
            return redirect(url_for('cadastro.reserva'),code=307)
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
        print(request.form)
        if "devolver" in request.form.keys():
            dia = dt.date.today()
            cod_emp = request.form['cod']
            cur.execute(
                'select cod_exemplar from emprestimos WHERE cod_emprestimo = %s',(cod_emp,)
            )
            exemps = cur.fetchall()
            for exemp in exemps:
                cur.execute(
                    'select cod_livro from exemplares '
                    'WHERE cod_exemplar = %s',(exemp["cod_exemplar"],)
                )
                cod_livro = cur.fetchall()[0]["cod_livro"]
                cur.execute(
                    'SELECT * '
                    'FROM reservas '
                    'WHERE cod_livro = %s',(cod_livro,)
                )
                reservas = cur.fetchall()
                if reservas != []:
                    cur.execute(
                        'UPDATE exemplares '
                        'SET bool_disponivel = 0, bool_emprestado = 0, bool_reservado = 1 '
                        'WHERE cod_exemplar = %s',(exemp["cod_exemplar"],)
                    )
                    db.commit()
                    cur.execute(
                        'UPDATE reservas '
                        'SET cod_exemplar = %s, bool_emprestado = 0, bool_reservado = 1 '
                        'WHERE cod_reserva = %s',(exemp["cod_exemplar"],reservas[0]["cod_reserva"])
                    )
                    db.commit()
                    ################################
                    #TODO enviar email
                    ################################
                else:
                    cur.execute(
                        'UPDATE exemplares '
                        'SET bool_disponivel = 1, bool_emprestado = 0, bool_reservado = 0 '
                        'WHERE cod_exemplar = %s',(exemp["cod_exemplar"],)
                    )
                    db.commit()
            cur.execute(
                'UPDATE emprestimos '
                'SET data_devol = %s '
                'WHERE cod_emprestimo = %s',(dia.strftime("%Y-%m-%d"),cod_emp)
            )
            db.commit()
            cur.execute(
                'Select * '
                'FROM '
                    '(emprestimos LEFT JOIN '
                        '(exemplares LEFT JOIN livros on exemplares.cod_livro = livros.cod_livro) '
                    'on emprestimos.cod_exemplar = exemplares.cod_exemplar) '
                    'LEFT JOIN clientes on emprestimos.CPF = clientes.CPF '
                    'WHERE data_devol IS NULL',
            )
            posts = cur.fetchall()
            return render_template('view/emprestimo.html',posts=posts)
        elif "deletar" in request.form.keys():
            cod_emp = request.form['cod']
            cur.execute(
                'select cod_exemplar from emprestimos WHERE cod_emprestimo = %s',(cod_emp,)
            )
            exemps = cur.fetchall()
            for exemp in exemps:
                cur.execute(
                    'UPDATE exemplares '
                    'SET bool_disponivel = 1, bool_emprestado = 0, bool_reservado = 0 '
                    'WHERE cod_exemplar = %s',(exemp["cod_exemplar"],)
                )
                db.commit()
            cur.execute(
                'DELETE FROM emprestimos '
                'WHERE cod_emprestimo = %s',(cod_emp,)
            )
            db.commit()

            cur.execute(
                'Select * '
                'FROM '
                    '(emprestimos LEFT JOIN '
                        '(exemplares LEFT JOIN livros on exemplares.cod_livro = livros.cod_livro) '
                    'on emprestimos.cod_exemplar = exemplares.cod_exemplar) '
                    'LEFT JOIN clientes on emprestimos.CPF = clientes.CPF ',
            )
            posts = cur.fetchall()
            return render_template('view/emprestimo.html',posts=posts)
        else:
            if "atrasados" in request.form.keys():
                atrasado = True
                dia = dt.date.today()
            else:
                atrasado = False
            pesquisa = request.form['title']
            if pesquisa != "":
                pesquisa = "%"+pesquisa+"%"
                if atrasado:
                    cur.execute(
                        'Select * '
                        'FROM '
                            '(emprestimos LEFT JOIN '
                                '(exemplares LEFT JOIN livros on exemplares.cod_livro = livros.cod_livro) '
                            'on emprestimos.cod_exemplar = exemplares.cod_exemplar) '
                            'LEFT JOIN clientes on emprestimos.CPF = clientes.CPF '
                            'WHERE (nome_cliente LIKE %s OR tit_livro LIKE %s OR nom_autor LIKE %s) AND prazo_devol < %s  AND data_devol IS NULL',(pesquisa,pesquisa,pesquisa,dia.strftime("%Y-%m-%d")),
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
                            'LEFT JOIN clientes on emprestimos.CPF = clientes.CPF '
                            'WHERE (nome_cliente LIKE %s OR tit_livro LIKE %s OR nom_autor LIKE %s)',(pesquisa,pesquisa,pesquisa),
                        )
                    posts = cur.fetchall()
                    db.commit()
            else:
                if atrasado:
                    cur.execute(
                        'Select * '
                        'FROM '
                            '(emprestimos LEFT JOIN '
                                '(exemplares LEFT JOIN livros on exemplares.cod_livro = livros.cod_livro) '
                            'on emprestimos.cod_exemplar = exemplares.cod_exemplar) '
                            'LEFT JOIN clientes on emprestimos.CPF = clientes.CPF '
                            'WHERE prazo_devol < %s  AND data_devol IS NULL',(dia.strftime("%Y-%m-%d"),),
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
                        'LEFT JOIN clientes on emprestimos.CPF = clientes.CPF ',
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
                    'LEFT JOIN clientes on emprestimos.CPF = clientes.CPF ',
                )
        posts = cur.fetchall()
    return render_template('view/emprestimo.html', posts=posts)

@bp.route('/reserva', methods=('GET', 'POST'))
def reserva():
    db = get_db()
    cur = get_cursor()
    if request.method == 'POST':
        print(request.form)
        if "devolver" in request.form.keys():
            dia = dt.date.today()
            cod_emp = request.form['cod']
            cur.execute(
                'select cod_exemplar from emprestimos WHERE cod_emprestimo = %s',(cod_emp,)
            )
            exemps = cur.fetchall()
            for exemp in exemps:
                cur.execute(
                    'select cod_livro from exemplares '
                    'WHERE cod_exemplar = %s',(exemp["cod_exemplar"],)
                )
                cod_livro = cur.fetchall()[0]["cod_livro"]
                cur.execute(
                    'SELECT * '
                    'FROM reservas '
                    'WHERE cod_livro = %s',(cod_livro,)
                )
                reservas = cur.fetchall()
                if reservas != []:
                    cur.execute(
                        'UPDATE exemplares '
                        'SET bool_disponivel = 0, bool_emprestado = 0, bool_reservado = 1 '
                        'WHERE cod_exemplar = %s',(exemp["cod_exemplar"],)
                    )
                    db.commit()
                    cur.execute(
                        'UPDATE reservas '
                        'SET cod_exemplar = %s, bool_emprestado = 0, bool_reservado = 1 '
                        'WHERE cod_reserva = %s',(exemp["cod_exemplar"],reservas[0]["cod_reserva"])
                    )
                    db.commit()
                    ################################
                    #TODO enviar email
                    ################################
                else:
                    cur.execute(
                        'UPDATE exemplares '
                        'SET bool_disponivel = 1, bool_emprestado = 0, bool_reservado = 0 '
                        'WHERE cod_exemplar = %s',(exemp["cod_exemplar"],)
                    )
                    db.commit()
            cur.execute(
                'UPDATE emprestimos '
                'SET data_devol = %s '
                'WHERE cod_emprestimo = %s',(dia.strftime("%Y-%m-%d"),cod_emp)
            )
            db.commit()
            cur.execute(
                'Select * '
                'FROM '
                    '(emprestimos LEFT JOIN '
                        '(exemplares LEFT JOIN livros on exemplares.cod_livro = livros.cod_livro) '
                    'on emprestimos.cod_exemplar = exemplares.cod_exemplar) '
                    'LEFT JOIN clientes on emprestimos.CPF = clientes.CPF '
                    'WHERE data_devol IS NULL',
            )
            posts = cur.fetchall()
            return render_template('view/emprestimo.html',posts=posts)
        elif "deletar" in request.form.keys():
            cod_emp = request.form['cod']
            cur.execute(
                'select cod_exemplar from emprestimos WHERE cod_emprestimo = %s',(cod_emp,)
            )
            exemps = cur.fetchall()
            for exemp in exemps:
                cur.execute(
                    'UPDATE exemplares '
                    'SET bool_disponivel = 1, bool_emprestado = 0, bool_reservado = 0 '
                    'WHERE cod_exemplar = %s',(exemp["cod_exemplar"],)
                )
                db.commit()
            cur.execute(
                'DELETE FROM emprestimos '
                'WHERE cod_emprestimo = %s',(cod_emp,)
            )
            db.commit()

            cur.execute(
                'Select * '
                'FROM '
                    '(emprestimos LEFT JOIN '
                        '(exemplares LEFT JOIN livros on exemplares.cod_livro = livros.cod_livro) '
                    'on emprestimos.cod_exemplar = exemplares.cod_exemplar) '
                    'LEFT JOIN clientes on emprestimos.CPF = clientes.CPF '
                    'WHERE data_devol IS NULL',
            )
            posts = cur.fetchall()
            return render_template('view/emprestimo.html',posts=posts)
        else:
            if "atrasados" in request.form.keys():
                atrasado = True
                dia = dt.date.today()
            else:
                atrasado = False
            pesquisa = request.form['title']
            if pesquisa != "":
                pesquisa = "%"+pesquisa+"%"
                if atrasado:
                    cur.execute(
                        'Select * '
                        'FROM '
                            '(emprestimos LEFT JOIN '
                                '(exemplares LEFT JOIN livros on exemplares.cod_livro = livros.cod_livro) '
                            'on emprestimos.cod_exemplar = exemplares.cod_exemplar) '
                            'LEFT JOIN clientes on emprestimos.CPF = clientes.CPF '
                            'WHERE (nome_cliente LIKE %s OR tit_livro LIKE %s OR nom_autor LIKE %s) AND prazo_devol < %s AND data_devol IS NULL',(pesquisa,pesquisa,pesquisa,dia.strftime("%Y-%m-%d")),
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
                            'LEFT JOIN clientes on emprestimos.CPF = clientes.CPF '
                            'WHERE (nome_cliente LIKE %s OR tit_livro LIKE %s OR nom_autor LIKE %s) AND data_devol IS NULL',(pesquisa,pesquisa,pesquisa),
                        )
                    posts = cur.fetchall()
                    db.commit()
            else:
                if atrasado:
                    cur.execute(
                        'Select * '
                        'FROM '
                            '(emprestimos LEFT JOIN '
                                '(exemplares LEFT JOIN livros on exemplares.cod_livro = livros.cod_livro) '
                            'on emprestimos.cod_exemplar = exemplares.cod_exemplar) '
                            'LEFT JOIN clientes on emprestimos.CPF = clientes.CPF '
                            'WHERE prazo_devol < %s AND data_devol IS NULL',(dia.strftime("%Y-%m-%d"),),
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
                        'LEFT JOIN clientes on emprestimos.CPF = clientes.CPF '
                        'WHERE data_devol IS NULL',
                    )
                    posts = cur.fetchall()
                    db.commit()
    else:
        cur.execute(
                'Select cod_reserva, tit_livro, nome_cliente, data_reserva, reservas.cod_exemplar '
                'FROM reservas '
                'LEFT JOIN exemplares ON reservas.cod_exemplar = exemplares.cod_exemplar '
                'LEFT JOIN livros ON reservas.cod_livro = livros.cod_livro '
                'LEFT JOIN clientes on reservas.CPF = clientes.CPF',
                )
        posts = cur.fetchall()
    return render_template('view/reserva.html', posts=posts)

