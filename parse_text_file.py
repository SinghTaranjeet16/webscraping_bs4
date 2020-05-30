# Standart imports
import os
from itertools import count

# New page identifier
PAGE_START_IDENTIFIER = "VANDE BHARAT MISSION"

# First is departure station and second is departure time
COLUMN_NAMES = ["DATE", "FLIGHT", "DEPARTURE", "ARRIVAL"]

# File path and itenary details for testing standalone app
LEAVING_FROM = "DELHI"
GOING_TO = "TORONTO"
TXT_FILE_PATH = os.path.join(os.getcwd(), "webscraping_bs4/pdfToText.txt")

# Standalone check for printing debug statments
STANDALONE = False


def print_standalone(str):
    """
    Print only when running as a standalone program

    Arguments:
        str {String} -- String to print
    """
    if STANDALONE:
        print(str)


def save_imp_routes(file_path, depart=LEAVING_FROM, arrival=GOING_TO):
    """
    This function will parse the text file that contains the data for all evacuation flights itenary


    Arguments:
        file_path {path} -- OS file path to the text data file
        depart {string} -- Departure location. E.g. DELHI
        arrival {string} -- Arriving location. E.g. TORONTO

    Returns:
        List -- Nested list of all the found appropriate itenaries
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
    # start_header_read: True when we start reading a new header
    # Headers that exists are: DATE, FLIGHT, DEPARTURE STATION. ARRIVAL STATION, DEPARTURE TIME
    # header_used: Current header that we're parsing data for
    # is_final_header: Identify if current header is also the final header (DEPARTURE_TIME)
    start_header_read = False
    header_used = None
    is_final_header = False

    # Dictionary that will save the parsed iternary details
    entries = {"DATE": [],
               "FLIGHT": [],
               "DEPARTURE_STATION": [],
               "ARRIVAL": [],
               "DEPARTURE_TIME": []}

    # Since we need to move the list item index manually, enumerator didn't seem useful
    list_idx = 0

    # Keep running loop until the departure flight entries aren't exhausted
    while True:
        line_text = file_content[list_idx].strip()

        # New page identifier
        if PAGE_START_IDENTIFIER in line_text:
            page_number = next(counter) + 1

        # Arrival flights section
        # We will break the loop here since we're looking for outbound flights
        elif "arrival into India" in line_text:
            print_standalone(f"Departure flights section ended. Total pages parsed: {page_number}")
            break

        # Check if current line is not empty AND
        # Check either a new header is detected OR
        # Check if current header values are still being collected
        elif line_text != "" and (any(x in line_text for x in COLUMN_NAMES) or start_header_read):
            # Since it's a new header, enable the boolean and increment list item index
            # It's done becaused the text file parsed from pdf have empty line OR
            # Header name is being continued in the next index
            if not start_header_read:
                start_header_read = True
                header_used = line_text
                list_idx += 1  # ['departure','station'] or ['date','']
            # If's it's not new header, make sure its entry is added to correct iternary dict element key
            # For understanding about list_idx-1, see the {if} loop comment above.
            # In short, it contains the continuing text of the header string
            else:
                if header_used == "DEPARTURE" and file_content[list_idx - 1].strip() == "STATION":
                    header_used += '_STATION'
                elif header_used == "DEPARTURE" and file_content[list_idx - 1].strip() == "TIME":
                    header_used += '_TIME'
                    # Departure_time is final column data we need to parse
                    if not is_final_header:
                        is_final_header = True
                entries[header_used].append(line_text)

        # If current line is empty string AND we have header is currently being process
        # Implies that all data is parsed (since data is in continuous index followed by new line)
        elif line_text == "" and start_header_read:
            start_header_read = False
            # If it's final DEPARTURE_TIME header, then clear out the variables
            if is_final_header:
                is_final_header = False

        # Read next item in the file_content list
        list_idx += 1

    print_standalone("All departing flights list exhausted")

    # Create a nested list of all the iternaries found IF condition matched
    dep_avail_dates = []
    for date, flight, dep_sta, arr, dep_time in zip(entries['DATE'],
                                                    entries['FLIGHT'],
                                                    entries['DEPARTURE_STATION'],
                                                    entries['ARRIVAL'],
                                                    entries['DEPARTURE_TIME']):
        if dep_sta.upper() == depart.upper() and arr.upper() == arrival.upper():
            dep_avail_dates.append({'date': date,
                                    'flight': flight,
                                    'dep_sta': dep_sta,
                                    'arr_sta': arr,
                                    'dep_time': dep_time})

    print_standalone(f"Available routes: {dep_avail_dates}")
    return dep_avail_dates


def main():
    """
    Main function
    """
    global STANDALONE
    STANDALONE = True

    save_imp_routes(TXT_FILE_PATH, LEAVING_FROM, GOING_TO)


if __name__ == "__main__":
    main()
