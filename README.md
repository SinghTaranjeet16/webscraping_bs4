# Webscraping using beautifulsoup(4) and python(3.7.7)
* Current project code will scrap the Air-India web page to see if there a new entry for evacuation flights leaving India. 
* Will also check travel advisory page and changes are reported if pass a certain threshold
* Grabs the pdf file for evacuation routes, convert to text and parse it to find the appropriate to/from route details and eventually send the notification through _pushbullet_ to android.
* Route details will looks like this
```python
['20-May-2020', '1-Jun-2020']
```

# USAGE
* Clone the repo
* Fill in the correct credentials for _pushbullet_ in `pushbullet_credentials`
* Either you can run the code as `python3 main.py` or through Dockerfile as follows
    * Build image from Dockerfile `docker build --tag <name>:<tag> .`
    * Run the image in detatched mode `docker run -d -v $(pwd)/logs:/webscraping/logs --name <container_name> <name>:<tag>`
        * Or run it in interactive mode by using `-it` instead of `-d`
    * It should create a directory called _logs_ with the log file in it

# Requirements
* Python 3+ (tested on version 3.7.7)
* Do `pip install -r requirements.txt` (you might need to use `pip3` if you have Python 2 installed as well)
* Create 2 files _without extension_ in parent directory named `pushbullet_credentials` and `praw_credentials` and save information in those. Format will be `key=value`
* This code is dependent upon [PdfToText](https://github.com/jalan/pdftotext) python module for converting pdf to text file
    * A sub-dependency is _poppler_ which is easy to install on *nix* systems but require some elbow grease to work on windows
    * Best way to use it on windows is download binary from [Anaconda](https://anaconda.org/conda-forge/poppler/files)
* I am also using [Notifiers](https://github.com/notifiers/notifiers) to send notifications to android

# Optional
* Install Docker _(ext-id: ms-azuretools.vscode-docker)_ extension in VSCode for easy docker operations