from selenium import webdriver
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import requests
from bs4 import BeautifulSoup, Comment


def parse_round(round_url, base_url):
    round_r = requests.get(round_url)
    round_soup = BeautifulSoup(round_r.content, 'html.parser')

    all_heats = round_soup.select('[class="hot-heat__action-link"]')
    return [f'{base_url}{heat["href"]}' for heat in all_heats]


def get_heat_urls(years):
    base_url = 'https://www.worldsurfleague.com'
    
    heat_urls = set()

    for year in years:
        url = f'{base_url}/events/{year}/ct?all=1'
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')

        events = soup.find_all('a', attrs={'class':'event-schedule-details__event-name'})

        for event in events[6:7]:
            event_r = requests.get(event['href'])
            event_soup = BeautifulSoup(event_r.content, 'html.parser')
            replay_link = event_soup.find('a', string='Replay')
            replay_url = f'{base_url}{replay_link["href"]}'

            heat_urls.add(replay_url)

            # parse opening round
            round_r = requests.get(replay_url)
            round_soup = BeautifulSoup(round_r.content, 'html.parser')
            
            round_urls = parse_round(replay_url, base_url)
            heat_urls.update(round_urls)

            # parse elimination round
            elim_link = round_soup.find(lambda tag: tag.name == "a" and 'Elimination Round' in tag.text)
            elim_url = f'{base_url}{elim_link["href"]}'

            round_urls = parse_round(elim_url, base_url)
            heat_urls.update(round_urls)

            # parse bracket stage
            bracket_link = round_soup.find(lambda tag: tag.name == "a" and 'Bracket Stage' in tag.text)
            bracket_url = f'{base_url}{bracket_link["href"]}'

            round_urls = parse_round(bracket_url, base_url)
            heat_urls.update(round_urls)
            
    return list(heat_urls)



def main():

    # parser = argparse.ArgumentParser(description='Input JSON file with required credentials')
    # parser.add_argument('filename', help='name of credentials file')
    # args = parser.parse_args()

    # config_file = vars(args)['filename']
    # config_file = './utils/config.json'

    # with open(config_file, 'r') as f:
    #     config = json.load(f)

    # years = config['years']
    # scores_only = config['scores_only']

    years = ['2024']
    heat_urls = get_heat_urls(years)
    for u in heat_urls:
        print(u)


if __name__ == '__main__':
    main()
    




# r = requests.get(url)   # send request to the starting url
# soup = BeautifulSoup(r.content, 'html.parser')
# eventsRaw = soup.findAll('span', attrs={'class':'tour-event-name'})
# events = [e.text for e in eventsRaw]   # collect all names of the events that happened in the corresponding year

# driver = webdriver.Chrome('/usr/bin/chromedriver')   # create an instance of a selenium web driver
# driver.get(url)