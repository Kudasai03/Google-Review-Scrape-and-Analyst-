from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

# Đường dẫn đến file chromedriver.exe
driver_path = r"D:\Toan\Scrape\google-review-scraper-main\chromedriver.exe"

# Khởi tạo Service và Options cho ChromeDriver
service = Service(executable_path=driver_path)
chrome_options = Options()
chrome_options.add_argument("--log-level=3")  # Tắt bớt log của Chrome

# Khởi tạo driver với Service và Options
driver = webdriver.Chrome(service=service, options=chrome_options)

# Hàm lấy thông tin đánh giá từ một tập kết quả
def get_review_summary(result_set):
    rev_dict = {'Review Name': [], 'Review Text': [], 'Review Time': [], 'Rating': []}
    for result in result_set:
        review_name = result.find(class_='d4r55').text if result.find(class_='d4r55') else 'N/A'
        review_text_elements = result.find_all('span', class_='wiI7pd')
        review_text = ' '.join([text_element.get_text(separator=' ', strip=True).replace('\n', ' ') for text_element in review_text_elements]) if review_text_elements else 'N/A'
        review_time = result.find('span', class_='rsqaWe').text if result.find('span', class_='rsqaWe') else 'N/A'
        star_rating = result.find('span', class_='kvMYJc')['aria-label'] if result.find('span', class_='kvMYJc') else 'N/A'
        rev_dict['Review Name'].append(review_name)
        rev_dict['Review Text'].append(review_text)
        rev_dict['Review Time'].append(review_time)
        rev_dict['Rating'].append(star_rating)
    return pd.DataFrame(rev_dict)

# Hàm mở rộng các đánh giá bằng cách bấm vào nút "Thêm"
def expand_reviews(driver):
    try:
        more_buttons = driver.find_elements(By.CLASS_NAME, 'w8nwRe')
        for button in more_buttons:
            driver.execute_script("arguments[0].click();", button)
            time.sleep(1)
    except Exception as e:
        print(f"Error expanding reviews: {e}")

# Hàm lưu dữ liệu vào file CSV
def save(df):
    file_exists = os.path.isfile('datareview.csv')
    existing_df = pd.read_csv('datareview.csv') if file_exists else pd.DataFrame(columns=['Review Name', 'Review Text', 'Review Time', 'Rating'])
    combined_df = pd.concat([existing_df, df], ignore_index=True)
    combined_df.to_csv('datareview.csv', index=False)

urls = ['https://www.google.com/maps/place/FPT+Telecom/@10.771313,106.6706782,15z/data=!4m10!1m2!2m1!1sfpt+telecom!3m6!1s0x31752f694ed35d8d:0x4c3b2871bd2a5ec4!8m2!3d10.771313!4d106.6881877!15sCgtmcHQgdGVsZWNvbSIDiAEBkgEbYnVzaW5lc3NfbmV0d29ya2luZ19jb21wYW554AEA!16s%2Fg%2F1tdznmp1?hl=vi&entry=ttu&g_ep=EgoyMDI0MDkyNS4wIKXMDSoASAFQAw%3D%3D']
final_df = pd.DataFrame()

# Duyệt từng URL và lấy đánh giá
for c, url in enumerate(urls):
    driver.get(url)
    time.sleep(5)

    try:
        driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div/div/div/button[2]/div[2]').click()
    except Exception as e:
        print(f"Error clicking on reviews: {e}")
    time.sleep(3)

    SCROLL_PAUSE_TIME = 5
    scrollable_div = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[3]')
    last_height = driver.execute_script("return arguments[0].scrollHeight;", scrollable_div)

    while True: 
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scrollable_div)
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return arguments[0].scrollHeight;", scrollable_div)
        if new_height == last_height:
            break 
        last_height = new_height 

    expand_reviews(driver)
    response = BeautifulSoup(driver.page_source, 'html.parser')
    next_items = response.find_all('div', class_='jftiEf')
    df = get_review_summary(next_items)
    final_df = pd.concat([final_df, df], ignore_index=True)

save(final_df)
driver.quit()
