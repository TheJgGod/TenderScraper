from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
import sys
from email.message import EmailMessage
import requests
import cv2
import pytesseract
import os 
import smtplib
import re
import urllib3
import unittest
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level to DEBUG
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    
)

urlconstant = "https://www.pelitabrunei.gov.bn/Lists/IklanIklan/NewDisplayForm.aspx?ID="
SenderOfMail = os.environ["sender_email"]
ReceiverOfMail = os.environ["group_email"]
PassOfSender = os.environ["sender_pass"]

#Loads the counter of which site to look at
def setup_counter():
    try:
        with open("PelitaCounter.txt", 'r') as f:
            return f.readline()
    except IOError:
        logging.error("PelitaCounter file cannot be found")
        #sys.exit("Pelita Counter file cannot be found")
        return "PelitaCounter file cannot be found"

#Updates the PelitaCounter
def save_counter(counter):
    with open("PelitaCounter.txt", 'w') as f:
            f.write(str(counter))

#Function to initialise the chrome webpage
def setup_webdriver():
    try:
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(service=ChromeService(), options=options)
        driver.maximize_window()
        logging.info("Webdriver setup successful")
        return driver
    except WebDriverException as e:
        logging.error("Error initializing WebDriver: {e}")
        #sys.exit("Error initializing WebDriver")
        return None
    except Exception as e:
        logging.error("Unexpected error occured: {e}")
        #sys.exit("Unexpected error occured when initializing WebDriver")
        return None

def extract_heading_text(driver, url):
    try:
        driver.get(url)
        heading = driver.find_element(By.TAG_NAME, "h1").text
        return heading
    except Exception as e:
        logging.error(f"Failed to extract heading: {e}")
        return "Tender"

#Function to search for image URL
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
    
    if len(image_URLS) >= 8:
        logging.info("Image URL:", image_URLS[7])
        return image_URLS[7]
    else:
        logging.error("Insufficient number of images")
        #sys.exit("Insufficient number of images")
        return "Insufficient number of images"

#Finds the url of Pelita Brunei to look at
def get_next_url(counter, urlconstant):
    return urlconstant + str(counter)

#Procedure to install image
def image_download(image_url):
    try:
        response = requests.get(image_url)
        with open("PelitaImage.jpg", 'wb') as file:
            file.write(response.content)
        logging.info("Image downloaded successfully!")
        return "Image downloaded successfully!"
    except requests.exceptions.RequestException as e:
        logging.error("Error occured during image download")
        #sys.exit("Error occured during image download")
        return "Error occured during image download"

#Procedure to extract text from JPEG
def text_extraction(image_path, output_path):
    try:
        # Read the image
        image = cv2.imread(image_path)
        
        # Check if the image was loaded successfully
        if image is None:
            logging.error("Image file not found or cannot be opened: %s", image_path)
            #sys.exit("Image file not found or cannot be opened")
            return "Image file not found or cannot be opened"
        
        # Extract text from the image
        try:
            text = pytesseract.image_to_string(image)
        except Exception as e:
            logging.error("Error extracting text from image: %s", e)
            #sys.exit("Error extracting text from image")
            return "Error extracting text from image"
        
        # Write text to the file
        with open(output_path, 'w') as f:
            f.write(text)
        logging.info("Text extracted and saved to file: %s", output_path)
        return "Text extracted and saved to file!"
    
    except Exception as e:
        logging.error("An unexpected error occurred: %s", e)
        #sys.exit("An unexpected error occurred")
        return "An unexpected error occurred"

#Procedure to send email
def send_email(sender, receiver, password, email_body, image_path, subject="Tender"):
    try:
        msg = EmailMessage()
        msg.set_content(email_body, charset='utf-8')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = receiver

        try:
            with open(image_path,'rb') as file:
                msg.add_attachment(file.read(),
                                    maintype = 'image',
                                    subtype = 'jpeg',
                                    filename = "PelitaImage.jpg")

        except FileNotFoundError:
            logging.error("Image file not found: %s", image_path)
            #sys.exit( "Image file not found")
            return "Image file not found"

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender, password)
                server.send_message(msg)
            logging.info("Email has been sent successfully!")
            return "Email sent successfully"

        except smtplib.SMTPAuthenticationError:
            logging.error("Login failed for sender %s", sender)
            #sys.exit("Login failed, email or password incorrect")
            return "Login failed, email or password incorrect"

    except Exception as e:
        logging.error("An error occurred while sending email: %s", e)
        #sys.exit("An error occured while sending email")
        return "An error occured while sending email"


#Function to read text for the email body
def read_text(output_file):
    try:
        with open(output_file, 'r') as textfile:
            return textfile.read()
    except IOError:
        logging.error("Text file not found %s", output_file)
        #sys.exit("Text file not found when trying to read from file")
        return "Text file not found when trying to read from file"

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
            logging.info("Search complete")
            sys.exit(0)

        if "JAWATAN KOSONG" not in driver.page_source:
            image_url = imagesearch(driver)

            if image_url:
                download_result = image_download(image_url)
                file_name = os.path.join(os.path.dirname(__file__), 'PelitaImage.jpg')
                extraction_result = text_extraction(file_name, output_file)
                email_body = read_text(output_file)
                subject = extract_heading_text(driver,site_url)
                result = send_email(SenderOfMail, ReceiverOfMail, PassOfSender, email_body, file_name, subject)
                os.remove("PelitaImage.jpg")

        counter += 1
        save_counter(counter)
        site_url = get_next_url(counter, urlconstant)
        response = requests.get(site_url)
    
    driver.quit()


if __name__ == "__main__":
    __main__()


