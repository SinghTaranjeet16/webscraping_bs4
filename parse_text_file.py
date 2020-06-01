# Standart imports
import os
import re
from itertools import count

# New page identifier
PAGE_START_IDENTIFIER = "VANDE BHARAT MISSION"

# First is departure station and second is departure time
COLUMN_NAMES = ["DATE", "FLIGHT", "DEPARTURE", "ARRIVAL"]

# File path and itenary details for testing standalone app
LEAVING_FROM = "DELHI"
GOING_TO = "TORONTO"
TXT_FILE_PATH = os.path.join(
    os.getcwd(), "webscraping_bs4/Web-schedule-phase-2-complete-30-May-20-1400-Hrs-converted.txt")

# Standalone check for printing debug statments
STANDALONE = False


def print_standalone(arg):
    """
    Print only when running as a standalone program

    Arguments:
        str {String} -- String to print
    """
    if STANDALONE:
        print(arg)


def save_imp_routes(file_path, depart=LEAVING_FROM, arrival=GOING_TO):
    """
    This funciton will parse the text file that contains the data for all evacuation flights itenary

    Arguments:
        file_path {os.path} -- OS file path to the text data file

    Keyword Arguments:
        depart {string} -- Departure location (default: {LEAVING_FROM})
        arrival {string} -- Arrival location (default: {GOING_TO})

    Returns:
        List -- List of dictionaries of all the found routes based upon the parameters
    """
    # Page number counter
    counter = count()

    # Verify if file path exits
    # Read all file content in a list
    if not os.path.isfile(file_path):
        print_standalone(f"File path [{file_path}] is not valid!")
        return
    with open(file_path, 'r') as f:
        file_content = f.readlines()

    # Variables used for parsing
    # start_header_read: True when header related strings are found
    # Headers that exists are: DATE, FLIGHT, DEPARTURE STATION. ARRIVAL STATION, DEPARTURE TIME
    # header_used: A header section is found implying we can start collecting data
    start_header_read = False
    header_used = None

    # Dictionary that will save each parsed iternary details
    key_names = ["Date",
                 "Flight",
                 "Departure Station",
                 "Arrival Station",
                 "Departure Time"]

    # Final list containing all the routes
    final_route = []

    # Since we need to move the list item index manually, enumerator didn't seem useful
    list_idx = 0

    # Keep running loop until the departure flight entries aren't exhausted
    while True:
        line_text = file_content[list_idx].strip()
        print_standalone(f'Current line text: {line_text}')

        # New page identifier
        if PAGE_START_IDENTIFIER in line_text:
            page_number = next(counter) + 1
            print_standalone(f"On page number #{page_number}")

        # Arrival flights section
        # We will break the loop here since we're looking for outbound flights
        elif "arrival into India" in line_text:
            print_standalone(f"Departure flights section ended. Total pages parsed: {page_number}")
            break

        # Check if current line is not empty AND
        # Check if a header string element is detected. If yes, since data is a table...
        # ...all entries will start from same line index until empty line is detected
        elif line_text != "" and (any(x in line_text for x in COLUMN_NAMES) or start_header_read):
            # Since it's a new header, enable the boolean and increment list item index
            # It's done becaused the text file parsed from pdf have empty line OR
            # Header name is being continued in the next index
            if not start_header_read:
                start_header_read = True
                print_standalone(f"Header detected: {header_used}")
                header_used = line_text
                list_idx += 2
            # If's it's not new header, means it's the data porttion of the table
            # Each table entry is seperated by multiple spaces, however, data can also be spaced (eg NEW YORK)
            # Data is in the order as follows: Data, Flight, Dep station, Arr station, Dep data
            else:
                match_and_split_list = re.split("\s{2,}[^a-z0-9A-Z-]", line_text)
                if match_and_split_list and \
                   match_and_split_list[2] == depart and \
                   match_and_split_list[3] == arrival:
                    final_route.append(dict(zip(key_names, match_and_split_list)))
                else:
                    print_standalone(f"[WARNING] - No matching pattern found in '{line_text}'")
        # If current line is empty string AND we have header is currently being process...
        # ...implies that all data is parsed
        elif line_text == "" and start_header_read:
            start_header_read = False

        # Read next item in the file_content list
        list_idx += 1

    print_standalone("All departing flights list exhausted")
    print_standalone(f"Total available routes: {final_route}")
    return final_route


def main():
    """
    Main function
    """
    global STANDALONE
    STANDALONE = True

    save_imp_routes(TXT_FILE_PATH, LEAVING_FROM, GOING_TO)


if __name__ == "__main__":
    main()
