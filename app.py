from flask import Flask, request, jsonify, render_template, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from models import db, Produto, Cesta, ItemCesta

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cesta.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('cadastro.html')

@app.route('/cadastro')
def pagina_cadastro():
    return render_template('cadastro.html')

@app.route('/estoque')
def pagina_estoque():
    return render_template('estoque.html')

@app.route('/montar_cesta')
def pagina_montar_cesta():
    return render_template('montar_cesta.html')

@app.route('/produtos', methods=['GET', 'POST'])
def gerenciar_produtos():
    if request.method == 'POST':
        data = request.get_json()
        produto = Produto(
            descricao=data.get('descricao'),
            marca=data.get('marca'),
            data_compra=data.get('data_compra'),
            data_validade=data.get('data_validade'),
            quantidade=int(data.get('quantidade')),
            valor=float(data.get('valor'))
        )
        db.session.add(produto)
        db.session.commit()
        return jsonify({"mensagem": "Produto cadastrado com sucesso!"}), 201

    elif request.method == 'GET':
        hoje = datetime.now().date()
        resultado = []
        produtos = Produto.query.all()
        for p in produtos:
            validade = datetime.strptime(p.data_validade, "%Y-%m-%d").date()
            dias = (validade - hoje).days
            alerta = dias <= 20
            resultado.append({
                'id': p.id,
                'descricao': p.descricao,
                'marca': p.marca,
                'quantidade': p.quantidade,
                'valor': p.valor,
                'total': p.total(),
                'data_validade': p.data_validade,
                'alerta_vencimento': alerta
            })
        return jsonify(resultado)

@app.route('/api/montar_cesta', methods=['POST'])
def montar_cesta():
    data = request.get_json()
    itens = data.get('itens', [])
    valor_total = 0
    nova_cesta = Cesta()
    db.session.add(nova_cesta)

    for item in itens:
        produto = Produto.query.filter_by(descricao=item['descricao'], marca=item['marca']).first()
        if produto and produto.quantidade >= item['quantidade']:
            produto.quantidade -= item['quantidade']
            total_item = produto.valor * item['quantidade']
            novo_item = ItemCesta(
                cesta=nova_cesta,
                descricao=produto.descricao,
                marca=produto.marca,
                quantidade=item['quantidade'],
                valor_unitario=produto.valor,
                total=total_item
            )
            db.session.add(novo_item)
            valor_total += total_item
        else:
            return jsonify({'erro': f'Estoque insuficiente para {item["descricao"]}'}), 400

    db.session.commit()

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle("Relatório de Cesta")

    pdf.drawString(100, 800, f"Relatório da Cesta - {nova_cesta.data.strftime('%d/%m/%Y %H:%M:%S')}")
    y = 770
    for item in nova_cesta.itens:
        linha = f"{item.descricao} ({item.marca}) - {item.quantidade} x R$ {item.valor_unitario:.2f} = R$ {item.total:.2f}"
        pdf.drawString(50, y, linha)
        y -= 20

    pdf.drawString(50, y - 20, f"Total da Cesta: R$ {valor_total:.2f}")
    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=relatorio_cesta.pdf'
    return response

if __name__ == '__main__':
    app.run(debug=True)
