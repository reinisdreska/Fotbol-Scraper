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

lejupieladet_lapas()