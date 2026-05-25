import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
# Chave secreta necessária para gerir as sessões e mensagens flash
app.secret_key = os.environ.get("SECRET_KEY", "troque-esta-chave-em-producao")

# ── CONFIGURAÇÃO DE E-MAIL (FLASK-MAIL) ───────────────────────────────────────
app.config["MAIL_SERVER"]         = os.environ.get("MAIL_SERVER",   "smtp.gmail.com")
app.config["MAIL_PORT"]           = int(os.environ.get("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"]        = True
app.config["MAIL_USERNAME"]       = os.environ.get("MAIL_USERNAME", "comcatraiodeluz@gmail.com")

# ⚠️ ATENÇÃO: Substitui as letras abaixo pelas 16 letras da Senha de App que vais gerar na Google
app.config["MAIL_PASSWORD"]       = os.environ.get("MAIL_PASSWORD", "fnmn nlxm cuai plnv") 
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_USERNAME", "comcatraiodeluz@gmail.com")

mail = Mail(app)

# ── CONFIGURAÇÃO DO FLASK-LOGIN (CONTROLO DE ACESSO) ──────────────────────────
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para aceder a esta página.'

# Classe simples para o utilizador administrador
class Usuario(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id == "admin":
        return Usuario("admin")
    return None

# Lista na memória do computador para guardar as mensagens enviadas e exibi-las no Painel Admin
MENSAGENS_DB = []

# ── DADOS DA ORGANIZAÇÃO ───────────────────────────────────────────────────────
ORG = {
    "nome": "Raio de Luz",
    "slogan": "Unidos pela fé, movidos pelo amor",
    "missao": "Evangelizar com criatividade e amor, levando esperança a cada coração.",
    "visao": "Ser uma comunidade de referência, formando pessoas transformadas pelo Evangelho.",
    "email": "comcatraiodeluz@gmail.com",
    "telefone": "+55 (45) 99955-0227",
    "endereco": "Av. Roberto Fachini , 377 — Toledo, PR",
    "instagram": "https://instagram.com/comunidaderaiodeluz",
    "youtube": "https://youtube.com/@raiodeltuz",
}

MINISTERIOS = [
    {"icone": "🙏", "nome": "Oração", "descricao": "Grupos de oração que se reúnem semanalmente para adorar e interceder."},
    {"icone": "👨‍👩‍👧", "nome": "Família", "descricao": "Acompanhamento e fortalecimento das famílias em sua vocação."},
    {"icone": "🎵", "nome": "Música & Arte", "descricao": "Evangelização através da música, teatro e expressões artísticas."},
    {"icone": "📖", "nome": "Formação", "descricao": "Cursos, retiros e encontros para crescimento espiritual e humano."},
    {"icone": "🌍", "nome": "Missão", "descricao": "Equipes missionárias que levam a fé para além das fronteiras."},
    {"icone": "👶", "nome": "Infância & Juventude", "descricao": "Espaços especiais para crianças, adolescentes e jovens."},
 ]

# Lista de Eventos estruturada com ID para permitir a edição no painel administrativo
EVENTOS = [
    {
        "id": 1, 
        "titulo": "NENHUM EVENTO NO MOMENTO", 
        "data": "A definir", 
        "descricao": "Fique atento às nossas redes sociais para acompanhar os próximos eventos da comunidade."
    }
]

# ── ROTAS PÚBLICAS DO SITE ────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html", org=ORG, ministerios=MINISTERIOS, eventos=EVENTOS)

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

        if not nome or not email or not message:
            flash("Por favor, preencha todos os campos.", "erro")
        else:
            # 1. Guarda a mensagem localmente para que apareça no painel admin do site
            MENSAGENS_DB.append({
                "nome": nome, 
                "email": email, 
                "mensagem": mensagem, 
                "assunto": "Nova Mensagem do Site"
            })
            
            # 2. Tenta enviar por e-mail real utilizando o Flask-Mail
            try:
                # E-mail com a mensagem para a administração da comunidade
                msg = Message(
                    subject=f"[{ORG['nome']}] Nova mensagem de {nome}",
                    recipients=[ORG["email"]],
                    body=f"Nome: {nome}\nE-mail: {email}\n\nMensagem:\n{mensagem}",
                )
                mail.send(msg)

                # E-mail automático de confirmação para o utilizador que enviou
                confirmacao = Message(
                    subject=f"Recebemos sua mensagem — {ORG['nome']}",
                    recipients=[email],
                    body=f"Olá, {nome}!\n\nRecebemos sua mensagem e entraremos em contato em breve.\n\nEquipe {ORG['nome']}",
                )
                mail.send(confirmacao)

                flash("Mensagem enviada com sucesso! Você receberá uma confirmação por e-mail.", "sucesso")
                return redirect(url_for("contato"))

            except Exception as e:
                app.logger.error(f"Erro ao enviar e-mail: {e}")
                # Avisa que a mensagem foi guardada no painel, apesar de o e-mail ter falhado devido à senha
                flash("Guardamos a sua mensagem no painel do site, mas houve um problema temporário com o servidor de e-mail.", "sucesso")
                return redirect(url_for("contato"))

    return render_template("contato.html", org=ORG)

# ── ROTAS DE AUTENTICAÇÃO E PAINEL ADMINISTRATIVO ─────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Dados de acesso padrão do teu site
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
    # Passa também a lista de eventos para poder ser gerenciada no admin.html
    return render_template('admin.html', org=ORG, mensagens=MENSAGENS_DB, eventos=EVENTOS)

@app.route("/admin/evento/editar/<int:evento_id>", methods=["POST"])
@login_required
def editar_evento(evento_id):
    novo_titulo = request.form.get("titulo", "").strip()
    nova_data = request.form.get("data", "").strip()
    nova_descricao = request.form.get("descricao", "").strip()
    
    # Procura o evento na lista global e altera os dados
    for ev in EVENTOS:
        if ev.get("id") == evento_id:
            ev["titulo"] = novo_titulo
            ev["data"] = nova_data
            ev["descricao"] = nova_descricao
            break
            
    flash("Evento atualizado com sucesso!", "sucesso")
    return redirect(url_for("admin_dashboard"))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == "__main__":
    # Lê a porta que a Render oferece ou usa a 5000 por padrão se for no PC
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta)