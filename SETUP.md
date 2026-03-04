# Guia de Configuração — Daily Recipe WhatsApp Bot

Guia detalhado para configurar e rodar o projeto do zero. Presume-se que o usuário já tem `pipx` e `poetry` instalados.

---

## 1. Criar conta na Twilio e obter credenciais

1. Acesse https://www.twilio.com e crie uma conta gratuita
2. No Dashboard da Twilio, copie o **Account SID** e o **Auth Token**
3. Localize o número Twilio para WhatsApp Sandbox

---

## 2. Configurar Sandbox do WhatsApp

1. No Twilio Console, vá em **Messaging → Try it out → Send a WhatsApp message**
2. Envie a mensagem de opt-in do celular destino para o número sandbox da Twilio (geralmente `+14155238886`)
3. A mensagem de ativação será algo como: `join <palavra-chave>`
4. Copie o número sandbox no formato `whatsapp:+14155238886` para usar no `.env`

---

## 3. Obter chave da API OpenAI

1. Acesse https://platform.openai.com/api-keys
2. Crie uma nova chave de API
3. Copie a chave (formato `sk-...`) para usar no `.env`

---

## 4. Obter chave da API Unsplash

1. Acesse https://unsplash.com/developers
2. Crie uma nova aplicação
3. Copie o **Access Key** para usar no `.env`

---

## 5. Instalar dependências

```bash
poetry install
```

---

## 6. Configurar arquivo `.env`

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais reais:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/daily_recipe_db
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
UNSPLASH_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
APP_ENV=development
LOG_LEVEL=INFO
```

---

## 7. Criar banco de dados e rodar migrations

```bash
# Rodar migrations dentro do container do banco de dados
docker exec -it sigaocaue_daily_receipe_app poetry run alembic upgrade head
```

---

## 8. Popular dados iniciais

```bash
docker exec -it sigaocaue_daily_receipe_app poetry run python -m src.infrastructure.database.seed
```

Isso irá cadastrar:
- 7 proteínas iniciais (Frango, Carne moída de patinho, etc.)
- 1 número de telefone inicial (Sara)

---

## 9. Subir a aplicação

```bash
poetry run uvicorn src.presentation.main:app --reload --port 8000
```

A API estará disponível em:
- http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 10. (Alternativa) Subir com Docker

Se preferir usar Docker em vez de instalar tudo localmente:

```bash
# Configurar .env (se ainda não fez)
cp .env.example .env
# Editar .env com suas credenciais reais

# Subir todos os serviços
docker-compose up --build
```

O Docker Compose irá:
- Criar e iniciar o banco PostgreSQL automaticamente
- Buildar a imagem da aplicação com todas as dependências
- Iniciar a API na porta `8000`

A API estará disponível em:
- http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

> **Nota:** No ambiente Docker, o `DATABASE_URL` é sobrescrito para apontar ao serviço `db` interno do Compose. As demais variáveis são carregadas do `.env`.

---

## 11. (Opcional) Gerar requirements.txt para deploy

```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```
