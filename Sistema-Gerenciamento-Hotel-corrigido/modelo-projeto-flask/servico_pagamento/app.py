import logging
import os
from pathlib import Path

from flask import Flask, jsonify, request

import regras
from erros import ErroIntegracao, RegraDeNegocioError
from models import db
from rotas import rotas

NOME = "servico_pagamentos"
PORTA = 5004
BANCO = "pagamentos.db"
BASE_DIR = Path(__file__).resolve().parent

logging.getLogger("werkzeug").setLevel(logging.ERROR)


def criar_app():
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.json.sort_keys = False
    caminho_banco = BASE_DIR / BANCO
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{caminho_banco.as_posix()}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()
        regras.dados_iniciais()

    app.register_blueprint(rotas)

    @app.get("/api/health")
    def health():
        return jsonify(status="no ar", servico=NOME), 200

    @app.after_request
    def mostrar_no_terminal(resposta):
        print(f"[{NOME}] {request.method} {request.path} -> {resposta.status_code}", flush=True)
        return resposta

    @app.errorhandler(RegraDeNegocioError)
    def erro_de_regra(erro):
        return jsonify(erro=str(erro)), erro.status_code

    @app.errorhandler(ErroIntegracao)
    def erro_de_integracao(erro):
        print(f"[{NOME}] falha de integração: {erro}", flush=True)
        return jsonify(erro=str(erro)), erro.status_code

    return app


app = criar_app()

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", PORTA))
    print(f"[{NOME}] iniciando na porta 5004...", flush=True)
    app.run(host="0.0.0.0", port=porta, debug=False)
