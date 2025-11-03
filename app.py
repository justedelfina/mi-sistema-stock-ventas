import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Stock y Ventas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
   .main-header {
       font-size: 2.5rem;
       color: #1f77b4;
       text-align: center;
       margin-bottom: 2rem;
   }
   .section-header {
       font-size: 1.8rem;
       color: #2e86ab;
       margin-bottom: 1rem;
   }
   .success-box {
       background-color: #d4edda;
       border: 1px solid #c3e6cb;
       border-radius: 5px;
       padding: 10px;
       margin: 10px 0;
   }
</style>
""", unsafe_allow_html=True)


class InventorySystem:
    def __init__(self):
        self.products_file = "data/products.json"
        self.sales_file = "data/sales.json"
        self.stock_file = "data/stock.json"
        self.categories_file = "data/categories.json"
        self._initialize_files()

    def _initialize_files(self):
        """Inicializa los archivos JSON si no existen"""
        os.makedirs("data", exist_ok=True)

        if not os.path.exists(self.products_file):
            with open(self.products_file, 'w') as f:
                json.dump([], f)

        if not os.path.exists(self.sales_file):
            with open(self.sales_file, 'w') as f:
                json.dump([], f)

        if not os.path.exists(self.stock_file):
            with open(self.stock_file, 'w') as f:
                json.dump({}, f)

        if not os.path.exists(self.categories_file):
            with open(self.categories_file, 'w') as f:
                json.dump([], f)

    def load_data(self, file_type):
        """Carga datos desde archivos JSON"""
        try:
            if file_type == "products":
                with open(self.products_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif file_type == "sales":
                with open(self.sales_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif file_type == "stock":
                with open(self.stock_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif file_type == "categories":
                with open(self.categories_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            if file_type == "categories":
                return []
            return [] if file_type in ["products", "sales"] else {}

    def save_data(self, file_type, data):
        """Guarda datos en archivos JSON"""
        try:
            if file_type == "products":
                with open(self.products_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            elif file_type == "sales":
                with open(self.sales_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            elif file_type == "stock":
                with open(self.stock_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            elif file_type == "categories":
                with open(self.categories_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            st.error(f"Error al guardar datos: {e}")
            return False

    def add_category(self, category_name):
        """Agrega una nueva categoría si no existe"""
        categories = self.load_data("categories")
        if category_name and category_name.strip() and category_name not in categories:
            categories.append(category_name.strip())
            self.save_data("categories", categories)
            return True
        return False

    def delete_product(self, product_id):
        """Elimina un producto y su stock"""
        products = self.load_data("products")
        stock_data = self.load_data("stock")

        # Eliminar producto
        products = [p for p in products if p['id'] != product_id]

        # Eliminar stock del producto
        product_id_str = str(product_id)
        if product_id_str in stock_data:
            del stock_data[product_id_str]

        # Guardar cambios
        success1 = self.save_data("products", products)
        success2 = self.save_data("stock", stock_data)

        return success1 and success2


def main():
    # Inicializar el sistema
    system = InventorySystem()

    # Título principal
    st.markdown('<h1 class="main-header">📊 Sistema de Control de Stock y Ventas</h1>', unsafe_allow_html=True)

    # Sidebar para navegación
    st.sidebar.title("Navegación")
    menu_options = [
        "Gestión de Productos",
        "Control de Stock",
        "Registro de Ventas",
        "Reportes y Estadísticas",
        "Dashboard Principal"
    ]
    choice = st.sidebar.selectbox("Selecciona una opción:", menu_options)

    # Cargar datos
    products = system.load_data("products")
    sales = system.load_data("sales")
    stock_data = system.load_data("stock")
    categories = system.load_data("categories")

    if choice == "Dashboard Principal":
        show_dashboard(products, sales, stock_data)

    elif choice == "Gestión de Productos":
        show_product_management(system, products, categories)

    elif choice == "Control de Stock":
        show_stock_management(system, products, stock_data)

    elif choice == "Registro de Ventas":
        show_sales_management(system, products, sales, stock_data)

    elif choice == "Reportes y Estadísticas":
        show_reports(products, sales, stock_data)


def show_dashboard(products, sales, stock_data):
    """Muestra el dashboard principal"""
    st.markdown('<h2 class="section-header">📈 Dashboard Principal</h2>', unsafe_allow_html=True)

    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_products = len(products)
        st.metric("Total Productos", total_products)

    with col2:
        total_sales = len(sales)
        st.metric("Total Ventas", total_sales)

    with col3:
        total_revenue = sum(sale.get('total', 0) for sale in sales)
        st.metric("Ingresos Totales", f"${total_revenue:,.2f}")

    with col4:
        # Productos sin stock
        out_of_stock = 0
        for product in products:
            product_id = str(product['id'])
            if stock_data.get(product_id, {}).get('quantity', 0) == 0:
                out_of_stock += 1
        st.metric("Productos Sin Stock", out_of_stock)

    # Gráficos recientes
    col1, col2 = st.columns(2)

    with col1:
        if sales:
            sales_df = pd.DataFrame(sales)
            sales_df['date'] = pd.to_datetime(sales_df['date'])
            daily_sales = sales_df.groupby(sales_df['date'].dt.date)['total'].sum().reset_index()

            fig = px.line(daily_sales, x='date', y='total',
                          title='Ventas Diarias', labels={'total': 'Ingresos', 'date': 'Fecha'})
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if products:
            # Stock por categoría
            categories_stock = {}
            for product in products:
                category = product.get('category', 'Sin categoría')
                product_id = str(product['id'])
                stock_quantity = stock_data.get(product_id, {}).get('quantity', 0)

                if category not in categories_stock:
                    categories_stock[category] = 0
                categories_stock[category] += stock_quantity

            if categories_stock:
                fig = px.pie(values=list(categories_stock.values()), names=list(categories_stock.keys()),
                             title='Stock por Categoría')
                st.plotly_chart(fig, use_container_width=True)


def show_product_management(system, products, categories):
    """Módulo de gestión de productos"""
    st.markdown('<h2 class="section-header">📦 Gestión de Productos</h2>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Agregar Producto", "Lista de Productos", "Configurar Stock y Precio", "Eliminar Productos"])

    with tab1:
        st.subheader("Agregar Nuevo Producto")

        with st.form("add_product_form"):
            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("Nombre del Producto*")
                price = st.number_input("Precio*", min_value=0.0, step=0.1, format="%.2f")

            with col2:
                description = st.text_area("Descripción")
                initial_stock = st.number_input("Stock Inicial", min_value=0, value=0)

            # Sistema de categorías CORREGIDO
            st.write("**Categoría del Producto:**")

            # Inicializar variables
            existing_category = ""
            new_category = ""
            final_category = ""

            # Opción 1: Seleccionar categoría existente (solo si hay categorías)
            if categories:
                st.write("**Categorías existentes:**")
                existing_category = st.selectbox(
                    "Selecciona una categoría existente:",
                    options=[""] + categories,
                    key="existing_category"
                )
            else:
                st.info("📝 No hay categorías existentes. Crea una nueva categoría.")

            # Opción 2: Crear nueva categoría - SIEMPRE VISIBLE
            st.write("**O crear nueva categoría:**")
            new_category = st.text_input(
                "Escribe el nombre de la nueva categoría:",
                placeholder="Ej: Electrónicos, Ropa, Hogar...",
                key="new_category"
            )

            # Determinar qué categoría usar (CORREGIDO)
            if new_category and new_category.strip():
                final_category = new_category.strip()
            elif existing_category:
                final_category = existing_category

            # Botón de submit CORREGIDO - debe estar DENTRO del form
            submitted = st.form_submit_button("Agregar Producto")

            if submitted:
                if name and price and final_category:
                    # Agregar nueva categoría si se creó una
                    if new_category and new_category.strip():
                        if system.add_category(new_category.strip()):
                            st.success(f"✅ Nueva categoría '{new_category.strip()}' creada y guardada")
                        else:
                            st.info(f"ℹ️ La categoría '{new_category.strip()}' ya existe")

                    new_product = {
                        "id": len(products) + 1,
                        "name": name,
                        "price": float(price),
                        "category": final_category,
                        "description": description,
                        "created_at": datetime.now().isoformat()
                    }

                    products.append(new_product)

                    # Configurar stock inicial
                    stock_data = system.load_data("stock")
                    stock_data[str(new_product['id'])] = {
                        'quantity': initial_stock,
                        'last_updated': datetime.now().isoformat()
                    }

                    if system.save_data("products", products) and system.save_data("stock", stock_data):
                        st.success("✅ Producto agregado exitosamente!")
                        st.rerun()
                else:
                    st.error("❌ Por favor completa los campos obligatorios (*)")

        # Mostrar ayuda (fuera del form)
        with st.expander("ℹ️ Ayuda sobre categorías"):
            st.write("""
            **Cómo usar las categorías:**
            - **Selecciona una categoría existente** del menú desplegable
            - **O escribe una nueva categoría** en el campo de texto
            - Las nuevas categorías se guardan automáticamente para usarlas después
            - Si escribes una nueva categoría, esta tendrá prioridad sobre la seleccionada
            """)

    with tab2:
        st.subheader("Lista de Productos")

        if products:
            # Obtener stock actual para cada producto
            stock_data = system.load_data("stock")
            products_with_stock = []

            for product in products:
                stock_quantity = stock_data.get(str(product['id']), {}).get('quantity', 0)
                products_with_stock.append({
                    'ID': product['id'],
                    'Nombre': product['name'],
                    'Precio': f"${product['price']:.2f}",
                    'Categoría': product['category'],
                    'Stock': stock_quantity,
                    'Descripción': product.get('description', '')
                })

            df_products = pd.DataFrame(products_with_stock)
            st.dataframe(df_products, use_container_width=True)

            # Mostrar estadísticas de categorías
            st.subheader("📊 Estadísticas por Categoría")
            category_stats = {}
            for product in products:
                category = product['category']
                if category not in category_stats:
                    category_stats[category] = 0
                category_stats[category] += 1

            if category_stats:
                col1, col2, col3 = st.columns(3)
                for i, (cat, count) in enumerate(category_stats.items()):
                    with [col1, col2, col3][i % 3]:
                        st.metric(f"Categoría: {cat}", count)
        else:
            st.info("📝 No hay productos registrados aún.")

    with tab3:
        st.subheader("Configurar Stock y Precio de Productos")

        if products:
            product_options = {f"{p['id']} - {p['name']}": p for p in products}
            selected_product_key = st.selectbox("Selecciona un producto:",
                                                options=list(product_options.keys()))

            if selected_product_key:
                product = product_options[selected_product_key]
                product_id = str(product['id'])

                # Cargar datos actuales
                stock_data = system.load_data("stock")
                current_stock = stock_data.get(product_id, {}).get('quantity', 0)
                current_price = product['price']

                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Información Actual:**")
                    st.write(f"- **Producto:** {product['name']}")
                    st.write(f"- **Categoría:** {product['category']}")
                    st.write(f"- **Stock actual:** {current_stock}")
                    st.write(f"- **Precio actual:** ${current_price:.2f}")

                with col2:
                    st.write("**Actualizar Valores:**")
                    new_stock = st.number_input("Nuevo stock:", min_value=0, value=current_stock, key="stock_update")
                    new_price = st.number_input("Nuevo precio:", min_value=0.0, value=float(current_price), step=0.1,
                                                format="%.2f", key="price_update")

                if st.button("💾 Actualizar Stock y Precio", type="primary"):
                    # Actualizar stock
                    stock_data[product_id] = {
                        'quantity': new_stock,
                        'last_updated': datetime.now().isoformat()
                    }

                    # Actualizar precio en la lista de productos
                    for p in products:
                        if p['id'] == product['id']:
                            p['price'] = float(new_price)
                            break

                    # Guardar cambios
                    if system.save_data("stock", stock_data) and system.save_data("products", products):
                        st.success(f"✅ ¡Actualizado exitosamente!")
                        st.success(f"📦 Nuevo stock: {new_stock}")
                        st.success(f"💰 Nuevo precio: ${new_price:.2f}")
                        st.rerun()
        else:
            st.info("📝 Primero agrega productos para configurar stock y precio.")

    with tab4:
        st.subheader("Eliminar Productos")

        if products:
            product_options = {f"{p['id']} - {p['name']}": p for p in products}
            product_to_delete = st.selectbox("Selecciona producto a eliminar:",
                                             options=list(product_options.keys()),
                                             key="delete_select")

            if product_to_delete:
                product = product_options[product_to_delete]
                st.warning(
                    f"⚠️ ¿Estás seguro de que quieres eliminar **{product['name']}**? Esta acción no se puede deshacer.")

                if st.button("🗑️ Eliminar Producto", type="primary"):
                    if system.delete_product(product['id']):
                        st.success(f"✅ Producto '{product['name']}' eliminado exitosamente!")
                        st.rerun()
                    else:
                        st.error("❌ Error al eliminar el producto")
        else:
            st.info("📝 No hay productos para eliminar.")


def show_stock_management(system, products, stock_data):
    """Módulo de gestión de stock"""
    st.markdown('<h2 class="section-header">📊 Control de Stock</h2>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Estado de Stock", "Ajustar Stock"])

    with tab1:
        st.subheader("Estado Actual del Stock")

        if products:
            # Crear lista de productos con stock
            stock_list = []
            for product in products:
                product_id = str(product['id'])
                stock_info = stock_data.get(product_id, {})

                stock_list.append({
                    'ID': product_id,
                    'Producto': product['name'],
                    'Categoría': product['category'],
                    'Precio': f"${product['price']:.2f}",
                    'Stock Actual': stock_info.get('quantity', 0),
                    'Última Actualización': stock_info.get('last_updated', 'Nunca')
                })

            if stock_list:
                df_stock = pd.DataFrame(stock_list)

                # Mostrar métricas rápidas
                total_products = len(stock_list)
                total_stock = sum(item['Stock Actual'] for item in stock_list)
                out_of_stock = sum(1 for item in stock_list if item['Stock Actual'] == 0)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Productos", total_products)
                with col2:
                    st.metric("Stock Total", total_stock)
                with col3:
                    st.metric("Sin Stock", out_of_stock)

                st.dataframe(df_stock, use_container_width=True)
            else:
                st.info("📝 No hay datos de stock registrados.")
        else:
            st.info("📝 No hay productos para mostrar stock.")

    with tab2:
        st.subheader("Ajustar Stock Rápidamente")

        if products:
            col1, col2, col3 = st.columns(3)

            with col1:
                product_options = {f"{p['id']} - {p['name']}": p for p in products}
                selected_product_key = st.selectbox("Producto:",
                                                    options=list(product_options.keys()),
                                                    key="stock_adjust")

            with col2:
                operation = st.radio("Operación:", ["Agregar Stock", "Restar Stock", "Establecer Stock"])
                quantity = st.number_input("Cantidad", min_value=0, value=1)

            with col3:
                if selected_product_key:
                    product = product_options[selected_product_key]
                    product_id = str(product['id'])
                    current_stock = stock_data.get(product_id, {}).get('quantity', 0)

                    st.write(f"**Stock actual:** {current_stock}")

                    if st.button("Aplicar Cambio", type="primary"):
                        if operation == "Agregar Stock":
                            new_quantity = current_stock + quantity
                        elif operation == "Restar Stock":
                            new_quantity = max(0, current_stock - quantity)
                        else:  # Establecer Stock
                            new_quantity = quantity

                        stock_data[product_id] = {
                            'quantity': new_quantity,
                            'last_updated': datetime.now().isoformat()
                        }

                        if system.save_data("stock", stock_data):
                            st.success(f"✅ Stock actualizado! Nuevo stock: {new_quantity}")
                            st.rerun()
        else:
            st.info("📝 Primero agrega productos para ajustar stock.")


def show_sales_management(system, products, sales, stock_data):
    """Módulo de registro de ventas"""
    st.markdown('<h2 class="section-header">💰 Registro de Ventas</h2>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Nueva Venta", "Historial de Ventas"])

    with tab1:
        st.subheader("Registrar Nueva Venta")

        # Inicializar session state para los productos seleccionados
        if 'selected_products' not in st.session_state:
            st.session_state.selected_products = []
        if 'total_amount' not in st.session_state:
            st.session_state.total_amount = 0.0

        if products:
            # Selección de productos para la venta
            st.write("**Selecciona productos para la venta:**")

            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                product_options = {
                    f"{p['id']} - {p['name']} (Stock: {stock_data.get(str(p['id']), {}).get('quantity', 0)})": p
                    for p in products if stock_data.get(str(p['id']), {}).get('quantity', 0) > 0}
                selected_product_key = st.selectbox("Producto:", options=list(product_options.keys()))

            with col2:
                quantity = st.number_input("Cantidad", min_value=1, value=1, key="sale_quantity")

            with col3:
                if st.button("➕ Agregar"):
                    if selected_product_key:
                        product = product_options[selected_product_key]
                        available_stock = stock_data.get(str(product['id']), {}).get('quantity', 0)

                        if quantity <= available_stock:
                            # Verificar si el producto ya está en la lista
                            existing_item = next((item for item in st.session_state.selected_products
                                                  if item['product_id'] == product['id']), None)

                            if existing_item:
                                # Actualizar cantidad si ya existe
                                existing_item['quantity'] += quantity
                                existing_item['subtotal'] = existing_item['price'] * existing_item['quantity']
                            else:
                                # Agregar nuevo producto
                                st.session_state.selected_products.append({
                                    'product_id': product['id'],
                                    'name': product['name'],
                                    'price': product['price'],
                                    'quantity': quantity,
                                    'subtotal': product['price'] * quantity
                                })

                            # Recalcular total
                            st.session_state.total_amount = sum(
                                item['subtotal'] for item in st.session_state.selected_products)
                            st.success(f"✅ Producto agregado a la venta")
                            st.rerun()
                        else:
                            st.error(f"❌ Stock insuficiente. Disponible: {available_stock}")

            # Mostrar productos seleccionados
            if st.session_state.selected_products:
                st.subheader("Detalle de la Venta")

                # Crear copia para evitar modificación durante iteración
                products_to_show = st.session_state.selected_products.copy()

                for i, item in enumerate(products_to_show):
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    with col1:
                        st.write(f"**{item['name']}**")
                    with col2:
                        st.write(f"${item['price']:.2f} x {item['quantity']}")
                    with col3:
                        st.write(f"${item['subtotal']:.2f}")
                    with col4:
                        if st.button("❌", key=f"remove_{i}"):
                            st.session_state.selected_products.pop(i)
                            st.session_state.total_amount = sum(
                                item['subtotal'] for item in st.session_state.selected_products)
                            st.rerun()

                st.write(f"**Total: ${st.session_state.total_amount:.2f}**")

                # Finalizar venta
                if st.button("💳 Finalizar Venta", type="primary"):
                    if st.session_state.selected_products:
                        # Actualizar stock
                        for item in st.session_state.selected_products:
                            product_id = str(item['product_id'])
                            current_stock = stock_data.get(product_id, {}).get('quantity', 0)
                            new_stock = current_stock - item['quantity']

                            stock_data[product_id] = {
                                'quantity': new_stock,
                                'last_updated': datetime.now().isoformat()
                            }

                        # Registrar venta
                        new_sale = {
                            "id": len(sales) + 1,
                            "date": datetime.now().isoformat(),
                            "products": st.session_state.selected_products.copy(),
                            "total": st.session_state.total_amount,
                            "items_count": sum(item['quantity'] for item in st.session_state.selected_products)
                        }

                        sales.append(new_sale)

                        # Guardar cambios
                        if system.save_data("sales", sales) and system.save_data("stock", stock_data):
                            st.success(f"✅ Venta registrada exitosamente! Total: ${st.session_state.total_amount:.2f}")
                            st.balloons()

                            # Limpiar productos seleccionados
                            st.session_state.selected_products = []
                            st.session_state.total_amount = 0.0
                            st.rerun()
                    else:
                        st.error("❌ No hay productos en la venta")
        else:
            st.info("📝 Primero agrega productos para realizar ventas.")

    with tab2:
        st.subheader("Historial de Ventas")

        if sales:
            # Convertir ventas para visualización
            sales_list = []
            for sale in sales:
                sales_list.append({
                    'ID': sale['id'],
                    'Fecha': sale['date'][:10],
                    'Hora': sale['date'][11:16],
                    'Productos': len(sale['products']),
                    'Items': sale['items_count'],
                    'Total': f"${sale['total']:.2f}"
                })

            df_sales = pd.DataFrame(sales_list)
            st.dataframe(df_sales, use_container_width=True)

            # Opción para ver detalles de una venta específica
            sale_ids = [s['id'] for s in sales]
            selected_sale_id = st.selectbox("Ver detalles de venta:", sale_ids)

            if selected_sale_id:
                sale_detail = next(s for s in sales if s['id'] == selected_sale_id)
                st.write("**Detalles de la venta:**")
                for product in sale_detail['products']:
                    st.write(
                        f"- {product['name']}: {product['quantity']} x ${product['price']:.2f} = ${product['subtotal']:.2f}")
                st.write(f"**Total: ${sale_detail['total']:.2f}**")
        else:
            st.info("📝 No hay ventas registradas aún.")


def show_reports(products, sales, stock_data):
    """Módulo de reportes y estadísticas"""
    st.markdown('<h2 class="section-header">📈 Reportes y Estadísticas</h2>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Reportes de Ventas", "Análisis de Stock", "Métricas Generales"])

    with tab1:
        st.subheader("Reportes de Ventas")

        if sales:
            # Convertir datos de ventas a DataFrame
            sales_df = pd.DataFrame(sales)
            sales_df['date'] = pd.to_datetime(sales_df['date'])

            # Filtros de fecha
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Fecha inicial", value=sales_df['date'].min().date())
            with col2:
                end_date = st.date_input("Fecha final", value=sales_df['date'].max().date())

            # Filtrar ventas por fecha
            filtered_sales = sales_df[
                (sales_df['date'].dt.date >= start_date) &
                (sales_df['date'].dt.date <= end_date)
                ]

            # Métricas de ventas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Ventas", len(filtered_sales))
            with col2:
                total_revenue = filtered_sales['total'].sum()
                st.metric("Ingresos Totales", f"${total_revenue:,.2f}")
            with col3:
                avg_sale = filtered_sales['total'].mean()
                st.metric("Venta Promedio", f"${avg_sale:.2f}")
            with col4:
                total_items = filtered_sales['items_count'].sum()
                st.metric("Items Vendidos", total_items)

            # Gráficos
            col1, col2 = st.columns(2)

            with col1:
                # Ventas por día
                daily_sales = filtered_sales.groupby(filtered_sales['date'].dt.date)['total'].sum().reset_index()
                fig = px.line(daily_sales, x='date', y='total',
                              title='Ventas Diarias', labels={'total': 'Ingresos', 'date': 'Fecha'})
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Productos más vendidos
                all_products = []
                for sale in filtered_sales.to_dict('records'):
                    for product in sale['products']:
                        all_products.append(product)

                if all_products:
                    products_df = pd.DataFrame(all_products)
                    top_products = products_df.groupby('name')['quantity'].sum().nlargest(10)
                    fig = px.bar(top_products, x=top_products.values, y=top_products.index,
                                 orientation='h', title='Productos Más Vendidos',
                                 labels={'x': 'Cantidad Vendida', 'y': 'Producto'})
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📝 No hay ventas registradas para generar reportes.")

    with tab2:
        st.subheader("Análisis de Stock")

        if products and stock_data:
            # Datos de stock para análisis
            stock_analysis = []
            for product in products:
                product_id = str(product['id'])
                stock_info = stock_data.get(product_id, {})
                stock_quantity = stock_info.get('quantity', 0)

                stock_analysis.append({
                    'Producto': product['name'],
                    'Categoría': product['category'],
                    'Stock Actual': stock_quantity,
                    'Estado': 'Sin Stock' if stock_quantity == 0 else 'Con Stock'
                })

            df_stock_analysis = pd.DataFrame(stock_analysis)

            # Gráfico de estado de stock
            status_counts = df_stock_analysis['Estado'].value_counts()
            fig = px.pie(values=status_counts.values, names=status_counts.index,
                         title='Estado del Stock')
            st.plotly_chart(fig, use_container_width=True)

            # Tabla de análisis
            st.dataframe(df_stock_analysis, use_container_width=True)
        else:
            st.info("📝 No hay datos suficientes para análisis de stock.")

    with tab3:
        st.subheader("Métricas Generales del Negocio")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Resumen de Productos:**")
            if products:
                total_products = len(products)
                categories = len(set(p['category'] for p in products))
                avg_price = sum(p['price'] for p in products) / total_products

                # Calcular stock total
                total_stock = 0
                for product in products:
                    product_id = str(product['id'])
                    total_stock += stock_data.get(product_id, {}).get('quantity', 0)

                st.write(f"- Total de productos: {total_products}")
                st.write(f"- Categorías: {categories}")
                st.write(f"- Stock total: {total_stock}")
                st.write(f"- Precio promedio: ${avg_price:.2f}")
            else:
                st.write("No hay productos registrados")

        with col2:
            st.write("**Resumen de Ventas:**")
            if sales:
                total_sales = len(sales)
                total_revenue = sum(s['total'] for s in sales)
                total_items = sum(s['items_count'] for s in sales)
                avg_sale_value = total_revenue / total_sales

                st.write(f"- Total de ventas: {total_sales}")
                st.write(f"- Ingresos totales: ${total_revenue:,.2f}")
                st.write(f"- Items vendidos: {total_items}")
                st.write(f"- Valor promedio por venta: ${avg_sale_value:.2f}")
            else:
                st.write("No hay ventas registradas")


if __name__ == "__main__":
    main()