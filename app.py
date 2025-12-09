import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración básica de la página
st.set_page_config(page_title="Rastreo de Pedidos", page_icon="📦")
st.title("📦 Consulta el estado de tu pedido")
st.markdown("Ingresa tu número de ticket (columna 'Id') para ver el progreso.")

# 2. Conexión a Google Sheets (usando el worksheet "Ticket")
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(worksheet="Ticket", ttl=0) 

# 3. Componente de entrada de datos
ticket_input = st.text_input("Número de Ticket", placeholder="Ej: 1234")

if ticket_input:
    ticket = str(ticket_input).strip()
    
    # 4. Filtramos la información. ¡USAMOS 'Id' COMO CLAVE DE BÚSQUEDA!
    # El nombre de la columna 'Id' DEBE coincidir con la capitalización exacta.
    pedido = df[df['Id'].astype(str) == ticket]
    
    if not pedido.empty:
        info = pedido.iloc[0] 
        
        st.success(f"¡Pedido encontrado para: **{info['Cliente']}**!")
        
        # Usamos la columna 'Estado Orden'
        st.subheader(f"Estado Actual: **{info['Estado']}**")
        
        # Información adicional usando las columnas exactas (con espacio)
        st.markdown(f"**Repartidor Asignado:** {info['Repartidor']}")
        st.markdown(f"**Dirección de Entrega:** {info['Direccion']}")
        
        st.divider()
        st.subheader("Historial de Fechas")
        
        # 5. Muestra el historial de fechas
        col1, col2, col3 = st.columns(3)
        
        # Usamos los nombres de columna exactos: 'Cargado', 'Fecha empaquetado', 'Fecha entrega'
        col1.metric("📦 Cargado", str(info['Cargado']))
        col2.metric("🎁 Empaquetado", str(info['Fecha empaquetado']))
        col3.metric("🏠 Entrega (Tentativa/Real)", str(info['Fecha entrega']))

    else:
        st.error(f"❌ No encontramos un pedido con el ticket **{ticket}**. Por favor verifica.")
