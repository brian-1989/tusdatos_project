from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import psycopg2
import time

# Configura el driver de Selenium (Firefox en este caso)
driver = webdriver.Firefox()
driver.get("https://procesosjudiciales.funcionjudicial.gob.ec/busqueda-filtros")

# Conectar a la base de datos PostgreSQL
conn = psycopg2.connect(
    dbname="railway",
    user="postgres",
    password="oOvoiZizblnksdOWPiNYWzHfMrlTEJIM",
    host="roundhouse.proxy.rlwy.net",
    port="13760"
)
cursor = conn.cursor()

input_element = driver.find_element(By.ID, "mat-input-1")
input_element.send_keys("0968599020001" + Keys.ENTER)

time.sleep(1)

html = driver.page_source
soap = BeautifulSoup(html, "html.parser")
results = soap.find_all("div", class_="causa-individual ng-star-inserted")
data = []
for result in results:
    # Insertar información del proceso
    id = result.select_one("div.id").text
    date_of_entry = result.select_one("div.fecha").text
    process_number = result.select_one("div.numero-proceso").text
    action_infraction = result.select_one("div.accion-infraccion").text
    cursor.execute("""
        INSERT INTO public.process
        (id, date_of_entry, process_number, action_infraction)
        VALUES(%s, %s, %s, %s);
    """, (id, date_of_entry, process_number, action_infraction))
    conn.commit()

    # Proceso para hacer click e ir a la página de los detalles del proceso
    process_number = result.select_one("div.numero-proceso").text
    WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//*[@aria-label[contains(., '{process_number}')]]"))).click()
    time.sleep(1)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "lista-movimiento")))
    # Obtener el Html de la página de los detalles
    html_2 = driver.page_source
    soap_2 = BeautifulSoup(html_2, "html.parser")
    details = soap_2.find("div", class_="lista-movimiento")
    for detail in details:
        if detail.text == "":
            break
        # Insertar información del detalle
        incident_number = detail.select_one("div.numero-incidente").text
        date = detail.select_one("div.fecha-ingreso").text
        offended_actors = detail.select_one("div.lista-actores").text
        defendants = detail.select_one("div.lista-demandados").text
        cursor.execute("""
            INSERT INTO public.detalles
            (incident_number, date, offended_actors, defendants, process_number)
            VALUES(%s, %s, %s, %s, %s);
        """, (incident_number, date, offended_actors, defendants, process_number))
        conn.commit()
        date = detail.select_one("div.fecha-ingreso").text
        date_parseada = datetime.strptime(date, " %d/%m/%Y %H:%M ")
        date_iso = date_parseada.isoformat()[:-3] + "" * -3
        text = f"Vínculo para ingresar al incidente del {date_iso}"
        print(WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//*[@aria-label[contains(., '{text}')]]"))))
        judicial_proceedings_element = driver.find_element(
            By.XPATH, f"//*[@aria-label[contains(., '{date_iso}')]]")
        driver.execute_script(
            "arguments[0].scrollIntoView();", judicial_proceedings_element)
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//*[@aria-label[contains(., '{text}')]]"))).click()
        time.sleep(1)
        # html_3 = driver.page_source
        # soap_3 = BeautifulSoup(html_3, "html.parser")
        # export_pdf = soap_3.find("span", "mdc-button__label")
        # data_2 = export_pdf.text
        va = " Exportar PDF "
        pdf_element = driver.find_element(By.CLASS_NAME, "mdc-button__label")
        pdf_content = pdf_element.text
        with open("export.pdf", "wb") as f:
            f.write(pdf_content.encode("utf-8"))
        driver.back()
        print('helloooooooooooooooo')

        time.sleep(1)
    driver.back()
    time.sleep(1)

# Cerrar conexiones
cursor.close()
conn.close()
driver.quit()