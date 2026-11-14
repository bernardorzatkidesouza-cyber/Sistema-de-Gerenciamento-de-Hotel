from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Pagamento(db.Model):
    __tablename__ = "pagamentos"

    id = db.Column(db.Integer, primary_key=True)
    # ID da reserva pertence a outro microsserviço; não usar ForeignKey.
    id_reserva = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    forma_pagamento = db.Column(db.String(30), nullable=False)
    data_pagamento = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="aprovado")

    def para_dict(self):
        return {"id": self.id, "id_reserva": self.id_reserva, "valor": self.valor,
                "forma_pagamento": self.forma_pagamento,
                "data_pagamento": self.data_pagamento.isoformat(timespec="seconds") + "Z",
                "status": self.status}
