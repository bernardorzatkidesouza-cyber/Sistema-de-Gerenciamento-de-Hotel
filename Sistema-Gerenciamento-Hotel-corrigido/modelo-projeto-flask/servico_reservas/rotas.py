from flask import Blueprint, jsonify, request
import regras

rotas = Blueprint("reservas", __name__, url_prefix="/api/reservas")


@rotas.post("")
def criar():
    reserva = regras.criar(request.get_json(silent=True) or {})
    return jsonify(reserva.para_dict()), 201


@rotas.get("")
def listar():
    return jsonify([r.para_dict() for r in regras.listar()])


@rotas.get("/<int:reserva_id>")
def buscar(reserva_id):
    reserva = regras.buscar(reserva_id)
    return (jsonify(reserva.para_dict()), 200) if reserva else (jsonify(erro="Reserva não encontrada."), 404)


@rotas.put("/<int:reserva_id>/status")
def atualizar_status(reserva_id):
    dados = request.get_json(silent=True) or {}
    reserva = regras.atualizar_status(reserva_id, dados.get("status"))
    return (jsonify(reserva.para_dict()), 200) if reserva else (jsonify(erro="Reserva não encontrada."), 404)


@rotas.delete("/<int:reserva_id>")
def excluir(reserva_id):
    if not regras.excluir(reserva_id):
        return jsonify(erro="Reserva não encontrada."), 404
    return jsonify(mensagem="Reserva excluída com sucesso."), 200
