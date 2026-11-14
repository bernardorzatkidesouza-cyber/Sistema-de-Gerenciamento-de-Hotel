from flask import Blueprint, jsonify, request
import regras

rotas = Blueprint("hospedes", __name__, url_prefix="/api/hospedes")


@rotas.post("")
def criar():
    hospede = regras.criar(request.get_json(silent=True) or {})
    return jsonify(hospede.para_dict()), 201


@rotas.get("")
def listar():
    return jsonify([h.para_dict() for h in regras.listar()])


@rotas.get("/<int:hospede_id>")
def buscar(hospede_id):
    hospede = regras.buscar(hospede_id)
    return (jsonify(hospede.para_dict()), 200) if hospede else (jsonify(erro="Hóspede não encontrado."), 404)


@rotas.put("/<int:hospede_id>")
def atualizar(hospede_id):
    hospede = regras.atualizar(hospede_id, request.get_json(silent=True) or {})
    return (jsonify(hospede.para_dict()), 200) if hospede else (jsonify(erro="Hóspede não encontrado."), 404)


@rotas.delete("/<int:hospede_id>")
def excluir(hospede_id):
    if not regras.excluir(hospede_id):
        return jsonify(erro="Hóspede não encontrado."), 404
    return jsonify(mensagem="Hóspede excluído com sucesso."), 200
