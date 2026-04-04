import csv_parser as csp
import pandas as pd
from prophet import Prophet
from google import genai
global model 

def train():
    data = csp.merge_data()

    print(data.dtypes)

    data = data.rename(columns={'datetime': 'ds', 'patient_count': 'y'})

    model = Prophet(growth='flat')

    model.add_regressor('temp')
    model.add_regressor('humidity')
    model.add_regressor('precip')
    model.add_regressor('snow')
    model.add_regressor('windspeed')

    model.fit(data)

    date_viitor = pd.DataFrame({
        'ds': ['2026-05-10'],    
        'temp': [22.5], 
        'humidity': [50.0],
        'precip': [0.0],
        'snow': [0.0],
        'windspeed': [15.2],
        'preciptype_rain': [0.0], 
        'preciptype_snow': [0.0]
        })

    date_viitor['ds'] = pd.to_datetime(date_viitor['ds'])

    predictie = model.predict(date_viitor)

    medie = data['y'].mean()

    valoare_prezisa = predictie['yhat'].iloc[0]

    diferenta_procentuala = ((valoare_prezisa - medie) / medie) * 100

    data_tinta = date_viitor['ds'].iloc[0].date()
    vreme_temp = date_viitor['temp'].iloc[0]
    vreme_precip = date_viitor['precip'].iloc[0]
    vreme_vant = date_viitor['windspeed'].iloc[0]

    # Datele de la Prophet
    pacienti_estimati = int(valoare_prezisa)
    pacienti_medie = int(medie)
    procent = round(diferenta_procentuala, 1)

    param_list = [data_tinta, vreme_temp, vreme_precip, vreme_vant, pacienti_estimati, pacienti_medie, procent]

    return param_list

def llm_setup():
    param_list = train()

    prompt_pentru_llm = f"""
    Ești un asistent medical și manager de spital cu experiență.
    Sarcina ta este să interpretezi următoarele date și să oferi un scurt raport de pregătire pentru personalul de la primiri urgențe.

    DATELE PENTRU ZIUA DE {param_list[0]}:
    - Variație față de medie: {param_list[6]}% 

    CONDIȚII METEO PROGNOZATE:
    - Temperatură: {param_list[1]}°C
    - Precipitații: {param_list[2]} mm
    - Viteza vântului: {param_list[3]} km/h

    CERINȚE:
    1. Scrie un rezumat de 2-3 propoziții care să explice cum va fi ziua (ex: aglomerată, normală, lejeră).
    2. Cum crezi că va influența vremea tipul de afecțiuni cu care vor veni pacienții?
    3. Dă 2 recomandări practice pentru personal (ex: suplimentarea personalului, pregătirea anumitor echipamente).
    """

    key = 'AIzaSyA2wWs0_hVQWeYC8mLNCFrGj-y3t1L9fAo'

    # Aici îți pui cheia ta secretă de API
    client = genai.Client(api_key='AIzaSyA2wWs0_hVQWeYC8mLNCFrGj-y3t1L9fAo')

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt_pentru_llm
    )

    print(response.text)

if __name__ == "__main__":
    llm_setup()