import streamlit as st
#teste
def show_form():
    # Formulário após o mapa
    st.title("Formulário - Walkability maps")
    # Formulário
    with st.form(key='form_transporte'):
        # Campo de minutos
        minutos_input = st.number_input('Minutos:', value=10, min_value=1, max_value=120, step=1, help="Informe o tempo estimado em minutos.")

        # Dropdown para selecionar o transporte
        transporte_dropdown = st.selectbox(
            'Transporte:',
            options=['Carro', 'Ônibus', 'Bicicleta', 'A pé'],
            help="Escolha o meio de transporte utilizado."
        )
        # Dropdown para escolher o horário
        horario_dropdown = st.selectbox(
            'Horário:',
            options=['Horário de pico', 'Horário tranquilo'],
            help="Escolha o horário da viagem."
        )
        # Botão de envio
        submit_button = st.form_submit_button('Enviar')
