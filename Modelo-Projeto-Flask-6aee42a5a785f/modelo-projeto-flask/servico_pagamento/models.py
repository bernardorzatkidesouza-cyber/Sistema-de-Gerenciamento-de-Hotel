from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Registro(db.Model):
    """TROQUE o nome e os campos pelo assunto do seu serviço.

    Exemplo: no serviço de residências, a classe vira Residencia
    e os campos viram numero, rua, ativa...
    """
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # Para guardar a referência a algo de OUTRO serviço, use só um número
    # (sem ForeignKey), por exemplo:
    # morador_id = db.Column(db.Integer, nullable=True)

    def para_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "ativo": self.ativo,
            "criado_em": self.criado_em.isoformat(timespec="seconds"),
        }
