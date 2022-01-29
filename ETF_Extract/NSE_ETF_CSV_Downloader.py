
#To by the security checks
#https://github.com/ultrafunkamsterdam/undetected-chromedriver
import undetected_chromedriver as uc
from selenium import webdriver
import time
#To extract the values from the html tags
#https://selenium-python.readthedocs.io/locating-elements.html#
from selenium.webdriver.common.by import By
if __name__ == '__main__':
	options = webdriver.ChromeOptions()
	options.binary_location=r'/Applications/Google Chrome 2.app/Contents/MacOS/Google Chrome'
#undetected_chromedriver require a profile information
#Sets to create profile in chrome
#https://stackoverflow.com/questions/50635087/how-to-open-a-chrome-profile-through-user-data-dir-argument-of-selenium
	options.user_data_dir = r'/Users/amithkanatt/Library/Application Support/Google/Chrome/Profile 1'
	driver = uc.Chrome(options=options)
#with helps better exception handling
#https://www.geeksforgeeks.org/with-statement-in-python/
	with driver:
		driver.get('https://www.nseindia.com/market-data/exchange-traded-funds-etf')
		time.sleep(5)
#To find out the elements in HTML
#https://selenium-python.readthedocs.io/locating-elements.html#
#This option is very resuable one
		downloadcsv= driver.find_element(By.XPATH,"//img[@title='csv']/parent::a")
		driver.execute_script("arguments[0].click();",downloadcsv)
		driver.quit()

