import folium
import pandas as pd
import numpy as np
import time
import os
from selenium import webdriver


def main():
    df = pd.read_csv('surf_breaks.csv')
    temp_df = df[df['Fixed'] == 'N']
    start_idx = temp_df.index[0]

    new_lats = np.zeros((len(temp_df)))
    new_longs = np.zeros((len(temp_df)))
    fn='temp_map.html'
    path = path=os.getcwd()

    for idx in range(len(temp_df)):
        lat = temp_df.iloc[idx].Lat
        long = temp_df.iloc[idx].Long

        m = folium.Map(location=[lat,long], zoom_start=18)
        folium.TileLayer(
            tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr = 'Esri',
            name = 'Esri Satellite',
            overlay = False,
            control = True
        ).add_to(m)
        
        kw = {"prefix": "fa", "color": "green", "icon": "arrow-up"}
        angle = 180
        icon = folium.Icon(angle=angle, **kw)
        folium.Marker(location=[lat, long], icon=icon, tooltip=str(angle)).add_to(m)

        m.add_child(
            folium.ClickForMarker('${lat},${lng}')
        )

        # m.show_in_browser()
        tmpurl=f'file://{path}/{fn}'
        m.save(fn)
        browser = webdriver.Chrome()
        browser.get(tmpurl)
        time.sleep(10)

        copied_coords = input(f'{idx+1} New Coordinates: ')
        if copied_coords == 'n':
            new_lats[idx] = float(lat)
            new_longs[idx] = float(long)
        elif copied_coords == 'stop':
            break
        else:
            split_data = copied_coords.split(',')
            new_lats[idx] = float(split_data[0])
            new_longs[idx] = float(split_data[1])

        browser.quit()
        time.sleep(5)

    browser.quit()
    time.sleep(1)
    df.Lat.iloc[start_idx:start_idx+idx] = new_lats[:idx]
    df.Long.iloc[start_idx:start_idx+idx] = new_longs[:idx]
    df.Fixed.iloc[start_idx:start_idx+idx] = 'Y'

    df.to_csv('surf_breaks.csv', index=False)


if __name__ == '__main__':
    main()