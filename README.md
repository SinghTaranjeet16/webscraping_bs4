# Webscraping using beautifulsoup(4) and python(3)
Current project code will scrap the A!r!nd1A web page to see if there a new entry for evacuation flights leaving India. 
Grab the pdf file for evacuation routes, convert to text and parse it to find the appropriate to/from route details and eventually send the notification through _pushbullet_ to android.
Route details will looks like this
```python
[{'date': '20-May-20', 'flight': 'AI  0187', 'dep_sta': 'DELHI', 'arr_sta': 'TORONTO', 'dep_time': '1:00'}, {'date': '21-May-20', 'flight': 'AI  0187', 'dep_sta': 'DELHI', 'arr_sta': 'TORONTO', 'dep_time': '1:00'}, {'date': '24-May-20', 'flight': 'AI  0187', 'dep_sta': 'DELHI', 'arr_sta': 'TORONTO', 'dep_time': '1:00'}]
```
