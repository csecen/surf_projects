import csv
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup, Comment
import folium

def parse_regions(soup, spotss):
    spots_list = soup.find('div', attrs={'class':'block spot-list'})
    
    if spots_list:
        spots = spots_list.findAll('a', attrs={'class':'country'})
        for i in range(len(spots)):
            url = spots[i].attrs['href']
            req = requests.get(url)
            soup2 = BeautifulSoup(req.content, 'html.parser')
            found_spots = parse_regions(soup2, spotss)
            spotss.extend(found_spots)
    else:
        try:
            regional_spots = soup.find('table', attrs={'class':'spotTable'}).findAll('a')
            return regional_spots
        except AttributeError as e:
            return []
    
    return []
        

url = 'https://surfing-waves.com/atlas.html'
req = requests.get(url)
soup = BeautifulSoup(req.content, 'html.parser')
spotss = []
parse_regions('atlas', soup, spotss)
print(spotss)
