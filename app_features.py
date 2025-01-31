
import streamlit as st
import folium
from folium.plugins import Draw

from selenium import webdriver
from PIL import Image
import time
import tempfile

from io import BytesIO

#teste
# Função para criar o mapa com o estilo Positron
def create_map(map_style, zoom=13, is_drawable=True, location=[-23.55052, -46.633308]):
    # Criação do mapa centrado em um ponto
    m = folium.Map(location=location, 
                   zoom_start=zoom, 
                   tiles=map_style,
                   control_scale=False,
                   zoom_control=False,
                   dragging=True,
                   scrollWheelZoom=True,
                   attributionControl=False,
                   zoomControl= False,    # Remove zoom control buttons
                   fullscreenControl= False,  # Remove full-screen button
        )
    
    # Adiciona o plugin de desenho (Draw) ao mapa
    if is_drawable:
        draw = Draw()
        draw.add_to(m)
    return m

def create_img_map(bounds, map_style):
    # Criação do mapa ajustado ao bounding box
    img_map = folium.Map(
        zoom_start=16,
        tiles=map_style,
        control_scale=False,
        zoom_control=False,
        dragging=False,
        scrollWheelZoom=False,
        attributionControl=False
    )
    # Ajustar o mapa aos limites fornecidos
    img_map.fit_bounds(bounds)
    return img_map

# Função para adicionar a geometria ao mapa
def add_polygon_to_map(geometry, base_map, map_color):
    if not geometry:
        return base_map  # Retorna o mapa base se a geometria for inválida
    else:
        if len(geometry) < 3:
            return base_map  # Retorna o mapa base se a geometria for inválida
        else:
            # Adiciona o polígono ao mapa base
            folium.Polygon(
                locations=[coord[::-1] for coord in geometry],  # Reverter para (lat, lon)
                color= map_color,
                fill=True,
                fill_color=map_color,
                fill_opacity=0.5
            ).add_to(base_map)
            return base_map
        

# Função para salvar o mapa como imagem
def save_map_as_image(map_object):
    # Salvar o mapa em HTML temporariamente
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_html:
        map_object.save(tmp_html.name)
        temp_html_path = tmp_html.name

    # Configurar o Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Executar o navegador em modo headless
    driver = webdriver.Chrome(options=options)

    # Abrir o arquivo HTML com o mapa no navegador
    driver.get(f"file://{temp_html_path}")
    time.sleep(2)  # Aguardar para que o mapa carregue completamente

    # Capturar o tamanho do conteúdo da página
    map_element = driver.find_element("tag name", "body")
    map_size = map_element.size
    driver.set_window_size(1440, 810)

    # Salvar um screenshot
    screenshot_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
    driver.save_screenshot(screenshot_path)
    driver.quit()

    # Recortar a imagem se necessário
    img = Image.open(screenshot_path)
    return img

# Função para calcular o bounding box do polígono com margem
def calculate_bounding_box(geometry, margin_factor=3):
    latitudes = [coord[1] for coord in geometry]
    longitudes = [coord[0] for coord in geometry]
    min_lat, max_lat = min(latitudes), max(latitudes)
    min_lon, max_lon = min(longitudes), max(longitudes)

    # Aplicar uma margem adicional
    lat_margin = (max_lat - min_lat) * margin_factor
    lon_margin = (max_lon - min_lon) * margin_factor

    return [
        [min_lat - lat_margin, min_lon - lon_margin],  # Coordenada sudoeste
        [max_lat + lat_margin, max_lon + lon_margin]   # Coordenada nordeste
    ]


def download_image(map, map_name):
    
    if map_name == "Radius Map":
        try:
            # Generate the image
            img = save_map_as_image(map)

            # Save the image to a BytesIO buffer for downloading
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            # Add a download button for the image
            st.download_button(
                label="Download Map Image",
                data=buffer,
                file_name="img_map_object.png",
                mime="image/png",
                key="button_1"
            )
        except Exception as e:
            st.error(f"An error occurred: {e}")

    elif map_name == "city_map":
        try:
            # Generate the image
            img = save_map_as_image(map)

            # Save the image to a BytesIO buffer for downloading
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            # Add a download button for the image
            st.download_button(
                label="Download Map Image",
                data=buffer,
                file_name="img_map_object.png",
                mime="image/png",
                key="button_2"
            )
        except Exception as e:
            st.error(f"An error occurred: {e}")

    elif map_name == "Lot map":
        try:
            # Generate the image
            img = save_map_as_image(map)

            # Save the image to a BytesIO buffer for downloading
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            # Add a download button for the image
            st.download_button(
                label="Download Map Image",
                data=buffer,
                file_name="img_map_object.png",
                mime="image/png",
                key="button_3"
            )
        except Exception as e:
            st.error(f"An error occurred: {e}")

    elif map_name == "Walkability":
        try:
            # Generate the image
            img = save_map_as_image(map)

            # Save the image to a BytesIO buffer for downloading
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            # Add a download button for the image
            st.download_button(
                label="Download Map Image",
                data=buffer,
                file_name="img_map_object.png",
                mime="image/png",
                key="button_4"
            )
        except Exception as e:
            st.error(f"An error occurred: {e}")