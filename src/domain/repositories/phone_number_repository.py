from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.phone_number import PhoneNumber


class PhoneNumberRepository(ABC):
    @abstractmethod
    async def create(self, phone_number: PhoneNumber) -> PhoneNumber: ...

    @abstractmethod
    async def get_by_id(self, phone_number_id: UUID) -> PhoneNumber | None: ...

    @abstractmethod
    async def get_all(self) -> list[PhoneNumber]: ...

    @abstractmethod
    async def get_active(self) -> list[PhoneNumber]: ...

    @abstractmethod
    async def update(self, phone_number_id: UUID, **kwargs) -> PhoneNumber | None: ...

    @abstractmethod
    async def delete(self, phone_number_id: UUID) -> bool: ...
