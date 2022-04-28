#To extract the ETF's NAV,AUM,Tracking error,Expense ratio
#This code needs to rewritten to extract the values from  DB rather than file
#Pending DB table needs to be created to store the URLS of the ETF's
#How to connect to DB and read the values
import pandas as PD
import datetime
#To bypass the security checks
#https://github.com/ultrafunkamsterdam/undetected-chromedriver
import undetected_chromedriver as uc
from selenium import webdriver
import time
#To extract the values from the html tags
#https://selenium-python.readthedocs.io/locating-elements.html#
from selenium.webdriver.common.by import By

if __name__ == '__main__':
	options = webdriver.ChromeOptions()
	options.binary_location=r'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
#undetected_chromedriver require a profile information
#Sets to create profile in chrome
#https://stackoverflow.com/questions/50635087/how-to-open-a-chrome-profile-through-user-data-dir-argument-of-selenium
	#options.user_data_dir = r'/Users/amithkanatt/Library/Application Support/Google/Chrome/Profile 1'
	driver = uc.Chrome(options=options)
#Create empty dataframe with column name
#https://www.kite.com/python/answers/how-to-create-an-empty-dataframe-with-column-names-in-python

	columnname=['NAV','AUM','Expense_Ratio','Sctr_Expense_Ratio','Tracking_Error','Asset_Tracking_Error','Sector','ETFname','ETFSymbol','URL']
	extracted_value = PD.DataFrame(columns=columnname)
#To get the month information	
	monthinfo = (datetime.datetime.now()).strftime("%b")
#Read the url file,using panda
#Navigate to the location and read the data
	loc='/Volumes/Project/ETFAnalyser/ETF/ETF_Data/ETF_fund_details/ETF_URLS/ETF_URL.xlsx'
	df = PD.read_excel(loc,sheet_name = 'Batch4')
#Loop through the rows using "index",to extract the URL
#https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.index.html
	for rwCount in  df.index:
		etf_url=df['URL'][rwCount]
		etf_sector=df['Sector'][rwCount]
		etf_symbol=df['Symbol'][rwCount]
		with driver:
			driver.get(etf_url)
			time.sleep(5)
#Extract all the text values under the class tag
#Retrieve the values by looping the list
#Source:https://stackoverflow.com/questions/28022764/python-and-how-to-get-text-from-selenium-element-webelement-object

			elements = driver.find_elements(By.XPATH,'//div[@class="jsx-3420801268"]')
			NAV=elements[0].text
			AUM = elements[1].text
			Expense_Ratio=elements[2].text
			Sctr_Expense_Ratio=elements[3].text
			Tracking_Error=elements[4].text
			Asset_Tracking_Error=elements[5].text
#Extract the etfname(it was tricky)
#Need to add the get_attribute function to get the text information from th H1		
#https://stackoverflow.com/questions/43429788/python-selenium-finds-h1-element-but-returns-empty-text-string
			etfName = driver.find_element(By.XPATH,'//h1[@class="jsx-1588473315 typography-h4 mb4 ellipsis"]').get_attribute('textContent')

#Append the row details to the data frame using 'append' 
#https://www.geeksforgeeks.org/how-to-create-an-empty-dataframe-and-append-rows-columns-to-it-in-pandas

			extracted_value=extracted_value.append({'NAV':NAV,'AUM':AUM,'Expense_Ratio':Expense_Ratio,'Sctr_Expense_Ratio':Sctr_Expense_Ratio,'Tracking_Error':Tracking_Error,'Asset_Tracking_Error':Asset_Tracking_Error,'Sector':etf_sector,'ETFname':etfName,'ETFSymbol':etf_symbol,'URL':etf_url},ignore_index=True)
			print("\nExtracte values",NAV)
			print("\n Extacted values AUM",AUM)
			print("\nETF name",etfName)
#To remove the text that's captured during the scraping 
	extracted_value=extracted_value.replace('High','',regex=True)
	extracted_value=extracted_value.replace('Low','',regex=True)
	extracted_value=extracted_value.replace('Returns','',regex=True)
	extracted_value=extracted_value.replace('Realtime NAV','',regex=True)
	extracted_value=extracted_value.replace('AUM','',regex=True)
	extracted_value=extracted_value.replace('Expense Ratio','',regex=True)

#Write the data into the excel file
	extracted_value.to_excel(r'/Volumes/Project/ETFAnalyser/ETF/ETF_Data/ETF_fund_details/ETFdetails'+monthinfo+'_4'+'.xlsx',index=False)
#https://www.browserstack.com/guide/close-browser-in-selenium
#Closing the browser
	driver.close()