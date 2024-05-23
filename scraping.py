from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import psycopg2
import time

# Configure Selenium driver (Firefox in this case)
driver = webdriver.Firefox()
driver.get(
    "https://procesosjudiciales.funcionjudicial.gob.ec/busqueda-filtros")

# Connect to PostgreSQL database
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

# Zoom is set to 80% to facilitate data mining
driver.execute_script("document.body.style.zoom='80%'")

time.sleep(1)

html = driver.page_source
soap = BeautifulSoup(html, "html.parser")

pages = soap.find_all(
    "div", class_="mat-mdc-paginator-range-label")[0].text.split(' ')[4]

next_page = "Página siguiente"

for page in range(1, int(pages)):
    if page != 1:
        html_next_page = driver.page_source
        soap_next_page = BeautifulSoup(html_next_page, "html.parser")
        results = soap_next_page.find_all(
            "div", class_="causa-individual ng-star-inserted")
    else:
        results = soap.find_all(
            "div", class_="causa-individual ng-star-inserted")
    for result in results:
        # Insert process information
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

        # Process to click and go to the process details page.
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable(
            (By.XPATH, f"//*[@aria-label[contains(., '{process_number}')]]"))
        ).click()
        time.sleep(1)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "lista-movimiento")))
        # Get the Html of the detail page
        html_2 = driver.page_source
        soap_2 = BeautifulSoup(html_2, "html.parser")
        details = soap_2.find("div", class_="lista-movimiento")
        for detail in details:
            if detail.text == "":
                break
            # Insert detail information
            incident_number = detail.select_one("div.numero-incidente").text
            date = detail.select_one("div.fecha-ingreso").text
            offended_actors = detail.select_one("div.lista-actores").text
            defendants = detail.select_one("div.lista-demandados").text
            cursor.execute("""
                INSERT INTO public.details
                (incident_number, date, offended_actors, defendants,
                process_number) VALUES(%s, %s, %s, %s, %s);
            """, (incident_number,
                  date,
                  offended_actors, defendants, process_number))
            conn.commit()
        driver.back()
        """
            In this part we did this procedure because when you go back
            from the details page to the processes page, you immediately go
            back to the first search page, so you had to increment (by clicking
            the button) to find the correct page and enter the details.
        """
        if page != 1:
            new_page_performances = page - 1
            for new_page_performances in range(0, new_page_performances):
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                    (By.XPATH, f"//*[@aria-label[contains(., '{next_page}')]]")
                )).click()
                time.sleep(1)
        else:
            time.sleep(1)
    """
        In this part we did this procedure because when you go
        back from the details page to the processes page, you immediately
        go back to the first search page, so you had to increment (by
        clicking the button) to find the correct page and enter the details.
    """
    if page != 1:
        for new in range(0, 1):
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                (By.XPATH, f"//*[@aria-label[contains(., '{next_page}')]]")
            )).click()
            time.sleep(1)
    else:
        for page in range(0, page):
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                (By.XPATH, f"//*[@aria-label[contains(., '{next_page}')]]")
            )).click()
            time.sleep(1)

# Close connections
cursor.close()
conn.close()
driver.quit()
