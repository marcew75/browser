import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from io import BytesIO
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

# Cargar secretos desde el archivo secrets.toml
BROWSERSTACK_USERNAME = st.secrets["BROWSERSTACK_USERNAME"]
BROWSERSTACK_ACCESS_KEY = st.secrets["BROWSERSTACK_ACCESS_KEY"]
BROWSERSTACK_URL = f"https://{BROWSERSTACK_USERNAME}:{BROWSERSTACK_ACCESS_KEY}@hub-cloud.browserstack.com/wd/hub"

def configurar_driver():
    chrome_options = Options()
    chrome_options.set_capability('browserName', 'chrome')
    chrome_options.set_capability('browserVersion', 'latest')
    chrome_options.set_capability('bstack:options', {
        "os": "Windows",
        "osVersion": "10",
        "sessionName": "Búsqueda",
        "local": "false",
        "seleniumVersion": "4.0.0"
    })

    driver = webdriver.Remote(
        command_executor=BROWSERSTACK_URL,
        options=chrome_options
    )
    return driver

def realizar_scraping(marca, categoria):
    # Construir la URL directamente
    url = f"https://pe.wiautomation.com/{marca}/{categoria}"
    driver = configurar_driver()
    driver.get(url)
   
    productos = []
    try:
        wait = WebDriverWait(driver, 10)
        # Esperar a que los contenedores estén presentes
        contenedores = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.main_elem_products_section")))
        
        # Scroll para cargar todos los elementos
        for contenedor in contenedores:
            ActionChains(driver).move_to_element(contenedor).perform()
        
        # Recorrer los contenedores y extraer la información
        for contenedor in contenedores:
            descripcion = contenedor.find_element(By.CSS_SELECTOR, "span.name").text
            precio = contenedor.find_element(By.CSS_SELECTOR, "div.price").text
            productos.append({"Descripción": descripcion, "Precio": precio})
    except Exception as e:
        st.error(f"Error durante el scraping: {e}")
    finally:
        driver.quit()

    return pd.DataFrame(productos)

# Función para convertir a Excel
def convertir_a_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Resultados")
    return output.getvalue()

# Interfaz en Streamlit
st.title("Scraper de Productos con BrowserStack")
marca = st.text_input("Marca", value="ABB")
categoria = st.text_input("Categoría", value="Fuente-de-alimentación")

if st.button("Realizar Búsqueda"):
    with st.spinner("Conectando con BrowserStack y realizando búsqueda..."):
        df = realizar_scraping(marca, categoria)

    if not df.empty:
        st.success("Búsqueda completada con éxito.")
        st.dataframe(df)

        archivo_excel = convertir_a_excel(df)
        st.download_button(
            label="Descargar Resultados en Excel",
            data=archivo_excel,
            file_name=f"resultados_{marca}_{categoria}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No se encontraron productos.")

        
  

