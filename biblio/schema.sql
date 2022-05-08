DROP TABLE if exists emprestimos;

DROP TABLE if exists exemplares;

DROP TABLE if exists livros;

DROP TABLE if exists clientes;


CREATE TABLE livros(
    cod_livro integer not null unique,
    tit_livro VARCHAR(20),
    nom_autor VARCHAR(40),
    num_volume integer,
    num_edicao smallint,
    anoPublic smallint,
    PRIMARY key (cod_livro)
    );

CREATE TABLE exemplares(
    cod_exemplar integer not null unique,
    cod_livro integer not null,
    num_exemplar smallint not null default 1,
    bool_disponivel tinyint,
    desc_local VARCHAR(40),
    PRIMARY KEY (cod_exemplar),
    FOREIGN KEY (cod_livro) REFERENCES livros(cod_livro)
);

CREATE TABLE clientes(
    cod_cliente integer not null unique,
    nome_cliente VARCHAR(40),
    CPF VARCHAR(20),
    dsc_endereco_cliente VARCHAR(60),
    PRIMARY KEY (cod_cliente)
);

CREATE TABLE emprestimos(
    cod_emprestimo integer not null unique,
    cod_exemplar integer not null,
    cod_cliente integer not null,
    data_emp Date,
    data_devol Date,
    prazo_devol Date,
    PRIMARY KEY (cod_emprestimo),
    FOREIGN KEY (cod_exemplar) REFERENCES exemplares(cod_exemplar),
    FOREIGN KEY (cod_cliente) REFERENCES clientes(cod_cliente)
);