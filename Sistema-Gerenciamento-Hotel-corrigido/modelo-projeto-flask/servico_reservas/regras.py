from datetime import date
import integracao
from erros import ErroIntegracao, RegraDeNegocioError
from models import Reserva, db


def _data(valor, campo):
    try:
        return date.fromisoformat(valor)
    except (TypeError, ValueError):
        raise RegraDeNegocioError(f"'{campo}' deve estar no formato AAAA-MM-DD.")


def _consultar_servico(destino, caminho, descricao):
    resposta = integracao.chamar(destino, "GET", caminho)
    if resposta.status_code == 404:
        raise RegraDeNegocioError(f"{descricao} não encontrado.", 404)
    if resposta.status_code != 200:
        raise ErroIntegracao(f"Não foi possível consultar {descricao.lower()}. O serviço {destino} respondeu HTTP {resposta.status_code}.", 502)
    try:
        return resposta.json()
    except ValueError as erro:
        raise ErroIntegracao(f"O serviço {destino} retornou uma resposta inválida.", 502) from erro


def criar(dados):
    try:
        hospede_id = int(dados.get("hospede_id"))
        quarto_id = int(dados.get("quarto_id"))
    except (TypeError, ValueError):
        raise RegraDeNegocioError("Informe hospede_id e quarto_id válidos.")
    entrada = _data(dados.get("data_entrada"), "data_entrada")
    saida = _data(dados.get("data_saida"), "data_saida")
    if saida <= entrada:
        raise RegraDeNegocioError("A data de saída deve ser posterior à data de entrada.")

    _consultar_servico("hospedes", f"/api/hospedes/{hospede_id}", "Hóspede")
    resposta_quarto = integracao.chamar(
        "quartos", "GET", f"/api/quartos/{quarto_id}/disponibilidade",
        params={"data_entrada": entrada.isoformat(), "data_saida": saida.isoformat()},
    )
    if resposta_quarto.status_code == 404:
        raise RegraDeNegocioError("Quarto não encontrado.", 404)
    if resposta_quarto.status_code != 200:
        raise ErroIntegracao(
            f"Não foi possível consultar a disponibilidade do quarto. HTTP {resposta_quarto.status_code}.", 502
        )
    try:
        quarto = resposta_quarto.json()
    except ValueError as erro:
        raise ErroIntegracao("O serviço de quartos retornou uma resposta inválida.", 502) from erro
    if not quarto.get("disponivel"):
        raise RegraDeNegocioError("O quarto está indisponível.")

    conflito = Reserva.query.filter(
        Reserva.quarto_id == quarto_id,
        Reserva.status != "cancelada",
        Reserva.data_entrada < saida,
        Reserva.data_saida > entrada,
    ).first()
    if conflito:
        raise RegraDeNegocioError("Já existe uma reserva para este quarto em datas que se sobrepõem.")

    noites = (saida - entrada).days
    valor_total = round(float(quarto["valor_diaria"]) * noites, 2)
    reserva = Reserva(hospede_id=hospede_id, quarto_id=quarto_id,
                      data_entrada=entrada, data_saida=saida,
                      valor_total=valor_total, status="pendente")
    db.session.add(reserva)
    db.session.commit()
    return reserva


def dados_iniciais():
    # Não cria reservas fictícias que dependam de IDs de outros serviços.
    pass


def listar():
    return Reserva.query.order_by(Reserva.id).all()


def buscar(reserva_id):
    return db.session.get(Reserva, reserva_id)


def atualizar_status(reserva_id, status):
    reserva = buscar(reserva_id)
    if reserva is None:
        return None
    if status not in ("pendente", "confirmada", "cancelada"):
        raise RegraDeNegocioError("Status inválido. Use pendente, confirmada ou cancelada.")
    if reserva.status == "cancelada" and status != "cancelada":
        raise RegraDeNegocioError("Uma reserva cancelada não pode ser reativada.")
    reserva.status = status
    db.session.commit()
    return reserva


def excluir(reserva_id):
    reserva = buscar(reserva_id)
    if reserva is None:
        return False
    db.session.delete(reserva)
    db.session.commit()
    return True
