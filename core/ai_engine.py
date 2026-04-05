import os
import sys


base_path = os.path.dirname(os.path.dirname(__file__))

if base_path not in sys.path:
    sys.path.append(base_path)

import csv_parser as csp
import pandas as pd
from prophet import Prophet
from google import genai
from prophet.serialize import model_to_json, model_from_json
import json
from data.keys import Keys
from api_parser import parse_api

def prediction (date, medie):
    valoare_prezisa = date['yhat'].iloc[0]

    diferenta_procentuala = ((valoare_prezisa - medie) / medie) * 100

    data_tinta = date['ds'].iloc[0].date()
    vreme_temp = date['temp'].iloc[0]
    vreme_precip = date['precip'].iloc[0]
    vreme_vant = date['windspeed'].iloc[0]
   
    extra_data = [data_tinta, vreme_temp, vreme_precip, vreme_vant]

    return [diferenta_procentuala, extra_data]

def train():
    global model
    base_path = os.path.dirname(__file__)
    cale_model = os.path.join(base_path, 'prophet_model.json')

    if os.path.exists(cale_model):
        print("Incarc modelul deja antrenat din fisier...")
        with open(cale_model, 'r') as f:
            model = model_from_json(json.load(f))

        data = csp.merge_data()
        data = data.rename(columns={'datetime': 'ds', 'patient_count': 'y'})

    else:
        print("Modelul nu exista. Incep antrenarea...")
        data = csp.merge_data()
        data = data.rename(columns={'datetime': 'ds', 'patient_count': 'y'})

        model = Prophet(growth='flat')
        model.add_regressor('temp')
        model.add_regressor('humidity')
        model.add_regressor('precip')
        model.add_regressor('snow')
        model.add_regressor('windspeed')

        model.fit(data)

        with open(cale_model, 'w') as f:
            json.dump(model_to_json(model), f)
        print("Modelul a fost antrenat si salvat cu succes!")

    medie = data['y'].mean()

    return medie

    # date_viitor = pd.DataFrame({
    #     'ds': ['2026-05-10'],    
    #     'temp': [22.5], 
    #     'humidity': [50.0],
    #     'precip': [0.0],
    #     'snow': [0.0],
    #     'windspeed': [15.2],
    #     'preciptype_rain': [0.0], 
    #     'preciptype_snow': [0.0]
    #     })

    # date_viitor['ds'] = pd.to_datetime(date_viitor['ds'])

def process_coords(lat, long, start, end, medie):
    date_viitor = parse_api(lat, long, start, end)

    predictie_centru = model.predict(date_viitor[0])

    predictie_nord = model.predict(date_viitor[1])

    predictie_sud = model.predict(date_viitor[2])

    predictie_est = model.predict(date_viitor[3])

    predictie_vest = model.predict(date_viitor[4])

    predictions = [
        prediction (predictie_centru, medie),
        prediction (predictie_nord, medie),
        prediction (predictie_sud, medie),
        prediction (predictie_est, medie),
        prediction (predictie_vest, medie)
    ]

    diferenta_procentuala, extra_data = predictions[0]
    for pr in predictions:
        if pr[0] > diferenta_procentuala:
            diferenta_procentuala, extra_data = pr
    

 

    #ce algoritm are prophet in spate
    # Datele de la Prophet
    # pacienti_estimati = int(valoare_prezisa)
    # pacienti_medie = int(medie)
    procent = round(diferenta_procentuala, 1)

    extra_data.append(procent)
    param_list = extra_data

    return param_list



def llm_process(lat, long, date):
    medie = train()

    param_list = process_coords(lat, long, date, date, medie)

    prompt_pentru_llm = f"""
    Ești un asistent medical și manager de spital cu experiență.
    Sarcina ta este să interpretezi următoarele date și să oferi un scurt raport de pregătire pentru personalul de la primiri urgențe.

    DATELE PENTRU ZIUA DE {param_list[0]}:
    - Variație față de medie: {param_list[4]}% 

    CONDIȚII METEO PROGNOZATE:
    - Temperatură: {param_list[1]}°C
    - Precipitații: {param_list[2]} mm
    - Viteza vântului: {param_list[3]} km/h

    CERINȚE:
    1. Scrie un rezumat de 2-3 propoziții care să explice cum va fi ziua (ex: aglomerată, normală, lejeră).
    2. Cum crezi că va influența vremea tipul de afecțiuni cu care vor veni pacienții?
    3. Dă 2 recomandări practice pentru personal (ex: suplimentarea personalului, pregătirea anumitor echipamente).
    """

    # Aici îți pui cheia ta secretă de API
    client = genai.Client(api_key=Keys.AI_KEY)

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt_pentru_llm
    )

    print(response.text)

if __name__ == "__main__":
    llm_process()