# Clean Architecture - Daily Recipe WhatsApp Bot

## Visao Geral

Este projeto segue os principios da **Clean Architecture** (Arquitetura Limpa), proposta por Robert C. Martin (Uncle Bob). A ideia central e que as regras de negocio ficam isoladas de frameworks, bancos de dados e servicos externos. As dependencias sempre apontam para dentro — ou seja, camadas externas conhecem as internas, mas nunca o contrario.

```
┌─────────────────────────────────────────────────────────┐
│                   Presentation Layer                    │
│              (FastAPI, routers, schemas)                │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │              Application Layer                  │    │
│  │           (use cases, DTOs)                     │    │
│  │                                                 │    │
│  │  ┌─────────────────────────────────────────┐    │    │
│  │  │           Domain Layer                  │    │    │
│  │  │  (entities, repositories*, services*)   │    │    │
│  │  │        * interfaces apenas              │    │    │
│  │  └─────────────────────────────────────────┘    │    │
│  │                                                 │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│                  Infrastructure Layer                   │
│          (SQLAlchemy, OpenAI, Twilio, etc.)             │
└─────────────────────────────────────────────────────────┘
```

**Regra de dependencia:** As setas de import sempre apontam para o centro. A camada Domain nao importa nada das outras camadas.

---

## Estrutura de Pastas

```
src/
├── domain/                          # Camada de Dominio (nucleo)
│   ├── entities/                    # Entidades de negocio
│   │   ├── recipe.py                # Entidade Recipe
│   │   ├── protein.py               # Entidade Protein
│   │   ├── phone_number.py          # Entidade PhoneNumber
│   │   └── message_log.py           # Entidade MessageLog
│   ├── repositories/                # Interfaces (contratos) de repositorios
│   │   ├── recipe_repository.py     # ABC com metodos CRUD para Recipe
│   │   ├── protein_repository.py    # ABC com metodos CRUD para Protein
│   │   ├── phone_number_repository.py
│   │   └── message_log_repository.py
│   └── services/                    # Interfaces de servicos de dominio
│       ├── recipe_service.py        # ABC para geracao de receitas (IA)
│       └── whatsapp_service.py      # ABC para envio de mensagens
│
├── application/                     # Camada de Aplicacao (casos de uso)
│   ├── dtos/                        # Data Transfer Objects
│   │   ├── recipe_dto.py            # CreateRecipeDTO, GenerateRecipeDTO
│   │   ├── protein_dto.py           # CreateProteinDTO
│   │   └── message_dto.py           # SendMessageDTO
│   └── use_cases/                   # Casos de uso (orquestracao)
│       ├── generate_recipe_use_case.py  # Gera receita via IA
│       ├── send_recipe_use_case.py      # Envia receita via WhatsApp
│       ├── list_recipes_use_case.py     # Lista receitas existentes
│       └── create_protein_use_case.py   # Cadastra nova proteina
│
├── infrastructure/                  # Camada de Infraestrutura (implementacoes)
│   ├── database/
│   │   ├── connection.py            # Engine e session do SQLAlchemy
│   │   ├── seed.py                  # Dados iniciais (seed)
│   │   ├── models/                  # Modelos SQLAlchemy (ORM)
│   │   │   ├── recipe_model.py
│   │   │   ├── protein_model.py
│   │   │   ├── phone_number_model.py
│   │   │   └── message_log_model.py
│   │   └── repositories/            # Implementacoes concretas dos repositorios
│   │       ├── sqlalchemy_recipe_repository.py
│   │       ├── sqlalchemy_protein_repository.py
│   │       ├── sqlalchemy_phone_number_repository.py
│   │       └── sqlalchemy_message_log_repository.py
│   ├── ai/
│   │   └── openai_recipe_generator.py   # Implementa RecipeGeneratorService (OpenAI)
│   ├── messaging/
│   │   └── twilio_whatsapp_service.py   # Implementa WhatsAppService (Twilio)
│   └── logging/
│       └── logger.py                    # Configuracao de logs
│
├── presentation/                    # Camada de Apresentacao (API)
│   ├── main.py                      # Ponto de entrada do FastAPI
│   └── api/
│       ├── routers/                 # Endpoints REST
│       │   ├── recipe_router.py
│       │   ├── protein_router.py
│       │   ├── phone_number_router.py
│       │   └── message_router.py
│       └── schemas/                 # Schemas Pydantic (request/response)
│           ├── recipe_schema.py
│           ├── protein_schema.py
│           ├── phone_number_schema.py
│           ├── message_schema.py
│           └── response_schema.py   # ApiResponse generico
│
config.py                            # Configuracoes (variaveis de ambiente)
migrations/                          # Migrations do Alembic
tests/                               # Testes
```

---

## Descricao de Cada Camada

### 1. Domain (Dominio)

A camada mais interna. Contem a logica de negocio pura, sem nenhuma dependencia de framework ou biblioteca externa.

**`entities/`** — Dataclasses que representam os conceitos centrais do negocio:

```python
@dataclass
class Recipe:
    title: str
    ingredients: str
    instructions: str
    id: UUID = field(default_factory=uuid4)
    # ...
```

**`repositories/`** — Interfaces abstratas (ABCs) que definem os contratos de persistencia. A camada de dominio nao sabe _como_ os dados sao salvos — apenas _o que_ precisa ser feito:

```python
class RecipeRepository(ABC):
    @abstractmethod
    async def create(self, recipe: Recipe) -> Recipe: ...

    @abstractmethod
    async def get_by_id(self, recipe_id: UUID) -> Recipe | None: ...
```

**`services/`** — Interfaces abstratas para servicos externos que o dominio precisa (geracao de receitas, envio de mensagens):

```python
class RecipeGeneratorService(ABC):
    @abstractmethod
    async def generate_recipe(self, protein_name: str, existing_recipe_titles: list[str]) -> Recipe: ...
```

### 2. Application (Aplicacao)

Orquestra as entidades e servicos do dominio para executar processos de negocio completos.

Use cases (ou Application Services no DDD) representam as ações que o sistema pode executar. Pensa assim: uma ação = algo que um usuário (ou o sistema) quer fazer.

**Exemplos por domínio**

**E-commerce**
- `PlaceOrder` — cliente finaliza uma compra
- `CancelOrder` — cliente cancela um pedido
- `ApplyDiscountCoupon` — aplica cupom antes de pagar
- `ProcessRefund` — devolve dinheiro após cancelamento

**Blog / CMS**
- `PublishPost` — autor publica um rascunho
- `AddComment` — leitor comenta num post
- `ModerateComment` — admin aprova ou rejeita comentário
- `ArchivePost` — move post para arquivo

**Sistema bancário**
- `TransferMoney` — transfere entre contas
- `PayBill` — paga uma conta
- `BlockCard` — bloqueia cartão por suspeita de fraude
- `GenerateStatement` — gera extrato do período

**Teu projeto (daily-recipe-whatsapp-bot)**
- `SendDailyRecipe` — sistema envia receita do dia via WhatsApp
- `CreateRecipe` — admin cadastra uma receita nova
- `ScheduleRecipe` — admin agenda qual receita vai para qual dia
- `AddSubscriber` — cadastra número que vai receber as receitas
- `UnsubscribeUser` — remove número da lista de envio

**`use_cases/`** — Cada use case tem uma unica responsabilidade. Recebe dependencias por injecao no construtor e um DTO no metodo `execute()`:

```python
class GenerateRecipeUseCase:
    def __init__(
        self,
        recipe_repository: RecipeRepository,       # interface
        protein_repository: ProteinRepository,      # interface
        recipe_generator: RecipeGeneratorService,   # interface
    ):
        self._recipe_repo = recipe_repository
        self._protein_repo = protein_repository
        self._recipe_generator = recipe_generator

    async def execute(self, dto: GenerateRecipeDTO) -> Recipe:
        # 1. Busca proteinas
        # 2. Seleciona aleatoriamente
        # 3. Gera receita via IA
        # 4. Salva no banco
        # 5. Retorna entidade
```

**`dtos/`** — Data Transfer Objects. Servem como contrato de entrada para os use cases, desacoplando a API da logica interna:

```python
@dataclass
class CreateRecipeDTO:
    title: str
    ingredients: str
    instructions: str
    # ...
```

### 3. Infrastructure (Infraestrutura)

Implementa as interfaces definidas no dominio usando tecnologias concretas.

**`database/models/`** — Modelos SQLAlchemy que mapeiam tabelas do banco. Sao diferentes das entidades de dominio:

```python
class RecipeModel(Base):
    __tablename__ = "recipes"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    # ... relacionamentos ORM
```

**`database/repositories/`** — Implementacoes concretas dos repositorios. Fazem a conversao entre Model (banco) e Entity (dominio):

```python
class SQLAlchemyRecipeRepository(RecipeRepository):
    def _to_entity(self, model: RecipeModel) -> Recipe:
        return Recipe(id=model.id, title=model.title, ...)

    async def create(self, recipe: Recipe) -> Recipe:
        model = RecipeModel(id=recipe.id, title=recipe.title, ...)
        self._session.add(model)
        await self._session.commit()
        return self._to_entity(model)
```

**`ai/`** — Implementacao do servico de IA (OpenAI) que gera receitas.

**`messaging/`** — Implementacao do servico de mensagens (Twilio/WhatsApp).

### 4. Presentation (Apresentacao)

Camada mais externa. Lida com HTTP, validacao de request/response e roteamento.

**`api/schemas/`** — Schemas Pydantic para validacao de entrada e formatacao de saida da API:

```python
class RecipeCreate(BaseModel):
    title: str
    ingredients: str
    # ...

class RecipeResponse(BaseModel):
    id: UUID
    title: str
    # ...
```

**`api/routers/`** — Endpoints FastAPI. Instanciam repositorios, criam use cases e delegam a execucao:

```python
@router.post("", response_model=ApiResponse[RecipeResponse], status_code=201)
async def create_recipe(body: RecipeCreate, session: AsyncSession = Depends(get_session)):
    repo = SQLAlchemyRecipeRepository(session)
    use_case = CreateRecipeUseCase(repo)
    recipe = await use_case.execute(CreateRecipeDTO(title=body.title, ...))
    return {"data": _recipe_response(recipe), "message": "Recipe created"}
```

**`api/schemas/response_schema.py`** — Wrapper generico para respostas padronizadas:

```python
class ApiResponse(BaseModel, Generic[T]):
    data: T
    message: str
```

---

## Fluxo de uma Requisicao

Exemplo: `POST /recipes/generate`

```
1. Cliente envia request HTTP
         │
         ▼
2. Router (presentation) recebe e valida o body via schema Pydantic
         │
         ▼
3. Router instancia repositorios e servicos (infrastructure)
         │
         ▼
4. Router cria o UseCase injetando as dependencias
         │
         ▼
5. Router converte schema → DTO e chama use_case.execute(dto)
         │
         ▼
6. UseCase (application) orquestra:
   a. Busca proteinas no repositorio
   b. Chama servico de IA para gerar receita
   c. Salva receita no repositorio
   d. Retorna entidade Recipe
         │
         ▼
7. Router converte entidade → schema de response
         │
         ▼
8. FastAPI serializa e retorna JSON ao cliente
```

---

## Como Criar um Novo Endpoint (Passo a Passo)

Vamos usar como exemplo a criacao de um CRUD para uma entidade `Category`.

### Passo 1: Criar a Entidade (Domain)

Arquivo: `src/domain/entities/category.py`

```python
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Category:
    name: str
    description: str | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
```

### Passo 2: Criar a Interface do Repositorio (Domain)

Arquivo: `src/domain/repositories/category_repository.py`

```python
from abc import ABC, abstractmethod
from uuid import UUID
from src.domain.entities.category import Category


class CategoryRepository(ABC):
    @abstractmethod
    async def create(self, category: Category) -> Category: ...

    @abstractmethod
    async def get_by_id(self, category_id: UUID) -> Category | None: ...

    @abstractmethod
    async def get_all(self) -> list[Category]: ...
```

### Passo 3: Criar o DTO (Application)

Arquivo: `src/application/dtos/category_dto.py`

```python
from dataclasses import dataclass


@dataclass
class CreateCategoryDTO:
    name: str
    description: str | None = None
```

### Passo 4: Criar o Use Case (Application)

Arquivo: `src/application/use_cases/create_category_use_case.py`

```python
from src.domain.entities.category import Category
from src.domain.repositories.category_repository import CategoryRepository
from src.application.dtos.category_dto import CreateCategoryDTO


class CreateCategoryUseCase:
    def __init__(self, repository: CategoryRepository):
        self._repository = repository

    async def execute(self, dto: CreateCategoryDTO) -> Category:
        category = Category(name=dto.name, description=dto.description)
        return await self._repository.create(category)
```

### Passo 5: Criar o Model do Banco (Infrastructure)

Arquivo: `src/infrastructure/database/models/category_model.py`

```python
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from src.infrastructure.database.connection import Base


class CategoryModel(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

### Passo 6: Criar o Repositorio Concreto (Infrastructure)

Arquivo: `src/infrastructure/database/repositories/sqlalchemy_category_repository.py`

```python
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.entities.category import Category
from src.domain.repositories.category_repository import CategoryRepository
from src.infrastructure.database.models.category_model import CategoryModel


class SQLAlchemyCategoryRepository(CategoryRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: CategoryModel) -> Category:
        return Category(
            id=model.id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
        )

    async def create(self, category: Category) -> Category:
        model = CategoryModel(
            id=category.id,
            name=category.name,
            description=category.description,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, category_id: UUID) -> Category | None:
        result = await self._session.execute(
            select(CategoryModel).where(CategoryModel.id == category_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_all(self) -> list[Category]:
        result = await self._session.execute(select(CategoryModel))
        return [self._to_entity(m) for m in result.scalars().all()]
```

### Passo 7: Criar os Schemas da API (Presentation)

Arquivo: `src/presentation/api/schemas/category_schema.py`

```python
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    description: str | None = None


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
```

### Passo 8: Criar o Router (Presentation)

Arquivo: `src/presentation/api/routers/category_router.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.connection import get_session
from src.infrastructure.database.repositories.sqlalchemy_category_repository import (
    SQLAlchemyCategoryRepository,
)
from src.application.use_cases.create_category_use_case import CreateCategoryUseCase
from src.application.dtos.category_dto import CreateCategoryDTO
from src.presentation.api.schemas.category_schema import CategoryCreate, CategoryResponse
from src.presentation.api.schemas.response_schema import ApiResponse

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("", response_model=ApiResponse[CategoryResponse], status_code=201)
async def create_category(
    body: CategoryCreate,
    session: AsyncSession = Depends(get_session),
):
    repo = SQLAlchemyCategoryRepository(session)
    use_case = CreateCategoryUseCase(repo)
    category = await use_case.execute(
        CreateCategoryDTO(name=body.name, description=body.description)
    )
    return {
        "data": CategoryResponse(
            id=category.id,
            name=category.name,
            description=category.description,
            created_at=category.created_at,
        ),
        "message": "Category created",
    }
```

### Passo 9: Registrar o Router no FastAPI

Arquivo: `src/presentation/main.py`

```python
from src.presentation.api.routers.category_router import router as category_router

app.include_router(category_router)
```

### Passo 10: Criar a Migration

```bash
alembic revision --autogenerate -m "add categories table"
alembic upgrade head
```

---

## Checklist para Novos Endpoints

- [ ] **Domain**: Entidade criada em `domain/entities/`
- [ ] **Domain**: Interface de repositorio criada em `domain/repositories/`
- [ ] **Domain** (se necessario): Interface de servico criada em `domain/services/`
- [ ] **Application**: DTO criado em `application/dtos/`
- [ ] **Application**: Use case criado em `application/use_cases/`
- [ ] **Infrastructure**: Model SQLAlchemy criado em `infrastructure/database/models/`
- [ ] **Infrastructure**: Repositorio concreto criado em `infrastructure/database/repositories/`
- [ ] **Infrastructure** (se necessario): Servico externo implementado em `infrastructure/`
- [ ] **Presentation**: Schema Pydantic criado em `presentation/api/schemas/`
- [ ] **Presentation**: Router criado em `presentation/api/routers/`
- [ ] **Presentation**: Router registrado em `presentation/main.py`
- [ ] **Migration**: Criada e aplicada via Alembic
- [ ] **Exportar** nos `__init__.py` de cada pasta (quando aplicavel)

---

## Principios Importantes

### Inversao de Dependencia
O dominio define **interfaces** (ABCs). A infraestrutura **implementa** essas interfaces. O use case recebe as interfaces por **injecao de dependencia** no construtor. Isso permite trocar implementacoes sem alterar a logica de negocio (ex: trocar OpenAI por Claude, trocar PostgreSQL por MongoDB).

### Separacao Entity vs Model
Entidades de dominio (`Recipe`) sao **diferentes** dos modelos de banco (`RecipeModel`). A conversao acontece no repositorio via `_to_entity()`. Isso garante que mudancas no schema do banco nao afetem a logica de negocio.

### Separacao Schema vs DTO vs Entity
- **Schema** (Pydantic): validacao HTTP, vive na camada de apresentacao
- **DTO** (dataclass): contrato de entrada do use case, vive na camada de aplicacao
- **Entity** (dataclass): conceito de negocio, vive na camada de dominio

Cada um tem seu proprio ciclo de vida e pode evoluir independentemente.

### Um Use Case, Uma Responsabilidade
Cada use case faz **uma coisa**. `GenerateRecipeUseCase` gera receita. `SendRecipeUseCase` envia receita. Nao misture responsabilidades.

### Testes
A Clean Architecture facilita testes unitários: basta criar mocks das interfaces de repositorio/servico e testar os use cases isoladamente, sem banco de dados ou APIs externas.

---

## Erros Comuns a Evitar

1. **Importar infraestrutura no dominio** — A camada domain nunca deve importar SQLAlchemy, FastAPI, Pydantic, etc.
2. **Usar entidades de dominio como response da API** — Sempre converta para schemas Pydantic.
3. **Colocar logica de negocio no router** — O router apenas converte dados e delega ao use case.
4. **Criar use cases que fazem muita coisa** — Quebre em use cases menores.
5. **Pular o DTO e passar o schema direto ao use case** — Isso acopla a API ao use case.
