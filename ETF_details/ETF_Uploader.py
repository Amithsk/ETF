#To upload the ETF data into the DB for reporting purpose
#This will be single program used to upload ETF from various index
import pandas as PD
from datetime import datetime
from calendar import month_name

dateInfo=datetime.now()
yearInfo=str(dateInfo.year)
dateNumber=str(dateInfo.strftime("%d"))
monthInfo=str(dateInfo.strftime("%b"))

print("Date information",yearInfo)
print("Year information",dateNumber)
print("Month information",monthInfo)
fileName='MW-ETF-'+dateNumber+'-'+monthInfo+'-'+yearInfo+'.csv'
loc='/Users/amithkanatt/Downloads/'+fileName
print("The file name is",fileName)
print("The location information",loc)




#NIFTY():
  #Read the data
  #Upload the data
#BSE():
	#Read the data
	#Upload the data


