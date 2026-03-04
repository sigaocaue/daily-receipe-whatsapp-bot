from uuid import UUID

from src.domain.entities.phone_number import PhoneNumber
from src.domain.entities.protein import Protein
from src.domain.entities.recipe import Recipe


def test_protein_creation():
    protein = Protein(name="Frango")
    assert protein.name == "Frango"
    assert protein.active is True
    assert isinstance(protein.id, UUID)


def test_recipe_creation():
    recipe = Recipe(
        title="Frango Grelhado",
        ingredients="Frango, temperos",
        instructions="Grelhe o frango",
    )
    assert recipe.title == "Frango Grelhado"
    assert recipe.ai_generated is True
    assert isinstance(recipe.id, UUID)


def test_phone_number_creation():
    phone = PhoneNumber(phone="+5511999999999", name="Test")
    assert phone.phone == "+5511999999999"
    assert phone.active is True
