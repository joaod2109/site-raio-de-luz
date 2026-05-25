import os
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "troque-esta-chave-em-producao")

# ── CONFIGURAÇÃO DE E-MAIL ───────────────────────────────────────────────────
app.config["MAIL_SERVER"]         = os.environ.get("MAIL_SERVER",   "smtp.gmail.com")
app.config["MAIL_PORT"]           = int(os.environ.get("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"]        = True
app.config["MAIL_USERNAME"]       = os.environ.get("MAIL_USERNAME", "comcatraiodeluz@gmail.com")
app.config["MAIL_PASSWORD"]       = os.environ.get("MAIL_PASSWORD", "fnmn nlxm cuai plnv") 
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_USERNAME", "comcatraiodeluz@gmail.com")

mail = Mail(app)

# ── CONFIGURAÇÃO DO FLASK-LOGIN ──────────────────────────────────────────────
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class Usuario(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id == "admin":
        return Usuario("admin")
    return None

MENSAGENS_DB = []
ORACAO_DB = []

ORG = {
    "nome": "Raio de Luz",
    "slogan": "Unidos pela fé, movidos pelo amor",
    "missao": "Evangelizar com criatividade e amor, levando esperança a cada coração.",
    "visao": "Ser uma comunidade de referência, formando pessoas transformadas pelo Evangelho.",
    "email": "comcatraiodeluz@gmail.com",
    "telefone": "+55 (45) 99955-0227",
    "endereco": "Comunidade 100% Online — Onde você estiver!",
    "instagram": "https://instagram.com/comunidaderaiodeluz",
    "youtube": "https://youtube.com/@raiodeltuz",
    "id_video_ao_vivo": "HlG5T7FGHng"
}

MINISTERIOS = [
    {"icone": "🙏", "nome": "Oração", "descricao": "Grupos de oração que se reúnem semanalmente para adorar e interceder."},
    {"icone": "👨‍👩‍👧", "nome": "Família", "descricao": "Acompanhamento e fortalecimento das famílias em sua vocação."},
    {"icone": "🎵", "nome": "Música & Arte", "descricao": "Evangelização através da música, teatro e expressões artísticas."},
    {"icone": "📖", "nome": "Formação", "descricao": "Cursos, retiros e encontros para crescimento espiritual e humano."},
    {"icone": "🌍", "nome": "Missão", "descricao": "Equipes missionárias que levam a fé para além das fronteiras."},
    {"icone": "👶", "nome": "Infância & Juventude", "descricao": "Espaços especiais para crianças, adolescentes e jovens."},
]

# GRUPOS ONLINE INICIAIS
GRUPOS_ONLINE = [
    {"id": 1, "nome": "Conexão Jovem", "dia_nome": "Terça-feira", "dia_semana": 1, "horario": "20:00", "lider": "Lucas & Sara", "link": "https://meet.google.com/abc-defg-hij"},
    {"id": 2, "nome": "Célula Famílias", "dia_nome": "Quinta-feira", "dia_semana": 3, "horario": "19:30", "lider": "Roberto & Maria", "link": "https://zoom.us/j/123456789"},
]

EVENTOS = [
    {
        "id": 1, 
        "titulo": "NENHUM EVENTO NO MOMENTO", 
        "data": "A definir", 
        "descricao": "Fique atento às nossas redes sociais para acompanhar os próximos eventos da comunidade."
    }
]

# Função auxiliar para garantir o dia da semana correto no fuso horário do Brasil (UTC-3)
def obter_dia_semana_brasil():
    fuso_brasil = timezone(timedelta(hours=-3))
    return datetime.now(fuso_brasil).weekday()

# ── ROTAS PÚBLICAS DO SITE ────────────────────────────────────────────────────
@app.route("/")
def index():
    dia_hoje = obter_dia_semana_brasil()
    return render_template("index.html", org=ORG, ministerios=MINISTERIOS, eventos=EVENTOS, grupos=GRUPOS_ONLINE, dia_hoje=dia_hoje)

@app.route("/sobre")
def sobre():
    return render_template("sobre.html", org=ORG)

@app.route("/ministerios")
def ministerios():
    return render_template("ministerios.html", org=ORG, ministerios=MINISTERIOS)

@app.route("/eventos")
def eventos():
    return render_template("eventos.html", org=ORG, eventos=EVENTOS)

@app.route("/contato", methods=["GET", "POST"])
def contato():
    if request.method == "POST":
        nome     = request.form.get("nome", "").strip()
        email    = request.form.get("email", "").strip()
        mensagem = request.form.get("mensagem", "").strip()

        if not nome or not email or not mensagem:
            flash("Por favor, preencha todos os campos.", "erro")
        else:
            MENSAGENS_DB.append({"nome": nome, "email": email, "mensagem": mensagem, "assunto": "Nova Mensagem do Site"})
            try:
                msg = Message(subject=f"[{ORG['nome']}] Nova mensagem de {nome}", recipients=[ORG["email"]], body=f"Nome: {nome}\nE-mail: {email}\n\nMensagem:\n{mensagem}")
                mail.send(msg)
                flash("Mensagem enviada com sucesso!", "sucesso")
                return redirect(url_for("contato"))
            except Exception as e:
                flash("Guardamos a sua mensagem no painel do site, mas o servidor de e-mail falhou.", "sucesso")
                return redirect(url_for("contato"))
    return render_template("contato.html", org=ORG)

@app.route("/oracao", methods=["GET", "POST"])
def oracao():
    if request.method == "POST":
        nome = request.form.get("nome", "Anónimo").strip() or "Anónimo"
        pedido = request.form.get("pedido", "").strip()
        if not pedido:
            flash("Por favor, escreva o seu pedido de oração.", "erro")
        else:
            ORACAO_DB.append({"nome": nome, "pedido": pedido})
            flash("O seu pedido de oração foi recebido!", "sucesso")
            return redirect(url_for("oracao"))
    return render_template("oracao.html", org=ORG)

# ── PAINEL ADMINISTRATIVO ─────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'Luz123@Comunidade':
            user = Usuario('admin')
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Usuário ou senha incorretos.', 'erro')
    return render_template('login.html', org=ORG)

@app.route('/admin')
@login_required
def admin_dashboard():
    return render_template('admin.html', org=ORG, mensagens=MENSAGENS_DB, eventos=EVENTOS, oracoes=ORACAO_DB, grupos=GRUPOS_ONLINE)

@app.route("/admin/evento/editar/<int:evento_id>", methods=["POST"])
@login_required
def editar_evento(evento_id):
    for ev in EVENTOS:
        if ev.get("id") == evento_id:
            ev["titulo"] = request.form.get("titulo", "").strip()
            ev["data"] = request.form.get("data", "").strip()
            ev["descricao"] = request.form.get("descricao", "").strip()
            break
    flash("Evento atualizado com sucesso!", "sucesso")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/grupo/editar/<int:grupo_id>", methods=["POST"])
@login_required
def editar_grupo(grupo_id):
    for gp in GRUPOS_ONLINE:
        if gp.get("id") == group_id or gp.get("id") == grupo_id:
            gp["nome"] = request.form.get("nome", "").strip()
            gp["lider"] = request.form.get("lider", "").strip()
            gp["horario"] = request.form.get("horario", "").strip()
            gp["dia_nome"] = request.form.get("dia_nome", "").strip()
            gp["dia_semana"] = int(request.form.get("dia_semana"))
            gp["link"] = request.form.get("link", "").strip()
            break
    flash("Grupo online atualizado com sucesso!", "sucesso")
    return redirect(url_for("admin_dashboard"))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta)