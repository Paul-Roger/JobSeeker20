import requests
import json
from hhapp.models import Currency

#returns list with information reqired to connect to hh.ru
def hhlogindata():
    # Opening JSON file
    f = open('.\Cfg\RestAPI.cfg')
    cfgdata = json.load(f)
    cfgdict = cfgdata['hh']
    #Closing file
    f.close()
    return cfgdict


def getAreas():  #returns list of lists with area data [AreaCode, AreaName, ParentCode]
    accessdata = hhlogindata()
    url = accessdata['MainURL']+"/areas"

    req = requests.get(url, verify=False)
    data = req.content.decode()
    req.close()
    jsObj = json.loads(data)
    #pprint(jsObj)
    areas = []
    for k in jsObj:
        #print(k)
        areas.append([k['id'], k['name'], 0])
        for i in range(len(k['areas'])):
            #print(i)
            areas.append([k['areas'][i]['id'],
                          k['areas'][i]['name'],
                          k['areas'][i]['parent_id']])
            if len(k['areas'][i]['areas']) != 0:                      # Если у зоны есть внутренние зоны
                for j in range(len(k['areas'][i]['areas'])):
                    areas.append([k['areas'][i]['areas'][j]['id'],
                                  k['areas'][i]['areas'][j]['name'],
                                  k['areas'][i]['areas'][j]['parent_id']])
    return areas


def getSchedule(): #returns list of lists with Schedule type data [AreaCode, AreaName, ParentCode]
    accessdata = hhlogindata()
    url = accessdata['MainURL']+"/dictionaries"

    req = requests.get(url, verify=False)
    data = req.content.decode()
    req.close()
    #pprint(data)
    jsObj = json.loads(data)
    #pprint(jsObj)
    schedules = []
    sheddict = jsObj['schedule']
    #pprint(jsObj)
    for k in sheddict:
        schedules.append([k['id'], k['name']])
    return schedules

def getType(): #returns list of lists with Schedule type data [AreaCode, AreaName, ParentCode]
    accessdata = hhlogindata()
    url = accessdata['MainURL']+"/dictionaries"

    req = requests.get(url, verify=False)
    data = req.content.decode()
    req.close()
    #pprint(data)
    jsObj = json.loads(data)
    #pprint(jsObj)
    types = []
    typedict = jsObj['employment']
    #pprint(jsObj)
    for k in typedict:
        types.append([k['id'], k['name']])
    return types


def UpdateRates():
    #Get currency data from CBR.ru and update Currency table
        data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js', verify=False).json()
        data1 = data['Valute'].items()
        for i in data1:
            try:
                dbcurr = Currency.objects.get(sym = i[1]["CharCode"])
            except Currency.DoesNotExist:
                dbcurr = None
            if dbcurr == None: #if does not exist - add
                # Create
                Currency.objects.create(name=i[1]["Name"], sym=i[1]["CharCode"], code=i[1]["NumCode"], cbid=i[1]["ID"], rate=i[1]["Value"], nominal=i[1]["Nominal"])
            else: #else update
                dbcurr.name = i[1]["Name"]
                dbcurr.code = i[1]["NumCode"]
                dbcurr.cbid = i[1]["ID"]
                dbcurr.rate = i[1]["Value"]
                dbcurr.nominal = i[1]["Nominal"]
                dbcurr.save()
