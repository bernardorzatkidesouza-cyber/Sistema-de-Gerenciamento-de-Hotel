"""Regras de negócio. Aqui ficam as decisões do serviço (sem Flask, sem rotas)."""
from erros import RegraDeNegocioError
from models import Registro, db


def criar(dados):
    nome = (dados.get("nome") or "").strip()
    if not nome:
        raise RegraDeNegocioError("O campo 'nome' é obrigatório.")
    registro = Registro(nome=nome)
    db.session.add(registro)
    db.session.commit()
    return registro


def dados_iniciais():
    """Cria um registro de exemplo se o banco estiver vazio.

    No Render gratuito o arquivo .db é apagado quando o serviço reinicia ou hiberna;
    por isso o serviço recria os dados de exemplo sempre que acorda.
    TROQUE pelos dados de exemplo do seu domínio.
    """
    if Registro.query.count() == 0:
        db.session.add(Registro(nome="Exemplo inicial"))
        db.session.commit()


def listar():
    return Registro.query.order_by(Registro.id).all()


def buscar(registro_id):
    return db.session.get(Registro, registro_id)


def atualizar(registro_id, dados):
    registro = buscar(registro_id)
    if registro is None:
        return None
    nome = (dados.get("nome") or "").strip()
    if not nome:
        raise RegraDeNegocioError("O campo 'nome' é obrigatório.")
    registro.nome = nome
    db.session.commit()
    return registro


def inativar(registro_id):
    registro = buscar(registro_id)
    if registro is None:
        return None
    if not registro.ativo:
        raise RegraDeNegocioError("O registro já está inativo.")
    registro.ativo = False
    db.session.commit()
    return registro


# TODO (integração): quando uma regra precisar de dados de outro serviço,
# importe o módulo integracao e use a função chamar(). Exemplo comentado:
#
# import integracao
# resposta = integracao.chamar("SERVICO2", "GET", "/api/registros/1/ativo")
# if not resposta.json()["ativo"]:
#     raise RegraDeNegocioError("O registro do outro serviço está inativo.")
