from erros import RegraDeNegocioError
from models import Hospede, db


def criar(dados):
    campos = {k: (dados.get(k) or "").strip() for k in ("nome", "cpf", "telefone", "email", "endereco")}
    faltando = [k for k, v in campos.items() if not v]
    if faltando:
        raise RegraDeNegocioError("Campos obrigatórios: " + ", ".join(faltando) + ".")
    if Hospede.query.filter_by(cpf=campos["cpf"]).first():
        raise RegraDeNegocioError("Já existe um hóspede cadastrado com este CPF.")
    if Hospede.query.filter_by(email=campos["email"]).first():
        raise RegraDeNegocioError("Já existe um hóspede cadastrado com este e-mail.")
    hospede = Hospede(**campos)
    db.session.add(hospede)
    db.session.commit()
    return hospede


def dados_iniciais():
    if Hospede.query.count() == 0:
        db.session.add(Hospede(nome="João da Silva", cpf="00000000000", telefone="48999990000", email="joao@exemplo.com", endereco="Rua Central, 100"))
        db.session.commit()


def listar():
    return Hospede.query.order_by(Hospede.id).all()


def buscar(hospede_id):
    return db.session.get(Hospede, hospede_id)


def atualizar(hospede_id, dados):
    hospede = buscar(hospede_id)
    if hospede is None:
        return None
    for campo in ("nome", "cpf", "telefone", "email", "endereco"):
        if campo in dados:
            valor = (dados.get(campo) or "").strip()
            if not valor:
                raise RegraDeNegocioError(f"O campo '{campo}' não pode ficar vazio.")
            outro = Hospede.query.filter(getattr(Hospede, campo) == valor, Hospede.id != hospede_id).first()
            if outro:
                raise RegraDeNegocioError(f"O campo '{campo}' já está cadastrado.")
            setattr(hospede, campo, valor)
    db.session.commit()
    return hospede


def excluir(hospede_id):
    hospede = buscar(hospede_id)
    if hospede is None:
        return False
    db.session.delete(hospede)
    db.session.commit()
    return True
