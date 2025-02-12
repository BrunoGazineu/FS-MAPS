from app_features import *
from geocoder import *
from map_features import *
from walkability_radius_map import *

import streamlit as st
import plotly.graph_objects as go

from streamlit_folium import st_folium
from staticmap import Polygon
from shapely.geometry import Polygon, MultiPolygon


st.set_page_config(
    layout="wide",  # Escolha entre 'centered' ou 'wide'
    page_title="FS Maps",  # Título da aba do navegador
    page_icon="🏢"  # Ícone da aba do navegador
)



# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def authenticate(username, password, st_username, st_passoword):
    """Check if the username exists and password matches."""
    return st_username == username and st_passoword == password


# Login form
if not st.session_state.authenticated:
    st.title("🔐 Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")

    if login_button:
        if authenticate(username, password, st.secrets["USERNAME"], st.secrets["PASSWORD"] ):
            st.session_state.authenticated = True
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Invalid credentials. Try again.")

# Protected content
if st.session_state.authenticated:
    st.sidebar.header("Automações FS")
    st.sidebar.markdown("""
    <p style='font-size:12px;'>Selecione se deseja gerar mapas para sua apresentação ou verificar os inputs necessários para gerar textos os textos referenctes ao local com IA</p>
    """, unsafe_allow_html=True)
    page = st.sidebar.selectbox("Selecione:", ["Mapas", "IA textos"])

    # Exemplo de conteúdo na sidebar
    st.sidebar.header("Walkability definitions")
    st.sidebar.markdown("""
    <p style='font-size:12px;'>1. Desenhe o terreno no mapa ao lado.</p>
    <br>
    <p style='font-size:12px;'>2. Preencha os campos dentro de 'Walkability definitions' para definir as características que serão utilizadas para gerar o mapa de walkability. Obs: sempre que alterar os valores, clicar no botão gerar mapa novamente.</p>
    """, unsafe_allow_html=True)




    # Sidebar inputs
    walk_time_minutes = st.sidebar.slider("Walking Time (minutes)", 5, 60, 15)

    vehicle_type_options = {"A pé": 4, "Automóvel": 20}
    selected_vehicle_type = st.sidebar.selectbox("Selecione o meio de transporte utilizado", list(vehicle_type_options.keys()))
    vehicle_type = vehicle_type_options[selected_vehicle_type]  

    vehicle_speed_options = {"Horário tranquilo": 1, "Horário de pico": 0.5}
    selected_vehicle_speed= st.sidebar.selectbox("Selecione o tipo de trânsito que deseja analisar", list(vehicle_speed_options.keys()))
    vehicle_speed = vehicle_speed_options[selected_vehicle_speed]                                   

    st.sidebar.header("Map style definitions")
    st.sidebar.markdown("""
    <p style='font-size:12px;'>1. Escolha abaixo os estilos de mapa e cores desejadas para a sua apresentação.Obs: sempre que alterar os valores, clicar no botão gerar mapa novamente.</p>
    """, unsafe_allow_html=True)

    map_style = []

    map_color = st.sidebar.color_picker("Walkability Area Color", "#FFFFFF")
    radius_text = False
    
    st.sidebar.header("Local")
    st.sidebar.markdown("""
    <p style='font-size:12px;'>Caso o mapa não gere o BAIRRO desejado, informe o local abaixo.</p>
    """, unsafe_allow_html=True)
    option_neighborhood = st.sidebar.text_input("Informe o BAIRRO formato: 'Bairro, Cidade, Estado, País'")
    st.sidebar.markdown("""
    <p style='font-size:12px;'>Caso o mapa não gere a CIDADE desejada, informe o local abaixo.</p>
    """, unsafe_allow_html=True)
    option_city = st.sidebar.text_input("Informe a CIDADE no formato: 'Cidade, Estado, País'")

    if page == "Mapas":
        # Título da aplicação
        st.title("Gerar mapas - Apresentação FS")
        st.markdown("Desenhe o terreno do estudo no mapa abaixo. Em seguida serão gerados os mapas do **terreno**, **cidade** e **walkability**.")
        # Criação do mapa inicial
        map_object = create_map('CartoDB positron', 13, True)
        # Exibe o mapa interativo no Streamlit (o mapa padrão será mostrado primeiro)
        output = st_folium(map_object, width=1920)

        st.title("Mapa de Walkability")
        if 'geometry' not in st.session_state:
            st.session_state.geometry = None  # Inicializa no estado da sessão
        if 'clicked' not in st.session_state:
            st.session_state.clicked = False
        def click_button():
            st.session_state.clicked = True
        st.sidebar.button("Gerar mapa", on_click=click_button, type = "primary")


        if st.session_state.clicked:
                        
            # Verifica se o 'all_drawings' está no output e contém dados
            if output and 'all_drawings' in output and (output['all_drawings']):
                # Extrai as coordenadas do primeiro desenho
                geometry = output['all_drawings'][0].get('geometry', {}).get('coordinates', [])
                if geometry:
                    geometry = geometry[0]  # Pode ser necessário pegar o primeiro item para polígonos simples
                    # Atualiza a geometria no estado da sessão
                    st.session_state.geometry = geometry
                    
                    # Generate map
                    if st.session_state.geometry:
                        try:
                            #MAPA WALKABILITY
                            walkability_gdf, bounds, centroid = calculate_walkability(st.session_state.geometry, walk_time_minutes, vehicle_speed, vehicle_type)
                            geometry = walkability_gdf.geometry.iloc[0]
                            polygon_coords = [(lon, lat) for lon, lat in list(geometry.exterior.coords)]              
                            plot_plotly(st.session_state.geometry, polygon_coords, map_style, map_color, 14, centroid, True, "walkability_id" ,"walkability_lot_id", False)
                            

                            #MAPA DO TERRENO
                            map_lot_object = create_map(map_style, 16, False, [centroid.y, centroid.x])
                            st.title("Mapa do terreno")
                            if st.session_state.geometry:
                                # Adiciona a geometria (polígono) ao mapa base
                                plot_plotly(st.session_state.geometry, polygon_coords, map_style, map_color, 16, centroid, False, "lot_id", "lot_polygon_id", False)
                                # Provide a download button


                            #MAPA DO BAIRRO
                            st.title("Mapa do Bairro")
                            limites_neighborhood_gdf = create_place_limits(st.session_state.geometry, option_neighborhood, option_city, "suburb")
                            neighborhood_geometry_geometry = limites_neighborhood_gdf.geometry.iloc[0]

                            if isinstance(neighborhood_geometry_geometry, Polygon):  # Caso seja um único polígono
                                neighborhood_geometry_coords = [(lon, lat) for lon, lat in list(neighborhood_geometry_geometry.exterior.coords)]
                                
                            elif isinstance(neighborhood_geometry_geometry, MultiPolygon):  # Caso seja um MultiPolygon
                                neighborhood_geometry_coords = []
                                for poly in neighborhood_geometry_geometry.geoms:
                                    coords = [(lon, lat) for lon, lat in poly.exterior.coords]  # Lista de tuplas (lon, lat) para cada polígono
                                    neighborhood_geometry_coords.append(coords)  # Adiciona cada polígono à lista principal

                            plot_plotly(st.session_state.geometry, neighborhood_geometry_coords, map_style, map_color, 13, centroid, True, "lot_city_id","nieghborhood_city_id", False)


                            #MAPA DA CIDADE
                            st.title("Mapa da cidade")
                            limites_cidade_gdf = create_place_limits(st.session_state.geometry, option_neighborhood, option_city, "city" )
                            city_geometry = limites_cidade_gdf.geometry.iloc[0]
                            

                            if isinstance(city_geometry, Polygon):  # Caso seja um único polígono
                                city_geometry_coords = [(lon, lat) for lon, lat in list(city_geometry.exterior.coords)]
                                
                            elif isinstance(city_geometry, MultiPolygon):  # Caso seja um MultiPolygon
                                largest_polygon = max(city_geometry.geoms, key=lambda poly: poly.area)
                                city_geometry_coords = [(lon, lat) for lon, lat in largest_polygon.exterior.coords]
                            plot_plotly(st.session_state.geometry, city_geometry_coords, map_style, map_color, 9, centroid, True, "lot_city_id","polygon_city_id", False)
                            
                            #MAPA REDONDO
                            st.title("Raio walkability")
                            radius_gdf, center_projected, unproject = create_map_circle(st.session_state.geometry, map_style, map_color, vehicle_speed, vehicle_type, walk_time_minutes)
                            circle_geometry = radius_gdf.geometry.iloc[0]
                            circle_geometry_coords = [(lon, lat) for lon, lat in list(circle_geometry.exterior.coords)]
                            if radius_text:
                                #walkability_radius_map = add_text_to_circle(walk_time_minutes, vehicle_speed, vehicle_type, walkability_radius_map,center_projected, unproject, map_color)
                                plot_plotly(st.session_state.geometry, circle_geometry_coords, map_style, map_color, 14, centroid, True, "lot_city_id","polygon_city_id", True)
                            else:
                                plot_plotly(st.session_state.geometry, circle_geometry_coords, map_style, map_color, 14, centroid, True, "lot_city_id","polygon_city_id", True)
                            

                        except Exception as e:
                            st.error(f"An error occurred: {e}")

        #Reset the clicked flag after generating the maps
        st.session_state.clicked = False
    elif page == "IA textos": 
        st.title('Instruções de input para textos IA dos mapas')
        st.subheader("Copie as instruções abaixo para o chatgpt alterando apenas o seu consteúdo em **negrito**, de acordo com o local do estudo")
        st.markdown("Descreva a seguinte cidade preenchendo cada apecto listado em até 350 caracteres.")
        
        st.markdown("**Cidade**: nome relevância para o seu Estado e/ou proximidade com eixos relevantes, uso principal (turismo, comércio, serviços, industrial, etc). Foi uma cidade planejada?")

        st.markdown("**Bairro**: qual a relação do terreno com o centro da cidade? Se situa em uma região consolidada ou em desenvolvimento? Qual o caráter do bairro (verde, residencial unifamiliar, uso misto, vazio)?")

        st.markdown("Walkability score **informar o score**, **Bairro**: explicar o que é o walkscore, citar que é de 0-100 e como ele avalia isso. Criar um texto padrão para a) 0-50, b) 51-85, c) 86-100. Explicar o motivo da região ser ou não caminhável.")

        st.markdown("Pedestre/Carro: explicar como é a relação de pedestres e veículos no bairro informado.")

