from erros import RegraDeNegocioError
from models import Quarto, db


def _validar(dados, parcial=False):
    obrigatorios = ("numero", "tipo", "capacidade", "valor_diaria", "status")
    if not parcial:
        faltando = [c for c in obrigatorios if c not in dados]
        if faltando:
            raise RegraDeNegocioError("Campos obrigatórios: " + ", ".join(faltando) + ".")
    numero = dados.get("numero")
    capacidade = dados.get("capacidade")
    valor = dados.get("valor_diaria")
    try:
        if numero is not None and int(numero) <= 0:
            raise RegraDeNegocioError("O número do quarto deve ser positivo.")
        if capacidade is not None and int(capacidade) <= 0:
            raise RegraDeNegocioError("A capacidade deve ser maior que zero.")
        if valor is not None and float(valor) <= 0:
            raise RegraDeNegocioError("O valor da diária deve ser maior que zero.")
    except (TypeError, ValueError):
        raise RegraDeNegocioError("Número, capacidade e valor da diária devem ser numéricos.")
    if "status" in dados and dados["status"] not in ("disponivel", "indisponivel"):
        raise RegraDeNegocioError("O status deve ser 'disponivel' ou 'indisponivel'.")


def criar(dados):
    _validar(dados)
    numero = int(dados["numero"])
    if Quarto.query.filter_by(numero=numero).first():
        raise RegraDeNegocioError("Já existe um quarto com este número.")
    quarto = Quarto(numero=numero, tipo=str(dados["tipo"]).strip(), capacidade=int(dados["capacidade"]),
                    valor_diaria=float(dados["valor_diaria"]), status=dados["status"])
    if not quarto.tipo:
        raise RegraDeNegocioError("O tipo do quarto é obrigatório.")
    db.session.add(quarto)
    db.session.commit()
    return quarto


def dados_iniciais():
    if Quarto.query.count() == 0:
        db.session.add_all([
            Quarto(numero=101, tipo="simples", capacidade=1, valor_diaria=150.0, status="disponivel"),
            Quarto(numero=102, tipo="duplo", capacidade=2, valor_diaria=220.0, status="disponivel"),
            Quarto(numero=201, tipo="suite", capacidade=3, valor_diaria=350.0, status="disponivel"),
        ])
        db.session.commit()


def listar():
    return Quarto.query.order_by(Quarto.numero).all()


def buscar(quarto_id):
    return db.session.get(Quarto, quarto_id)


def disponibilidade(quarto_id):
    quarto = buscar(quarto_id)
    if quarto is None:
        return None
    return {"id": quarto.id, "numero": quarto.numero, "tipo": quarto.tipo,
            "capacidade": quarto.capacidade, "valor_diaria": quarto.valor_diaria,
            "disponivel": quarto.status == "disponivel", "status": quarto.status}


def atualizar(quarto_id, dados):
    quarto = buscar(quarto_id)
    if quarto is None:
        return None
    _validar(dados, parcial=True)
    if "numero" in dados:
        numero = int(dados["numero"])
        outro = Quarto.query.filter(Quarto.numero == numero, Quarto.id != quarto_id).first()
        if outro:
            raise RegraDeNegocioError("Já existe outro quarto com este número.")
        quarto.numero = numero
    if "tipo" in dados:
        quarto.tipo = str(dados["tipo"]).strip()
        if not quarto.tipo:
            raise RegraDeNegocioError("O tipo do quarto é obrigatório.")
    if "capacidade" in dados: quarto.capacidade = int(dados["capacidade"])
    if "valor_diaria" in dados: quarto.valor_diaria = float(dados["valor_diaria"])
    if "status" in dados: quarto.status = dados["status"]
    db.session.commit()
    return quarto


def excluir(quarto_id):
    quarto = buscar(quarto_id)
    if quarto is None:
        return False
    db.session.delete(quarto)
    db.session.commit()
    return True
