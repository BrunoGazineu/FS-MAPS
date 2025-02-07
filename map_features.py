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


def plot_walkability_map(walkability_gdf, map_style, map_color, geometry):
    """
    Plot the walkability map using Folium for interactive visualization.
    """
    # Get the center of the polygon
    centroid = walkability_gdf.geometry.iloc[0].centroid
    

    
    return m


def create_city_limits(cidade):
    city_boundary = ox.geocode_to_gdf(cidade)
    return city_boundary

import folium
import geopandas as gpd
import osmnx as ox

def create_city_limits(cidade):
    """Cria os limites da cidade usando osmnx."""
    city_boundary = ox.geocode_to_gdf(cidade)
    return city_boundary


def create_city_map(geometry, map_style, map_color, zoom, option):
    """Cria um mapa com os limites da cidade."""
    center_point = calculate_polygon_center(geometry)  # Substitua com sua lógica
    cidade, country = geocode_city(center_point)  # Substitua com sua lógica

    if option:
        limites_cidade = create_city_limits(option)
    else:
        limites_cidade = create_city_limits(f"{cidade}, {country}")

    # Definir um CRS projetado adequado (exemplo: Web Mercator EPSG:3857)
    limites_proj = limites_cidade.to_crs(epsg=3857)
    # Calcular o centróide corretamente
    centroid = limites_proj.geometry.centroid.iloc[0]
    # Reprojetar de volta para EPSG:4326
    centroid = gpd.GeoSeries([centroid], crs="EPSG:3857").to_crs("EPSG:4326").iloc[0]
    # Passar para a função create_map()

    return limites_cidade
