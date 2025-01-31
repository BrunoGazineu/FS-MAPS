from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from ratelimit import limits, sleep_and_retry

#Encontra a cidade a partir do centro de uma geometria desenhada no streamlit
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from ratelimit import limits, sleep_and_retry
import streamlit as st

#teste
# Função para calcular o centro do polígono
def calculate_polygon_center(geometry):
    latitudes = [coord[1] for coord in geometry]
    longitudes = [coord[0] for coord in geometry]
    center_lat = sum(latitudes) / len(latitudes)
    center_lon = sum(longitudes) / len(longitudes)
    return [center_lat, center_lon]


# Configuração de limites: máximo de requisições por minuto
MAX_CALLS_PER_MINUTE = 20

# Decorador para limitar a taxa de requisições
@sleep_and_retry
@limits(calls=MAX_CALLS_PER_MINUTE, period=60)
def geocode_city(center_point):
    """
    Encontra a cidade a partir de um ponto central.
    
    Parâmetros:
    - center_point (tuple): Coordenadas (latitude, longitude).
    
    Retorno:
    - str: Nome da cidade ou mensagem de erro.
    """
    try:
        geolocator = Nominatim(user_agent="map_app")
        location = geolocator.reverse(center_point, exactly_one=True)
        if location and "address" in location.raw:
            city = location.raw.get('address', {}).get('city')
            country = location.raw.get('address', {}).get('country')
            if city and country:
                return city, country
            return "Local não encontrado"
        else:
            return "Nenhum local encontrado"
    
    except GeocoderTimedOut:
        return "Erro: Tempo limite excedido para a geocodificação"
    except GeocoderUnavailable:
        return "Erro: Serviço de geocodificação indisponível"
    except Exception as e:
        return f"Erro inesperado: {e}"
    