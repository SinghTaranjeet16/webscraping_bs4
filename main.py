# Standart imports
import os
import glob
import json
import traceback
from io import StringIO
from time import sleep, strftime, localtime

# 3rd party imports
import requests
from bs4 import BeautifulSoup
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from notifiers import get_notifier
from parse_text_file import save_imp_routes


URL_HOME = "http://www.airindia.in/"
PAGE = "evacuation-flight.htm"
DIR_PATH = os.path.dirname(os.path.realpath(__file__))

# Credentials used for notifiers library
# Credentials dictionary has the format {token=xxx}
PUSHBULLET_CRED_FILE = os.path.join(os.getcwd(), 'pushbullet_credentials')
PUSHBULLET_CRED_DICT = {}

# Wait time between sending queries to url (in minutes)
WAIT_TIME = 30


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


def extract_text_from_pdf(path):
    """
    Extract text from PDF file. Code copied from stackoverflow
    https://stackoverflow.com/questions/26494211/extracting-text-from-a-pdf-file-using-pdfminer-in-python#26495057s

    Arguments:
        path {path} -- OS file path for PDF file

    Returns:
        String -- Text format of the PDF file
    """
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()

    for page in PDFPage.get_pages(fp,
                                  pagenos,
                                  maxpages=maxpages,
                                  password=password,
                                  caching=caching,
                                  check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()

    return text


def main():

    # Initialize notifier instance and set credentials
    pushbullet_notifier = get_notifier('pushbullet')
    read_credentials(PUSHBULLET_CRED_FILE, PUSHBULLET_CRED_DICT)

    # Main processing loop
    while True:
        print(f"---------------------------------------------------")
        print(f"-      Running parser to fetch route details      -")
        print(f"-\t\t[{strftime('%Y-%m-%d %H:%M:%S',localtime())}]-")
        print(f"---------------------------------------------------")

        try:
            # HTML content of the website
            source = requests.get(URL_HOME + PAGE)
            if source.status_code != 200:
                raise Exception(f"Error getting to address {URL_HOME + PAGE} [Code = {source.status_code}]")

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
                print("[WARNING] Empty list for <h2> tag elements")
            for h2_tag in all_h2_tags:
                h2_tag_text = h2_tag.text.split('\n')[0]
                if 'evacuation flight schedule' in h2_tag_text.lower():
                    print(f"[INFO] - Found header '{h2_tag_text}'")
                    # Get pdf file name from href string
                    if not h2_tag.a['href']:
                        print(f"[WARNING] - Missing href for <h2> '{h2_tag_text}'")
                    else:
                        file_to_copy = os.path.join(DIR_PATH, h2_tag.a['href'].split('/')[-1])
                        if not os.path.isfile(file_to_copy):
                            print(f"[INFO] - PDF '{file_to_copy}' doesn't exists. Downloading...")
                            pdf_web_path = URL_HOME + h2_tag.a['href']
                            r = requests.get(pdf_web_path)
                            if r.status_code == 200:
                                with open(file_to_copy, 'wb') as f:
                                    f.write(r.content)
                                msg = f"File '{file_to_copy}' downloaded successfully"
                                print(f"[INFO] - {msg}")
                            else:
                                raise Exception(f"Failed to downloading {pdf_web_path} [Code = {r.status_code}]")
                        else:
                            print(f"[INFO] - PDF '{file_to_copy}' already exist!")

            # Extract text from PDF and save it to a text file
            pdf_file_list = glob.glob(os.path.join(DIR_PATH, "*.pdf"))
            if not pdf_file_list:
                raise Exception(f"No PDF files found in '{DIR_PATH}'")
            else:
                for pdf_file in pdf_file_list:
                    txt_file_path = os.path.join(DIR_PATH, f'{pdf_file}.txt')
                    if os.path.isfile(txt_file_path):
                        print(f"[INFO] - Text file '{txt_file_path}' already exists. Not parsing pdf")
                        # under the assumption that file already exists, notifiction has been sent before
                        notification_send = True
                        continue
                    # If text file doesn't exists before, parse text from pdf
                    notification_send = False
                    print(f"[INFO] - Converting {pdf_file} ...")
                    with open(txt_file_path, 'w') as f:
                        f.write(extract_text_from_pdf(pdf_file))

            # Parse text file to grab all the possible itenary details
            txt_file_list = glob.glob(os.path.join(DIR_PATH, "*.txt"))
            for txt_file in txt_file_list:
                route_info_list = save_imp_routes(txt_file, depart="DELHI", arrival="TORONTO")
                if not route_info_list:
                    print(f"[WARNING] - Missing or empty route info list: {route_info_list}")
                else:
                    print(f"[INFO] - Route found {route_info_list}")
                    if not notification_send:
                        print("[INFO] - Sending pushbullet notification")
                        pushbullet_notifier.notify(message=json.dumps(route_info_list), **PUSHBULLET_CRED_DICT)

        except Exception as err:
            err_str = f"Exception occured [{repr(err)}]"
            print(f"[ERROR] - {err_str}")
            print(f"[INFO] Traceback: {traceback.format_exc()}")
            pushbullet_notifier.notify(message=json.dumps(traceback.format_exc()), **PUSHBULLET_CRED_DICT)

        finally:
            print(f"[INFO] - Waiting {WAIT_TIME} minutes for next iteration...")
            sleep(WAIT_TIME * 60)


if __name__ == '__main__':
    main()
