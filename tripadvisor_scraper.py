from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import re

reviews_dic = {}
rate_reg = re.compile('ui_bubble_rating bubble_(\d\d)')
auth_reg = re.compile(',.*')

auth_list = []
num_reviews_list = []
rating_list = []

url = {
    'South Kensington': 'https://www.tripadvisor.co.uk/Restaurant_Review-g186338-d3784979-Reviews'
                        '-Macellaio_RC_South_Kensington-London_England.html '
}

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')

try:
    # Select driver, get url, select window and define waiting time for web browser to load

    driver = webdriver.Chrome('/Users/lele/Dropbox/PycharmProjects/rc_reports v2/chromedriver', options=chrome_options)
    driver.get(url.get('South Kensington'))
    wait = WebDriverWait(driver, 10)  # save wait to use later, throw error if wait longer than 10sec
    original_window = driver.current_window_handle  # optional
    assert len(driver.window_handles) == 1  # optional
    wait.until(EC.visibility_of_element_located((By.XPATH, f"//*[text()= 'I Accept']")))
    driver.find_element_by_xpath(f"//*[text()= 'I Accept']").click()
    wait.until(EC.visibility_of_element_located((By.XPATH, f"//*[text()= 'All languages']")))
    driver.find_element_by_xpath(f"//*[text()= 'All languages']").click()
    time.sleep(3)

    page_source = driver.page_source

    strainer = SoupStrainer(class_='rev_wrap ui_columns is-multiline')
    reviews_soup = BeautifulSoup(page_source, features='html.parser', parse_only=strainer)

    for review in reviews_soup:
        author = review.find(class_='info_text pointer_cursor')
        num_reviews = review.find(class_='reviewerBadge badge')
        auth_list.append(author.text)
        num_reviews_list.append(num_reviews.text)

    time.sleep(3)
    more_button = driver.find_element_by_xpath(f"//*[text()= 'More']")
    if more_button.is_displayed():
        driver.execute_script("arguments[0].click();", more_button)
    time.sleep(3)

    page_source = driver.page_source

    strainer = SoupStrainer(class_='rev_wrap ui_columns is-multiline')
    reviews_soup = BeautifulSoup(page_source, features='html.parser', parse_only=strainer)

    for review in reviews_soup:
        rate = review.find(class_=rate_reg)
        rating = re.findall(re.compile('[1-9]'), str(rate))
        rating_list.append(rating[0])

    for i in range(len(auth_list)):
        print(auth_list[i] + ' / ', num_reviews_list[i], ' / Rating: ' + rating_list[i])
        print('..........................')




finally:
    driver.quit()


