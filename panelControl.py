import pandas as pd
import numpy as np
from buscaAutos import buscaAutos
from utilsScraper import is_number

models=pd.read_csv('baseModelos.csv')
numModels = np.sum(models['marca'].notnull().tolist())

for i in range(numModels):
    carDetail=models.iloc[i][models.iloc[i].notnull()].tolist()
    tipo = carDetail[0]
    marca = carDetail[1]
    if is_number(carDetail[2]):
        modelo = str(carDetail[2])
    else:
        modelo = carDetail[2]
    vVersiones = carDetail[3:]
    buscaAutos(tipo,marca,modelo,vVersiones)
    
    
