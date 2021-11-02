import requests
import time
from bs4 import BeautifulSoup as bs
import csv

URL = "https://lff.lv/sacensibas/viriesi/optibet-virsliga/"
LAPAS = "lapas/"
DATI = "dati/"

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
    

    for row in galvena:
        spele = {}

        tags = row.find_all("h6")
        if not tags:
            continue
        spele["menesis"] = tags
        spele["menesis"] = str(spele["menesis"])
        size = len(spele["menesis"])
        spele["menesis"] = spele["menesis"][5:size - 6]
        #print(spele["menesis"])

        tags = row.find_all("h5")
        if not tags:
            continue
        spele["diena"] = tags
        spele["diena"] = str(spele["diena"])
        size = len(spele["diena"])
        spele["diena"] = spele["diena"][5:size - 6]
        #print(spele["diena"])

        tags = row.find_all("div", class_="stadium")
        if not tags:
            continue
        spele["arena"] = tags
        spele["arena"] = str(spele["arena"])
        size = len(spele["arena"])
        spele["arena"] = spele["arena"][22:size - 7]
        #print(spele["arena"])
        

info(f"lapas/1_lapa.html")