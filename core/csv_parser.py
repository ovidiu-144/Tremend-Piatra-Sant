import pandas as pd
import os

def get_data_from_adm_1():
    base_path = os.path.dirname(__file__) 
    path_admisie = os.path.abspath(os.path.join(base_path, '..', 'data', 'admission_data.csv'))

    adm_data = pd.read_csv(path_admisie, usecols=[2])
    
    adm_data['D.O.A'] = pd.to_datetime(adm_data['D.O.A'], format='mixed', dayfirst=False, errors='coerce')
    
    adm_data_daily = adm_data.groupby('D.O.A').size().reset_index(name='patient_count')

    adm_data_daily = adm_data_daily.rename(columns={'D.O.A': 'datetime'})

    #print(adm_data_daily)

    return adm_data_daily

def get_data_from_adm_2():
    base_path = os.path.dirname(__file__) 
    path_admisie = os.path.abspath(os.path.join(base_path, '..', 'data', 'admission_data_2.csv'))

    adm_data = pd.read_csv(path_admisie, usecols=[2])
    
    adm_data['D.O.A'] = pd.to_datetime(adm_data['D.O.A'], format='mixed', dayfirst=True, errors='coerce')
    
    adm_data_daily = adm_data.groupby('D.O.A').size().reset_index(name='patient_count')

    adm_data_daily = adm_data_daily.rename(columns={'D.O.A': 'datetime'})

    #print(adm_data_daily.dtypes)

    return adm_data_daily

def get_data_from_meteo():
    base_path = os.path.dirname(__file__) 
    path_meteo = os.path.abspath(os.path.join(base_path, '..', 'data', 'meteo.csv'))

    meteo_data = pd.read_csv(path_meteo, usecols=[1, 4, 9, 10, 14, 17])

    meteo_data['datetime'] = pd.to_datetime(meteo_data['datetime'])

    #print(meteo_data)

    return meteo_data

def merge_data():
    adm_1 = get_data_from_adm_1()
    adm_2 = get_data_from_adm_2()

    adm = pd.concat([adm_1, adm_2])

    met = get_data_from_meteo()

    final_data = pd.merge(adm, met, on='datetime')

    #print(final_data.dtypes)

    return final_data

if __name__ == "__main__":
    merge_data()