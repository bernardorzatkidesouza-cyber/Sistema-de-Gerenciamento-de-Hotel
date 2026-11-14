from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Quarto(db.Model):
    __tablename__ = "quartos"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, unique=True, nullable=False)
    tipo = db.Column(db.String(40), nullable=False)
    capacidade = db.Column(db.Integer, nullable=False)
    valor_diaria = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="disponivel")

    def para_dict(self):
        return {"id": self.id, "numero": self.numero, "tipo": self.tipo,
                "capacidade": self.capacidade, "valor_diaria": self.valor_diaria,
                "status": self.status}
