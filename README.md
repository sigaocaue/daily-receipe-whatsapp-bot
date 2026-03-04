# Daily Recipe WhatsApp Bot

API backend em Python que envia receitas culinárias diárias via WhatsApp.

## Funcionalidades

- Geração automática de receitas via IA (OpenAI GPT-4o)
- Envio de receitas com imagem via WhatsApp (Twilio API)
- CRUD completo de proteínas, receitas e números de telefone
- Histórico de mensagens enviadas
- Seleção inteligente de receitas (evita repetição das últimas 5)
- Imagens ilustrativas via Unsplash API

## Tecnologias

- **Python 3.13** + **FastAPI**
- **PostgreSQL** + **SQLAlchemy** (async)
- **Alembic** para migrations
- **OpenAI GPT-4o** para geração de receitas
- **Twilio** para envio via WhatsApp
- **Unsplash API** para imagens
- **Poetry** para gerenciamento de dependências

## Pré-requisitos

- Python 3.13+
- PostgreSQL
- `pipx` e `poetry` instalados
- Conta na Twilio (sandbox WhatsApp configurado)
- Chave da API OpenAI
- Chave da API Unsplash

## Como executar

### 1. Instalar dependências

```bash
poetry install
```

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Editar .env com suas credenciais reais
```

### 3. Criar banco de dados e rodar migrations

```bash
createdb daily_recipe_db
poetry run alembic upgrade head
```

### 4. Popular dados iniciais

```bash
poetry run python -m src.infrastructure.database.seed
```

### 5. Iniciar a aplicação

```bash
poetry run uvicorn src.presentation.main:app --reload --port 8000
```

### 6. Acessar a documentação

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints principais

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/health` | Health check |
| POST | `/api/v1/recipes/generate` | Gera receita via IA |
| POST | `/api/v1/messages/send` | Envia receita via WhatsApp |
| GET | `/api/v1/proteins` | Lista proteínas |
| GET | `/api/v1/recipes` | Lista receitas |
| GET | `/api/v1/phone-numbers` | Lista números |
| GET | `/api/v1/messages/logs` | Histórico de envios |

## Testes

```bash
poetry run pytest
```

## Gerar requirements.txt

```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

Consulte [SETUP.md](SETUP.md) para instruções detalhadas de configuração.
