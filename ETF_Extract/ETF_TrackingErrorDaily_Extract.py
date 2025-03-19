from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import os
import shutil
import logging
import subprocess
import re

# Set up directories
download_dir = os.path.abspath(r"D:\ETF_Data\ETFDataProcessing\ETFRawData\TrackingError")
os.makedirs(download_dir, exist_ok=True)

temp_download_dir = os.path.abspath(r"D:\TempDownloads")  # Temporary directory for downloads
os.makedirs(temp_download_dir, exist_ok=True)

# Function to get installed Chrome version
def get_chrome_version():
    try:
        result = subprocess.run(["reg", "query", "HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon", "/v", "version"], capture_output=True, text=True, check=True)
        match = re.search(r'version\s+REG_SZ\s+([\d.]+)', result.stdout)
        if match:
            return match.group(1)
    except Exception as e:
        logging.error(f"Error fetching Chrome version: {e}")
    return None

# Get Chrome version
chrome_version = get_chrome_version()
if chrome_version:
    logging.info(f"Detected Chrome version: {chrome_version}")
else:
    logging.warning("Could not detect Chrome version, using default ChromeDriver")

# Initialize undetected-chromedriver
options = uc.ChromeOptions()
prefs = {
    "download.default_directory": temp_download_dir,  # Temp download folder
    "download.prompt_for_download": False,  
    "directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
#options.add_argument("--headless")

driver = uc.Chrome(options=options)

try:
    #Step1: Navigate to AMFI website
    amfi_url = "https://www.amfiindia.com/research-information/other-data/tracking_errordata"
    driver.get(amfi_url)
    print("AMFI India website loaded.")
    time.sleep(10)

    #Step2: Select "Tracking Error" radio button
    tracking_error_radio = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@type='radio' and @value='1']"))  # Changed value from '2' to '1'
    )
    tracking_error_radio.click()
    logging.info("Selected 'Tracking Error' option")
    time.sleep(2)

    # Function to update dropdown values
    def update_dropdown(dropdown_id, value):
        script = """
        var select = document.getElementById(arguments[0]);
        if (select) {
            select.value = arguments[1];
            select.dispatchEvent(new Event('change', { bubbles: true }));
            var combobox = document.querySelector('.custom-combobox-input');
            if (combobox) {
                var selectedText = select.options[select.selectedIndex].text;
                combobox.value = selectedText;
                combobox.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }"""
        driver.execute_script(script, dropdown_id, value)
        print(f"Updated '{dropdown_id}' to: {value}")
        time.sleep(10)

    #Step3: Select "All" in Mutual Fund dropdown
    update_dropdown("AccMFName", "-1")

    time.sleep(20)

    #Step4: Select "10-Mar-2025" in Date Picker
    date_picker = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "dptracking"))  # Correct ID
        )
    driver.execute_script("arguments[0].value = '10-Mar-2025';", date_picker)
    print("Selected date: 10-Mar-2025")
    time.sleep(10)

    # Step 5: Click the "Go" Button
    go_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, "hrfGo"))
    )
    driver.execute_script("arguments[0].click();", go_button)
    print("Clicked 'Go' button.")

    # Step 6: Wait for the Excel icon to appear
    download_form = WebDriverWait(driver, 50).until(
    EC.presence_of_element_located((By.XPATH, "//div[@id='divDownloads']//form"))
    )
    # Submit the form to trigger download
    driver.execute_script("arguments[0].submit();", download_form)
    print("Download triggered.")  
 
  
    time.sleep(10)

    # Step 7: Wait for the File to Download
    def wait_for_download(directory, timeout=60):
        start_time = time.time()
        while time.time() - start_time < timeout:
            files = [f for f in os.listdir(directory) if f.endswith(".xls") or f.endswith(".xlsx")]
            if files:
                return os.path.join(directory, files[0])
            time.sleep(10)
        return None

    downloaded_file = wait_for_download(temp_download_dir)
    if downloaded_file:
        print(f"File downloaded: {downloaded_file}")
        new_filename = "Tracking_Error_Daily_10_Mar_2025.xls"
        new_filepath = os.path.join(download_dir, new_filename)
        shutil.move(downloaded_file, new_filepath)
        print(f"File moved to: {new_filepath}")
    else:
        print("Download failed or took too long.")

except Exception as e:
    print(f"An error occurred: {e}")
    with open("debug_page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    raise e

finally:
    driver.quit()
