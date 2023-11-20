import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


def download_senhami_data(date):
    '''
    Descarga en un archivo .csv la data de la pagina https://www.senamhi.gob.pe/?p=mapa-reservorios-grafica
    Solo es necesario introducir la fecha en formato "day/month/year"
    '''

    day,month,year=date.split('/') # Separamos la fecha
    fecha= year+'-'+month+'-'+day # El servidor del Senahmi usa el formato year-month-day
    url= 'https://www.senamhi.gob.pe/?p=mapa-reservorios-grafica'

    browser= webdriver.Firefox()
    browser.get(url) # Abrimos la pagina

    fecha_ini=browser.find_element(By.XPATH, "//input[@id='txtfini']")
    fecha_ini.send_keys(fecha) # Seteamos la fecha inicial

    fecha_fin=browser.find_element(By.XPATH, "//input[@id='txtffin']")
    fecha_fin.send_keys(fecha) # Seteamos la fecha final

    boton_buscar=browser.find_element(By.ID, 'btnBuscar')
    boton_buscar.send_keys(Keys.ENTER) # Hacemos enter para obtener la data

    ### A continuacion, esperamos hasta que la tabla cargue en la pagina
    try:
        tabla=WebDriverWait(browser, 3).until(lambda x: x.find_element(By.ID, "tbltabular")) # Aca tiene un valor de 3 segundos mientras carga la tabla
    except:
        return "No Data Available" # En caso de algun error, ya sea porque timeout o a falta de data, se imprime el mensaje

    btn_sgte= browser.find_element(By.XPATH, "//li[@id='tbltabular_next']") # Seleccionamos el boton "Siguiente"
    clase_button=btn_sgte.get_attribute('class') # Determinamos su clase, tiene un valor especifico cuando tiene mas de 1 pagina


    heads=[] # Incializamos una lista de los headers de la tabla
    d=[] # Inicializamos una lista que poblaremos con data de la tabla

    ### Iteramos por cada elemento para obtener los headers

    for head in tabla.find_elements(By.XPATH, "./thead/tr"):
        for i in range(1,7):
            heads.append(head.find_element(By.XPATH, './th[{:d}]'.format(i)).get_attribute('textContent'))

    ### Iteramos mientras haya mas de una pagina para la tabla

    while clase_button != 'paginate_button page-item next disabled':
        btn_sgte= browser.find_element(By.XPATH, "//li[@id='tbltabular_next']")
        clase_button=btn_sgte.get_attribute('class')
        tabla= WebDriverWait(browser, 10).until(lambda x: x.find_element(By.ID, "tbltabular"))

        ### Iteramos en cada fila de la tabla
        for row in tabla.find_elements(By.XPATH, "./tbody/tr"):
            rows=[]
            # Iteramos en cada columna de la tabla, en este caso son 6 columnas
            for i in range(1,7):
                rows.append(row.find_element(By.XPATH, './td[{:d}]'.format(i)).get_attribute('textContent'))
            d.append(dict(zip(heads,rows)))   # Poblamos la lista con diccionarios de la forma {"Header": value}

        btn_sgte.click()

    browser.close() # Cerramos el browser
    df= pd.DataFrame(d) # Convertimos el diccionario obtenido en un dataframe

    ### Guardaremos el dataframe como un archivo .csv con la fecha de la data que queremos

    filename='Senhami_'+year+'_'+month+'_'+day+'.csv'
    df.to_csv(filename, sep=',', index=False, encoding='utf-8')
