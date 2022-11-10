from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from tqdm import tqdm
import json
import time
import re
print('')
reviews_dic_sk = {}
rate_reg = re.compile('ui_bubble_rating bubble_(\d\d)')
auth_reg = re.compile(',.*')

counter = 1

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')

try:
    # Select driver, get url, select window and define waiting time for web browser to load

    url = {
        f'South Kensington': 'https://www.tripadvisor.co.uk/Restaurant_Review-g186338-d3784979-Reviews-Macellaio_RC_South_Kensington-London_England.html'}

    driver = webdriver.Chrome('/Users/lele/Dropbox/PycharmProjects/rc_reports v2/chromedriver', options=chrome_options)
    driver.get(url.get('South Kensington'))
    wait = WebDriverWait(driver, 10)  # save wait to use later, throw error if wait longer than 10sec
    original_window = driver.current_window_handle  # optional
    assert len(driver.window_handles) == 1  # optional
    wait.until(EC.visibility_of_element_located((By.XPATH, f"//*[text()= 'I Accept']")))
    driver.find_element_by_xpath(f"//*[text()= 'I Accept']").click()
    wait.until(EC.visibility_of_element_located((By.XPATH, f"//*[text()= 'All languages']")))
    time.sleep(1)
    driver.find_element_by_xpath(f"//*[text()= 'All languages']").click()
    tot_rev = driver.find_element_by_xpath('//*[@id="REVIEWS"]/div[1]/div/div[1]/span')
    tot_rev_stripped = tot_rev.text.strip('()')
    total_reviews = int(tot_rev_stripped.replace(",", ""))
    pages = int(round(total_reviews / 15, 0))
    iteration = range(0, pages)
    bar_pages = tqdm(total=pages, colour='red', position=0, desc='Pages to go')
    bar_reviews = tqdm(total=total_reviews, leave=False, position=1, desc='Reviews scraped')

    try:
        for x in iteration:

            review_num = []
            auth_list = []
            num_reviews_list = []
            rating_list = []
            review_title = []
            review_body = []
            date_review = []
            link_list = []

            page_source = driver.page_source
            strainer = (SoupStrainer(class_='rev_wrap ui_columns is-multiline'))
            reviews_soup = BeautifulSoup(page_source, features='html.parser', parse_only=strainer)

            for review in reviews_soup:
                author = review.find(class_='info_text pointer_cursor')
                num_reviews = review.find(class_='reviewerBadge badge')
                review_num.append(str(counter))
                try:
                    auth_list.append(author.text)
                except AttributeError:
                    auth_list.append('Author Unknown')
                num_reviews_list.append(num_reviews.text)
                counter += 1
                bar_reviews.update(0.5)

            more_button = driver.find_element_by_xpath(f"//*[text()= 'More']")

            if more_button.is_displayed():
                driver.execute_script("arguments[0].click();", more_button)
            time.sleep(5)

            page_source = driver.page_source

            strainer = SoupStrainer(class_='rev_wrap ui_columns is-multiline')
            reviews_soup = BeautifulSoup(page_source, features='html.parser', parse_only=strainer)

            for review in reviews_soup:
                rate = review.find(class_=rate_reg)
                rating = re.findall(re.compile('[1-9]'), str(rate))
                rating_list.append(rating[0])
                title = review.find(class_="noQuotes")
                review_title.append(title.text)
                body = review.find(class_="partial_entry")
                review_body.append(body.text)
                date = review.find(class_="ratingDate")
                date_review.append(date.text)
                link = review.find('a', href=True)
                link_list.append(f"https://www.tripadvisor.co.uk{link.get('href')}")
                bar_reviews.update(0.5)

            for i in range(len(auth_list)):
                reviews_dic_sk[f'{review_num[i]}'] = [
                    f'{auth_list[i]}',
                    f'({num_reviews_list[i]})',
                    f'{rating_list[i]} stars',
                    date_review[i],
                    f'Title: {review_title[i]}',
                    f'Review: {review_body[i]}',
                    f'{link_list[i]}'
                ]

            bar_pages.update(1)
            next_button = driver.find_element_by_xpath(f"//*[text()= 'Next']")
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(5)

            with open('/Users/lele/Dropbox/PycharmProjects/review_feed/reviews_sk.json', 'w') as fp:
                json.dump(reviews_dic_sk, fp, indent=4)
                fp.close()


            review_num = []
            auth_list = []
            num_reviews_list = []
            rating_list = []
            review_title = []
            review_body = []
            date_review = []
            link_list = []
    except AttributeError:
        print(auth_list)
        print(date_review)

    counter = 0

finally:
    print('')
    driver.quit()
