DROP TABLE if exists emprestimos;

DROP TABLE if exists reservas;

DROP TABLE if exists exemplares;

DROP TABLE if exists livros;

DROP TABLE if exists clientes;

DROP TABLE if exists user;



CREATE TABLE livros(
    cod_livro integer not null unique AUTO_INCREMENT,
    tit_livro VARCHAR(20),
    nom_autor VARCHAR(40),
    num_volume integer,
    num_edicao smallint,
    anoPublic smallint,
    desc_local VARCHAR(40),
    PRIMARY key (cod_livro)
    );

CREATE TABLE exemplares(
    cod_exemplar integer not null unique AUTO_INCREMENT,
    cod_livro integer not null,
    num_exemplar smallint not null default 1,
    bool_disponivel tinyint,
    bool_reservado tinyint,
    bool_emprestado tinyint,
    PRIMARY KEY (cod_exemplar),
    FOREIGN KEY (cod_livro) REFERENCES livros(cod_livro)
);

CREATE TABLE clientes(
    cod_cliente integer not null unique AUTO_INCREMENT,
    nome_cliente VARCHAR(40),
    CPF VARCHAR(20) not null unique,
    dsc_email_cliente VARCHAR(60),
    dsc_endereco_cliente VARCHAR(60),
    PRIMARY KEY (CPF)
);

CREATE TABLE emprestimos(
    cod_emprestimo integer not null unique AUTO_INCREMENT,
    cod_exemplar integer not null,
    CPF VARCHAR(20) not null,
    data_emp Date,
    data_devol Date,
    prazo_devol Date,
    PRIMARY KEY (cod_emprestimo),
    FOREIGN KEY (cod_exemplar) REFERENCES exemplares(cod_exemplar),
    FOREIGN KEY (CPF) REFERENCES clientes(CPF)
);

CREATE TABLE reservas(
    cod_reserva integer not null unique AUTO_INCREMENT,
    cod_livro integer not null,
    cod_exemplar integer,
    CPF VARCHAR(20) not null,
    data_reserva Date,
    data_devol Date,
    data_emp Date,
    PRIMARY KEY (cod_reserva),
    FOREIGN KEY (cod_livro) REFERENCES livros(cod_livro),
    FOREIGN KEY (cod_exemplar) REFERENCES exemplares(cod_exemplar),
    FOREIGN KEY (CPF) REFERENCES clientes(CPF)
);

CREATE TABLE user (
    id INTEGER NOT NULL AUTO_INCREMENT,
    usuario VARCHAR(255) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    boolAdmin tinyint,
    PRIMARY KEY(id)
);