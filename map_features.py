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
    walkability_gdf = walkability_gdf.to_crs("EPSG:4326")
    return walkability_gdf, clean_polygon.bounds


def plot_walkability_map(walkability_gdf, map_style, map_color, geometry):
    """
    Plot the walkability map using Folium for interactive visualization.
    """
    # Get the center of the polygon
    centroid = walkability_gdf.geometry.iloc[0].centroid
    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=15, tiles=map_style, control_scale=False,  # Remove a escala
    zoom_control=False)

    # Add the walkability area
    folium.GeoJson(
        data=walkability_gdf.__geo_interface__,
        style_function=lambda x: {
            "fillColor": map_color,
            "color": map_color,
            "weight": 3,
            "fillOpacity": 0.5,
        },
    ).add_to(m)

    folium.Polygon(
        locations=[coord[::-1] for coord in geometry],  # Reverter para (lat, lon)
        color= map_color,
        fill=True,
        fill_color=map_color,
        fill_opacity=1
    ).add_to(m)

    if map_style == "Stadia.AlidadeSmooth":
        folium.TileLayer(
            tiles="https://{s}.basemaps.stadiamaps.com/AlidadeSmooth/{z}/{x}/{y}.png",
            attr="&copy; <a href='https://stadiamaps.com/'>Stadia Maps</a> contributors",
            name="Stadia.AlidadeSmooth",
            control=True  # This enables the basemap to be selectable in the layer control
        ).add_to(m)

    elif map_style == "CartoDB.Positron":
        folium.TileLayer(
            tiles="https://{s}.basemaps.stadiamaps.com/AlidadeSmooth/{z}/{x}/{y}.png",
            attr="&copy; <a href='https://stadiamaps.com/'>Stadia Maps</a> contributors",
            name="Stadia.AlidadeSmooth",
            control=True  # This enables the basemap to be selectable in the layer control
        ).add_to(m)

    elif map_style == "OpenStreetMap":
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="&copy; <a href='https://www.esri.com/'>Esri</a> &mdash; Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community",
            name="Esri.WorldImagery",
            control=True  # This enables the basemap to be selectable in the layer control # This enables the basemap to be selectable in the layer control
        ).add_to(m)

    elif map_style == "Stadia.AlidadeSmoothDark":
        folium.TileLayer(
            tiles="https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png",
            attr="&copy; <a href='https://stadiamaps.com/'>Stadia Maps</a> contributors",
            name="Stadia.AlidadeSmoothDark",
            control=True,
        ).add_to(m)

    elif map_style == "Stadia.AlidadeSmoothDark":
        folium.TileLayer(
            tiles="https://tiles.stadiamaps.com/tiles/alidade_satellite/{z}/{x}/{y}{r}.jpg",
            attr='&copy; CNES, Distribution Airbus DS, &copy; Airbus DS, &copy; PlanetObserver (Contains Copernicus Data) | '
                '&copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> '
                '&copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> '
                '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            name="Stadia.AlidadeSatellite",
    control=True,  # Permite a seleção no controle de camadas

        ).add_to(m)
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
        
    
    city_map = create_map(map_style, zoom, False, [limites_cidade.geometry.centroid.y, limites_cidade.geometry.centroid.x])  # Substitua com sua lógica    

    if not limites_cidade.empty:
        # Converter a geometria para GeoJSON
        geojson_data = limites_cidade.geometry.to_json()

        # Adicionar limites da cidade ao mapa
        folium.GeoJson(
            geojson_data,
            name="Limites da Cidade",
            style_function=lambda x: {
                "fillColor": map_color,
                "color": map_color,
                "weight": 2,
                "fillOpacity": 0.5
            },
        ).add_to(city_map)
    else:
        print("Não foi possível encontrar os limites para esta cidade.")

    return city_map
