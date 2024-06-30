import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
import folium
import numpy as np


def parse_regions(soup, breaks):
    '''
    Used to recursively parse through the countries and subregions until the surf break information page
    is reached.
    '''
    spots_list = soup.find('div', attrs={'class':'block spot-list'})
    
    if spots_list:
        spots = spots_list.findAll('a', attrs={'class':'country'})
        for spot in spots:
            url = spot.attrs['href']
            req = requests.get(url)
            local_soup = BeautifulSoup(req.content, 'html.parser')
            found_spots = parse_regions(local_soup, breaks)
            breaks.extend(found_spots)
    else:
        try:
            regional_spots = soup.find('table', attrs={'class':'spotTable'}).findAll('a')
            return regional_spots
        except AttributeError as e:
            return []
    
    return []
        
# request inital page with all starting links and identify all links to available breaks on the site
url = 'https://surfing-waves.com/atlas.html'
req = requests.get(url)   # send request to the starting url
soup = BeautifulSoup(req.content, 'html.parser')

breaks = []
parse_regions(soup, breaks)

# parse the page of each surf break and save off relevant data
data = []
for b in breaks:
    surl = b.attrs['href']
    sreq = requests.get(surl)
    ssoup = BeautifulSoup(sreq.content, 'html.parser')

    country = re.search(r'\/atlas\/\w+\/(\w+)', surl).group(1)
    
    latlong = re.search(r'=(-?\d+\.\d+),(-?\d+\.\d+)', ssoup.find('div', attrs={'class':'map big_map responsive_map'}).iframe.attrs['src'])
    lat = latlong.group(1)
    long = latlong.group(2)
    
    dets = ssoup.find('table', attrs={'class':'spot-details'})
    wave_type = dets.findAll('td')[1].text
    direction = dets.findAll('td')[2].text
    bottom = dets.findAll('td')[3].text
    difficulty = dets.findAll('td')[4].text
    
    data.append([country, b.text, lat, long, wave_type, direction, bottom, difficulty])

# save data to a csv
df = pd.DataFrame(np.array(data),
                   columns=['Country', 'Break', 'Lat', 'Long', 'Wave_type', 'Direction', 'Bottom', 'Difficulty'])
df.to_csv('surf_breaks.csv', index=False)

# map each break found as a spot check to ensure the parsing worked correctly
# Make an empty map
m = folium.Map(location=[20,0], tiles="OpenStreetMap", zoom_start=3)

for i in range(len(df)):
    folium.Marker(
        location=[df.iloc[i]['Lat'], df.iloc[i]['Long']],
        popup=df.iloc[i]['Break'],
    ).add_to(m)

# Show the map again
m.show_in_browser()
