import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from io import BytesIO
from selenium.webdriver.chrome.options import Options


# Configuración de BrowserStack
BROWSERSTACK_USERNAME = "marcelogil_KjOGfW"
BROWSERSTACK_ACCESS_KEY = "bs2t2TdAXJqNNNMqtnmg"
BROWSERSTACK_URL = f"https://{BROWSERSTACK_USERNAME}:{BROWSERSTACK_ACCESS_KEY}@hub-cloud.browserstack.com/wd/hub"




def realizar_scraping(marca, categoria):
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

    url = "https://pe.wiautomation.com/"
    driver.get(url)
    # Resto de tu código para realizar scraping
   


    productos = []
    try:
        wait = WebDriverWait(driver, 10)
        # Aquí adaptas tu scraping, por ejemplo:
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, marca))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//h3[text()='{categoria}']"))).click()
        
        contenedores = driver.find_elements(By.CSS_SELECTOR, "div.item_content")
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
