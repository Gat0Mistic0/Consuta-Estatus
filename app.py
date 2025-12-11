import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

def format_date(value):
    if value == 'Pendiente':
        return value
    try:
        dt = pd.to_datetime(value)
        return dt.strftime('%m/%d/%Y')
    except:
        return str(value)

st.set_page_config(page_title="Rastreo de Pedidos", page_icon="📦")
st.title("📦 Consulta el estado de tu pedido")
st.markdown("Ingresa tu número de ticket (columna 'Id') para ver el progreso.")

conn = st.connection("gsheets", type=GSheetsConnection)

df_pedidos = conn.read(worksheet="Ticket", ttl=0)

date_columns = ['Hora', 'Fecha empaquetado', 'Fecha entrega']

for col in date_columns:
    if col in df_pedidos.columns:
        df_pedidos[col] = df_pedidos[col].astype(str).str.split(' ').str[0]
        df_pedidos[col] = df_pedidos[col].replace({'NaT': 'Pendiente', 'nan': 'Pendiente'})

try:
    df_clientes = conn.read(worksheet="Clientes", ttl=0)
    df_merged = pd.merge(
        df_pedidos,
        df_clientes[['ID', 'Nombre']],
        left_on='Cliente',
        right_on='ID',
        how='left'
    )
except Exception as e:
    st.warning("⚠️ Error al cargar la tabla de 'Cliente'. Se mostrará solo el ID de cliente.")
    df_merged = df_pedidos

col_input, col_button = st.columns([0.8, 0.2])

ticket_input = col_input.text_input("Número de Ticket", placeholder="Ej: 1234", key="ticket_key")

col_button.markdown('<br>', unsafe_allow_html=True)

if col_button.button("🗑️ Limpiar", type="secondary"):
    st.session_state.ticket_key = ""
    st.rerun()

if ticket_input:
    ticket = str(ticket_input).strip()
    pedido = df_merged[df_merged['Id'].astype(str) == ticket]
    
    if not pedido.empty:
        info = pedido.iloc[0]
        nombre_cliente = info.get('Nombre', info['Cliente'])

        st.success(f"¡Pedido encontrado para: **{nombre_cliente}**!")
        st.subheader(f"Estado Actual: **{info['Estado']}**")
        
        match info['Estado']:
            case 'Cargado':
                st.markdown(f"**Ya tenemos tu pedido, estamos trabajando en armarlo**")
                st.divider()
                st.subheader("Historial de Fechas")
                col1, col2, col3 = st.columns(3)
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
                col1, col2, col3 = st.columns(3)
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
                col1, col2, col3 = st.columns(3)
                col1.metric("📦 Cargado", format_date(info['Hora']))
                col2.metric("🎁 Empaquetado", format_date(info['Fecha empaquetado']))
                col3.metric("🏠 Entrega (Tentativa)", format_date(info['Fecha entrega']))
            case 'Entregado':
                st.markdown(f"**En hora buena, tu pedido ya esta en casa**")
                st.divider()
                st.subheader("Historial de Fechas")
                col1, col2, col3 = st.columns(3)
                col1.metric("📦 Cargado", format_date(info['Hora']))
                col2.metric("🎁 Empaquetado", format_date(info['Fecha empaquetado']))
                col3.metric("🏠 Entrega (Tentativa)", format_date(info['Fecha entrega']))
    else:
        st.error(f"❌ No encontramos un pedido con el ticket **{ticket}**. Por favor verifica.")
