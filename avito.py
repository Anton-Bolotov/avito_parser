import os
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import base64
from PIL import Image
from io import BytesIO
import pytesseract
import cv2

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

start_time = time.time()
driver = webdriver.Chrome()
# driver.set_window_position(-3000, 0)

url_list = []
count = 0
count_of_check = 0


with open(file='input.txt', mode='r', encoding='utf-8') as file:
    for url in file:
        url = url.replace('\n', '')
        url_list.append(url)

while True:
    if count >= len(url_list):
        driver.quit()
        os.remove('accept.png')
        break
    try:
        driver.get(url_list[count])
        count += 1
        time.sleep(1)
        button = driver.find_element_by_xpath('//div/div[2]/div/div/span/span/button')
        button.click()

        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        phone_img = str(soup.find_all('img', attrs={'class': 'contacts-phone-3KtSI'})[0]).split('base64,')[1].split('"')[0]
        im = Image.open(BytesIO(base64.b64decode(phone_img)))
        im.save('accept.png', 'PNG')
        image = cv2.imread('accept.png')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = 255 - cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        thresh = cv2.GaussianBlur(thresh, (3, 3), 0)
        data = pytesseract.image_to_string(thresh, lang='eng', config='--psm 6 tessedit_char_whitelist=0123456789+-')
        phone_number = data.split('\n')[0]

    except IndexError:
        count -= 1
        continue

    except NoSuchElementException:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        if 'Пользователь предпочитает сообщения' in str(soup):
            phone_number = 'Без звонков. Пользователь предпочитает сообщения'
        elif 'Вы владелец объявления? Пожалуйста, подождите' in str(soup):
            print(url_list[count - 1] + '\t' + 'Объявление проверяется модератором')
            continue
        else:
            if count_of_check >= 2:
                count_of_check = 0
                print(url_list[count - 1] + '\t' + 'С этой ссылкой что то не так')
                continue
            else:
                count -= 1
                count_of_check += 1
                continue

    if 'Ой! Такой страницы на нашем сайте нет' in str(soup):
        print(url_list[count - 1] + '\t' + 'Ой! Такой страницы на нашем сайте нет')
    else:
        price = str(soup.find_all('span', attrs={'class': 'price-value-string js-price-value-string'})[0].get_text()).replace('\n', '').replace('\t', '').replace('  ', '')
        views = str(soup.find('div', attrs={'class': 'title-info-metadata-item title-info-metadata-views'})).split('</i>')[1].split('</div>')[0]
        print(url_list[count - 1] + '\t' + phone_number + '\t' + price + '\t' + views)

driver.quit()
finish_time = time.time()
print(round(finish_time - start_time, 2), 'секунд')



