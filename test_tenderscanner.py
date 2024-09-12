import unittest
import os
import requests
from smtplib import SMTPAuthenticationError
from unittest.mock import patch, MagicMock
from TenderScanner import read_text, text_extraction, image_download, send_email, imagesearch, setup_counter
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestTenderScraper(unittest.TestCase):
    
    @patch("builtins.open", side_effect=FileNotFoundError)  # Mock the open function to raise FileNotFoundError
    @patch("TenderScanner.logging.error")  # Mock the logging to verify if the error message is logged
    def test_counter_file_not_found(self, mock_logging_error, mock_open_file):
        # Call the function
        result = setup_counter()

        # Verify the return value
        self.assertEqual(result, "PelitaCounter file cannot be found")

        # Verify if the logging error was called with the expected message
        mock_logging_error.assert_called_with("PelitaCounter file cannot be found")


    def test_textfile_presence_when_reading(self):
        result = read_text('non-existant-file')
        self.assertEqual(result, "Text file not found when trying to read from file")

    def test_imagefile_presence_when_scanning(self):
        result = text_extraction("Non-existant-image","tendertext.txt")
        self.assertEqual(result, "Image file not found or cannot be opened")

    @patch('requests.get')
    def test_image_downloading_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        result = image_download("non existant image url")
        self.assertEqual(result, "Error occured during image download")

    @patch('selenium.webdriver.Chrome')  # Patch the WebDriver
    def test_imagesearch_insufficient_images(self, mock_driver):
        # Mocking elements returned by driver.find_elements (less than 8)
        mock_image_elements = [MagicMock() for _ in range(5)]
        
        # Each mock element should have a `src` attribute
        for i, mock_elem in enumerate(mock_image_elements):
            mock_elem.get_attribute.return_value = f"http://example.com/image{i}.jpg"
        
        # Mock WebDriverWait to return the image elements
        mock_wait = MagicMock()
        mock_wait.until.return_value = mock_image_elements
        mock_driver.find_elements.return_value = mock_image_elements

        # Patch WebDriverWait with the mock
        with patch('selenium.webdriver.support.ui.WebDriverWait', return_value=mock_wait):
            result = imagesearch(mock_driver)

        # Assert that "Insufficient number of images" is returned
        self.assertEqual(result, "Insufficient number of images")

    @patch('smtplib.SMTP') #Mock the smtplib.SMTP class
    def test_send_mail(self, mock_smtp):
        sender = "testsender@gmail.com"
        receiver = "testreceiver@gmail.com"
        password = "password123"
        email_body = "This is a test email"
        image_path = os.path.join(os.path.dirname(__file__), 'PelitaImage.jpg')
        subject = "Test Subject"

        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

        result = send_email(sender,receiver,password,email_body,image_path,subject)

        self.assertEqual(result, "Email sent successfully")

    @patch('smtplib.SMTP') #Mock the smtplib.SMTP class
    def test_send_mail_invalid_image(self, mock_smtp):
        sender = "testsender@gmail.com"
        receiver = "testreceiver@gmail.com"
        password = "password123"
        email_body = "This is a test email"
        image_path = os.path.join(os.path.dirname(__file__), 'non-existant.jpg')
        subject = "Test Subject"

        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

        result = send_email(sender,receiver,password,email_body,image_path,subject)
        self.assertEqual(result, "Image file not found")

    @patch('smtplib.SMTP') #Mock the smtplib.SMTP class
    def test_send_mail_invalid_login(self, mock_smtp):
        sender = "not_real_account@gmail.com"
        receiver = "testreceiver@gmail.com"
        password = "incorrect_pass"
        email_body = "This is a test email"
        image_path = "PelitaImage.jpg"
        subject = "Test Subject"

        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

        mock_smtp_instance.login.side_effect = SMTPAuthenticationError(535, b'Authentication failed')

        result = send_email(sender,receiver,password,email_body,image_path,subject)
        self.assertEqual(result, "Login failed, email or password incorrect")

        

if __name__ == "__main__":
    unittest.main()