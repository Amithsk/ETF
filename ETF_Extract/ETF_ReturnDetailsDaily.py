from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import shutil
import time
import os
import glob


# Set up directories
download_dir = os.path.abspath(r"D:\ETF_Data\ETFDataProcessing\ETFRawData\Returns")
os.makedirs(download_dir, exist_ok=True)

temp_download_dir = os.path.abspath(r"D:\TempDownloads")  # Temporary directory for downloads
os.makedirs(temp_download_dir, exist_ok=True)

# Initialize the undetected-chromedriver
options = uc.ChromeOptions()
prefs = {
    "download.default_directory": temp_download_dir,  # Set default download directory
    "download.prompt_for_download": False,      # Disable download prompt
    "directory_upgrade": True,                  # Auto-upgrade if directory exists
    "safebrowsing.enabled": True                # Enable safe browsing
}
options.add_experimental_option("prefs", prefs)
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
# options.add_argument("--headless")

driver = uc.Chrome(options=options)

try:
    # Step 1: Navigate to the AMFI website
    amfi_url = "https://www.amfiindia.com/research-information/other-data/mf-scheme-performance-details"
    driver.get(amfi_url)
    print("AMFI India website loaded.")

    # Step 2: Wait for Cloudflare challenge to resolve
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    print("Cloudflare challenge resolved.")

    # Step 3: Switch to the iframe containing the target content
    iframe = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, 'valueresearchonline.com/amfi/fund-performance')]"))
    )
    driver.switch_to.frame(iframe)
    print("Switched to iframe.")

    # Step 4: Use JavaScript to select dropdown values
    # Helper function to update dropdowns
    def update_dropdown(dropdown_id, value):
        dropdown_js = """
            var select = document.getElementById(arguments[0]);
            select.value = arguments[1];
            var event = new Event('change', { bubbles: true });
            select.dispatchEvent(event);
        """
        driver.execute_script(dropdown_js, dropdown_id, value)
        time.sleep(1)  # Allow the page to process the change
        # Verify the dropdown value
        current_value = driver.execute_script(f"return document.getElementById('{dropdown_id}').value;")
        print(f"Updated '{dropdown_id}' to: {current_value}")

    # Step 4: Update dropdowns
    update_dropdown("end-type", "1")  # Open-ended
    update_dropdown("primary-category", "SOTH")  # Other
    update_dropdown("category", "SOTH_IXETF")  # Index Funds/ETFs
    update_dropdown("amc", "ALL")  # All

    # Update the "nav-date" field to "22-Jan-2025"
    try:
        date='22-Jan-2025'
        driver.execute_script("""var dateInput = document.getElementById('nav-date');
        if (dateInput) {
            dateInput.value = arguments[0];
            var event = new Event('change', { bubbles: true });
            dateInput.dispatchEvent(event);
            console.log("Date input updated successfully.");
        } else {
            console.log("Error: Date input field not found.");
        }""", date)  # Pass 'date' as an argument
        print("Date input updated to ",date)
        time.sleep(10)
    except Exception as e:
        print(f"Error updating date: {e}")
        with open("debug_date.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        raise

    # Step 5: Click the "Go" button
    try:
        go_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//form[@id='form-fund-details']//button[@type='submit' and contains(@class, 'btn-primary')]"))
        )
        driver.execute_script("arguments[0].click();", go_button)
        print("Go button clicked.")
    except Exception as e:
        print(f"Error clicking 'Go' button: {e}")
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        raise

    # Step 6: Wait for the table to load
    try:
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#fund-data tbody tr"))
        )
        print("Table data loaded successfully.")
    except Exception as e:
        print(f"Error loading table: {e}")
        with open("debug_table.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        raise
    # Step 7: Click the "Download Excel" link
      # Click the download link
    try:
        # Wait for the download link to be clickable
        download_link = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, "download-report-excel")))
        # Scroll the element into view (if necessary)
        driver.execute_script("arguments[0].scrollIntoView(true);", download_link)
        # Click the download link
        download_link.click()
        print("Clicked the 'Download Excel' link.")
    except Exception as exc:
        print(f"Error clicking 'Download Excel' link: {exc}")
     # Save the page source and screenshot for debugging
        with open("debug_download.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
            driver.save_screenshot("debug_download.png")
    def wait_for_download(directory, timeout=60):
        start_time = time.time()
        last_files = set()
        last_size = {}
        print(f"[INFO] Monitoring directory: {directory}")

        while time.time() - start_time < timeout:
            # Get all .xls files in the directory
            xls_files = set(glob.glob(os.path.join(directory, '*.xls')))
        
            # Check if new files appeared
            new_files = xls_files - last_files

        if new_files:
            downloaded_file = new_files.pop()  # Get the first new file
            print(f"[SUCCESS] File detected: {downloaded_file}")
            return downloaded_file
        
        # Check if existing files are still growing
        for file in xls_files:
            try:
                current_size = os.path.getsize(file)
                if current_size > last_size.get(file, 0):
                    last_size[file] = current_size
                    print(f"[DEBUG] File still downloading: {file} ({current_size} bytes)")
                    break  # Continue monitoring as file is growing
                else:
                    print(f"[SUCCESS] File download complete: {file}")
                    return file
            except Exception as e:
                print(f"[WARNING] Error checking file {file}: {e}")

        last_files = xls_files
        time.sleep(2)  # Wait before checking again

        print(f"[ERROR] Timeout reached. No complete .xls file found in {directory}")
        return None

    # Step 9: Process the downloaded file
    try:
    
        downloaded_file = wait_for_download(temp_download_dir)

        if downloaded_file:
            print(f"[INFO] File downloaded successfully: {downloaded_file}")

         # Rename and move the file
            new_filename = f"fund_performance_{date}.xls"
            new_filepath = os.path.join(download_dir, new_filename)

         # Ensure target directory exists
            os.makedirs(download_dir, exist_ok=True)

            # Wait a moment to ensure file is released by browser
            time.sleep(1)

            # Move the file
            shutil.move(downloaded_file, new_filepath)
            print(f"[SUCCESS] File moved to: {new_filepath}")

        else:
            print("[ERROR] Download failed or took too long.")

    except Exception as e:
        print(f"[CRITICAL] Error in download process: {str(e)}")

except Exception as e:
    print(f"An error occurred: {e}")
    with open("debug_page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    raise e

finally:
    driver.quit()
