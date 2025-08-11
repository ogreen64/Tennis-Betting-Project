import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import json
import random

with open('ATP_Players_2025-08-04.json', 'r') as file: # Set this to the name of the file
    my_dict_1 = json.load(file)
with open('ATP_Players_2020-08-24.json', 'r') as file: # Set this to the name of the file
    my_dict_2 = json.load(file)
my_dict = my_dict_1 | my_dict_2

options = uc.ChromeOptions()
driver = uc.Chrome(options=options)
# driver.set_window_position(1920, 0)

def find(locator):
    return WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(locator))
    
def find_all(locator):
    return WebDriverWait(driver, 10).until(
        EC.visibility_of_all_elements_located(locator))

def click(locator):
    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(locator))
    time.sleep(0.5)
    button.click()

def accept_cookies():
    try:
        click((By.ID,'onetrust-pc-btn-handler'))
        click((By.ID,'accept-recommended-btn-handler'))
    except selenium.common.exceptions.TimeoutException:
        pass

def get_event_name(event):
    event_name = event.find_element(By.CLASS_NAME,'name')
    return event_name.text.strip()

def get_match_length(name):
    if name in ['Australian Open','Roland Garros','Wimbledon','US Open']:
        match_length = 'BO5'
    else:
        match_length = 'BO3'
    return match_length

def get_surface(name):
    if name in ['Singapore','Hangzhou']:
        return 'Hard'
    else:
        surface = find((By.XPATH,'//*[@class="tourn_details"]//*[text()="Clay" or text()="Hard" or text()="Grass"]'))
        return surface.text.strip()

def get_date(event):
    date = event.find_element(By.CLASS_NAME,'Date')
    return date.text.strip()

def convert_date(date):
    day = int(date[:2].strip())
    year = int(date[-4:])
    for month in months:
        if month in date:
            return f'{year}-{months[month]:02}-{day:02}'

def click_toggles():
    toggles = find_all((By.CLASS_NAME, 'atp_accordion-item-toggler'))
    toggles.pop(0)
    for toggle in toggles:
        time.sleep(0.5) 
        toggle.click()
    time.sleep(0.5)
    other_toggles = driver.find_elements(By.CLASS_NAME, 'match-group-toggler')
    if len(other_toggles) > 0:
        driver.execute_script("window.scrollTo(0, 0);")
    for other_toggle in other_toggles:
        time.sleep(0.5)
        other_toggle.click()

def get_round(match):
    round = match.find_element(By.CLASS_NAME,'match-header')
    round = round.text.split(' -')[0]
    return round.strip()

def fix_round(round):
    if round == 'Final' or round == 'Host City Finals':
        return 'Finals'
    elif round == 'Quarterfinals':
        return 'Quarter-Finals'
    elif round == 'Semifinals':
        return 'Semi_Finals'
    elif 'Robin' in round:
        return 'Round Robin'
    else:
        return round

def get_names(match):
    names = match.find_elements(By.CLASS_NAME,'name')
    names = [name.text.split('(')[0] for name in names]
    return [name.strip() for name in names]
    
def get_probability(player,winner):
    if player == winner:
        probability = 1
    else:
        probability = 0
    return probability

def change_date(date):
    while date not in my_dict:
        if date[-2:] != '01':
            date = f'{date[:8]}{int(date[-2:])-1:02}'
        else:
            if date[5:7] != '01':
                date = f'{date[:5]}{int(date[5:7])-1:02}-31'
            else:
                date = f'{int(date[:4])-1}-12-31'
    return date

months = {'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,'July':7,
          'August':8,'September':9,'October':10,'November':11,'December':12}
my_list = []
valid = False

try:
    for year in range(2024,2026): # Set the years to scrape from
        driver.get(f"https://www.atptour.com/en/scores/results-archive?year={year}")
        accept_cookies()
        events = find_all((By.CLASS_NAME,'events'))
        for i in range(len(events)):
            # Gets the list of events every time the page reloads to avoid errors
            events = find_all((By.CLASS_NAME,'events'))
            event = events[i]
            event_name = get_event_name(event)
            if not valid:
                if event_name == 'Winston-Salem': # Set this to the first event to scrape from
                    valid = True
                else:
                    continue
            if ('suspended' in event_name.lower() or 'cancelled' in event_name.lower()
                or 'davis' in event_name.lower()):
                continue
            match_length = get_match_length(event_name)
            date = get_date(event)
            date = convert_date(date)
            click((By.XPATH,f"(//*[@class='events'])[{i+1}]//*[@class='tournament__profile']"))
            surface = get_surface(event_name)
            driver.back()
            try:
                click((By.XPATH,f"(//*[@class='events'])[{i+1}]//*[contains(@class,'atp_button--secondary-transparent')]"))
            except selenium.common.exceptions.TimeoutException:
                print(f'{event_name} {year} has no results')
                continue
            click_toggles()
            matches = find_all((By.CLASS_NAME,'match'))
            for match in matches:
                round = get_round(match)
                round = fix_round(round)
                names = get_names(match)
                if len(names) != 2:
                    continue
                if 'Bye' in names:
                    continue
                winner = names[0]
                random.shuffle(names)
                p1 = names[0]
                p2 = names[1]
                probability = get_probability(p1,winner)
                ranking_date = change_date(date)
                try:
                    p1_rank = my_dict[ranking_date][p1]['rank']
                    p1_age = my_dict[ranking_date][p1]['age']
                    p1_points = my_dict[ranking_date][p1]['points']
                except KeyError:
                    p1_rank = None
                    p1_age = None
                    p1_points = None
                try:
                    p2_rank = my_dict[ranking_date][p2]['rank']
                    p2_age = my_dict[ranking_date][p2]['age']
                    p2_points = my_dict[ranking_date][p2]['points']
                except KeyError:
                    p2_rank = None
                    p2_age = None
                    p2_points = None
                my_sublist = [p1,p2,p1_rank,p2_rank,p1_age,p2_age,p1_points,p2_points,round,
                            event_name,surface,match_length,date,probability]
                my_list.append(my_sublist)
            driver.back()
            print(f'{year} {event_name} complete')
except Exception as e:
    print(e)
    # The name of the file includes the oldest date the data was taken from
    with open(f'ATP_Matches_{my_list[0][-2]}.json', 'w') as file:
        json.dump(my_list, file)
finally:
    driver.quit()