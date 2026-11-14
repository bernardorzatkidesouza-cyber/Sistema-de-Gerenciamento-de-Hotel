from flask import Blueprint, jsonify, request
import regras

rotas = Blueprint("quartos", __name__, url_prefix="/api/quartos")


@rotas.post("")
def criar():
    quarto = regras.criar(request.get_json(silent=True) or {})
    return jsonify(quarto.para_dict()), 201


@rotas.get("")
def listar():
    return jsonify([q.para_dict() for q in regras.listar()])


@rotas.get("/<int:quarto_id>/disponibilidade")
def disponibilidade(quarto_id):
    resultado = regras.disponibilidade(quarto_id)
    return (jsonify(resultado), 200) if resultado else (jsonify(erro="Quarto não encontrado."), 404)


@rotas.get("/<int:quarto_id>")
def buscar(quarto_id):
    quarto = regras.buscar(quarto_id)
    return (jsonify(quarto.para_dict()), 200) if quarto else (jsonify(erro="Quarto não encontrado."), 404)


@rotas.put("/<int:quarto_id>")
def atualizar(quarto_id):
    quarto = regras.atualizar(quarto_id, request.get_json(silent=True) or {})
    return (jsonify(quarto.para_dict()), 200) if quarto else (jsonify(erro="Quarto não encontrado."), 404)


@rotas.delete("/<int:quarto_id>")
def excluir(quarto_id):
    if not regras.excluir(quarto_id):
        return jsonify(erro="Quarto não encontrado."), 404
    return jsonify(mensagem="Quarto excluído com sucesso."), 200
