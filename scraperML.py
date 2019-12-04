from IPython.display import HTML
import numpy as np
import urllib2
import bs4 #this is beautiful soup
import time
import operator
import socket
import cPickle
import re # regular expressions
import math
import unicodedata
from pandas import Series
import pandas as pd
from pandas import DataFrame
import matplotlib
import matplotlib.pyplot as plt
from secret import *
from selenium import webdriver
from collections import Counter
from utilsScraper import extractNumbers

def scrapML(marca,modelo,zona,anio,numPages=None):
    # Variables para baseUrl fija
    #marca = "nissan"
    #modelo = "versa"
    #zona = "distrito-federal"
    #anio = "2015"

    # Create baseUrl
    baseUrl = "https://autos.mercadolibre.com.mx/"+marca+"/"+modelo+"/"+zona

    # Read the website
    source = urllib2.urlopen(baseUrl).read()
    # parse html code
    bs_tree = bs4.BeautifulSoup(source,"html5lib")


    # Count number of results
    mainTree = bs_tree.find(id = 'inner-main')
    allAreas = mainTree.findAll("div")
    numResultsString = [nR.text for nR in allAreas if not nR.get('class') is None 
                        and ''.join(nR.get('class')) =="quantity-results"]                    
    numResults = extractNumbers(numResultsString[0])

    vPrice = []
    vUrl = []
    vTitle = []
    vKms = []
    vYear = []
    
    if numPages is None:
        numPages = int(math.ceil(numResults/48.))
    
    for i in range(numPages): #do range(num_pages) if you want them all
        url = baseUrl + '_Desde_' + str((48*i)+1)
        html_page = urllib2.urlopen(url).read() 
        bs_tree = bs4.BeautifulSoup(html_page)
        ## Get the price per car                    
        resultsSection = bs_tree.find(id = 'searchResults')
        ListCarAds = resultsSection.findAll("li")
        allCarAds = [ca for ca in ListCarAds if not ca.get('class') is None 
                        and (''.join(ca.get('class')) =="results-itemarticlegrid"
                        or   ''.join(ca.get('class')) =="results-itemarticlegridproductitem-with-attributes"
                        or   ''.join(ca.get('class')) =="results-itemarticlestack")]                
        # Extract URL
        # allImagesViewer = resultsSection.findAll('div' , class_="images-viewer")  
        # urls = urls + [jp.get('item-url') for jp in allImagesViewer]
      
        time.sleep(1)
        for j in range(len(allCarAds)):
            ## Extract price
            priceString = allCarAds[j].find_all('span', class_="price-fraction")[0].text
            price = extractNumbers(priceString)
            vPrice.append(price)
            ## Extract main title
            mainTitle = allCarAds[j].find_all('span', class_="main-title")[0].text
            #mainTitleNorm = unicodedata.normalize('NFKD',mainTitle).encode('ascii','ignore')
            vTitle.append(mainTitle)
            ## Extract Year and Km
            itemAttributes = allCarAds[j].find_all('div', class_="item__attrs")[0].text
            itemAttNorm = unicodedata.normalize('NFKD',itemAttributes).encode('ascii','ignore')
            itemAttDigits = [int(d) for d in itemAttNorm if d.isdigit()]
            kmsCar = np.sum([digit*(10**exponent) for digit, exponent in 
                        zip(itemAttDigits[::-1], range(len(itemAttDigits)-4))])
            vKms.append(kmsCar)
            yearCar = np.sum([digit*(10**exponent) for digit, exponent in 
                        zip(itemAttDigits[3::-1], range(4))])
            vYear.append(yearCar)
            ## Extract URL
            imageViewer = allCarAds[j].find_all('div' , class_="images-viewer")
            carUrl = [jp.get('item-url') for jp in imageViewer][0]
            carUrl = unicodedata.normalize('NFKD',carUrl).encode('ascii','ignore') 
            vUrl.append(carUrl)
            
    #Cleaning Models
    vTitleClean = [unicodedata.normalize('NFKD',t).encode('ascii','ignore') for t in vTitle]
    vTitleClean = [t.strip().lower().replace(marca+' '+modelo,'') for t in vTitleClean]

    dBaseListDict = []
    for i in range(len(vTitleClean)):
        dBaseListDict.append({'model':vTitleClean[i],'year':vYear[i],'price':vPrice[i],'url':vUrl[i],'publiDate':''})
        
    dBasePanda = pd.DataFrame.from_dict(dBaseListDict)
    
    return dBasePanda