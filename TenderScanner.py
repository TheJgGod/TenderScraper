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
def setup_counter():
    with open("PelitaCounter.txt", 'r') as f:
        return f.readline()

#Updates the PelitaCounter
def save_counter(counter):
    with open("PelitaCounter.txt", 'w') as f:
            f.write(str(counter))

#Function to initialise the chrome webpage
def setup_webdriver():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=ChromeService(), options=options)
    driver.maximize_window()
    return driver

#Function to 
def imagesearch(driver):
    image_jpg_nodes = driver.find_elements(By.CSS_SELECTOR, "[data-test=\"photo-grid-masonry-img\"]")

    image_URLS = []

    image_jpg_nodes = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "img"))
    )

    for image_jpg_node in image_jpg_nodes:
        try:
            # Use the URL in the "src" as the default behavior
            image_url = image_jpg_node.get_attribute("src")
            # Add the image URL to the list
            image_URLS.append(image_url)
        except StaleElementReferenceException:
            continue
    
    print("Image URL:", image_URLS[7])

    return image_URLS[7]

#Finds the url of Pelita Brunei to look at
def get_next_url(counter, urlconstant):
    return urlconstant + str(counter)

#Procedure to install image
def image_download(image_url):
    response = requests.get(image_url)
    with open("PelitaImage.jpg", 'wb') as file:
        file.write(response.content)
    print("Image downloaded successfully!")

#Procedure to extract text from JPEG
def text_extraction(image_path, output_path):
    image = cv2.imread(image_path)
    text = pytesseract.image_to_string(image)
    with open(output_path, 'w') as f:
        f.write(text)
    print("Text extracted and saved to file!")

#Procedure to send email
def send_email(sender, receiver, password, email_body, subject="Tender"):
    try:
        msg = EmailMessage()
        msg.set_content(email_body, charset='utf-8')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = receiver

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        print("Email has been sent successfully!")
    except Exception as e:
        print(f"An error occurred while sending email: {e}")

#Function to read text for the email body
def read_text(output_file):
    with open(output_file, 'r') as textfile:
        return textfile.read()

def __main__():
    counter = int(setup_counter())
    site_url = get_next_url(counter, urlconstant)
    driver = setup_webdriver()
    response = requests.get(site_url)

    output_file = os.path.join(os.path.dirname(__file__), 'tendertext.txt')

    while response.status_code == 200:
        driver.get(site_url)

        if "Sorry, something went wrong" in driver.page_source:
            print("Counter =", counter)
            driver.quit()
            save_counter(counter)
            print("Search complete")
            sys.exit(0)

        image_url = imagesearch(driver)

        if image_url:
            image_download(image_url)
            file_name = os.path.join(os.path.dirname(__file__), 'PelitaImage.jpg')
            text_extraction(file_name, output_file)
            email_body = read_text(output_file)
            send_email(SenderOfMail, ReceiverOfMail, PassOfSender, email_body)
            os.remove("PelitaImage.jpg")

        counter += 1
        save_counter(counter)
        site_url = get_next_url(counter, urlconstant)
        response = requests.get(site_url)
    
    driver.quit()

__main__()
