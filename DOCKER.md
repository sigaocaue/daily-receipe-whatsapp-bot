# Docker — Instruções de Containerização

## COMPORTAMENTO DO ASSISTENTE

- Todas as respostas, explicações e perguntas de esclarecimento devem ser em **português brasileiro (pt-BR)**, independentemente do idioma usado na pergunta;
- Todo o código-fonte, nomes de variáveis, funções, comentários, arquivos e estrutura de pastas devem estar em **inglês**.

---

## OBJETIVO

Containerizar a aplicação `daily-recipe-whatsapp-bot` usando Docker e orquestrar os serviços do ambiente local com `docker-compose.yml`.

---

## ARQUIVOS A CRIAR

- `Dockerfile` — para buildar a imagem da aplicação FastAPI
- `docker-compose.yml` — para orquestrar todos os serviços locais
- `.dockerignore` — para excluir arquivos desnecessários da imagem

---

## DOCKERFILE

O `Dockerfile` deve:

- Usar como base a imagem oficial `python:3.14.3-slim`;
- Instalar o Poetry dentro da imagem via pipx;
- Copiar apenas os arquivos necessários (`pyproject.toml`, `poetry.lock`, `src/`, `config.py`, `alembic.ini`, `migrations/`);
- Instalar as dependências via `poetry install --no-root --no-dev`;
- Expor a porta `8000`;
- Usar `uvicorn` como entrypoint:
  ```
  uvicorn src.presentation.main:app --host 0.0.0.0 --port 8000
  ```

---

## DOCKER-COMPOSE

O `docker-compose.yml` deve orquestrar os seguintes serviços:

### `app`
- Build a partir do `Dockerfile` local;
- Porta: `8000:8000`;
- Depende de: `db`;
- Carrega variáveis do arquivo `.env`;
- Restart: `unless-stopped`.

### `db` (PostgreSQL)
- Imagem: `postgres:16-alpine`;
- Porta: `5432:5432`;
- Variáveis de ambiente:
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_DB`
- Volume persistente para os dados: `.persistence/postgres:/var/lib/postgresql/data`;
- Restart: `unless-stopped`.

---

## `.dockerignore`

Deve ignorar:
```
.env
.git
.venv
__pycache__
*.pyc
*.pyo
*.egg-info
.pytest_cache
tests/
.python-version
```

---

## VARIÁVEIS DE AMBIENTE

O `docker-compose.yml` deve carregar as variáveis do arquivo `.env` já existente no projeto. O `DATABASE_URL` deve apontar para o serviço `db` interno do compose:

```env
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/daily_recipe_db
```

> Atenção: no ambiente local sem Docker, o host é `localhost`. Com Docker Compose, o host deve ser o nome do serviço: `db`.

---

## OBSERVAÇÕES FINAIS

- Não execute nenhum comando Docker, `alembic upgrade head` ou seed. Apenas crie os arquivos;
- O `poetry.lock` deve ser gerado localmente antes do build (`poetry lock`);
- Adicionar ao `README.md` e ao `SETUP.md` uma seção explicando como subir o ambiente com Docker:
  ```bash
  docker-compose up --build
  ```