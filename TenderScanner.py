from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import sys
from email.message import EmailMessage
import requests
import cv2
import pytesseract
import os 
import smtplib
import re
import urllib3

urlconstant = "https://www.pelitabrunei.gov.bn/Lists/IklanIklan/NewDisplayForm.aspx?ID="
SenderOfMail = os.environ["sender_email"]
ReceiverOfMail = os.environ["group_email"]
PassOfSender = os.environ["sender_pass"]

#Loads the counter of which site to look at
with open("PelitaCounter.txt", 'r') as f:
        counter = int(f.readline())

# to run Chrome in headless mode
options = Options()
options.add_argument("--headless") # comment while developing

# initialize a Chrome WerbDriver instance
# with the specified options
driver = webdriver.Chrome(
    service=ChromeService(),
    options=options
)

driver.maximize_window()

#The actual URL of the PelitaBrunei site
#url = urlconstant + str(urlpointer)
url = urlconstant + str(counter)
response = requests.get(url)

while response.status_code == 200:
    driver.get(url)

    if "Sorry, something went wrong" in driver.page_source:
        print("Counter =", counter)
        driver.quit()
        with open("PelitaCounter.txt", 'w') as f:
            f.write(str(counter))
        print("Search complete")
        sys.exit(0)

    image_jpg_nodes = driver.find_elements(By.CSS_SELECTOR, "[data-test=\"photo-grid-masonry-img\"]")

    image_URLS = []

    image_jpg_nodes = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "img"))
    )

    image_URLS = []

    for image_jpg_node in image_jpg_nodes:
        try:
            # Use the URL in the "src" as the default behavior
            image_url = image_jpg_node.get_attribute("src")
            # Add the image URL to the list
            image_URLS.append(image_url)
        except StaleElementReferenceException:
            continue

    url = image_URLS[7]

    print("Image url:",url)

    response = requests.get(url)

    filename = "PelitaImage.jpg" # You can name the file as you want
    with open(filename, 'wb') as file:
        file.write(response.content)

    print("Image downloaded successfully!")

    file_name = os.path.join(os.path.dirname(__file__), 'PelitaImage.jpg')
    output_file = os.path.join(os.path.dirname(__file__), 'tendertext.txt')

    image = cv2.imread(file_name)
    text = pytesseract.image_to_string(image)
    f = open(output_file,'w')
    f.write(text)
    f.close()


    try:

        with open("tendertext.txt", 'r') as textfile:
            email_body = textfile.read()

        msg = EmailMessage()
        msg.set_content(email_body, charset='utf-8')
        msg['Subject'] = "Tender"
        msg['From'] = SenderOfMail
        msg['To'] = ReceiverOfMail

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SenderOfMail, PassOfSender)
            server.send_message(msg)

        print("Email has been sent")

    except Exception as e:
        print(f"An error occurred: {e}")

    os.remove("PelitaImage.jpg")

    counter += 1
    url = urlconstant + str(counter)
    response = requests.get(url)
