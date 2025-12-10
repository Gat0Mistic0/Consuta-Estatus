import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración básica de la página
st.set_page_config(page_title="Rastreo de Pedidos", page_icon="📦")
st.title("📦 Consulta el estado de tu pedido")
st.markdown("Ingresa tu número de ticket (columna 'Id') para ver el progreso.")

# 2. Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 2a. Leer la tabla principal de Pedidos
df_pedidos = conn.read(worksheet="Ticket", ttl=0) 

# --- NUEVO: UNIÓN DE DATOS (JOIN) ---

try:
    # 2b. Leer la tabla de Clientes (de la pestaña "Clientes")
    # Si la pestaña se llama diferente, cambia "Clientes"
    df_clientes = conn.read(worksheet="Cliente", ttl=0)
    
    # 2c. Realizar la unión de las dos tablas (JOIN)
    # Unimos usando 'IdCliente' de ambas tablas. La nueva columna 'Nombre' (real) se añade a los pedidos.
    df_merged = pd.merge(
        df_pedidos, 
        # Seleccionamos solo las columnas necesarias de Clientes
        df_clientes[['IdCliente', 'Nombre']], 
        on='IdCliente', 
        how='left' # Usamos left join para mantener todos los pedidos
    )
except Exception as e:
    # Si la unión falla (por ejemplo, si la hoja "Clientes" no existe), usamos solo la tabla de pedidos
    # y el campo 'Cliente' mostrará el ID
    st.warning("⚠️ Error al cargar la tabla de 'Clientes'. Se mostrará solo el ID de cliente.")
    df_merged = df_pedidos

# 3. Componente de entrada de datos (el filtro se aplica sobre df_merged)
ticket_input = st.text_input("Número de Ticket", placeholder="Ej: 1234")

if ticket_input:
    ticket = str(ticket_input).strip()
    
    # 4. Filtramos el DataFrame MERGED usando 'Id'
    pedido = df_merged[df_merged['Id'].astype(str) == ticket]
    
    if not pedido.empty:
        info = pedido.iloc[0] 
        
        # 5. MOSTRAR EL NOMBRE REAL DEL CLIENTE
        # Usamos .get('Nombre', ...) para asegurar que si la columna 'Nombre' no se creó (por el error anterior),
        # se muestre el ID de la columna 'Cliente' como alternativa.
        nombre_cliente = info.get('Nombre', info['Cliente'])

        st.success(f"¡Pedido encontrado para: **{nombre_cliente}**!")
        
        # Usamos la columna 'Estado Orden'
        st.subheader(f"Estado Actual: **{info['Estado']}**")
        
        # Información adicional usando las columnas exactas
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
