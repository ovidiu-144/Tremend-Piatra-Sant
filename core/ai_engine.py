import os
import sys


base_path = os.path.dirname(os.path.dirname(__file__))

if base_path not in sys.path:
    sys.path.append(base_path)

from core import csv_parser as csp
import pandas as pd
from prophet import Prophet
from google import genai
from prophet.serialize import model_to_json, model_from_json
import json
from data.keys import Keys
from core.api_parser import parse_api
from data.events import get_romania_events
from data.holidays import get_romania_holidays

def _build_holidays_df(years):
    all_holidays = []
    for year in years:
        year_holidays = get_romania_holidays(year)
        for h in year_holidays:
            all_holidays.append({'holiday': h.nume, 'ds': h.data})
    if not all_holidays:
        return None
    holidays_df = pd.DataFrame(all_holidays)
    holidays_df['ds'] = pd.to_datetime(holidays_df['ds'])
    holidays_df['lower_window'] = 0
    holidays_df['upper_window'] = 1
    return holidays_df

def prediction(forecast, medie, weather_input):
    """forecast = output Prophet; weather_input = același DataFrame dat la predict() cu temp/precip reale."""
    valoare_prezisa = forecast['yhat'].iloc[0]

    diferenta_procentuala = ((valoare_prezisa - medie) / medie) * 100

    data_tinta = weather_input['ds'].iloc[0].date()
    # Nu folosi forecast['temp']: în Prophet e contribuția regresorului la yhat, nu °C (de aceea apărea ~0).
    vreme_temp = weather_input['temp'].iloc[0]
    vreme_precip = weather_input['precip'].iloc[0]
    vreme_vant = weather_input['windspeed'].iloc[0]

    extra_data = [data_tinta, vreme_temp, vreme_precip, vreme_vant]

    return [diferenta_procentuala, extra_data]

def train():
    global model
    base_path = os.path.dirname(__file__)
    cale_model = os.path.join(base_path, 'prophet_model.json')

    data = csp.merge_data()
    data = data.rename(columns={'datetime': 'ds', 'patient_count': 'y'})

    if os.path.exists(cale_model):
        print("Incarc modelul deja antrenat din fisier...")
        with open(cale_model, 'r') as f:
            model = model_from_json(json.load(f))

    else:
        print("Modelul nu exista. Incep antrenarea...")

        training_years = list(range(2017, 2020))
        holidays_df = _build_holidays_df(training_years)

        model = Prophet(growth='flat', holidays=holidays_df)
        model.add_regressor('temp')
        model.add_regressor('humidity')
        model.add_regressor('precip')
        model.add_regressor('snow')
        model.add_regressor('windspeed')
        model.add_regressor('is_event_day')

        data['is_event_day'] = 0.0  # No historical event data available for training years

        model.fit(data)

        with open(cale_model, 'w') as f:
            json.dump(model_to_json(model), f)
        print("Modelul a fost antrenat si salvat cu succes!")

    if 'is_event_day' not in data.columns:
        # Backward compatibility: model was saved before is_event_day regressor was added
        data['is_event_day'] = 0.0

    medie = data['y'].mean()

    return medie

def process_coords(lat, long, start, end, medie):
    events = get_romania_events(lat, long, Keys.EVENT_API_KEY, start, end)

    date_viitor = parse_api(lat, long, start, end, events)

    predictie_centru = model.predict(date_viitor[0])

    predictie_nord = model.predict(date_viitor[1])

    predictie_sud = model.predict(date_viitor[2])

    predictie_est = model.predict(date_viitor[3])

    predictie_vest = model.predict(date_viitor[4])

    predictions = [
        prediction(predictie_centru, medie, date_viitor[0]),
        prediction(predictie_nord, medie, date_viitor[1]),
        prediction(predictie_sud, medie, date_viitor[2]),
        prediction(predictie_est, medie, date_viitor[3]),
        prediction(predictie_vest, medie, date_viitor[4]),
    ]

    diferenta_procentuala, extra_data = predictions[0]
    for pr in predictions:
        if pr[0] > diferenta_procentuala:
            diferenta_procentuala, extra_data = pr
    

 

    procent = round(diferenta_procentuala, 1)

    extra_data.append(procent)
    param_list = extra_data

    return param_list, events



def what_if_process(lat, long, date, prompt_utilizator):
    medie = train()

    param_list, events = process_coords(lat, long, date, date, medie)

    year = int(str(date)[:4])
    holidays = get_romania_holidays(year)
    holiday_names = [h.nume for h in holidays if h.data == str(date)[:10]]
    holiday_info = f"Ziua de {date} este sarbatoare legala: {', '.join(holiday_names)}." if holiday_names else ""

    event_info = ""
    if events:
        event_summaries = [
            f"{e.titlu} ({e.categorie}, ~{e.estimare_participanti} participanti)"
            for e in events
        ]
        event_info = f"Evenimente majore in apropierea spitalului: {'; '.join(event_summaries)}."

    prompt_pentru_llm = f"""
    Ești un asistent medical și manager de spital cu experiență.
    Dispui de predicțiile modelului Prophet pentru ziua de {param_list[0]}, bazate pe date istorice reale.

    PREDICȚIILE MODELULUI PROPHET PENTRU {param_list[0]}:
    - Variație estimată față de medie: {param_list[4]}%
    - Temperatură prognozată: {param_list[1]}°C
    - Precipitații prognozate: {param_list[2]} mm
    - Viteza vântului prognozată: {param_list[3]} km/h

    CONTEXT SUPLIMENTAR:
    {holiday_info}
    {event_info}

    ÎNTREBAREA / SCENARIUL UTILIZATORULUI:
    {prompt_utilizator}

    Răspunde la întrebarea de mai sus ținând cont de predicțiile modelului Prophet prezentate.
    Oferă un răspuns concret, practic și fundamentat pe datele furnizate.
    """

    client = genai.Client(api_key=Keys.AI_KEY)

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt_pentru_llm
    )

    return response.text


def llm_process(lat, long, date):
    medie = train()

    param_list, events = process_coords(lat, long, date, date, medie)

    year = int(str(date)[:4])
    holidays = get_romania_holidays(year)
    holiday_names = [h.nume for h in holidays if h.data == str(date)[:10]]
    holiday_info = f"Ziua de {date} este sarbatoare legala: {', '.join(holiday_names)}." if holiday_names else ""

    event_info = ""
    if events:
        event_summaries = [
            f"{e.titlu} ({e.categorie}, ~{e.estimare_participanti} participanti)"
            for e in events
        ]
        event_info = f"Evenimente majore in apropierea spitalului: {'; '.join(event_summaries)}."

    prompt_pentru_llm = f"""
    Ești un asistent medical și manager de spital cu experiență.
    Sarcina ta este să interpretezi următoarele date și să oferi un scurt raport de pregătire pentru personalul de la primiri urgențe.

    DATELE PENTRU ZIUA DE {param_list[0]}:
    - Variație față de medie: {param_list[4]}% 

    CONDIȚII METEO PROGNOZATE:
    - Temperatură: {param_list[1]}°C
    - Precipitații: {param_list[2]} mm
    - Viteza vântului: {param_list[3]} km/h

    CONTEXT SUPLIMENTAR:
    {holiday_info}
    {event_info}

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

    return response.text

if __name__ == "__main__":
    llm_process(45.6427, 25.5887, "2026-04-01")