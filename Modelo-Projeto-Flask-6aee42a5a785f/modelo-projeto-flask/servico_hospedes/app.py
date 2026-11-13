import logging
import os

from flask import Flask, jsonify, request

import regras
from erros import RegraDeNegocioError
from models import db
from rotas import rotas

NOME = "servicohospede"      # TROQUE pelo nome do seu serviço, ex.: "RESIDENCIAS"
PORTA = 5001
BANCO = "hospedes.db"  # cada serviço tem o SEU banco

logging.getLogger("werkzeug").setLevel(logging.ERROR)  # esconde o log padrão do Flask


def criar_app():
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.json.sort_keys = False

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BANCO}"
    db.init_app(app)
    with app.app_context():
        db.create_all()
        regras.dados_iniciais()

    app.register_blueprint(rotas)

    @app.get("/api/health")
    def health():
        return jsonify(status="no ar", servico=NOME)

    @app.after_request
    def mostrar_no_terminal(resposta):
        print(f"[{NOME}] recebi {request.method} {request.path} "
              f"-> respondi {resposta.status_code}", flush=True)
        return resposta

    @app.errorhandler(RegraDeNegocioError)
    def erro_de_regra(erro):
        print(f"[{NOME}] regra violada: {erro}", flush=True)
        return jsonify(erro=str(erro)), 400

    return app


# O Render (e outros servidores) usam esta variável; localmente usamos o bloco abaixo.
app = criar_app()

if __name__ == "__main__":
    print(f"[{NOME}] iniciando na porta {PORTA}...", flush=True)
    app.run(port=int(os.environ.get("PORT", PORTA)), debug=True)
