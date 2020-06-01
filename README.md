# Webscraping using beautifulsoup(4) and python(3.7.7)
* Current project code will scrap the A!r!nd1A web page to see if there a new entry for evacuation flights leaving India. 
* Will also keep checking for changes on the travel advisory page
* Grab the pdf file for evacuation routes, convert to text and parse it to find the appropriate to/from route details and eventually send the notification through _pushbullet_ to android.
* Also required pushbullet credentials saved in a file in the same directory as the main.py
    * Pushbullet credentials have format `token=abc123def`
* Route details will looks like this
```python
[{'Date': '20-May-20', 'Flight': 'AI 0187', 'Departure Station': 'DELHI', 'Arrival Station': 'TORONTO', 'Departure Time': '1:00'},{'Date': '21-May-20', 'Flight': 'AI 0187', 'Departure Station': 'DELHI', 'Arrival Station': 'TORONTO', 'Departure Time': '1:00'}]
```
**NOTE**
* This code is dependent upon [PdfToText](https://github.com/jalan/pdftotext) python module for converting pdf to text file
    * A sub-dependency is _poppler_ which is easy to install on *nix* systems but require some elbow grease to work on windows
    * Best way to use it on windows is download binary from [Anaconda](https://anaconda.org/conda-forge/poppler/files)
* I am also using [Notifiers](https://github.com/notifiers/notifiers) to send notifications to android
