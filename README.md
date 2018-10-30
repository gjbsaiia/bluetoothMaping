# bluetoothMaping
For linux: creates running 'manifest' of bluetooth devices around you with their RSSI</br>

- didn't want to bother with a database, so  I had 'buildManifest.py' literally write entries into 'manifest.py'. 

- this does a couple things. it means that you have a listing accessable by all other programs, and a dictionary
for all your python programs.

- I was using this for bluetooth tracking, but can definitely be used for a bunch of other purposes.

## also beacon-scan.h is not my code. 
It is only being used here as it properly starts bluetoothctl (which I had a hard time doing in my own shell script), </br>
and prints a nice feed to look at while buildManifest.py runs. All the data is collected and processed by my own code</br>
in buildManifest.py.

#### sidenote:
because you're updating manifest.py with each run of buildManifest.py. You need to restart a program that has ported</br>
manifest.py in order to get any updates to it. I suggest a control program that uses subprocess to call each .py </br>
script using manifest.py. This allows for manifest.pyc to be regenerated with each run.
