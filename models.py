from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    data_compra = db.Column(db.String(10), nullable=False)
    data_validade = db.Column(db.String(10), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.Float, nullable=False)

    def total(self):
        return self.quantidade * self.valor

class Cesta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    itens = db.relationship('ItemCesta', backref='cesta', lazy=True)

class ItemCesta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cesta_id = db.Column(db.Integer, db.ForeignKey('cesta.id'), nullable=False)
    descricao = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    valor_unitario = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
