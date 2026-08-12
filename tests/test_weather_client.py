import pytest
import requests
import responses


from src.weather_client import get_hourly_forecast


@responses.activate
def test_exemplo_mock_sucesso():
    # 1. PREPARAÇÃO (Arrange): Interceptamos a URL que o requests vai tentar acessar
    url_alvo = "https://api.open-meteo.com/v1/forecast" # ajuste para a URL completa que usar
    
    responses.add(
        responses.GET,
        url_alvo,
        json={"exemplo": "dados de mentira para o teste"}, 
        status=200
    )
    
    # 2. AÇÃO (Act): Aqui você chama a sua função real
    # resultado = get_hourly_forecast(48.13, 11.57)
    
    # 3. VERIFICAÇÃO (Assert): Você valida se a função tratou os dados corretamente
    # assert resultado["exemplo"] == "dados de mentira para o teste"

@responses.activate
def test_exemplo_mock_timeout():
    # Para simular um timeout, o responses tem um gatilho específico
    url_alvo = "https://api.open-meteo.com/v1/forecast"
    
    responses.add(
        responses.GET,
        url_alvo,
        body=requests.exceptions.Timeout("O servidor demorou muito!")
    )
    
    # Aqui você usa o pytest para garantir que a SUA função não quebra o sistema inteiro
    # e levanta a exceção correta (ou retorna um erro amigável)
    # with pytest.raises(requests.exceptions.Timeout):
    #     get_hourly_forecast(48.13, 11.57)