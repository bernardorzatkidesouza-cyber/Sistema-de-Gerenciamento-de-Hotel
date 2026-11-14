from datetime import date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Reserva(db.Model):
    __tablename__ = "reservas"

    id = db.Column(db.Integer, primary_key=True)
    # IDs de outros microsserviços: não usar ForeignKey entre bancos diferentes.
    hospede_id = db.Column(db.Integer, nullable=False)
    quarto_id = db.Column(db.Integer, nullable=False)
    data_entrada = db.Column(db.Date, nullable=False)
    data_saida = db.Column(db.Date, nullable=False)
    valor_total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pendente")

    def para_dict(self):
        return {"id": self.id, "hospede_id": self.hospede_id,
                "quarto_id": self.quarto_id,
                "data_entrada": self.data_entrada.isoformat(),
                "data_saida": self.data_saida.isoformat(),
                "valor_total": self.valor_total, "status": self.status}
