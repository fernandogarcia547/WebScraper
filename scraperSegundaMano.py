# Variables para baseUrl fija
marca = "nissan"
modelo = "versa"
zona = "ciudad-de-mexico"
anio = "2015"

# Create baseUrl

baseUrl = "https://www.segundamano.mx/anuncios/"+zona+"/autos/"+marca+"?q="+modelo
### Get Browser for extracting number Ads
chromeOptions = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images":2}
chromeOptions.add_experimental_option("prefs",prefs)
browser = webdriver.Chrome("C:/Users/Fernando/Anaconda3/envs/py2/Lib/site-packages/selenium/webdriver/chrome/chromedriver.exe",chrome_options=chromeOptions)
#browser = webdriver.Chrome("C:/Users/Fernando/Anaconda3/envs/py2/Lib/site-packages/selenium/webdriver/chrome/chromedriver.exe")  # can be Firefox(), PhantomJS() and more
browser.get(baseUrl) #navigate to the page
innerHTML = browser.execute_script("return document.body.innerHTML")
bs_tree = bs4.BeautifulSoup(innerHTML,'html.parser')
#mainTree = bs_tree.find(id = 'top-filters-listing-box')
#numResultsString = mainTree.findAll("span",style="")[0].text
numResultsString = bs_tree.findAll("h1",class_="ad-listing-title")[0].text
numResultsDigits = [int(d) for d in numResultsString if d.isdigit()]
numResults = np.sum([digit*(10**exponent) for digit, exponent in 
                    zip(numResultsDigits[::-1], range(len(numResultsDigits)))])

num_pages = 5 # int(math.ceil(numResults/36.))

vPrice = []
vUrl = []
vTitle = []
vKms = []
vYear = []
vTranss = []
vModel = []
vLocation = []
vPubliDate = []
vName = []
vAdInfo = []

url = baseUrl + '&page=' + str(num_pages)
browser.get(url) #navigate to the page
time.sleep(4)
innerHTML = browser.execute_script("return document.body.innerHTML")
bs_tree = bs4.BeautifulSoup(innerHTML,'html.parser')
allAds=bs_tree.findAll("a",class_="wrapped-link")

for j in range(len(allAds)):
    print(j)
    #Url
    carUrl = allAds[j].get('href')
    vUrl.append("https://www.segundamano.mx"+carUrl)
    #Price
    priceString = allAds[j].findAll("div",class_="ad-price")[0].text
    priceDigits = [int(d) for d in priceString if d.isdigit()]
    price = np.sum([digit*(10**exponent) for digit, exponent in 
                    zip(priceDigits[::-1], range(len(priceDigits)))])
    vPrice.append(price)
    #Title
    #try:
    #    title = data["itemListElement"][j]["item"]["name"]
    #    vTitle.append(title)
    #except KeyError:
    #    vTitle.append('s/t')
    
    ## Enter per add page 
    browser.get("https://www.segundamano.mx"+carUrl) #navigate to the page
    time.sleep(4)
    innerHTML = browser.execute_script("return document.body.innerHTML")
    bs_tree = bs4.BeautifulSoup(innerHTML,'html.parser')    
    ## Extract info from per add page
    #km
    #vKmstring = bs_tree.findAll("div",class_="av-IconDetailTextValue")[3].text
    #kmDigits = [int(d) for d in vKmstring if d.isdigit()]
    #km = np.sum([digit*(10**exponent) for digit, exponent in 
    #                    zip(kmDigits[::-1], range(len(kmDigits)))])
    #vKms.append(km)
    #year
    try:
        yearString = bs_tree.findAll("div",class_="av-IconDetailTextValue")[1].text
        yearDigits = [int(d) for d in yearString if d.isdigit()]
        year = np.sum([digit*(10**exponent) for digit, exponent in 
                            zip(yearDigits[::-1], range(len(yearDigits)))])
        vYear.append(year)
    except IndexError:
        vYear.append(0)
    vAdInfo.append(bs_tree.findAll("div",class_="av-AdInformation-info"))
      
browser.close()

for i in range(len(vAdInfo)):
    model=''
    ubicacion=''
    publiDate = ''
    name = ''
    for j in range(len(vAdInfo[i])):
        text = unicodedata.normalize('NFKD',vAdInfo[i][j].text).encode('ascii','ignore') 
        if 'Version:' in text:
            model = text.replace('\n','').replace('Version:','').lower()
        elif 'Ubicacion:' in text:
            ubicacion = text.replace('\n','').replace('Ubicacion:','')
        elif 'Publicado:' in text:
            publiDate = text.replace('\n','').replace('Publicado:','')
        elif 'Modelo :' in text:
            name = text.replace('\n','').replace('Modelo :','').replace(',','-')
    vModel.append(model.strip())
    vPubliDate.append(publiDate.strip())
    vLocation.append(ubicacion.strip())
    vName.append(name.strip())
    
#csvWriter('versaSM.csv',zip(vModel,vYear,vPrice,vUrl,vPubliDate))

df = pd.DataFrame.from_records(vYear)

dBaseListDict = []
for i in range(len(vModel)):
    dBaseListDict.append({'model':vModel[i],'year':vYear[i],'price':vPrice[i],'url':vUrl[i],'publiDate':vPubliDate[i]})
    
dBasePanda = pd.DataFrame.from_dict(dBaseListDict)

dFilterPanda = dBasePanda.loc[dBasePanda['model'].str.contains("sens") 
                                & (dBasePanda['year']==2015)]

dFilterPanda.to_csv('out.csv')
                                
dFilterPanda.price.quantile(.25)

import openpyxl
writer = pd.ExcelWriter('output.xlsx')
dFilterPanda.to_excel(writer,'Sheet1')
dFilterPanda.to_excel(writer,'Sheet2')
writer.save()

frames=[dBasePanda2,dBasePanda]
result = pd.concat(frames)