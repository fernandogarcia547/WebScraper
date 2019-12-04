from pandas import Series
import pandas as pd
from pandas import DataFrame
import openpyxl
from openpyxl import load_workbook
from time import localtime, strftime
from utilsScraper import encode

def buscaAutos(tipo,marca,modelo,vVersiones):

    #marca = "nissan"
    #modelo = "versa"
    #vVersiones=['custom','sens','advan']
    execTime = strftime("%d-%m %H:%M", localtime())
    vacio = True
    ### Mercado Libre
    try:
        import scraperML
        dBaseML = pd.read_csv(marca+modelo.title()+'ML'+'.csv')
        #Consulta ultimos anuncios
        dNewAdsML = scraperML.scrapML(marca,modelo,"distrito-federal",2015,5)
        #Obtiene anuncios nuevos
        nullsDb = pd.merge(dNewAdsML,dBaseML,how='left', on=['url'])
        onlyNew=nullsDb[nullsDb.price_y.isnull()][['model_x','price_x','publiDate_x','url','year_x']]
        onlyNew = onlyNew.rename(index=str,columns={'model_x':'model','price_x':'price','publiDate_x':'publiDate','year_x':'year'})
        onlyNew['publiDate'] = execTime
        # Junta con base e imprime
        dBaseML = pd.concat([dBaseML,onlyNew])
        dBaseML = encode(dBaseML)
        dBaseML.to_csv(marca+modelo.title()+'ML'+'.csv',index=False)
    except IOError:
        import scraperML
        dBaseML = scraperML.scrapML(marca,modelo,"distrito-federal",2015)
        dBaseML = encode(dBaseML)
        dBaseML.to_csv(marca+modelo.title()+'ML'+'.csv',index=False)

    ### Segunda Mano
    try:
        import scraperSM
        dBaseSM = pd.read_csv(marca+modelo.title()+'SM'+'.csv')
        #Consulta ultimos anuncios
        dNewAdsSM = scraperSM.scrapSM(tipo,marca,modelo,"ciudad-de-mexico",2015,1)
        #Obtiene anuncios nuevos
        nullsDb = pd.merge(dNewAdsSM,dBaseSM,how='left', on=['url'])
        onlyNew = nullsDb[nullsDb.price_y.isnull()][['model_x','price_x','publiDate_x','url','year_x']]
        onlyNew = onlyNew.rename(index=str,columns={'model_x':'model','price_x':'price','publiDate_x':'publiDate','year_x':'year'})
        onlyNew['publiDate']= execTime + ' ' +onlyNew['publiDate'].astype(str)
        # Junta con base e imprime
        dBaseSM = pd.concat([dBaseSM,onlyNew])
        dBaseSM = encode(dBaseSM)
        dBaseSM.to_csv(marca+modelo.title()+'SM'+'.csv',index=False)
    except IOError:
        import scraperSM
        dBaseSM = scraperSM.scrapSM(tipo,marca,modelo,"ciudad-de-mexico",2015,1)
        dBaseSM = encode(dBaseSM)
        dBaseSM.to_csv(marca+modelo.title()+'SM'+'.csv',index=False)


    frames=[dBaseML,dBaseSM]
    dBase = pd.concat(frames)    
    dBase['model'] = dBase['model'].fillna('')

    WriterYearModel = pd.ExcelWriter(marca+modelo.title()+'.xlsx')
    #Prepare book for writing in existance book
    book = load_workbook('newModels'+'.xlsx')
    WriterOnlyNew = pd.ExcelWriter('newModels'+'.xlsx',engine='openpyxl')
    WriterOnlyNew.book = book
    WriterOnlyNew.sheets = dict((ws.title, ws) for ws in book.worksheets)
    #Crea DataFrame para versiones no encontradas
    foundDict = {'encontrado':[0 for a in range(len(dBase))]}
    found = pd.DataFrame.from_dict(foundDict)
    
    # Busca e imprime versiones
    for version in vVersiones:
        dVersion = dBase.loc[dBase['model'].str.contains(version)]
        found[dBase['model'].str.contains(version).tolist()]=1
        countAdsPerYear = dVersion.groupby(["year"], as_index=False)['model'].count()
        years =  countAdsPerYear.loc[countAdsPerYear['model']>1 
                                    & (countAdsPerYear['year']>2005) ].year.tolist()
        for year in years:
            #dFilterPanda = dBasePanda.loc[dBasePanda['model'].str.contains("sens") 
            #                        & (dBasePanda['year']==2015)]
            dFilter = dVersion.loc[dVersion['year']==year].sort_values(['price'])
            dFilter.to_excel(WriterYearModel,version+str(year),index=False)
            #Review for Printing in Just New Cars
            ptile = dFilter["price"].quantile(.5)
            dBaseNuevos = dFilter.loc[dFilter['publiDate'].str.contains(execTime)
                                   & (dFilter['price']<ptile)]
            if not dBaseNuevos.empty:
                vacio = False
                dFilter.to_excel(WriterOnlyNew,marca[:3]+'_'+modelo+version[:3]+str(year),index=False)
                
            
    # Imprime autos con version no encontrada
    dVersion = dBase.loc[(found['encontrado']==0).tolist()]
    countAdsPerYear = dVersion.groupby(["year"], as_index=False)['model'].count()
    years =  countAdsPerYear.loc[countAdsPerYear['model']>1 
                                    & (countAdsPerYear['year']>2005) ].year.tolist()
    for year in years:
        dFilter = dVersion.loc[dVersion['year']==year].sort_values(['price'])
        dFilter.to_excel(WriterYearModel,'SinVersion'+str(year),index=False)  
        #Review for Printing in Just New Cars
        ptile = dFilter["price"].quantile(.3)
        dBaseNuevos = dFilter.loc[dFilter['publiDate'].str.contains(execTime)
                               & (dFilter['price']<ptile)]
        if not dBaseNuevos.empty:
            vacio = False
            dFilter.to_excel(WriterOnlyNew,marca[:3]+'_'+modelo+'SinVersion'+str(year),index=False)
         
    
    if vacio:
        dFilter.to_excel(WriterOnlyNew,'relleno',index=False)
    WriterYearModel.save()
    WriterOnlyNew.save()
     
    #dFilterPanda.to_csv('out.csv')                            
    #dFilterPanda.price.quantile(.25)

