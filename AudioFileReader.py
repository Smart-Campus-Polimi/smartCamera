from os import listdir
from os.path import isfile, join
mypath="/home/pi/Desktop/clientGate/Gate_Sounds"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
file = open("/home/pi/Desktop/clientGate/audioList.txt","w")
for x in onlyfiles:
	if not (x.endswith('.flac'))and not (x.startswith('.')):
		file.write(x)
		file.write("\n") 
file.close()
