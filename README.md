#TenderScraper

This program will search through the Iklan Tawaran category on the Pelita Brunei site and send an email to the tender scraper group email containing any new jobs posted at 8am everyday

__TenderScanner.py__

Modules:

**Selenium**
- Allows the program to open a web browser (In this case Chrome)
- Allows the program to interact with web browser (open pages using URL, search through the page and more)
- Used for webscraping
 
**Requests**
- Used for webscraping
 
**Email**
- Allows the program to log into an email and send an email using that account
 
**cv2**
- Allows for image processing

**Pytesseract**
- Used to convert the image file to text
  
**smtplib**
- This is the type of email protocol being used to send the email
  
**re**
- This is used to allow for the program to search for the text which indicates that there are no more sites to search
  
**Urllib3**
- Used to open website using URL

Variables:
- **urlconstant** - assigned the main part of the url to direct the website to the iklan tawaran section of the Pelita Brunei website
- **SenderOfMail** - contains the email address of the sender
- **PassOfSender** - contains the password of the sender email since it must be logged into in order to send an email
- **ReceiverOfMail** - contains the email address of the recipient email address
- **counter** - holds the pointer towards the correct website of Pelita Brunei
- **site_url** - holds the url of the site on Pelita Brunei to search for the image
- **driver** - holds the chrome browser
- **response** - holds the data of the site opened
- **output_file** - contains the file path of “tendertext.txt”
- **image_url** - contains the url of the image which needs to be downloaded and scanned
- **file_name** - holds the file path to the “PelitaImage.jpg” file
- **email_body** - contains the text read from the tendertext file

Subroutines:
- **setup_counter** - this function will open the PelitaCounter file and returns the value stored in it which points to the exact website of Pelita Brunei to open
- **save_counter** - this procedure takes the current counter variable as a parameter which points to the next web address to view and saves it in the PelitaCounter file
- **setup_webdriver** - this function opens a chrome webdriver. It is opened in headless mode so that it does not show the chrome webdriver on the screen (this is only helpful while running locally)
- **imagesearch** - this function locates all images in the website and appends it to an array. It then appends the image url to an array. The url at position 7 in the array is then returned as that is the jpg which we wish to scan
- **get_next_url** - this function returns the url of the next site to be opened. It takes counter and the urlconstant as parameters
- **image_download** - this procedure uses the image_url as a parameter and uses it to download the image and gives it the name “PelitaImage”
- **text_extraction** - this procedure takes the image_path and the output_path as parameters. It uses the pytesseract library to scan the image and convert the text to string. It then saves the string to the tendertext file
- **send_email** - this procedure takes sender, receiver, password, email_body and subject as parameters. It uses these to send an email
- **read_text** - this function takes the path of the tendertext file as a parameter and reads the text file

Main program:
1. First the value from the Pelita counter is read
2. The url of the site is then obtained and its data is obtained
3. The web page is opened
4. It then check whether the text “Sorry, something went wrong” is present
5. If found then it will close the web browser, save the counter value and end the program
6. Otherwise it will find the url of the image which needs to be scanned
7. It will then download the image, extract the text from the image and send the information as an email
8. Then it will delete the image
9. The counter value is then saved and the next web page is opened
10. Then steps 3 to 8 are repeated until the response code != 200 or the “Sorry, something went wrong” text is found

How to run it locally
First create a virtual environment using python version 3.10
Install the necessary modules from the requirements.txt file
The pelita counter must contain a valid number and the tendertext must be present
Since you won’t be able to use github secrets you must replace the SenderOfMail, ReceiverOfMail, PassOfSender assignment to the actual values you wish to use.
Recommended to use an app password for the PassOfSender which has limited access to the email account in case the password is leaked.

Setup (github)
The modules must be installed in the specific versions specified by the requirements document
In the settings of the github repository, under actions → general → workflow permissions, set it to read and write permissions
In github secrets, settings → secrets and variables → actions, you must have 3 secrets, GROUP_EMAIL containing the email address of the recipient email, SENDER_EMAIL containing the email address of the sender, and SENDER_PASS containing the password of the sender email
For improved security recommended to use app password for PassOfSender

Testing:
setup_counter - print the return value of the function and if its printing the same value as what’s stored by the PelitaCounter.txt file then it is working
save_counter - run the save_counter procedure and check the new value of the PelitaCounter.txt file 
setup_webdriver - remove the headless argument and run the function which should open a chrome web browser
imagesearch - test by using a range of sites in the tawaran iklan category on pelita brunei, then type the url of the returned url and check to see if it opens the url of the intended image
get_next_url - print the value of the return value while giving it the parameters of the urlconstant and a random number, the output should be the 2 values concatenated together
Image_download - run the procedure with a url of an image and check if the image is installed and the correct text is output
text_extraction - run the procedure with an image containing text and afterwards view the content of the tendertext.txt file and compare the files to see if the text was extracted correctly
send_email - test the procedure with the SenderOfMail, ReceiverOfMail and PassOfSender variables and use some random text for the email_body parameter. Check the recipient email to see if the email was sent and the appropriate output was sent
read_text - print the return value of the procedure to see if it correctly reads a text file (use the tendertext.txt file to test it for example)
If all subroutines work then you can test the __main__ subroutine. Run the program with an appropriate number in the pelita counter file. Compare the emails received to the images in the site to ensure it is working correctly.


Improvements:
Possibly use AI to filter the titles of tasks so that only certain tasks are send to the email
Translate to english
Remove the weird lines where they aren’t words since the image to string conversion reads the logo as if its text to be read
Add exception handling in more places where it's needed
Attach the image file to the email
Improve the run time of the repository
