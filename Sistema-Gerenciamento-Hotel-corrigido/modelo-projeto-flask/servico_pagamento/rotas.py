from flask import Blueprint, jsonify
import regras
from flask import request

rotas = Blueprint("pagamentos", __name__, url_prefix="/api/pagamentos")


@rotas.post("")
def criar():
    pagamento = regras.criar(request.get_json(silent=True) or {})
    return jsonify(pagamento.para_dict()), 201


@rotas.get("")
def listar():
    return jsonify([p.para_dict() for p in regras.listar()])


@rotas.get("/<int:pagamento_id>")
def buscar(pagamento_id):
    pagamento = regras.buscar(pagamento_id)
    return (jsonify(pagamento.para_dict()), 200) if pagamento else (jsonify(erro="Pagamento não encontrado."), 404)


@rotas.delete("/<int:pagamento_id>")
def excluir(pagamento_id):
    if not regras.excluir(pagamento_id):
        return jsonify(erro="Pagamento não encontrado."), 404
    return jsonify(mensagem="Pagamento excluído com sucesso."), 200
