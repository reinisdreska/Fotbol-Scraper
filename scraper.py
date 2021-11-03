import requests
from bs4 import BeautifulSoup as bs
import datetime as dt
import json

URL = "https://lff.lv/sacensibas/viriesi/optibet-virsliga/"
LAPAS = "lapas/"
DATI = "dati/"

#Lejuplade lapas ----------------------------------------------------------------------------------------------------------------------------------
def saglabat(url, datne):
    rezultats = requests.get(url)
    if rezultats.status_code == 200:
        with open(f"{LAPAS}{datne}", 'w', encoding='UTF-8') as f:
            f.write(rezultats.text)
    else:
        print(f"ERROR: Statusa kods {rezultats.status_code}")


def lejupieladet_lapas():
    saglabat(f"{URL}", f"1_lapa.html")

#lejupieladet_lapas()

def info(datne):
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
        if not tags:
            continue
        spele["menesis"] = tags
        spele["menesis"] = spele["menesis"].text
        if spele["menesis"] == "kārta":
            continue
        spele["menesis"] = menesi.get(spele["menesis"])
        spele["menesis"] = str(spele["menesis"])
        #print("Spēles mēnesis: " + spele["menesis"])
        #atrod speles dienu -----------------------------------------------------
        tags = row.find("h5")
        if not tags:
            continue
        spele["diena"] = tags
        spele["diena"] = spele["diena"].text
        #print("Spēles datums: " + spele["diena"])
        #atrod spele laiku -------------------------------------------------------
        tags = row.find("div", class_="time")
        if not tags:
            continue
        spele["laiks"] = tags
        spele["laiks"] = spele["laiks"].text
        #print("Spēles laiks: " + spele["laiks"])
        #Laiku parveido par stundam ----------------------------------------------
        spele["stunda"] = spele["laiks"]
        spele["stunda"] = spele["stunda"][:-3]
        #print("Spēles sākšanās laiks stundas: " + spele["stunda"])
        #laiku parveido par minutem ----------------------------------------------
        spele["minutes"] = spele["laiks"]
        spele["minutes"] = spele["minutes"][3:]
        #print("Spēles sākšanās laiks minūtēs: " + spele["minutes"])
        #Visus vajadzīgos pārveido pa int-----------------------------------------
        if not spele["stunda"]:
            continue
        spele["stunda"] = int(spele["stunda"])
        spele["minutes"] = int(spele["minutes"])
        spele["menesis"] = int(spele["menesis"])
        spele["diena"] = int(spele["diena"])
        #Time stamp ---------------------------------------------------------------
        spele["date"] = dt.date(spele["gads"], spele["menesis"], spele["diena"])
        spele["time"] = dt.time(spele["stunda"], spele["minutes"])
        spele["timestamp"] = dt.datetime.combine(spele["date"], spele["time"])
        print("Timesamp: ", end =""), print(spele["timestamp"])
        #Atrod arenu --------------------------------------------------------------
        tags = row.find("div", class_="stadium")
        if not tags:
            continue
        spele["arena"] = tags
        spele["arena"] = spele["arena"].text
        print("Spēles arēna: " + spele["arena"])
        #Atrod pirmak kluba nosaukumu ---------------------------------------------
        tags = row.find_all("a")
        if not tags:
            continue
        spele["klubs1"] = tags[0]
        spele["klubs1"] = spele["klubs1"].text
        print("Pirmā kluba nosaukums: " + spele["klubs1"])
        #Atrod pirma kluba rezultatu -----------------------------------------------
        tags = row.find("span", class_="res1")
        if not tags:
            continue
        spele["rezultars1"] = tags
        spele["rezultars1"] = spele["rezultars1"].text
        print("Pirmā kluba rezultāts: " + spele["rezultars1"])
        #Atrod otra kluba rezultatu -------------------------------------------------
        tags = row.find("span", class_="res2")
        if not tags:
            continue
        spele["rezultars2"] = tags
        spele["rezultars2"] = spele["rezultars2"].text
        print("Otrā kluba rezultāts: " + spele["rezultars2"])
        #Atrod atra kluba nosaukumu --------------------------------------------------
        tags = row.find_all("a")
        if not tags:
            continue
        spele["klubs2"] = tags[1]
        spele["klubs2"] = spele["klubs2"].text
        print("Otrā kluba nosaukums: " + spele["klubs2"])
        #Atrod abu komandu linkus ----------------------------------------------------
        tags = row.find_all("a")
        spele["klubslinks"] = tags
        for tag in spele["klubslinks"]:
            print("Koamndu links: https://lff.lv/"+tag["href"])

        print("-------------------------------")    

info(f"lapas/1_lapa.html")
#spele["timestamp"], spele["arena"], spele["klubs1"], spele["rezultars1"], spele["rezultars2"], spele["klubs2"]