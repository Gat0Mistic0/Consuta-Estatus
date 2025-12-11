import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

def format_date(value):
    if value == 'Pendiente':
        return value
    try:
        dt = pd.to_datetime(value)
        return dt.strftime('%d/%m/%Y')
    except:
        return str(value)

# 1. Configuración básica de la página
st.set_page_config(page_title="Rastreo de Pedidos", page_icon="📦")
st.title("📦 Consulta el estado de tu pedido")
st.markdown("Ingresa tu número de ticket (columna 'Id') para ver el progreso.")

# 2. Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 2a. Leer la tabla principal de Pedidos
df_pedidos = conn.read(worksheet="Ticket", ttl=0) 

# 🚨 NUEVO BLOQUE: Limpieza y Formato de Fechas 🚨
date_columns = ['Hora', 'Fecha empaquetado', 'Fecha entrega']

for col in date_columns:
    if col in df_pedidos.columns:
        # 1. Convierte la columna a string (para manejar celdas vacías o nulas)
        # 2. Usa .str.split() para dividir en el primer espacio (entre fecha y hora)
        # 3. Toma la primera parte [0], que es la fecha
        df_pedidos[col] = df_pedidos[col].astype(str).str.split(' ').str[0]
        
        # Opcional: Si el valor es 'NaT' o 'nan' (por celdas vacías), lo reemplazamos
        df_pedidos[col] = df_pedidos[col].replace({'NaT': 'Pendiente', 'nan': 'Pendiente'})
# ----------------------------------------------------

# --- NUEVO: UNIÓN DE DATOS (JOIN) ---

try:
    # 2b. Leer la tabla de Clientes (de la pestaña "Clientes")
    # Si la pestaña se llama diferente, cambia "Clientes"
    df_clientes = conn.read(worksheet="Clientes", ttl=0)
    
    # 2c. Realizar la unión de las dos tablas (JOIN)
    # Unimos usando 'IdCliente' de ambas tablas. La nueva columna 'Nombre' (real) se añade a los pedidos.
    df_merged = pd.merge(
        df_pedidos, 
        # Seleccionamos solo las columnas necesarias de Clientes
        df_clientes[['ID', 'Nombre']], 
        left_on='Cliente',             # La clave en la tabla Pedidos es 'Cliente'
        right_on='ID',                 # La clave en la tabla Clientes es 'ID'
        how='left'
    )
except Exception as e:
    # Si la unión falla (por ejemplo, si la hoja "Clientes" no existe), usamos solo la tabla de pedidos
    # y el campo 'Cliente' mostrará el ID
    st.warning("⚠️ Error al cargar la tabla de 'Cliente'. Se mostrará solo el ID de cliente.")
    df_merged = df_pedidos

# 3. Componente de entrada de datos (Input) y Botón de Limpieza

# Usamos st.empty() y st.columns para colocar el botón junto al input
col_input, col_button = st.columns([0.8, 0.2]) # 80% para el input, 20% para el botón

# Creamos el campo de texto DENTRO de la primera columna
ticket_input = col_input.text_input("Número de Ticket", placeholder="Ej: 1234", key="ticket_key")

# Creamos el botón DENTRO de la segunda columna
# Usamos un espacio en blanco ('') como etiqueta del input para alinearlo
# Añadimos un salto de línea con st.markdown para bajar el botón al nivel del input
col_button.markdown('<br>', unsafe_allow_html=True) 

# El botón de limpiar se usa para determinar si la aplicación debe reiniciarse sin el valor de búsqueda
if col_button.button("🗑️ Limpiar", type="secondary"):
    # Si se hace clic en 'Limpiar', Streamlit se reinicia con el input vacío
    st.session_state.ticket_key = "" # Borra el valor guardado en el estado de la sesión
    st.rerun()           # Fuerza el reinicio de la app para aplicar el cambio

# NOTA: Usamos 'ticket_key' como una clave persistente para que el botón pueda manipular el valor.

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
        match info['Estado']:
            case 'Cargado':
                st.markdown(f"**Ya tenemos tu pedido, estamos trabajando en armarlo**")
                st.divider()
                st.subheader("Historial de Fechas")
                
                # 5. Muestra el historial de fechas
                col1, col2, col3 = st.columns(3)
                    
                # Usamos los nombres de columna exactos: 'Cargado', 'Fecha empaquetado', 'Fecha entrega'
                col1.metric("📦 Cargado", format_date(info['Hora']))
                try:
                    fecha_entrega = pd.to_datetime(info['Fecha entrega'])
                    fecha_entrega_plus_1 = fecha_entrega + pd.Timedelta(days=1)
                    col3.metric("🏠 Entrega (Tentativa)", fecha_entrega_plus_1.strftime('%d/%m/%Y'))
                except:
                    col3.metric("🏠 Entrega (Tentativa)", format_date(info['Fecha entrega']))
            case 'Empacado':
                st.markdown(f"**Tu pedido ya esta armado, esta esperando a ser embarcado para llegar a tus brazos**")
                st.divider()
                st.subheader("Historial de Fechas")
            
                # 5. Muestra el historial de fechas
                col1, col2, col3 = st.columns(3)
            
                # Usamos los nombres de columna exactos: 'Cargado', 'Fecha empaquetado', 'Fecha entrega'
                col1.metric("📦 Cargado", format_date(info['Hora']))
                col2.metric("🎁 Empaquetado", format_date(info['Fecha empaquetado']))
                try:
                    fecha_entrega = pd.to_datetime(info['Fecha entrega'])
                    fecha_entrega_plus_1 = fecha_entrega + pd.Timedelta(days=1)
                    col3.metric("🏠 Entrega (Tentativa)", fecha_entrega_plus_1.strftime('%d/%m/%Y'))
                except:
                    col3.metric("🏠 Entrega (Tentativa)", format_date(info['Fecha entrega']))
            case 'Enrutado':
                st.markdown(f"**Ya casi llega!!! tu pedido va en camino**")
                st.divider()
                st.subheader("Historial de Fechas")
            
                # 5. Muestra el historial de fechas
                col1, col2, col3 = st.columns(3)
            
                # Usamos los nombres de columna exactos: 'Cargado', 'Fecha empaquetado', 'Fecha entrega'
                col1.metric("📦 Cargado", format_date(info['Hora']))
                col2.metric("🎁 Empaquetado", format_date(info['Fecha empaquetado']))
                col3.metric("🏠 Entrega (Tentativa)", format_date(info['Fecha entrega']))
            case 'Entregado':
                st.markdown(f"**En hora buena, tu pedido ya esta en casa**")
                st.divider()
                st.subheader("Historial de Fechas")
                # 5. Muestra el historial de fechas
                col1, col2, col3 = st.columns(3)
            
                # Usamos los nombres de columna exactos: 'Cargado', 'Fecha empaquetado', 'Fecha entrega'
                col1.metric("📦 Cargado", format_date(info['Hora']))
                col2.metric("🎁 Empaquetado", format_date(info['Fecha empaquetado']))
                col3.metric("🏠 Entrega (Tentativa)", format_date(info['Fecha entrega']))
        #st.markdown(f"**Repartidor Asignado:** {info['Repartidor']}")
        #st.markdown(f"**Dirección de Entrega:** {info['Direccion']}")
        
        

    else:
        st.error(f"❌ No encontramos un pedido con el ticket **{ticket}**. Por favor verifica.")
