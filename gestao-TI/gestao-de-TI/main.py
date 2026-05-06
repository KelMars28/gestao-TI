from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'chave_muito_segura_123'

# --- CONFIGURAÇÃO PARA XAMPP (MYSQL) ---
# Certifique-se de ter criado o banco 'gestao_ti' no phpMyAdmin antes de rodar
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/gestao_ti'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELOS ---
class Equipamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patrimonio = db.Column(db.String(20), unique=True, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Disponível')
    valor_compra = db.Column(db.Float, default=0.0)
    historicos = db.relationship('Suporte', backref='equip', lazy=True, cascade="all, delete-orphan")

class Suporte(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_abertura = db.Column(db.DateTime, default=datetime.now)
    problema = db.Column(db.Text, nullable=False)
    tecnico = db.Column(db.String(50))
    solucao = db.Column(db.Text)
    custo = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='Pendente')
    equipamento_id = db.Column(db.Integer, db.ForeignKey('equipamento.id'), nullable=False)

# CRIA AS TABELAS NO XAMPP AUTOMATICAMENTE
with app.app_context():
    db.create_all()

# --- ROTAS DE ACESSO ---
@app.route("/")
def index():
    if 'usuario_logado' in session:
        return redirect(url_for('dashboard'))
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    usuario = request.form.get("nome")
    senha = request.form.get("senha")
    if usuario == "admin" and senha == "admin":
        session['usuario_logado'] = usuario
        return redirect(url_for('dashboard'))
    return render_template("index.html", error="Credenciais inválidas")

@app.route("/logout")
def logout():
    session.clear() 
    return redirect(url_for('index'))

@app.route("/dashboard")
def dashboard():
    if 'usuario_logado' not in session: return redirect(url_for('index'))
    stats = {
        "total": Equipamento.query.count(),
        "em_uso": Equipamento.query.filter_by(status='Em Uso').count(),
        "manutencao": Equipamento.query.filter_by(status='Em Manutenção').count(),
        "disponivel": Equipamento.query.filter_by(status='Disponível').count()
    }
    return render_template("dashboard.html", stats=stats)

# --- ROTAS DE EQUIPAMENTOS ---
@app.route("/equipamentos")
def list_equipamentos():
    termo = request.args.get('search', '')
    filtro_tipo = request.args.get('tipo', '')
    filtro_status = request.args.get('status', '')

    query = Equipamento.query
    if termo:
        query = query.filter((Equipamento.patrimonio.like(f'%{termo}%')) | (Equipamento.marca.like(f'%{termo}%')))
    if filtro_tipo:
        query = query.filter(Equipamento.tipo == filtro_tipo)
    if filtro_status:
        query = query.filter(Equipamento.status == filtro_status)

    lista = query.all()
    marcas_sugestoes = [e.marca for e in Equipamento.query.with_entities(Equipamento.marca).distinct().all()]

    return render_template("list_equipamentos.html", 
                           equipamentos=lista, search=termo, 
                           tipo_selecionado=filtro_tipo, status_selecionado=filtro_status,
                           sugestoes=marcas_sugestoes)

@app.route("/cadastrar", methods=["GET", "POST"])
def cad_equipamento():
    if request.method == "POST":
        novo = Equipamento(
            patrimonio=request.form.get("patrimonio"),
            tipo=request.form.get("tipo"),
            marca=request.form.get("marca"),
            modelo=request.form.get("modelo"),
            valor_compra=float(request.form.get("valor_compra") or 0),
            status=request.form.get("status")
        )
        db.session.add(novo)
        db.session.commit()
        return redirect(url_for('list_equipamentos'))
    return render_template("cad_equipamento.html")

@app.route("/equipamento/<int:id>")
def detalhe_equipamento(id):
    equip = Equipamento.query.get_or_404(id)
    suportes = Suporte.query.filter_by(equipamento_id=id).order_by(Suporte.data_abertura.desc()).all()
    return render_template("detalhe_equipamento.html", equip=equip, suportes=suportes)

@app.route("/equipamento/editar/<int:id>", methods=["GET", "POST"])
def edit_equipamento(id):
    equip = Equipamento.query.get_or_404(id)
    if request.method == "POST":
        equip.patrimonio = request.form.get("patrimonio")
        equip.tipo = request.form.get("tipo")
        equip.marca = request.form.get("marca")
        equip.status = request.form.get("status")
        db.session.commit()
        return redirect(url_for('detalhe_equipamento', id=equip.id))
    return render_template("edit_equipamento.html", equip=equip)

@app.route("/equipamento/excluir/<int:id>")
def delete_equipamento(id):
    equip = Equipamento.query.get_or_404(id)
    db.session.delete(equip)
    db.session.commit()
    return redirect(url_for('list_equipamentos'))

# --- ROTAS DE SUPORTE / CHAMADOS ---

@app.route("/chamados")
def lista_chamados():
    chamados = Suporte.query.filter_by(status='Pendente').order_by(Suporte.data_abertura.desc()).all()
    return render_template("lista_chamados.html", chamados=chamados)

@app.route("/equipamento/abrir-chamado/<int:id>", methods=["POST"])
def abrir_chamado(id):
    equip = Equipamento.query.get_or_404(id)
    novo = Suporte(
        problema=request.form.get("problema"),
        status="Pendente",
        equipamento_id=id
    )
    equip.status = "Em Manutenção"
    db.session.add(novo)
    db.session.commit()
    flash("Chamado enviado com sucesso!", "success")
    return redirect(url_for('detalhe_equipamento', id=id))

# ROTA PARA ABRIR A TELA DE RESOLUÇÃO
@app.route("/suporte/resolver/<int:id_chamado>")
def tela_resolver_chamado(id_chamado):
    chamado = Suporte.query.get_or_404(id_chamado)
    return render_template("novo_suporte.html", chamado=chamado, equip=chamado.equip)

# ROTA PARA SALVAR A RESOLUÇÃO E FINALIZAR
@app.route("/suporte/finalizar/<int:id_chamado>", methods=["POST"])
def finalizar_resolucao(id_chamado):
    chamado = Suporte.query.get_or_404(id_chamado)
    equip = Equipamento.query.get(chamado.equipamento_id)
    
    chamado.tecnico = request.form.get("tecnico")
    chamado.solucao = request.form.get("solucao")
    chamado.custo = float(request.form.get("custo") or 0)
    chamado.status = "Concluído"
    
    equip.status = "Disponível" 
    db.session.commit()
    
    flash("Manutenção finalizada!", "success")
    return redirect(url_for('detalhe_equipamento', id=equip.id))

# --- OUTRAS ROTAS ---

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

@app.route("/contato")
def contato():
    return render_template("contato.html")

if __name__ == "__main__":
    app.run(debug=True, port=5001)