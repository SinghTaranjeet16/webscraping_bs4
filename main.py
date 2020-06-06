# Standart imports
import os
import glob
import json
import traceback
import logging
from difflib import Differ, SequenceMatcher
from time import sleep, strftime, localtime

# 3rd party imports
import requests
from bs4 import BeautifulSoup
import pdftotext
from notifiers import get_notifier
from parse_text_file import save_imp_routes

# URLs to track
URL_HOME = "http://www.airindia.in"
LANDING_PAGE = "/r1landingpage.htm"
EVAC_PAGE = "/evacuation-flight.htm"

# Directory path where the code and credentials will be saved
DIR_PATH = os.path.dirname(os.path.realpath(__file__))

# Logging settings for imported module
# Set logging level to WARNING for imported module(s), else it will also print
logging.getLogger("parse_text_file").setLevel(level=logging.WARNING)

# Logging settings for current module
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
fh = logging.StreamHandler()
fh_formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')
fh.setFormatter(fh_formatter)
logger.addHandler(fh)

# Credentials used for notifiers library
# Credentials dictionary has the format {token=xxx}
PUSHBULLET_CRED_FILE = os.path.join(DIR_PATH, 'pushbullet_credentials')
PUSHBULLET_CRED_DICT = {}

# Wait time between sending queries to url (in minutes)
WAIT_TIME = 15


def read_credentials(cred_file, cred_dict):
    """
    Read the credentials from file and save it in the dictionary

    Arguments:
        cred_file {path} -- OS path to the cred file location
        cred_dict {dict} -- Dictionary that will save the credentials

    Returns:
        dict -- Returns dict with 'token' as keyname and token value
    """
    with open(cred_file, 'r') as f:
        for line in f:
            key, value = line.partition("=")[::2]
            cred_dict[key.strip()] = value.strip()


def convert_pdf_to_txt_file(pdf_file_path, txt_file_path):
    """
    Extract text from PDF file. Save the text as a file

    Arguments:
        pdf_file_path {path} -- OS file path where PDF file is saved
        txt_file_path {path} -- OS file path where TXT file is saved
    """
    with open(pdf_file_path, "rb") as f:
        pdf_obj = pdftotext.PDF(f)

    with open(txt_file_path, 'w') as f:
        f.write("\n\n".join(pdf_obj))


def main():

    # Initialize notifier instance and set credentials
    pushbullet_notifier = get_notifier('pushbullet')
    read_credentials(PUSHBULLET_CRED_FILE, PUSHBULLET_CRED_DICT)

    # Create diff object for comparing html page text
    diff = Differ()
    old_landing_page_text = ""

    # Main processing loop
    main_loop_iter_count = 1
    while True:
        logger.info("+-------------------------------------------------+")
        logger.info("#       Running parser to fetch route details      ")
        logger.info(f"#\t\t[{strftime('%Y-%m-%d %H:%M:%S',localtime())}] ")
        logger.info(f"#\t           ITERATION - {main_loop_iter_count}   ")
        logger.info("+-------------------------------------------------+")

        if main_loop_iter_count % 6 == 0:
            hbeat_msg = f"Heartbeat signal #{int(main_loop_iter_count / 6)}"
            pushbullet_notifier.notify(message=hbeat_msg, **PUSHBULLET_CRED_DICT)

        try:
            """ PAGE UPDATE INFORMATION """
            # Checking if the landing page have any update in it's content
            # This check is very basic and will look for an update in the text
            # Any changes will be notified via pushbullet
            r = requests.get(URL_HOME + LANDING_PAGE)
            if r.status_code == 200:
                if old_landing_page_text:
                    seq = SequenceMatcher(a=r.text, b=old_landing_page_text)
                    # Check if seq ratio is not 1, implies that text is not same
                    # Create a diff generator and convert it to list and notify
                    # Only print first 10 elements as it could be large
                    similarity = seq.quick_ratio()
                    msg = f"Difference of {round((1-similarity)*100, 3)}% detected on {URL_HOME + LANDING_PAGE}"
                    if similarity < 0.997:  # Text not atleast 99.7% similar; depends on usecase
                        diff_string = json.dumps(list(diff.compare(r.text.splitlines(),
                                                                   old_landing_page_text.splitlines())))
                        logger.debug(diff_string[:10])  # only first 10 elements
                        pushbullet_notifier.notify(message=msg, **PUSHBULLET_CRED_DICT)
                    logger.info(msg)
                old_landing_page_text = r.text
            else:
                raise Exception(f"Error getting to address {URL_HOME + LANDING_PAGE} [Code = {r.status_code}]")

            """ ITENARY DETAILS PARSING """
            # HTML content of the website
            # This is a different webpage to parse the itenary details
            source = requests.get(URL_HOME + EVAC_PAGE)
            if source.status_code != 200:
                raise Exception(f"Error getting to address {URL_HOME + EVAC_PAGE} [Code = {source.status_code}]")

            # Parsed XML content from URL
            # Div content that contains evacuation schedule details
            soup = BeautifulSoup(source.text, 'lxml')
            page_content = soup.find("div", {"id": "content"})
            if not page_content:
                raise Exception(f"Could not find <div id='content'> in url source text")

            # Grab all the headings <h2> tags
            # For each <h2> tag, check if text matches what we're looking for AND
            # Grab the href value for that particular <h2> tag (if available)
            all_h2_tags = page_content.find_all("h2")
            if not all_h2_tags:
                logger.warning("Empty list for <h2> tag elements")
            for h2_tag in all_h2_tags:
                h2_tag_text = h2_tag.text.split('\n')[0]
                if 'evacuation flight schedule' in h2_tag_text.lower():
                    logger.info(f"Found header '{h2_tag_text}'")
                    # If href tag exists and it has a download link
                    # Save the link file (probably a pdf)
                    if not h2_tag.a['href']:
                        logger.warning(f"Missing href for <h2> '{h2_tag_text}'")
                    else:
                        href_file_name = h2_tag.a['href'].split('/')[-1]
                        file_to_copy = os.path.join(DIR_PATH, href_file_name)
                        # Check if this file isn't already saved
                        if not os.path.isfile(file_to_copy):
                            logger.info(f"PDF '{href_file_name} DOESN'T EXISTS. Downloading...")
                            pdf_web_path = URL_HOME + h2_tag.a['href']
                            r = requests.get(pdf_web_path)
                            if r.status_code == 200:
                                with open(file_to_copy, 'wb') as f:
                                    f.write(r.content)
                                logger.info(f"File '{href_file_name}' downloaded successfully")
                            else:
                                raise Exception(f"Failed to download '{pdf_web_path}' [Code = {r.status_code}]")
                        else:
                            logger.info(f"PDF '{href_file_name}' already exist!")

            # Extract text from PDF and save it to a text file
            # Sort files (in-place; use 'sorted' otherwise) list based upon the changed time
            # Newly created files are at last
            # This helps to overcome the issue where notification_send was being set as True...
            # ...when older file was parsed after a new file
            pdf_file_list = glob.glob(os.path.join(DIR_PATH, "*.pdf"))
            pdf_file_list.sort(key=os.path.getctime)
            if not pdf_file_list:
                raise Exception(f"No PDF files found in '{DIR_PATH}'")
            for pdf_file in pdf_file_list:
                pdf_file_name_without_ext = pdf_file.split('/')[-1].split('.')[0]
                txt_file_path = os.path.join(DIR_PATH, f'{pdf_file_name_without_ext}.txt')
                # Check if this file isn't saved already; else move on to the next file
                if os.path.isfile(txt_file_path):
                    logger.info(f"Text file '{pdf_file_name_without_ext}' already exists")
                    # under the assumption that file already exists, notifiction has been sent before
                    notification_already_sent = True
                    continue
                # If text file doesn't exists before, parse text from pdf
                # Also, unset the notification_send to mark that it's a new file
                notification_already_sent = False
                logger.info(f"Converting {pdf_file_name_without_ext} to text file...")
                convert_pdf_to_txt_file(pdf_file, txt_file_path)

            # Parse text file to grab all the possible itenary details
            txt_file_list = glob.glob(os.path.join(DIR_PATH, "*.txt"))

            if not txt_file_list:
                raise Exception(f"No TXT files found in '{DIR_PATH}'")

            for txt_file in txt_file_list:
                txt_file_name_without_ext = txt_file.split('/')[-1].split('.')[0]
                route_dates_list = save_imp_routes(txt_file, depart="DELHI", arrival="TORONTO")
                if not route_dates_list:
                    logger.warning(f"Missing or empty route dates list: {route_dates_list}")
                else:
                    logger.info(f"Route found in file '{txt_file_name_without_ext}'")
                    msg = URL_HOME + "/images/pdf/" + txt_file_name_without_ext + \
                        ".pdf" + f"\n{json.dumps(route_dates_list)}"
                    logger.info(msg)
                    if not notification_already_sent:
                        logger.info("Sending pushbullet notification...")
                        pushbullet_notifier.notify(message=msg, **PUSHBULLET_CRED_DICT)

        # Prints out and send a notifiction for any exception that occured
        except Exception as err:
            err_str = f"Exception occured: [{repr(err)}]"
            logger.error(err_str)
            logger.error(f"Traceback: {traceback.format_exc()}")
            pushbullet_notifier.notify(message=json.dumps(traceback.format_exc()), **PUSHBULLET_CRED_DICT)

        # Eventually, wait for next iteration
        finally:
            logger.info(f"Waiting {WAIT_TIME} minutes for next iteration...")
            main_loop_iter_count += 1
            sleep(WAIT_TIME * 60)


if __name__ == '__main__':
    main()
