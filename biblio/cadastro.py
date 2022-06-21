import functools
import datetime as dt
from logging import exception

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from biblio.db import get_db,get_cursor

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
        cur = db.cursor()
        error = None

        if not titulo:
            error = 'favor inserir título.'
        elif not autor:
            error = 'favor inserir autor.'
        elif not volume:
            error = 'favor inserir volume.'
        elif not edicao:
            error = 'favor inserir ediço.'
        elif not publicacao:
            error = 'favor inserir ano de publicação.'

        if error is None:
            try:
                cur.execute(
                    "INSERT INTO livros (tit_livro, nom_autor,num_volume,num_edicao,anoPublic) VALUES (%s, %s, %s, %s, %s)",
                    (titulo, autor, volume, edicao,publicacao),
                )
                db.commit()
                cur.execute('INSERT INTO exemplares (cod_livro,num_exemplar,bool_disponivel,bool_emprestado,bool_reservado)'
                ' SELECT cod_livro,0 as num_exemplar,1 as bool_disponivel,0 as bool_emprestado,0 as bool_reservado FROM livros'
                ' WHERE tit_livro=%s AND num_volume=%s AND num_edicao=%s',
                (titulo, volume, edicao))
                db.commit()
            except Exception as e:
                print(e)
                error = f"livro {titulo} is already registered."
            else:
                return redirect(url_for("home"))

        flash(error)

    return render_template('cadastro/livro.html')

@bp.route('/cliente', methods=('GET', 'POST'))
def cliente():
    db = get_db()
    cur = get_cursor()
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        end = request.form['descEnderecoCliente']
        email = request.form['dsc_email_cliente']
        db = get_db()
        error = None

        if not nome:
            error = 'nome is required.'
        elif not cpf:
            error = 'cpf is required.'
        elif not end:
            error = 'endereco is required.'
        elif not email:
            error = 'endereco is required.'

        if error is None:
            try:
                cur.execute(
                    "INSERT INTO clientes (nome_cliente, CPF, dsc_endereco_cliente, dsc_email_cliente) VALUES (%s, %s, %s, %s)",
                    (nome, cpf, end, email),
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
    db = get_db()
    cur = get_cursor()
    if request.method == 'POST':
        if "emprestar" in request.form.keys():
            cod = int(request.form['cod'])
            cur.execute(
            'Select * FROM livros'
            ' WHERE cod_livro = %s',
            (cod,),
            )
            posts = cur.fetchall()
            return render_template('cadastro/emprestimo.html', posts=posts)
        else:
            cdLivro = request.form['cdLivro']
            cpfCliente = request.form['cpfCliente']
            data = dt.date.today()
            dataemp = data.strftime("%Y-%m-%d")
            prazo = data + dt.timedelta(days=5)
            prazoemp = prazo.strftime("%Y-%m-%d")
            error = None

            if not cdLivro:
                error = 'favor inserir o Livro a ser emprestado.'
            elif not cpfCliente:
                error = 'Favor inserir o CPF do cliente.'

            if error is None:
                disp = False
                cur.execute("SELECT * from exemplares WHERE cod_livro = %s",(cdLivro,))
                exemps = cur.fetchall()
                for exemp in exemps:
                    if exemp["bool_disponivel"]:
                        disp = True
                        cdExemplar = exemp["cod_exemplar"]
                if disp:
                    try:
                        cur.execute(
                            "INSERT INTO emprestimos (cod_exemplar, CPF, data_emp, prazo_devol) VALUES (%s, %s, %s, %s)",
                            (cdExemplar, cpfCliente, dataemp, prazoemp),
                        )
                        db.commit()
                        try:
                            cur.execute(
                                "UPDATE exemplares SET bool_disponivel = 0, bool_emprestado = 1 WHERE cod_exemplar = %s",
                                (cdExemplar,),
                            )
                            db.commit()
                        except Exception as e:
                            print(e)
                            error = "falha ao registrar emprestimo"
                        else:
                            return redirect(url_for("home"))
                    except Exception as e:
                        print(e)
                        error = f"falha ao criar emprestimo"
                else:
                    error = "Livro indisponivel, favor reservar pela tela de pesquisa"

            flash(error)

    return render_template('cadastro/emprestimo.html')


@bp.route('/reserva', methods=('GET', 'POST'))
def reserva():
    db = get_db()
    cur = get_cursor()
    if request.method == 'POST':
        if "reservar" in request.form.keys():
            cod = int(request.form['cod'])
            cur.execute(
            'Select * FROM livros'
            ' WHERE cod_livro = %s',
            (cod,),
            )
            posts =cur.fetchall()
            return render_template('cadastro/reserva.html', posts=posts)
        else:
            cdLivro = request.form['cdLivro']
            cpfCliente = request.form['cpfCliente']
            data = dt.date.today()
            dataemp = data.strftime("%Y-%m-%d")
            error = None

            if not cdLivro:
                error = 'Favor inserir o Livro a ser reservado.'
            elif not cpfCliente:
                error = 'Favor inserir o CPF do cliente.'

            if error is None:
                try:
                    cur.execute(
                        "INSERT INTO reservas (cod_livro, CPF, data_reserva) VALUES (%s, %s, %s)",
                        (cdLivro, cpfCliente, dataemp),
                    )
                    db.commit()
                except Exception as e:
                    print(e)
                    error = f"falha ao criar reserva"
                else:
                    return redirect(url_for("home"))

            flash(error)

    return render_template('cadastro/reserva.html')



@bp.route('/exemplar', methods=('GET', 'POST'))
def exemplar():
    db = get_db()
    cur = get_cursor()
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
                cur.execute(
                    "INSERT INTO emprestimos (cod_exemplar, cod_cliente, data_emp) VALUES (%s, %s, %s)",
                    (cod_livro, num_exemplar, desc_local),
                )
                db.commit()
            except db.IntegrityError:
                error = f"livro {num_exemplar} is already registered."
            else:
                return redirect(url_for("home"))

        flash(error)

    return render_template('cadastro/exemplar.html')