from datetime import datetime
import integracao
from erros import ErroIntegracao, RegraDeNegocioError
from models import Pagamento, db


def criar(dados):
    try:
        reserva_id = int(dados.get("id_reserva"))
        valor = float(dados.get("valor"))
    except (TypeError, ValueError):
        raise RegraDeNegocioError("Informe id_reserva e valor válidos.")
    forma = (dados.get("forma_pagamento") or "").strip().lower()
    if valor <= 0:
        raise RegraDeNegocioError("O valor do pagamento deve ser maior que zero.")
    if forma not in ("pix", "cartao", "dinheiro"):
        raise RegraDeNegocioError("Forma de pagamento inválida. Use pix, cartao ou dinheiro.")
    if Pagamento.query.filter_by(id_reserva=reserva_id, status="aprovado").first():
        raise RegraDeNegocioError("Já existe um pagamento aprovado para esta reserva.", 409)

    # Registra o pagamento aprovado e solicita ao serviço de reservas a confirmação.
    # O próprio PUT responde 404 se a reserva não existir. Assim, esta é a única
    # chamada entre pagamentos e reservas, conforme a integração definida na ficha.

    pagamento = Pagamento(id_reserva=reserva_id, valor=valor, forma_pagamento=forma,
                          data_pagamento=datetime.utcnow(), status="aprovado")
    db.session.add(pagamento)
    db.session.commit()

    # Terceira integração: após registrar o pagamento, confirma a reserva.
    try:
        resposta_update = integracao.chamar(
            "reservas", "PUT", f"/api/reservas/{reserva_id}/status",
            json={"status": "confirmada", "valor_pago": valor},
        )
        if resposta_update.status_code in (400, 404, 409):
            # A reserva recusou a confirmação (não existe, já confirmada, cancelada
            # ou valor diferente do total): repassa a mensagem do serviço de reservas.
            try:
                mensagem = resposta_update.json().get("erro")
            except ValueError:
                mensagem = None
            raise RegraDeNegocioError(
                (mensagem or "A reserva não pôde ser confirmada.") + " O pagamento foi desfeito.",
                resposta_update.status_code,
            )
        if resposta_update.status_code != 200:
            raise ErroIntegracao(
                f"O serviço de reservas não confirmou a atualização (HTTP {resposta_update.status_code}).",
                502,
            )
    except Exception as erro:
        # Compensação: remove o pagamento local se a reserva não foi atualizada.
        try:
            db.session.delete(pagamento)
            db.session.commit()
        except Exception as erro_compensacao:
            db.session.rollback()
            raise ErroIntegracao(
                f"Falha ao atualizar a reserva e também ao desfazer o pagamento {pagamento.id}. "
                "É necessária correção manual.", 500
            ) from erro_compensacao
        if isinstance(erro, (RegraDeNegocioError, ErroIntegracao)):
            raise
        raise ErroIntegracao("A atualização da reserva falhou. O pagamento foi desfeito.", 502) from erro

    return pagamento


def dados_iniciais():
    # Não cria pagamento fictício, pois depende de uma reserva existente.
    pass


def listar():
    return Pagamento.query.order_by(Pagamento.id).all()


def buscar(pagamento_id):
    return db.session.get(Pagamento, pagamento_id)


def excluir(pagamento_id):
    pagamento = buscar(pagamento_id)
    if pagamento is None:
        return False
    db.session.delete(pagamento)
    db.session.commit()
    return True
