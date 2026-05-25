# Site Institucional — Flask

Site institucional completo com back-end em Python/Flask.

## Estrutura do Projeto

```
site_institucional/
├── app.py                  # Aplicação principal Flask
├── requirements.txt        # Dependências Python
├── templates/
│   ├── base.html           # Layout base (nav + footer)
│   ├── index.html          # Página inicial
│   ├── sobre.html          # Sobre nós
│   ├── ministerios.html    # Ministérios
│   ├── eventos.html        # Eventos
│   └── contato.html        # Contato (com formulário)
└── static/
    ├── css/
    │   └── style.css       # Estilos do site
    └── js/
        └── main.js         # Scripts (menu mobile, animações)
```

## Como rodar

### 1. Crie um ambiente virtual (recomendado)
```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Rode o servidor
```bash
python app.py
```

Acesse em: **http://localhost:5000**

---

## Personalização

Edite as variáveis no topo do `app.py`:

```python
ORG = {
    "nome": "Nome da sua organização",
    "slogan": "Seu slogan aqui",
    ...
}

MINISTERIOS = [...]   # Seus ministérios/serviços
EVENTOS = [...]       # Sua agenda
```

## Para produção

Use um servidor WSGI como **Gunicorn**:

```bash
pip install gunicorn
gunicorn app:app
```

Para envio real de e-mail no formulário de contato, integre o **Flask-Mail**:

```bash
pip install flask-mail
```

Configure no `app.py`:
```python
from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'seu@email.com'
app.config['MAIL_PASSWORD'] = 'sua-senha-de-app'
mail = Mail(app)
```
