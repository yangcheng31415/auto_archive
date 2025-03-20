
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

def archive_contact(li_element, driver):
    try:
        # Locate the archive button (Adjust XPath based on the actual page structure if needed)
        archive_button = li_element.find_element(By.XPATH, ".//div/div[2]/div[1]/button")
        archive_button.click()
        time.sleep(1)
        
        actions = ActionChains(driver)
        for _ in range(5):
            actions.send_keys(Keys.ARROW_DOWN)
            time.sleep(0.2)
        actions.send_keys(Keys.ENTER)
        actions.perform()
        time.sleep(1)
        print("Contact archived successfully.")
    except Exception as e:
        print(f"Error occurred while archiving contact: {e}")

def main():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    # Set persistent user data directory to ensure LinkedIn is logged in within this profile
    chrome_options.add_argument("user-data-dir=/Users/chengyang/Library/Application Support/Google/Chrome/Default")
    
    # Use chromedriver located at /opt/homebrew/bin/chromedriver
    chrome_service = Service(executable_path="/opt/homebrew/bin/chromedriver")
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    
    # Navigate to the messaging thread page (Ensure the URL is correct and the user is logged in)
    messaging_url = "https://www.linkedin.com/messaging/thread/2-ZDQzYjMxYWYtMzcxNC00Nzc1LThlYjUtNTFiNTRmN2VjMmQ3XzEwMA==/"
    driver.get(messaging_url)
    time.sleep(5)
    
    # Debugging: Print current page URL and title
    current_url = driver.current_url
    print("Current page URL:", current_url)
    print("Page title:", driver.title)
    
    if "login" in current_url.lower():
        print("Login page detected. Please log in manually before proceeding.")
        input("Press Enter after logging in to continue...")
        driver.get(messaging_url)
        time.sleep(5)
    
    # XPath for the contact list
    ul_xpath = '//*[@id="main"]/div/div[2]/div[1]/div[2]/ul'
    try:
        ul_element = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, ul_xpath))
        )
        print("Successfully located the contact list.")
    except TimeoutException as e:
        print("Timeout while waiting for the contact list:", e)
        print(driver.page_source[:2000])
        driver.quit()
        return

    # Loop through the contact list
    while True:
        try:
            ul_element = WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, ul_xpath))
            )
            li_elements = ul_element.find_elements(By.TAG_NAME, "li")
            print(f"Found {len(li_elements)} contacts.")
        except Exception as e:
            print("Failed to locate the contact list:", e)
            break

        if len(li_elements) < 2:
            print("Insufficient contacts. Exiting program.")
            break

        archived_any = False

        # Start from the second contact (assuming the first is a fixed element)
        for index, li in enumerate(li_elements[1:], start=2):
            try:
                # Check for unread message indicators
                # Example XPath for an unread message indicator: //*[@id="ember271"]/span/span[1]
                # Since IDs are dynamically generated, use starts-with for matching
                unread_element = li.find_element(By.XPATH, ".//*[starts-with(@id, 'ember')]/span/span[1]")
                unread_text = unread_element.text.strip()
                # If text is not empty and is numeric, it indicates unread messages
                if unread_text and unread_text.isdigit():
                    print(f"Contact {index} has unread messages ({unread_text}), skipping archive.")
                    continue
                else:
                    print(f"Contact {index} has no unread messages indicator, archiving.")
            except NoSuchElementException:
                # No unread message indicator found, assume no unread messages
                print(f"Contact {index} has no unread message indicator, archiving.")
            except Exception as e:
                print(f"Error while checking unread status for contact {index}: {e}")
                continue

            # Archive contacts without unread messages
            archive_contact(li, driver)
            archived_any = True
            # Exit loop after archiving one contact to allow DOM updates before reprocessing
            break

        if not archived_any:
            print("No contacts met the archiving criteria. Process complete.")
            break

        time.sleep(2)

    print("All contacts processed.")
    # If needed, close the browser: driver.quit()

if __name__ == "__main__":
    main()
