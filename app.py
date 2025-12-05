import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración básica de la página
st.set_page_config(page_title="Rastreo de Pedidos", page_icon="📦")
st.title("📦 Consulta el estado de tu pedido")
st.markdown("Ingresa tu número de ticket (columna 'Ticket') para ver el progreso.")

# 2. Conexión a Google Sheets (usa las credenciales guardadas en Secrets)
# Asegúrate que el 'worksheet' sea el correcto (usualmente "Hoja 1")
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(worksheet="Hoja 1", ttl=0) 

# 3. Componente de entrada de datos
ticket_input = st.text_input("Número de Ticket", placeholder="Ej: XYZ-001")

if ticket_input:
    # Limpiamos y convertimos el input
    ticket = str(ticket_input).strip()
    
    # 4. Filtramos la información. ¡Usamos 'Ticket' como clave de búsqueda!
    # Convertimos la columna 'Ticket' a string para asegurar la comparación
    pedido = df[df['Ticket'].astype(str) == ticket]
    
    if not pedido.empty:
        # Pedido encontrado
        info = pedido.iloc[0] # Tomamos la primera fila de resultados
        
        # Muestra la información general del cliente
        st.success(f"¡Pedido encontrado para: **{info['Cliente']}**!")
        
        # Muestra el estado actual de manera destacada
        # Usamos 'Estado Orden' como la columna de estado
        st.subheader(f"Estado Actual: **{info['Estado Orden']}**")
        
        st.markdown(f"**Repartidor Asignado:** {info['Repartidor']}")
        st.markdown(f"**Dirección de Entrega:** {info['Direccion']}")
        
        st.divider()
        st.subheader("Historial de Fechas")
        
        # 5. Muestra el historial de fechas en columnas
        # Ajustamos a las tres fechas clave que tienes
        col1, col2, col3 = st.columns(3)
        
        # Usamos los nombres de columna exactos: 'Cargado', 'Fecha empaquetado', 'Fecha entrega'
        col1.metric("📦 Pedido Cargado", str(info['Cargado']))
        col2.metric("🎁 Empaquetado", str(info['Fecha empaquetado']))
        col3.metric("🏠 Entrega (Tentativa/Real)", str(info['Fecha entrega']))

    else:
        # Pedido no encontrado
        st.error(f"❌ No encontramos un pedido con el ticket **{ticket}**. Por favor verifica.")