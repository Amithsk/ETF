from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import os


# Set up download directory
download_dir = os.path.abspath(r"D:\ETF_Data\ETFProcessData\Downloaded\AUMReturns")  # Ensure this path exists
os.makedirs(download_dir, exist_ok=True)

# Initialize the undetected-chromedriver
options = uc.ChromeOptions()
prefs = {
    "download.default_directory": download_dir,  # Set default download directory
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
        driver.execute_script("""
            var dateInput = document.getElementById('nav-date');
            dateInput.value = '22-Jan-2025';
            var event = new Event('change', { bubbles: true });
            dateInput.dispatchEvent(event);
        """)
        print("Date input updated to '22-Jan-2025'.")
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
        download_link = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, "download-report-excel")))
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
    # Step 8: Wait for the file to download
    try:
        time.sleep(10)  # Adjust sleep time based on file size and network speed
        print(f"File should be downloaded to: {download_dir}")
    except Exception as exc:
        print(f"Error clicking 'Download Excel' link: {exc}")
        with open("debug_download.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        driver.save_screenshot("debug_download.png")

except Exception as e:
    print(f"An error occurred: {e}")
    with open("debug_page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    raise e

finally:
    driver.quit()
