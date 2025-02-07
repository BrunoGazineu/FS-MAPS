from geocoder import *
from app_features import *

from shapely.geometry import *

import pyproj
from shapely.ops import transform
import geopandas as gpd
import folium
import streamlit as st
from streamlit_folium import st_folium

import math

def create_map_circle(geometry, map_style, map_color, vehicle_speed, vehicle_type, walk_time_minutes):

    distance = (vehicle_speed*vehicle_type) * (walk_time_minutes/60)*1000
    # Configurar Streamlit
    center = calculate_polygon_center(geometry)
    center_point = Point(center[1], center[0]) #Longitude, Latitude
    project = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True).transform
    center_projected = transform(project, center_point)

    # Criar buffer em metros
    buffer_projected = center_projected.buffer(distance)

    # Reprojetar de volta para EPSG:4326
    unproject = pyproj.Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True).transform
    buffer_in_degrees = transform(unproject, buffer_projected)

    # Criar GeoDataFrame
    gdf = gpd.GeoDataFrame({"geometry": [buffer_in_degrees]}, crs="EPSG:4326")
    # Criar o mapa
                                
    return gdf, center_projected, unproject

def add_text_to_circle(walk_time_minutes, vehicle_speed, vehicle_type, walkability_radius_map,center_projected, unproject, map_color):
    # Adicionar texto ao redor do círculo
                    texto = f"WALKABILITY - {walk_time_minutes} MINUTOS DE CAMINHADA"
                    travel_speed = vehicle_speed * vehicle_type
                    walk_distance = (travel_speed / 60) * walk_time_minutes
                    walk_distance_meters = walk_distance * 1100

                    google_fonts = """<link href="https://fonts.googleapis.com/css2?family=Barlow:wght@400&display=swap" rel="stylesheet">"""

                    radius = 1100
                    num_chars = len(texto)  # Número de pontos para o texto
                    angle_step = angle_step = 50 * math.pi / num_chars
                    for i in range(num_chars):
                        angle = (i-10) * angle_step  # Posição do caractere ao redor do círculo
                        angle_radians = math.radians(angle)
                        
                        # Calcular coordenadas no círculo
                        x_projected = (list(center_projected.coords)[0][0] + 0) + radius * math.cos(angle_radians)
                        y_projected = (list(center_projected.coords)[0][1] + 50) + radius * math.sin(angle_radians)
                        # Reprojetar de volta para EPSG:4326
                        projected_point = Point(x_projected, y_projected)
                        projected_back = transform(unproject, projected_point)
                        
                        x = projected_back.x  # Longitude
                        y = projected_back.y  # Latitude

                        # Rotação do texto tangencial ao círculo
                        rotation_angle = (angle) * 180 / math.pi - 90  # Ajustar para rotacionar corretamente
                        folium.Marker(
                            [y, x],
                            icon=folium.DivIcon(
                                html=f"""<div style='transform: rotate({i * -angle_step + 135}deg); text-align: center;'>
                                            <span style='font-size: 22px; color: {map_color};font-family: "Barlow", sans-serif;  font-weight: 700'>{texto[::-1][i]}</span>
                                        </div>"""
                            ),
                        ).add_to(walkability_radius_map)

                    # Exibir no Streamlit
                    st.title('Raio Walkability')
                    st_folium(walkability_radius_map, width=1440, height=810, returned_objects=[])