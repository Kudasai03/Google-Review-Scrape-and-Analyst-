from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

# Tạo hàm thu thập nội dung đánh giá
def get_review_summary(result_set):
    rev_dict = {'Review Name': [], 'Review Text': [], 'Review Time': [], 'Rating': []}

    for result in result_set:
        # Lấy tên người đánh giá
        review_name = result.find(class_='d4r55').text if result.find(class_='d4r55') else 'N/A'
        # Lấy nội dung đánh giá
        review_text_elements = result.find_all('span', class_='wiI7pd')
        review_text = ' '.join([text_element.get_text(separator=' ', strip=True).replace('\n', ' ') for text_element in review_text_elements]) if review_text_elements else 'N/A'
        # Lấy thời gian đánh giá
        review_time = result.find('span', class_='rsqaWe').text if result.find('span', class_='rsqaWe') else 'N/A'
        # Lấy số sao đánh giá
        star_rating = result.find('span', class_='kvMYJc')['aria-label'] if result.find('span', class_='kvMYJc') else 'N/A'
        # Lưu dữ liệu đã lấy được
        rev_dict['Review Name'].append(review_name)
        rev_dict['Review Text'].append(review_text)
        rev_dict['Review Time'].append(review_time)
        rev_dict['Rating'].append(star_rating)

    return pd.DataFrame(rev_dict)

def expand_reviews(driver):
    try:
        # Tìm tất cả các nút "Thêm" hoặc "Xem thêm" trên trang
        more_buttons = driver.find_elements(By.CLASS_NAME, 'w8nwRe')
        for button in more_buttons:
            # Click vào từng nút "Thêm" để mở rộng bình luận
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

user_input = input("Nhập các URL, ngăn cách bởi chữ 'and': ")
urls = [url.strip() for url in user_input.split("and")]  # Chuyển chuỗi đầu vào thành danh sách các URL
driver = webdriver.Chrome()

# urls = ['https://www.google.com/maps/place/FPT+Telecom/@10.771313,106.6706782,15z/data=!4m10!1m2!2m1!1sfpt+telecom!3m6!1s0x31752f694ed35d8d:0x4c3b2871bd2a5ec4!8m2!3d10.771313!4d106.6881877!15sCgtmcHQgdGVsZWNvbSIDiAEBkgEbYnVzaW5lc3NfbmV0d29ya2luZ19jb21wYW554AEA!16s%2Fg%2F1tdznmp1?hl=vi&entry=ttu&g_ep=EgoyMDI0MDkyNS4wIKXMDSoASAFQAw%3D%3D']

final_df = pd.DataFrame()  
for c, url in enumerate(urls):
    driver.get(url)
    time.sleep(5)

    # Expand the review section
    try:
        driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div/div/div/button[2]/div[2]').click()
    except Exception as e:
        print(f"Error clicking on reviews: {e}")
    time.sleep(3)

    SCROLL_PAUSE_TIME = 5
    # Tìm phần tử cụ thể mà bạn muốn cuộn đến
    scrollable_div = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[3]')

    # Lấy chiều cao hiện tại của phần tử
    last_height = driver.execute_script("return arguments[0].scrollHeight;", scrollable_div)

    while True: 
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scrollable_div)
        time.sleep(SCROLL_PAUSE_TIME)

        # Lấy chiều cao mới của phần tử
        new_height = driver.execute_script("return arguments[0].scrollHeight;", scrollable_div)
        if new_height == last_height:
            break  # Thoát vòng lặp nếu chiều cao không thay đổi
        last_height = new_height  # Cập nhật chiều cao cuối cùng

    expand_reviews(driver)

    response = BeautifulSoup(driver.page_source, 'html.parser')
    next_items = response.find_all('div', class_='jftiEf')

    df = get_review_summary(next_items)
    final_df = pd.concat([final_df, df], ignore_index=True)

save(final_df)
driver.quit()
