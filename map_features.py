import streamlit as st
import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import Polygon, MultiPolygon
import osmnx as ox
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw

from geocoder import *
from app_features import *


@st.cache_data
def calculate_walkability(lot_coords, walk_time_minutes, vehicle_speed, day_time):
    """
    Calculate walkability area based on input parameters.
    """
    travel_speed = vehicle_speed * day_time
    walk_distance = (travel_speed / 60) * walk_time_minutes
    walk_distance_meters = walk_distance * 1000

    # Convert lot_coords to a shapely polygon
    #polygon = string_to_coords(lot_coords)
    longitude = list(lot_coords)[0][0]
    latitude = list(lot_coords)[0][1]

    # Download the road network
    G = ox.graph_from_point((latitude, longitude), dist=walk_distance_meters*2, network_type="walk")
    subgraph = nx.ego_graph(
        G,
        ox.distance.nearest_nodes(G, longitude, latitude),
        radius=walk_distance_meters,
        distance="length",
    )
    G_proj = ox.project_graph(subgraph)

    # Convert edges to a GeoDataFrame
    edges = ox.graph_to_gdfs(G_proj, nodes=False)

    # Create a buffer around edges to represent walkability area
    buffer_distance = 20  # Buffer distance in meters
    edges["geometry"] = edges["geometry"].buffer(buffer_distance)
    walkability_area = edges.unary_union  # Merge all buffers into one geometry

    # Select the largest geometry (removing holes)
    if isinstance(walkability_area, MultiPolygon):
        largest_polygon = max(walkability_area, key=lambda p: p.area)
    else:
        largest_polygon = walkability_area

    # Create a new polygon without holes
    clean_polygon = Polygon(largest_polygon.exterior)  # Use only the exterior
    
    # Transform into a GeoDataFrame
    walkability_gdf = gpd.GeoDataFrame(
        geometry=[clean_polygon], crs=G_proj.graph["crs"]
    )
    # 🚀 **Reprojetar para um CRS projetado antes de calcular o centróide**
    walkability_gdf_proj = walkability_gdf.to_crs("EPSG:3857")  # Web Mercator

    # Calcular o centróide corretamente no CRS projetado
    centroid = walkability_gdf_proj.geometry.iloc[0].centroid

    # Reprojetar para EPSG:4326 antes de retornar
    walkability_gdf = walkability_gdf_proj.to_crs("EPSG:4326")
    centroid = gpd.GeoSeries([centroid], crs="EPSG:3857").to_crs("EPSG:4326").iloc[0]

    return walkability_gdf, clean_polygon.bounds, centroid



def create_city_limits(cidade):
    city_boundary = ox.geocode_to_gdf(cidade)
    return city_boundary

import folium
import geopandas as gpd
import osmnx as ox
import plotly.graph_objects as go


def create_city_limits(local):
    """Cria os limites da cidade usando osmnx."""
    city_boundary = ox.geocode_to_gdf(local)
    return city_boundary


def create_place_limits(geometry, option_neighborhood, option_city, area_type):
    """Cria um mapa com os limites da cidade."""
    center_point = calculate_polygon_center(geometry)  # Substitua com sua lógica
    cidade, country, neighborhood = geocode_city(center_point)  # Substitua com sua lógica
    if area_type == "city":
        if option_city:
            limites_local = create_city_limits(option_city)
        else:
            limites_local = create_city_limits(f"{cidade}, {country}")
        return limites_local
    elif area_type == "suburb":
        if option_neighborhood:
            limites_local = create_city_limits(option_neighborhood)
        else:
            limites_local = create_city_limits(f"{neighborhood}, {cidade}, {country}")
        return limites_local
    

def plot_plotly(lot_coords, geometry_coords, map_style, map_color, zoom, centroid, plot_polygon, walkability_id, walkability_lot_id,dashed):

    geometry_coords = geometry_coords
    # Garantir que geometry_coords é uma lista de tuplas
    # Remover camada extra se for uma lista de listas
    if isinstance(geometry_coords[0], list):
        geometry_coords = [coord for sublist in geometry_coords for coord in sublist]  # Achata a lista

    # Verificar se todos os elementos são tuplas antes de usar zip()
    if all(isinstance(pt, tuple) and len(pt) == 2 for pt in geometry_coords):
        lon, lat = zip(*geometry_coords)
    else:
        print("Erro: geometry_coords não está no formato correto!")

    #lon, lat = zip(*geometry_coords)
    lon_1,lat_1 = zip(*lot_coords) 
    hex_color = map_color.lstrip("#")  # Remove "#" se presente
    rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    fig = go.Figure()

    fig.add_trace(go.Scattermapbox(
        lon=lon_1, lat=lat_1,
        mode="lines",
        fill="toself",
        fillcolor=f"rgb({rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]})",  # Certifique-se de incluir transparência
        line=dict(color=f"rgb({rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]})", width=3),
        name= walkability_lot_id
    ))

    if plot_polygon:
        if dashed:
            lon_dashed = []
            lat_dashed = []

            for i in range(len(lon) - 1):
                if i % (2 * 1) < 1:
                    lon_dashed.extend([lon[i], lon[i + 1], None])  # Break the line with None
                    lat_dashed.extend([lat[i], lat[i + 1], None])
            
            fig.add_trace(go.Scattermapbox(
                lon=lon_dashed, lat=lat_dashed,
                mode="lines",
                line=dict(color=f"rgb({rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]})", width=4),
                name= walkability_id
            ))
            fig.add_trace(go.Scattermapbox(
                lon=lon, lat=lat,
                mode="none",
                fill="toself",
                fillcolor=f"rgba({rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]}, 0.5)",  # Certifique-se de incluir transparência
                name= walkability_id
            ))
        else:
            fig.add_trace(go.Scattermapbox(
                lon=lon, lat=lat,
                mode="none",
                fill="toself",
                fillcolor=f"rgba({rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]}, 0.5)",  # Certifique-se de incluir transparência
                name= walkability_id
            ))
            fig.add_trace(go.Scattermapbox(
                lon=lon, lat=lat,
                mode="lines",
                line=dict(color=f"rgb({rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]})", width=4),
                name= walkability_id
            ))

    fig.update_layout(
        mapbox=dict(
            accesstoken=st.secrets["API_TOKEN"],
            style= "mapbox://styles/brunapengo/cm6zjp0dc002g01qwb24n8ccp",  # Style
            center = {'lon': list(centroid.coords)[0][0], 'lat': list(centroid.coords)[0][1]},
            zoom= zoom,
        ),
        showlegend=False,
        margin={'l': 0, 'r': 0, 'b': 0, 't': 0},
        width=1440,
        height=880,
    )
    st.plotly_chart(fig)



