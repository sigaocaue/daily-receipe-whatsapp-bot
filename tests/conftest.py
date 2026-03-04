import pytest


@pytest.fixture
def sample_protein_data():
    return {"name": "Frango", "active": True}


@pytest.fixture
def sample_recipe_data():
    return {
        "title": "Frango Grelhado",
        "ingredients": "1 peito de frango, sal, pimenta, azeite",
        "instructions": "Tempere o frango e grelhe por 10 minutos de cada lado",
        "source_url": "https://www.tudogostoso.com.br/receita/frango-grelhado",
        "source_site": "TudoGostoso",
    }
