# Standart imports
import os
import re
import logging

# New page identifier
PAGE_START_IDENTIFIER = "CARES"

# Set logging details for this module
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
fh = logging.StreamHandler()
fh_formatter = logging.Formatter('%(asctime)s %(module)s - %(message)s')
fh.setFormatter(fh_formatter)
logger.addHandler(fh)

# File path and itenary details for testing standalone app
LEAVING_FROM = "DELHI"
GOING_TO = "TORONTO"
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
TXT_FILE_PATH = os.path.join(DIR_PATH, 'Corrected-Copy-of-Mission-Vande-phase-2-schedule.txt')
ITER_PATTERN = re.compile("([0-9]+-[A-Za-z]+-[0-9]+.*)")

# Standalone check for printing debug statments
STANDALONE = False


def save_imp_routes(file_path, depart=LEAVING_FROM, arrival=GOING_TO):
    """
    This funciton will parse the text file that contains the data for all evacuation flights itenary

    Arguments:
        file_path {os.path} -- OS file path to the text data file

    Keyword Arguments:
        depart {string} -- Departure location (default: {LEAVING_FROM})
        arrival {string} -- Arrival location (default: {GOING_TO})

    Returns:
        List -- List of departue dates
    """

    # Verify if file path exits
    # Read all file content in a list
    if not os.path.isfile(file_path):
        logger.critical(f"File path [{file_path}] is not valid!")
        return
    with open(file_path, 'r') as f:
        file_content = f.readlines()

    # Final list containing all the routes
    final_route_dates = []

    # Keep running loop until the departure flight entries aren't exhausted
    page_number = 0
    for line_text in file_content:
        line_text = line_text.strip()
        logger.debug(f'Current line text: {line_text}')

        # New page identifier
        # Removes any spaces in the line text
        if line_text.strip().upper() == PAGE_START_IDENTIFIER:
            page_number += 1
            logger.info(f"On page number #{page_number}")

        # Arrival flights section
        # We will break the loop here since we're looking for outbound flights
        elif "ARRIVAL INTO INDIA" in line_text.upper():
            logger.info(f"Departure flights section ended. Total pages parsed: {page_number}")
            break

        # If it's neither page starting string nor arrival flights
        # Then search for pattern of iternary details
        else:
            match_pattern = re.search(ITER_PATTERN, line_text)
            if match_pattern:
                logger.debug(f"Search group-1: {match_pattern.group(1)}")
                # Split the found pattern where each column is seperated by multiple spaces
                # Although a column item can have 1 space in between (e.g. NEW YORK)
                match_and_split_list = re.split("\s{2,}", match_pattern.group(1))
                # For some file parsed text, if flight name is split as well, join them
                if match_and_split_list[1].upper() == "AI":
                    match_and_split_list[1] += ' ' + match_and_split_list.pop(2)
                logger.debug(f"split list: {match_and_split_list}")
                # List items will be: Date, Flight, Dep station, Dep time, Arr station, Arr time, Arrival data
                if match_and_split_list[2].upper() == depart and \
                        match_and_split_list[4].upper() == arrival:
                    logger.info(f"MATCH FOUND IN LINE: {line_text}")
                    if not match_and_split_list[0] in final_route_dates:
                        final_route_dates.append(match_and_split_list[0])
                else:
                    logger.debug(f"No matching route found in '{line_text}'")

    logger.info("Departing flights list exhausted")
    logger.info(f"All available dates: {final_route_dates}")
    return final_route_dates


def main():
    """
    Main function
    """
    global STANDALONE
    STANDALONE = True

    save_imp_routes(TXT_FILE_PATH, LEAVING_FROM, GOING_TO)


if __name__ == "__main__":
    main()
