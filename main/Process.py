import py_vncorenlp
import pandas as pd
from tqdm import tqdm

# Tải về các thành phần của VnCoreNLPD:\Toan\Scrape\google-review-scraper-main
py_vncorenlp.download_model(save_dir='D:/Toan/Scrape/google-review-scraper-main/vncorenlp')  # Thay đổi đường dẫn này cho phù hợp

# Load the word and sentence segmentation component
rdrsegmenter = py_vncorenlp.VnCoreNLP(annotators=["wseg"], save_dir='D:/Toan/Scrape/google-review-scraper-main/vncorenlp')  # Thay đổi đường dẫn này cho phù hợp

# Đọc dữ liệu từ tệp CSV
data = pd.read_csv(r'D:\Toan\Scrape\google-review-scraper-main\datareview.csv')  # Sử dụng dấu 'r' để định dạng đường dẫn

# Tách cột Review Text
review_text = data['Review Text']
output_file_path = 'review_text.txt'

# Ghi nội dung vào tệp review_text.txt
with open(output_file_path, 'w', encoding='utf-8') as file:
    for review in review_text:
        file.write(review + '\n')

# Định nghĩa đường dẫn file đầu vào và đầu ra
input_file_path = 'review_text.txt'
output_file_path = 'output_segmented.txt'

# Đọc nội dung từ file đầu vào
with open(input_file_path, 'r', encoding='utf-8') as file:
    text = file.read()

# Tách từ bằng VnCoreNLP với thanh tiến trình tqdm
segmented_text = []
with tqdm(total=len(text.split('\n')), desc="Segmenting") as pbar:
    for line in text.split('\n'):
        segmented_line = rdrsegmenter.word_segment(line)
        segmented_text.append(segmented_line)
        pbar.update(1)

# Ghi kết quả vào tệp đầu ra
with open(output_file_path, 'w', encoding='utf-8') as file:
    for line in segmented_text:
        for sentence in line:
            file.write(sentence + '\n')
