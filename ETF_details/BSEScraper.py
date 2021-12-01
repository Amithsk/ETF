
#To bypass the security checks
#https://github.com/ultrafunkamsterdam/undetected-chromedriver
import undetected_chromedriver.v2 as uc
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import time
#To extract the values from the html tags
#https://selenium-python.readthedocs.io/locating-elements.html#
from selenium.webdriver.common.by import By
#To export the values,lets use Pandas
import pandas as PD
import datetime
dateInfo =  datetime.date.today()

options = webdriver.ChromeOptions()
#options.add_argument('--headless')
options.binary_location=r'/Applications/Google Chrome 2.app/Contents/MacOS/Google Chrome'
#undetected_chromedriver require a profile information
#Sets to create profile in chrome
#https://stackoverflow.com/questions/50635087/how-to-open-a-chrome-profile-through-user-data-dir-argument-of-selenium
options.user_data_dir = r'/Users/amithkanatt/Library/Application Support/Google/Chrome/Profile 1'
driver = uc.Chrome(r'/usr/local/Caskroom/chromedriver/94.0.4606.61/chromedriver',options=options)
#To extract the column values
#How to extract table value using selenium+python webdriver
#https://www.lambdatest.com/blog/how-to-handle-web-table-in-selenium-webdriver/
before_XPath = "//table[@name='eftfname6']//tbody//tr[1]//th["
afterth_XPath = "]"
#To extract the row values
rowbefore_XPath = "//table[@name='eftfname6']//tbody//tr["
rowafter_XPath = "]"
colbefore_Xpath="//td["
colafter_Xpath="]"

#To generate empty list 
columnname=[]
rowdata=[]
rowdetails=[]


#with helps better exception handling
#https://www.geeksforgeeks.org/with-statement-in-python/
with driver:
	driver.get('https://www.bseindia.com/markets/etf/ETF_MktWatch.aspx')
	time.sleep(5)
	
	#To find out the elements in HTML
	#https://selenium-python.readthedocs.io/locating-elements.html#
	#This option is very resuable one
	#find_elements will return a list find_element will return WebElement
	rowInfo= driver.find_elements(By.XPATH,"//table[@name='eftfname6']//tbody//tr")
	columnInfo=driver.find_elements(By.XPATH,"//table[@name='eftfname6']//tbody//tr[1]//th")
	print("The table row info",len(rowInfo))
	print("The table column info",len(columnInfo))
	#Extract the columnInformation
	for column in range(1,(len(columnInfo)+1)):
		finalXpath=before_XPath+str(column)+afterth_XPath
		columndetails=driver.find_element(By.XPATH,finalXpath).text
		columnname.append(columndetails)

		
	
	#Extract the rowInformation

	for row in range(2,(len(rowInfo)+1)):
		for column in range (1,(len(columnInfo)+1)):
			finalXpath=rowbefore_XPath+str(row)+rowafter_XPath+colbefore_Xpath+str(column)+colafter_Xpath
			#rowdetails will have all the row information as list,row information in a row
			rowdetails.append(driver.find_element(By.XPATH,finalXpath).text)
		
		#Append the row details to a list
		rowdata.append(rowdetails)
		
		#To flush out the row content,so that row information is not append in the next loop
		rowdetails=[]

	#Create empty dataframe with column name
	#https://www.kite.com/python/answers/how-to-create-an-empty-dataframe-with-column-names-in-python
	#df = PD.DataFrame(rowInfo,columns=columnname)

	#Write the extracted information into data frame
	df = PD.DataFrame(rowdata,columns=columnname)
	#print("The dataframe",df)
	#Write the data into the csv file
	df.to_excel(r'/Volumes/Project/WebScrapper/JVZOO/data/'+str(dateInfo)+'.xlsx',index=False)

	driver.quit()