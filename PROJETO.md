# Daily Recipe WhatsApp Bot — Instruções Completas do Projeto

## OBJETIVO

Crie uma aplicação backend em Python que envia uma receita culinária diferente por dia para o WhatsApp, com as seguintes características avançadas.

---

## COMPORTAMENTO DO ASSISTENTE

- Todas as respostas, explicações e perguntas de esclarecimento devem ser em **português brasileiro (pt-BR)**, independentemente do idioma usado na pergunta;
- Todo o código-fonte, nomes de variáveis, funções, comentários, arquivos e estrutura de pastas devem estar em **inglês**.

---

## CONTEXTO E OBJETIVOS

- Projeto pessoal cujo objetivo é enviar receitas diárias personalizadas via WhatsApp;
- As mensagens devem ser enviadas para números de telefone cadastrados no banco de dados (o número inicial é `+5511975408216`). Se houver mais de um número, enviar para todos;
- As mensagens do WhatsApp devem ser enviadas pela **API do Twilio**;
- O projeto será uma **API Python backend** usando **FastAPI**;
- Banco de dados: **PostgreSQL** (mais robusto, gratuito e amplamente suportado em cloud);
- A aplicação **DEVE usar IA (OpenAI GPT-4o)** para pesquisar e gerar a receita automaticamente. Após obter a receita, ela é cadastrada no banco de dados. Isso ocorre ao chamar um endpoint específico;
- Ao chamar outro endpoint específico, a aplicação busca uma receita no banco e envia para os números cadastrados;
- O sistema deve gravar data/hora, mensagem e receita enviada no banco de dados;
- O sistema deve enviar uma receita **diferente das últimas 5 receitas enviadas**;
- As receitas devem ser baseadas em **proteínas cadastradas no banco de dados**;
- Cada mensagem deve conter **UMA IMAGEM ilustrativa** da receita (usar URL de imagem pública pesquisada via IA ou Unsplash API);
- As receitas devem ser reais e referenciadas em sites como TudoGostoso, Panelinha, etc.;
- As mensagens devem ser **carinhosas e pessoais** (ex: "Bom dia, amor! A receita de hoje é...");
- O projeto deve ter arquivo `.env.example` com exemplos de todas as variáveis de ambiente;
- O sistema deve ter **sistema de logging** configurado;
- Deve ser criado um arquivo `SETUP.md` com instruções de configuração;
- Deve ser criado um arquivo `README.md` com instruções de como executar o projeto.

---

## FERRAMENTAS DE GERENCIAMENTO DO PROJETO

- O projeto usa **pipx** e **Poetry** para gerenciamento de dependências e ambiente virtual;
- O Poetry deve ser instalado via pipx: `pipx install poetry`;
- Presume-se que o usuário já tem `pipx` e `poetry` instalados no sistema;
- O arquivo `pyproject.toml` é a fonte de verdade das dependências do projeto;
- O arquivo `requirements.txt` deve ser mantido e gerado via `poetry export`, para compatibilidade com plataformas de deploy que não suportam Poetry diretamente:
  ```bash
  poetry export -f requirements.txt --output requirements.txt --without-hashes
  ```
- O arquivo `.python-version` deve existir na raiz do projeto, contendo a versão exata do Python usada (ex: `3.13.2`). Esse arquivo é o padrão reconhecido pelo **pyenv** e respeitado automaticamente pelo Poetry.

---

## ESTRUTURA DE PASTAS (Clean Architecture + DDD)

```
daily-recipe-whatsapp-bot/
├── src/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── recipe.py
│   │   │   ├── protein.py
│   │   │   ├── phone_number.py
│   │   │   └── message_log.py
│   │   ├── repositories/
│   │   │   ├── recipe_repository.py
│   │   │   ├── protein_repository.py
│   │   │   ├── phone_number_repository.py
│   │   │   └── message_log_repository.py
│   │   └── services/
│   │       ├── recipe_service.py
│   │       └── whatsapp_service.py
│   ├── application/
│   │   ├── use_cases/
│   │   │   ├── generate_recipe_use_case.py
│   │   │   ├── send_recipe_use_case.py
│   │   │   ├── create_protein_use_case.py
│   │   │   └── list_recipes_use_case.py
│   │   └── dtos/
│   │       ├── recipe_dto.py
│   │       ├── protein_dto.py
│   │       └── message_dto.py
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── connection.py
│   │   │   ├── models/
│   │   │   │   ├── recipe_model.py
│   │   │   │   ├── protein_model.py
│   │   │   │   ├── phone_number_model.py
│   │   │   │   └── message_log_model.py
│   │   │   └── repositories/
│   │   │       ├── sqlalchemy_recipe_repository.py
│   │   │       ├── sqlalchemy_protein_repository.py
│   │   │       ├── sqlalchemy_phone_number_repository.py
│   │   │       └── sqlalchemy_message_log_repository.py
│   │   ├── ai/
│   │   │   └── openai_recipe_generator.py
│   │   └── messaging/
│   │       └── twilio_whatsapp_service.py
│   ├── presentation/
│   │   ├── api/
│   │   │   ├── routers/
│   │   │   │   ├── recipe_router.py
│   │   │   │   ├── protein_router.py
│   │   │   │   ├── phone_number_router.py
│   │   │   │   └── message_router.py
│   │   │   └── schemas/
│   │   │       ├── recipe_schema.py
│   │   │       ├── protein_schema.py
│   │   │       └── phone_number_schema.py
│   │   └── main.py
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── tests/
│   ├── unit/
│   └── integration/
├── config.py
├── pyproject.toml
├── requirements.txt
├── .python-version
├── .env.example
├── .env
├── alembic.ini
├── SETUP.md
└── README.md
```

---

## BANCO DE DADOS — MODELOS E RELACIONAMENTOS

### Tabela: `proteins`
```sql
- id (UUID, PK)
- name (VARCHAR, unique, not null) — ex: "frango", "carne moída", "salmão"
- active (BOOLEAN, default true)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

### Tabela: `recipes`
```sql
- id (UUID, PK)
- title (VARCHAR, not null)
- ingredients (TEXT, not null) — resumo dos ingredientes
- instructions (TEXT, not null) — modo de preparo
- source_url (VARCHAR) — URL da receita no site original
- image_url (VARCHAR) — URL da imagem ilustrativa
- source_site (VARCHAR) — ex: "TudoGostoso", "Panelinha"
- ai_generated (BOOLEAN, default true)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

### Tabela: `recipe_proteins` (tabela de junção N:N)
```sql
- recipe_id (UUID, FK → recipes.id)
- protein_id (UUID, FK → proteins.id)
- PRIMARY KEY (recipe_id, protein_id)
```

### Tabela: `phone_numbers`
```sql
- id (UUID, PK)
- name (VARCHAR) — ex: "Esposa"
- phone (VARCHAR, unique, not null) — formato E.164: +5511975408216
- active (BOOLEAN, default true)
- created_at (TIMESTAMP)
```

### Tabela: `message_logs`
```sql
- id (UUID, PK)
- recipe_id (UUID, FK → recipes.id)
- phone_number_id (UUID, FK → phone_numbers.id)
- message_content (TEXT) — mensagem completa enviada
- sent_at (TIMESTAMP)
- status (VARCHAR) — "sent", "failed", "pending"
- twilio_message_sid (VARCHAR) — ID retornado pela Twilio
- error_message (TEXT, nullable)
```

---

## ENDPOINTS DA API

### Proteínas (CRUD completo)
```
POST   /api/v1/proteins           — Cadastrar nova proteína
GET    /api/v1/proteins           — Listar todas as proteínas
GET    /api/v1/proteins/{id}      — Buscar proteína por ID
PATCH  /api/v1/proteins/{id}      — Atualizar proteína
DELETE /api/v1/proteins/{id}      — Deletar proteína
```

### Receitas (CRUD completo)
```
POST   /api/v1/recipes            — Cadastrar receita manualmente
GET    /api/v1/recipes            — Listar todas as receitas
GET    /api/v1/recipes/{id}       — Buscar receita por ID
PATCH  /api/v1/recipes/{id}       — Atualizar receita
DELETE /api/v1/recipes/{id}       — Deletar receita
```

### Números de Telefone (CRUD completo)
```
POST   /api/v1/phone-numbers      — Cadastrar número
GET    /api/v1/phone-numbers      — Listar números
GET    /api/v1/phone-numbers/{id} — Buscar por ID
PATCH  /api/v1/phone-numbers/{id} — Atualizar
DELETE /api/v1/phone-numbers/{id} — Deletar
```

### Ações Principais
```
POST   /api/v1/recipes/generate   — Gera receita via IA e salva no banco
         Body: { "protein_ids": ["uuid1", "uuid2"] }  (opcional; se não informado, escolhe proteína ativa aleatória)

POST   /api/v1/messages/send      — Busca receita do banco e envia via WhatsApp para todos os números ativos
         Response: { "sent_to": [...], "recipe": {...}, "status": "sent" }
```

### Logs
```
GET    /api/v1/messages/logs      — Listar histórico de mensagens enviadas
GET    /api/v1/messages/logs/{id} — Detalhe de uma mensagem
```

### Health Check
```
GET    /health                    — Verifica se a aplicação está no ar
```

---

## LÓGICA DE GERAÇÃO DE RECEITA (IA)

Ao chamar `POST /api/v1/recipes/generate`:

1. Selecionar uma proteína ativa aleatória do banco (ou usar a informada no body);
2. Buscar **todas** as receitas já cadastradas no banco para evitar repetição e duplicação;
3. Montar prompt para o GPT-4o com:
   - Proteína selecionada
   - Títulos de todas as receitas cadastradas (para evitar repetição)
   - Instrução para retornar JSON estruturado com: título, ingredientes resumidos, modo de preparo, URL de referência (site real como TudoGostoso/Panelinha), nome do site fonte
4. Chamar a OpenAI API com `response_format: json_object`;
5. Buscar imagem ilustrativa via **Unsplash API** usando o nome da receita como query;
6. Salvar receita no banco com os relacionamentos de proteína;
7. Retornar a receita criada.

**Prompt modelo para GPT-4o:**
```
Você é um assistente culinário especializado em receitas brasileiras.

Gere uma receita real e deliciosa usando a proteína: {protein_name}.
Não gere as receitas a seguir: {existing_recipes}.

Retorne SOMENTE um JSON válido com esta estrutura:
{
  "title": "Nome da Receita",
  "ingredients": "Lista resumida dos ingredientes principais",
  "instructions": "Modo de preparo detalhado mas conciso",
  "source_url": "https://www.tudogostoso.com.br/receita/...",
  "source_site": "TudoGostoso"
}

A receita deve existir em sites reais como TudoGostoso, Panelinha, Receitas de Minuto, etc.
```

---

## LÓGICA DE ENVIO DE MENSAGEM

Ao chamar `POST /api/v1/messages/send`:

1. Buscar os últimos 5 IDs de receitas enviadas no `message_logs`;
2. Buscar uma receita do banco que **não** esteja nessa lista (ORDER BY RANDOM(), LIMIT 1);
3. Se não encontrar receita disponível, retornar erro 404 com mensagem clara;
4. Buscar todos os números de telefone ativos (`active = true`);
5. Para cada número, montar a mensagem carinhosa e enviar via Twilio;
6. Gravar cada envio no `message_logs`;
7. Retornar resumo do envio.

**Formato da mensagem:**
```
Bom dia, meu amor! 💕

Hoje preparei uma receita especial com *{PROTEÍNA}* para você:

🍽️ *{Título da Receita}* (fonte: {source_site})

Ingredientes:
{ingredientes}

Modo de preparo:
{instruções}

Beijos e bom apetite! 🥘
Para mais detalhes: {source_url}
```

> A imagem deve ser enviada como **Media URL** no Twilio (campo `media_url` com a `image_url` da receita).

---

## CONFIGURAÇÃO (`config.py`)

```python
# config.py deve:
# 1. Importar e carregar o .env usando python-dotenv
# 2. Validar que todas as variáveis obrigatórias existem (levantar erro claro se faltar)
# 3. Expor uma instância de Settings usando Pydantic BaseSettings

# Variáveis obrigatórias:
# DATABASE_URL, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN,
# TWILIO_WHATSAPP_FROM, OPENAI_API_KEY, UNSPLASH_ACCESS_KEY
```

---

## ARQUIVO `.env.example`

```env
# Banco de Dados
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/daily_recipe_db

# Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Unsplash (para imagens das receitas)
UNSPLASH_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# App
APP_ENV=development
LOG_LEVEL=INFO
```

---

## ARQUIVO `.python-version`

```
3.13.2
```

> Este arquivo é o padrão reconhecido pelo **pyenv** e respeitado automaticamente pelo Poetry. Garante que todos os desenvolvedores e ambientes de CI/CD usem a mesma versão do Python.

---

## DEPENDÊNCIAS (`pyproject.toml`)

O projeto usa **Poetry** para gerenciamento de dependências. O `pyproject.toml` deve ser configurado com:

```toml
[tool.poetry]
name = "daily-recipe-whatsapp-bot"
version = "0.1.0"
description = "API backend que envia receitas culinárias diárias via WhatsApp"
authors = ["Your Name <you@example.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.13"
fastapi = ">=0.115.0"
uvicorn = {extras = ["standard"], version = ">=0.30.0"}
sqlalchemy = {extras = ["asyncio"], version = ">=2.0.0"}
asyncpg = ">=0.29.0"
alembic = ">=1.13.0"
pydantic = ">=2.7.0"
pydantic-settings = ">=2.3.0"
python-dotenv = ">=1.0.0"
twilio = ">=9.0.0"
openai = ">=1.40.0"
httpx = ">=0.27.0"
python-multipart = ">=0.0.9"

[tool.poetry.group.dev.dependencies]
pytest = ">=8.0.0"
pytest-asyncio = ">=0.23.0"
httpx = ">=0.27.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

O `requirements.txt` deve ser gerado e mantido atualizado via:
```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

---

## SISTEMA DE LOGGING

- Usar o módulo `logging` do Python com configuração centralizada;
- Nível configurável via variável de ambiente `LOG_LEVEL`;
- Formato: `%(asctime)s | %(levelname)s | %(name)s | %(message)s`;
- Logar: início e fim de cada request, erros de envio Twilio, respostas da OpenAI, queries lentas;
- Criar um módulo `src/infrastructure/logging/logger.py` com a configuração centralizada.

---

## ARQUIVO `SETUP.md` (a ser criado dentro do projeto)

O arquivo `SETUP.md` deve conter instruções detalhadas para os passos abaixo. Presume-se que o usuário já tem `pipx` e `poetry` instalados.

### 1. Criar conta na Twilio e obter credenciais
- Acessar https://www.twilio.com e criar conta gratuita
- Copiar `Account SID` e `Auth Token` do dashboard
- Localizar o número Twilio para WhatsApp Sandbox

### 2. Configurar Sandbox do WhatsApp
- Acessar Twilio Console → Messaging → Try it out → Send a WhatsApp message
- Enviar mensagem de opt-in do celular destino para o número sandbox da Twilio
- Copiar o número sandbox (ex: `whatsapp:+14155238886`) para o `.env`

### 3. Instalar dependências
```bash
poetry install
```

### 4. Configurar arquivo `.env`
```bash
cp .env.example .env
# Editar .env com suas credenciais reais
```

### 5. Criar banco de dados e rodar migrations
```bash
# Criar banco PostgreSQL
createdb daily_recipe_db

# Rodar migrations
poetry run alembic upgrade head
```

### 6. Popular dados iniciais
```bash
# Rodar o script de seed
poetry run python -m src.infrastructure.database.seed
```

### 7. Subir a aplicação
```bash
poetry run uvicorn src.presentation.main:app --reload --port 8000
```

### 8. (Opcional) Gerar requirements.txt para deploy
```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

---

## DADOS INICIAIS (seed)

Após rodar as migrations, a aplicação deve ter um script `src/infrastructure/database/seed.py` que cadastra:

**Proteínas iniciais:**
- Frango
- Carne moída de patinho
- Carne moída de coxão duro
- Salmão
- Atum
- Bife Patinho
- Bife Contra Filé

**Número inicial:**
- Nome: "Sara (esposa)", Telefone: `+5511975408216`, Ativo: true

---

## OBSERVAÇÕES FINAIS

- Usar `async/await` em toda a stack (FastAPI async, SQLAlchemy async, httpx async);
- Usar `UUID` como tipo de PK em todas as tabelas;
- Todas as respostas da API devem seguir o padrão `{ "data": ..., "message": "..." }`;
- Tratar erros com `HTTPException` e retornar mensagens claras;
- O código deve estar em **inglês** (variáveis, funções, comentários);
- Documentação automática disponível em `/docs` (Swagger UI) e `/redoc`;
- Incluir `health check` em `GET /health`.
