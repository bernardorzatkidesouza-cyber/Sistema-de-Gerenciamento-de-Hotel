from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Hospede(db.Model):
    __tablename__ = "hospedes"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    endereco = db.Column(db.String(200), nullable=False)

    def para_dict(self):
        return {"id": self.id, 
                "nome": self.nome, 
                "cpf": self.cpf,
                "telefone": self.telefone, 
                "email": self.email, 
                "endereco": self.endereco}
