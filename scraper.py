#FootBot Scraper V2
import requests
from bs4 import BeautifulSoup as bs
import datetime as dt
import json
import csv

URL = "https://lff.lv/sacensibas/viriesi/optibet-virsliga/"
LAPAS = "lapas/"
DATI = "dati/"

#Lejuplade lapas ----------------------------------------------------------------------------------------------------------------------------------
def Saglabat(url, datne):
    rezultats = requests.get(url)
    if rezultats.status_code == 200:
        with open(f"{LAPAS}{datne}", 'w', encoding='UTF-8') as f:
            f.write(rezultats.text)
    else:
        print(f"ERROR: Statusa kods {rezultats.status_code}")

def Info(datne):
    dati = []
    with open(datne, 'r', encoding='UTF-8') as f:
        html = f.read()

    base = bs(html, "html.parser")

    galvena = base.find_all("tr")
    
    menesi = {"jan": 1, "feb":2, "mar":3, "apr":4, "mai":5, "jūn":6, "jūl":7, "aug":8, "sep":9, "okt":10, "nov":11, "dec":12}
    
    for row in galvena:
        spele = {}
        #Hardcode ka gads vienmer ir 2021 ---------------------------------------
        spele["gads"] = 2021
        #Atrod spele menesi -----------------------------------------------------
        tags = row.find("h6")
        if not tags or tags.text == "kārta":
            continue
        spele["menesis"] = int(menesi.get(tags.text))
        #atrod speles dienu -----------------------------------------------------
        tags = row.find("h5")
        if not tags:
            continue
        spele["diena"] = int(tags.text)
        #atrod spele laiku -------------------------------------------------------
        tags = row.find("div", class_="time")
        if not tags or not tags.text[:-3]:
            continue
        #laiku parveido par stundam ----------------------------------------------
        spele["stunda"] = int(tags.text[:-3])
        #laiku parveido par minutem ----------------------------------------------
        spele["minutes"] = int(tags.text[3:])
        #Time stamp ---------------------------------------------------------------
        spele["timestamp"] = str(dt.datetime.combine(dt.date(2021, spele["menesis"], spele["diena"]), dt.time(spele["stunda"], spele["minutes"])))
        print("Timestamp: ", spele["timestamp"])
        #Atrod arenu --------------------------------------------------------------
        tags = row.find("div", class_="stadium")
        if not tags:
            continue
        spele["arena"] = tags.text
        print("Spēles arēna: " + spele["arena"])
        #Atrod kluba nosaukumus ---------------------------------------------
        tags = row.find_all("a")
        if not tags:
            continue
        spele["klubs1"] = tags[0].text
        spele["klubs2"] = tags[1].text
        print("Pirmā kluba nosaukums: " + spele["klubs1"])
        #Atrod pirma kluba rezultatu -----------------------------------------------
        tags = row.find("span", class_="res1")
        if not tags:
            continue
        spele["rezultats1"] = tags.text
        print("Pirmā kluba rezultāts: " + spele["rezultats1"])
        #Atrod otra kluba rezultatu -------------------------------------------------
        tags = row.find("span", class_="res2")
        if not tags:
            continue
        spele["rezultats2"] = tags.text
        print("Otrā kluba rezultāts: " + spele["rezultats2"])
        #Atrod atra kluba nosaukumu --------------------------------------------------
        print("Otrā kluba nosaukums: " + spele["klubs2"])
  
        tags = row.find_all("a")
        for tag in tags:
            print("Koamndu links: https://lff.lv/"+tag["href"])

        print("-------------------------------------------")  

        dati.append({"timestamp": spele["timestamp"], "arena": spele["arena"], "klubs1": spele["klubs1"], "rezultats1": spele["rezultats1"], "klubs2": spele["klubs2"], "rezultats2": spele["rezultats2"]})
    return dati

def TableData(dati, table_data):
    for i in table_data:
        table_data[i]["skaits"] = 0
        table_data[i]["uzvaras"] = 0
        table_data[i]["neiskirts"] = 0
        table_data[i]["zaudejumi"] = 0
        table_data[i]["varti"] = 0
        table_data[i]["ielaistie_varti"] = 0
        table_data[i]["vartu_starpiba"] = 0
        table_data[i]["punkti"] = 0


    for i in dati:
        table_data[i["klubs1"]]["skaits"] += 1
        table_data[i["klubs2"]]["skaits"] += 1

        if i["rezultats1"] > i["rezultats2"]:
            table_data[i["klubs1"]]["uzvaras"] += 1
            table_data[i["klubs2"]]["zaudejumi"] += 1
        elif i["rezultats1"] < i["rezultats2"]:
            table_data[i["klubs1"]]["zaudejumi"] += 1
            table_data[i["klubs2"]]["uzvaras"] += 1
        elif i["rezultats1"] != "-" and i["rezultats1"] == i["rezultats2"]:
            table_data[i["klubs1"]]["neiskirts"] += 1
            table_data[i["klubs2"]]["neiskirts"] += 1
        else:
            continue

        table_data[i["klubs1"]]["varti"] += int(i["rezultats1"])
        table_data[i["klubs2"]]["varti"] += int(i["rezultats2"])

        table_data[i["klubs1"]]["ielaistie_varti"] += int(i["rezultats2"])
        table_data[i["klubs2"]]["ielaistie_varti"] += int(i["rezultats1"])

    for i in table_data:
        table_data[i]["vartu_starpiba"] = table_data[i]["varti"] - table_data[i]["ielaistie_varti"]
        table_data[i]["punkti"] = table_data[i]["uzvaras"] * 3 + table_data[i]["neiskirts"]

    return table_data

def Table(table_data):
    print()
    print("|-----------------------------------------|")
    print("|Komandas        |S |U |N |Z |GV|ZV|VA |P |")
    print("|-----------------------------------------|")
    for i in table_data:
        print("|{:<16}|{:<2}|{:<2}|{:<2}|{:<2}|{:<2}|{:<2}|{:<3}|{:<2}|".format(i, table_data[i]["skaits"], table_data[i]["uzvaras"], table_data[i]["neiskirts"], table_data[i]["zaudejumi"],  table_data[i]["varti"], table_data[i]["ielaistie_varti"], table_data[i]["vartu_starpiba"], table_data[i]["punkti"]))
        print("|-----------------------------------------|")

def Saglabat_datus(dati):
    with open(f"{DATI}speles_dati.csv", 'w', encoding='UTF-8', newline="") as f:
        kolonu_nosaukumi = ["timestamp", "arena", "klubs1", "rezultats1", "rezultats2", "klubs2"]
        w = csv.DictWriter(f, fieldnames= kolonu_nosaukumi)
        w.writeheader()
        for speles in dati:
            w.writerow(speles)

def Izvilkt_datus():
    visi_dati = []
    datne = f"{LAPAS}1_lapa.html"
    datnes_dati = Info(datne)
    visi_dati += datnes_dati
    Saglabat_datus(visi_dati)
Izvilkt_datus()

Saglabat(f"{URL}", f"1_lapa.html")
data = Info(f"lapas/1_lapa.html")

with open("speles_dati.json", "w") as outfile:
    json.dump(data, outfile)

table_data = {"RFS":{}, "Valmiera FC":{}, "Riga FC":{}, "FK Liepāja":{}, "FK Spartaks":{}, "BFC Daugavpils":{}, "FK Metta":{}, "FC Noah Jurmala":{}}
table_data = TableData(data, table_data)
Table(table_data)




#FootBot ScraperV1
# import requests
# from bs4 import BeautifulSoup as bs
# import datetime as dt
# import json
# import csv

# URL = "https://lff.lv/sacensibas/viriesi/optibet-virsliga/"
# LAPAS = "lapas/"
# DATI = "dati/"

# #Lejuplade lapas ----------------------------------------------------------------------------------------------------------------------------------
# def saglabat(url, datne):
#     rezultats = requests.get(url)
#     if rezultats.status_code == 200:
#         with open(f"{LAPAS}{datne}", 'w', encoding='UTF-8') as f:
#             f.write(rezultats.text)
#     else:
#         print(f"ERROR: Statusa kods {rezultats.status_code}")


# def lejupieladet_lapas():
#     saglabat(f"{URL}", f"1_lapa.html")

# #lejupieladet_lapas()

# def info(datne):
#     dati = []
#     with open(datne, 'r', encoding='UTF-8') as f:
#         html = f.read()

#     base = bs(html, "html.parser")

#     galvena = base.find_all("tr")
    
#     menesi = {"jan": 1, "feb":2, "mar":3, "apr":4, "mai":5, "jūn":6, "jūl":7, "aug":8, "sep":9, "okt":10, "nov":11, "dec":12}
    

#     for row in galvena:
#         spele = {}
#         #Hardcode ka gads vienmer ir 2021 ---------------------------------------
#         spele["gads"] = 2021
#         #Atrod spele menesi -----------------------------------------------------
#         tags = row.find("h6")
#         if not tags:
#             continue
#         spele["menesis"] = tags
#         spele["menesis"] = spele["menesis"].text
#         if spele["menesis"] == "kārta":
#             continue
#         spele["menesis"] = menesi.get(spele["menesis"])
#         spele["menesis"] = str(spele["menesis"])
#         #print("Spēles mēnesis: " + spele["menesis"])
#         #atrod speles dienu -----------------------------------------------------
#         tags = row.find("h5")
#         if not tags:
#             continue
#         spele["diena"] = tags
#         spele["diena"] = spele["diena"].text
#         #print("Spēles datums: " + spele["diena"])
#         #atrod spele laiku -------------------------------------------------------
#         tags = row.find("div", class_="time")
#         if not tags:
#             continue
#         spele["laiks"] = tags
#         spele["laiks"] = spele["laiks"].text
#         #print("Spēles laiks: " + spele["laiks"])
#         #Laiku parveido par stundam ----------------------------------------------
#         spele["stunda"] = spele["laiks"]
#         spele["stunda"] = spele["stunda"][:-3]
#         #print("Spēles sākšanās laiks stundas: " + spele["stunda"])
#         #laiku parveido par minutem ----------------------------------------------
#         spele["minutes"] = spele["laiks"]
#         spele["minutes"] = spele["minutes"][3:]
#         #print("Spēles sākšanās laiks minūtēs: " + spele["minutes"])
#         #Visus vajadzīgos pārveido pa int-----------------------------------------
#         if not spele["stunda"]:
#             continue
#         spele["stunda"] = int(spele["stunda"])
#         spele["minutes"] = int(spele["minutes"])
#         spele["menesis"] = int(spele["menesis"])
#         spele["diena"] = int(spele["diena"])
#         #Time stamp ---------------------------------------------------------------
#         spele["timestamp"] = str(dt.datetime.combine(dt.date(spele["gads"], spele["menesis"], spele["diena"]), dt.time(spele["stunda"], spele["minutes"])))
#         print("Timestamp: ", end =""), print(spele["timestamp"])
#         #Atrod arenu --------------------------------------------------------------
#         tags = row.find("div", class_="stadium")
#         if not tags:
#             continue
#         spele["arena"] = tags
#         spele["arena"] = spele["arena"].text
#         print("Spēles arēna: " + spele["arena"])
#         #Atrod pirmak kluba nosaukumu ---------------------------------------------
#         tags = row.find_all("a")
#         if not tags:
#             continue
#         spele["klubs1"] = tags[0]
#         spele["klubs1"] = spele["klubs1"].text
#         print("Pirmā kluba nosaukums: " + spele["klubs1"])
#         #Atrod pirma kluba rezultatu -----------------------------------------------
#         tags = row.find("span", class_="res1")
#         if not tags:
#             continue
#         spele["rezultats1"] = tags
#         spele["rezultats1"] = spele["rezultats1"].text
#         print("Pirmā kluba rezultāts: " + spele["rezultats1"])
#         #Atrod otra kluba rezultatu -------------------------------------------------
#         tags = row.find("span", class_="res2")
#         if not tags:
#             continue
#         spele["rezultats2"] = tags
#         spele["rezultats2"] = spele["rezultats2"].text
#         print("Otrā kluba rezultāts: " + spele["rezultats2"])
#         #Atrod atra kluba nosaukumu --------------------------------------------------
#         tags = row.find_all("a")
#         if not tags:
#             continue
#         spele["klubs2"] = tags[1]
#         spele["klubs2"] = spele["klubs2"].text
#         print("Otrā kluba nosaukums: " + spele["klubs2"])
#         #Atrod abu komandu linkus ----------------------------------------------------
#         tags = row.find_all("a")
#         spele["klubslinks"] = tags
#         for tag in spele["klubslinks"]:
#             print("Koamndu links: https://lff.lv/"+tag["href"])

#         print("-------------------------------")    
        
#         speles_dati = {}
#         speles_dati["timestamp"] = spele["timestamp"]
#         speles_dati["arena"] = spele["arena"]
#         speles_dati["klubs1"] = spele["klubs1"]
#         speles_dati["rezultats1"] = spele["rezultats1"]
#         speles_dati["rezultats2"] = spele["rezultats2"]
#         speles_dati["klubs2"] = spele["klubs2"]

#         dati.append(speles_dati)
#     return dati

# dati = info(f"lapas/1_lapa.html")
# with open("speles_dati.json", "w", encoding='UTF-8') as outfile:
#     json.dump(dati, outfile)

# def saglabat_datus(dati):
#     with open(f"{DATI}speles_dati.csv", 'w', encoding='UTF-8', newline="") as f:
#         kolonu_nosaukumi = ["timestamp", "arena", "klubs1", "rezultats1", "rezultats2", "klubs2"]
#         w = csv.DictWriter(f, fieldnames= kolonu_nosaukumi)
#         w.writeheader()
#         for speles in dati:
#             w.writerow(speles)

# def izvilkt_datus():
#     visi_dati = []
#     datne = f"{LAPAS}1_lapa.html"
#     datnes_dati = info(datne)
#     visi_dati += datnes_dati
#     saglabat_datus(visi_dati)
# izvilkt_datus()