#To extract the ETF's NAV,AUM,Tracking error,Expense ratio
import pandas as PD
#To bypass the security checks
#https://github.com/ultrafunkamsterdam/undetected-chromedriver
import undetected_chromedriver.v2 as uc
from selenium import webdriver
import time
#To extract the values from the html tags
#https://selenium-python.readthedocs.io/locating-elements.html#
from selenium.webdriver.common.by import By

options = webdriver.ChromeOptions()
options.binary_location=r'/Applications/Google Chrome 2.app/Contents/MacOS/Google Chrome'
#undetected_chromedriver require a profile information
#Sets to create profile in chrome
#https://stackoverflow.com/questions/50635087/how-to-open-a-chrome-profile-through-user-data-dir-argument-of-selenium
options.user_data_dir = r'/Users/amithkanatt/Library/Application Support/Google/Chrome/Profile 1'
driver = uc.Chrome(r'/usr/local/Caskroom/chromedriver/96.0.4664.45/chromedriver',options=options)

#Create empty dataframe with column name
#https://www.kite.com/python/answers/how-to-create-an-empty-dataframe-with-column-names-in-python
columnname=['NAV','AUM','Expense_Ratio','Sctr_Expense_Ratio','Tracking_Error','Asset_Tracking_Error','Sector','URL']
extracted_value = PD.DataFrame(columns=columnname)

#Empty list to hold the values
temp_rowdetails=[]
temp_rowdata=[]


#Read the url file,using panda
 #Navigate to the location and read the data
loc='/Volumes/Project/ETFAnalyser/ETF/ETF_Data/ETF_URL.xlsx'
df = PD.read_excel(loc,sheet_name = 'Main Data_Nifty')
#Loop through the rows using "index",to extract the URL
#https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.index.html
for rwCount in  df.index:
	etf_url=df['URL'][rwCount]
	etf_sector=df['Sector'][rwCount]
	with driver:
		driver.get(etf_url)
		time.sleep(5)
#Extract all the text values under the class tag
#Retrieve the values by looping the list
#Source:https://stackoverflow.com/questions/28022764/python-and-how-to-get-text-from-selenium-element-webelement-object
		elements = driver.find_elements(By.XPATH,'//div[@class="value   text-15 ellipsis"]')
		#	print(elements.text)
		NAV=elements[0].text
		AUM = elements[1].text
		Expense_Ratio=elements[2].text
		Sctr_Expense_Ratio=elements[3].text
		Tracking_Error=elements[4].text
		Asset_Tracking_Error=elements[5].text
#Append the row details to the data frame using 'append' 
#https://www.geeksforgeeks.org/how-to-create-an-empty-dataframe-and-append-rows-columns-to-it-in-pandas
		extracted_value=extracted_value.append({'NAV':NAV,'AUM':AUM,'Expense_Ratio':Expense_Ratio,'Sctr_Expense_Ratio':Sctr_Expense_Ratio,'Tracking_Error':Tracking_Error,'Asset_Tracking_Error':Asset_Tracking_Error,'Sector':etf_sector,'URL':etf_url},ignore_index=True)

#Write the data into the excel file
extracted_value.to_excel(r'/Volumes/Project/ETFAnalyser/ETF_Data/ETFdetail.xlsx',index=False)




		
driver.quit()

	


#Scrape the data
#Write into a csv file data