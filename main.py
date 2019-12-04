# Variables para baseUrl fija
marca = "nissan"
modelo = "versa"
zona = "distrito-federal"
anio = "2015"

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
numResultsDigits = [int(d) for d in numResultsString[0] if d.isdigit()]
numResults = np.sum([digit*(10**exponent) for digit, exponent in 
                    zip(numResultsDigits[::-1], range(len(numResultsDigits)))])

vPrice = []
vUrl = []
vTitle = []
vKms = []
vYear = []

for i in range(int(math.ceil(numResults/48.))): #do range(num_pages) if you want them all
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
        priceDigits = [int(d) for d in priceString if d.isdigit()]
        price = np.sum([digit*(10**exponent) for digit, exponent in 
                    zip(priceDigits[::-1], range(len(priceDigits)))])
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
vTitleClean = [t.replace(',',';').lower() for t in vTitleClean]

csvWriter('versaML.csv',zip(vTitleClean,vYear,vPrice,vUrl))
#vTitleClean = [(''.join([i for i in s if not i.isdigit()])) for s in vTitleClean ]

allWordsTitles = [t.split() for t in vTitleClean]
flat_list = [item for sublist in allWordsTitles for item in sublist]
counter = Counter(flat_list)

#from collections import OrderedDict
#counterOrdered = OrderedDict(sorted(counter.items(),
#                key=lambda counter: counter[1], reverse=True))
counterOrdered = sorted(counter.items(), key=operator.itemgetter(1), reverse=True)
vTitleCleanNew = vTitleClean   
for model in counterOrdered:
 for i in range(len(vTitleClean)):
    if len(model[0])>1 and model[0] in vTitleClean[i]:
        vTitleCleanNew[i] = model[0]
    else:
        vTitleCleanNew[i] = vTitleClean[i]
        
