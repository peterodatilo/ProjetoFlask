from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import sqlite3
app = Flask(__name__)
app.secret_key = 'minha_senha30*10'


# Configuração do banco (SQLite local)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///matriculas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo da tabela
class Matricula(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    curso = db.Column(db.String(80), nullable=False)

# Criar banco/tabelas ao iniciar a aplicação
with app.app_context():
    db.create_all()
    print("\n>>> Banco de dados criado/checado com sucesso!\n")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/matricula', methods=['GET', 'POST'])
def matricula():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        curso = request.form.get('curso')

        nova = Matricula(nome=nome, email=email, curso=curso)
        db.session.add(nova)

        try:
            db.session.commit()
            print(f"\n✔ SALVO: {nome} | {email} | {curso}\n")
        except Exception as e:
            db.session.rollback()
            print("\n❌ ERRO:", e, "\n")

        return redirect(url_for('sucesso'))

    return render_template('matricula.html')

@app.route('/sucesso')
def sucesso():
    return render_template('sucesso.html')

@app.route('/lista')
def lista():
    if not session.get('logado'):
        return redirect(url_for('login'))
    matriculas = Matricula.query.all()
    return render_template('lista.html', matriculas=matriculas)

@app.route('/excluir/<int:id>')
def excluir(id):
    if not session.get('logado'):
        return redirect(url_for('login'))
    aluno = Matricula.query.get(id)
    if aluno:
        db.session.delete(aluno)
        db.session.commit()
    return redirect(url_for('lista'))

@app.route('/logout')
def logout():
    session.pop('logado', None)
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')

        if usuario == 'admin' and senha == '123':  # Você pode trocar isso depois
            session['logado'] = True
            return redirect(url_for('lista'))
        else:
            return render_template('login.html', erro="Usuário ou senha incorretos!")

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logado'):
        return redirect(url_for('login'))

    total = Matricula.query.count()
    eng = Matricula.query.filter_by(curso="Engenharia de Software").count()
    cc = Matricula.query.filter_by(curso="Ciência da Computação").count()
    si = Matricula.query.filter_by(curso="Sistemas de Informação").count()

    return render_template(
        'dashboard.html',
        total=total,
        eng=eng,
        cc=cc,
        si=si
    )


@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    aluno = Matricula.query.get(id)

    if not aluno:
        return "Matrícula não encontrada."

    if request.method == "POST":
        aluno.nome = request.form["nome"]
        aluno.email = request.form["email"]
        aluno.curso = request.form["curso"]
        db.session.commit()
        return redirect(url_for("lista"))

    return render_template("editar.html", matricula=aluno)

if __name__ == "__main__":
    print("\n🚀 Iniciando servidor Flask...\n")
    app.run(host="0.0.0.0")
