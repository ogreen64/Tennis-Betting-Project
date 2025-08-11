import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import json
import random

options = uc.ChromeOptions()
driver = uc.Chrome(options=options)
driver.set_window_position(1920, 0)

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
    except Exception:
        pass

# This function gives me a list of dates needed for the link to each page I want to scrape
def get_dates_list():
    driver.get("https://www.atptour.com/en/rankings/singles"
            "?rankRange=1-5000&dateWeek=Current+Week")
    accept_cookies()
    dates = find_all((By.CSS_SELECTOR,'#dateWeek-filter *'))
    dates = [date.get_attribute('value') for date in dates]
    # The first element of the list is 'Current Week' so this needs to be changed to a date
    dates[0] = '2025-08-04' # Set this to the date of the most recent rankings
    dates = dates[dates.index('2025-08-04'):dates.index('2020-08-24')+1] # Set the dates to scrape from and to
    print('Dates acquired')
    return dates

def scrape_page(date):
    driver.get(f"https://www.atptour.com/en/rankings/singles?"
               f"rankRange=1-5000&dateWeek={date}")
    rows = find_all((By.CSS_SELECTOR,'.desktop-table .lower-row'))
    date_dict = {}
    for row in rows:
        name = row.find_element(By.CLASS_NAME,"name").text.strip()
        rank = row.find_element(By.CLASS_NAME,"rank").text.strip()
        age = row.find_element(By.CLASS_NAME,"age").text.strip()
        points = row.find_element(By.CLASS_NAME,"points").text.strip()
        player_dict = {'rank':rank,'age':age,'points':points}
        date_dict[name] = player_dict
    print(f'{date} complete')
    return date_dict

try:
    full_dict = {}
    for date in get_dates_list():
        full_dict[date] = scrape_page(date)
except Exception as e:
    print(e)
finally:
    driver.quit()
    # The name of the file includes the newest date the data was taken from
    with open(f'ATP_Players_{next(iter(full_dict))}.json', 'w') as file:
        json.dump(full_dict, file)

