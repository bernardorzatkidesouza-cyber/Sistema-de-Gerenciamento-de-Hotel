from flask import Blueprint, jsonify, request

import regras

rotas = Blueprint("registros", __name__, url_prefix="/api")


def _nao_encontrado():
    return jsonify(erro="Registro não encontrado."), 404


@rotas.post("/registros")
def criar():
    registro = regras.criar(request.get_json(silent=True) or {})
    return jsonify(registro.para_dict()), 201


@rotas.get("/registros")
def listar():
    return jsonify([r.para_dict() for r in regras.listar()])


@rotas.get("/registros/<int:registro_id>")
def buscar(registro_id):
    registro = regras.buscar(registro_id)
    return jsonify(registro.para_dict()) if registro else _nao_encontrado()


@rotas.put("/registros/<int:registro_id>")
def atualizar(registro_id):
    registro = regras.atualizar(registro_id, request.get_json(silent=True) or {})
    return jsonify(registro.para_dict()) if registro else _nao_encontrado()


@rotas.patch("/registros/<int:registro_id>/inativar")
def inativar(registro_id):
    registro = regras.inativar(registro_id)
    return jsonify(registro.para_dict()) if registro else _nao_encontrado()


# Rota pensada para OUTROS serviços perguntarem "está ativo?" (uma busca simples).
@rotas.get("/registros/<int:registro_id>/ativo")
def esta_ativo(registro_id):
    registro = regras.buscar(registro_id)
    if registro is None:
        return _nao_encontrado()
    return jsonify(id=registro.id, ativo=registro.ativo)
