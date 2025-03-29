from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
import time
import os
import subprocess
import re
import logging
import shutil

# Set up directories
download_dir = os.path.abspath(r"D:\ETF_Data\ETFDataProcessing\ETFRawData\ExpenseRatio")
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

def select_year(driver, year):
    """ Selects the financial year """
    print("Selecting Year...")
    
    # Click the dropdown using JavaScript to ensure it's interacted with
    dropdown = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='divFinTER']//a")))
    driver.execute_script("arguments[0].click();", dropdown)
    time.sleep(5)

    # Locate the input and enter the year
    dropdown_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='divFinTER']//input")))
    dropdown_input.clear()
    dropdown_input.send_keys(year)
    time.sleep(5)
    dropdown_input.send_keys("\n")
    
    print(f"Selected Year: {year}")

def select_month(driver, month):
    """ Selects the month """
    print("Selecting Month...")
    # Click the dropdown using JavaScript to ensure it's interacted with
    dropdown = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='divMonthTER']//a")))
    driver.execute_script("arguments[0].click();", dropdown)
    time.sleep(5)
    # Locate the input and enter the month
    dropdown_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='divMonthTER']//input")))
    dropdown_input.send_keys(month)
    dropdown_input.send_keys("\n")
    print(f"Selected Month: {month}")

def select_scheme_type(driver, scheme_type):
    """ Selects the scheme type (Open-ended) """
    print("Selecting Scheme Type...")
    # Click the dropdown using JavaScript to ensure it's interacted with
    dropdown = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='divNav']//a")))
    driver.execute_script("arguments[0].click();", dropdown)
    time.sleep(5)
    # Locate the input and enter the scheme type
    dropdown_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='divNav']//input")))
    dropdown_input.send_keys(scheme_type)
    dropdown_input.send_keys("\n")
    print(f"Selected Scheme Type: {scheme_type}")

def select_scheme_category(driver, category):
    """Selects the scheme category and ensures proper XHR triggering"""
    print("Selecting Scheme Category...")
    
    # Wait for and click the dropdown
    dropdown = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='divMFScheme']//a")))
    driver.execute_script("arguments[0].click();", dropdown)
    time.sleep(2)  # Small delay for dropdown to open
    
    # Clear and input the category
    dropdown_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='divMFScheme']//input")))
    dropdown_input.clear()
    dropdown_input.send_keys(category)
    
    # Wait for options to appear
    time.sleep(2)
    
    # Select the option by simulating key presses
    dropdown_input.send_keys(Keys.ARROW_DOWN)  # Navigate to first matching option
    dropdown_input.send_keys(Keys.RETURN)      # Select it
    
    print(f"Selected Scheme Category: {category}")
    
    # Additional wait to ensure XHR completes
    time.sleep(5)

def select_sub_category(driver, sub_category, max_attempts=3, wait_timeout=30):
    """Selects the sub-category with robust validation and detailed DOM logging"""
    from selenium.common.exceptions import NoSuchElementException, TimeoutException
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    import time
    import json

    def log_dom_state():
        """Logs current DOM state for debugging"""
        state = {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'input_value': input_field.get_attribute('value'),
            'select_element': {
                'selected_index': select_element.get_attribute('selectedIndex'),
                'options': [opt.text for opt in select_element.find_elements(By.TAG_NAME, 'option')],
                'selected_option': select_element.find_element(By.CSS_SELECTOR, 'option[selected]').text if len(select_element.find_elements(By.CSS_SELECTOR, 'option[selected]')) > 0 else None
            },
            'hidden_select_html': select_element.get_attribute('outerHTML'),
            'visible_input_html': input_field.get_attribute('outerHTML')
        }
        print("DOM State:", json.dumps(state, indent=2))
        return state

    wait = WebDriverWait(driver, wait_timeout)
    print(f"Attempting to select Sub-Category: {sub_category}...")

    for attempt in range(1, max_attempts + 1):
        try:
            # --- PHASE 1: Locate elements ---
            dropdown_container = wait.until(
                EC.presence_of_element_located((By.ID, "divSubSchemeComp")))
            select_element = dropdown_container.find_element(By.TAG_NAME, "select")
            input_field = dropdown_container.find_element(By.CSS_SELECTOR, "input.custom-combobox-input")
            toggle_button = dropdown_container.find_element(By.CSS_SELECTOR, "a.custom-combobox-toggle")

            # Log initial state
            print("\n=== Initial State ===")
            initial_state = log_dom_state()

            # --- PHASE 2: Open and select ---
            driver.execute_script("arguments[0].click();", toggle_button)
            time.sleep(1)
            
            input_field.clear()
            input_field.send_keys(sub_category)
            time.sleep(1)  # Wait for filtering
            
            input_field.send_keys(Keys.ARROW_DOWN)
            input_field.send_keys(Keys.RETURN)
            time.sleep(2)  # Wait for potential JavaScript handlers

            # --- PHASE 3: Verify and log ---
            print("\n=== After Selection ===")
            post_selection_state = log_dom_state()

            # Check if the website's JavaScript reset our selection
            if (post_selection_state['input_value'].lower() != sub_category.lower() or
                (post_selection_state['select_element']['selected_option'] and 
                 post_selection_state['select_element']['selected_option'].lower() != sub_category.lower())):
                
                print("\n=== Selection Was Reset ===")
                print("Possible causes:")
                print("- Website JavaScript event handlers")
                print("- AJAX call resetting the form")
                print("- Validation logic rejecting the selection")
                
                # Try direct DOM manipulation as last resort
                print("Attempting direct DOM manipulation...")
                driver.execute_script(f"""
                    var select = arguments[0];
                    var input = arguments[1];
                    var targetValue = arguments[2];
                    
                    // Find matching option
                    for (var i = 0; i < select.options.length; i++) {{
                        if (select.options[i].text.toLowerCase().includes(targetValue.toLowerCase())) {{
                            select.selectedIndex = i;
                            // Trigger change events
                            var event = new Event('change', {{ bubbles: true }});
                            select.dispatchEvent(event);
                            input.value = select.options[i].text;
                            input.dispatchEvent(new Event('input'));
                            break;
                        }}
                    }}
                """, select_element, input_field, sub_category)
                
                time.sleep(2)
                print("\n=== After DOM Manipulation ===")
                final_state = log_dom_state()

            # Final verification
            current_value = input_field.get_attribute('value')
            if current_value.lower() != sub_category.lower():
                raise ValueError(f"Final verification failed. Display shows: '{current_value}'")

            print(f"Successfully selected Sub-Category: {sub_category}")
            return True
            
        except Exception as e:
            print(f"\nAttempt {attempt} failed: {str(e)}")
            if attempt == max_attempts:
                print("\n=== Final Debug Info ===")
                print("Window.console logs:")
                logs = driver.get_log('browser')
                for log in logs[-5:]:  # Show last 5 browser logs
                    print(log)
                
                print("\nCurrent Form State:")
                try:
                    form_state = driver.execute_script("""
                        return {
                            subSchemeComp: document.getElementById('SubSchemeComp').value,
                            inputValue: document.querySelector('#divSubSchemeComp input').value,
                            eventListeners: {
                                change: jQuery._data(document.getElementById('SubSchemeComp'), 'events').change,
                                input: jQuery._data(document.querySelector('#divSubSchemeComp input'), 'events').input
                            }
                        }
                    """)
                    print(json.dumps(form_state, indent=2))
                except Exception as js_error:
                    print(f"Could not get form state: {str(js_error)}")
                
                print(f"Failed to select sub-category after {max_attempts} attempts")
                driver.save_screenshot("subcategory_failure_final.png")
                return False
            
            time.sleep(3)  # Wait before retrying

def select_mutual_fund(driver, mutualfund):
    """ Selects the mutal fund AMC """
    print("Selecting Mutual fund AMC...")
    dropdown = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='divMFNameScheme']//a")))
    driver.execute_script("arguments[0].click();", dropdown)    
    time.sleep(5)

    # Locate the input and enter the scheme category
    dropdown_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='divMFNameScheme']//input")))
    dropdown_input.send_keys(mutualfund)
    dropdown_input.send_keys("\n")
    print(f"Selected Sub-Category: {mutualfund}")

try:
    # Open the website
    url = "https://www.amfiindia.com/ter-of-mf-schemes"
    driver.get(url)
    print("AMFI India website loaded.")
    time.sleep(5)  # Ensure the page is fully loaded
    month_year="February-2025"

    # Explicit wait for elements
    wait = WebDriverWait(driver, 20)
    # Select dropdown values
    select_year(driver, "2024-2025")
    time.sleep(10)
    select_month(driver, month_year)
    time.sleep(10)
    select_scheme_type(driver, "Open Ended")
    time.sleep(10)
    select_scheme_category(driver, "Other Scheme")
    time.sleep(20)
    select_sub_category(driver, "Other  ETFs")
    time.sleep(10)
    select_mutual_fund(driver, "All")

    # Click the 'Go' button
    print("Clicking 'Go' button...")
    go_button = wait.until(EC.element_to_be_clickable((By.ID, "hrfGo")))
    go_button.click()
    print("Clicked 'Go' button.")
    
    time.sleep(20)

   
    # Step 10: Submit the Download Form
    form = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//div[@id='divDownloads']/form"))
    )
    driver.execute_script("arguments[0].submit();", form)
    print("Submitted download form.")
    time.sleep(20)

    

  # Step 11: Wait for the File to Download
    def wait_for_download(directory, filename="AMFI_Reports.xls", timeout=60):
        file_path = os.path.join(directory, filename)
        start_time = time.time()

        print(f"[INFO] Monitoring file: {file_path}")

        if not os.path.exists(file_path):
            print(f"[ERROR] File {filename} not found in directory!")
            return None

        last_size = -1
        while time.time() - start_time < timeout:
            try:
                current_size = os.path.getsize(file_path)

                if current_size == last_size:
                    print(f"[SUCCESS] File download complete: {file_path}")
                    return file_path

                last_size = current_size
                print(f"[DEBUG] File size changing... Current size: {current_size}")

            except Exception as e:
                print(f"[WARNING] Error accessing file: {e}")

            time.sleep(2)  # Wait before checking again

            print(f"[ERROR] Timeout reached. File {filename} might be incomplete.")
        return None

    downloaded_file = wait_for_download(temp_download_dir)
    if downloaded_file:
        print(f"File downloaded: {downloaded_file}")
        #Rename the file before moving
        new_filename = f"ExpenseRatio_{month_year}.xls"
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

