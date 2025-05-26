import toml
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
import time

def download_mod(mod_page, mod_loader, version):
    # Get mod loader id for search
    if mod_loader == "Forge":
        mod_loader_id = 1
    elif mod_loader == "Fabric":
        mod_loader_id = 4
    link = mod_page+f"/files/all?page=1&pageSize=20&version={version}&gameVersionTypeId={mod_loader_id}"
    # Go to the the mod page with all the dowloadable files
    driver.get(link)
    # Check if there is a 404 error for the modpage
    if driver.find_elements(By.XPATH, "//div[@class='error-container']"):
        print(f"Mod page '{mod_page}' does not exist, aborting")
        return
    time.sleep(0.5)
    # Get the download link for the most recent file
    download_link = driver.find_element(By.XPATH, "//div[@class='files-table']/div[@class='file-row']/div/div/ul/li[2]/a").get_attribute("href")
    driver.get(download_link)
    # We are required to wait 5 seconds for download to begin
    time.sleep(5.5)
    # Check for any dependencies to download for the mod to function
    driver.get(mod_page+f"/relations/dependencies?page=1&type=RequiredDependency")
    # Wait for possible dependenices to load
    time.sleep(2)
    all_dependencies =  [ele.get_attribute("href") for ele in driver.find_elements(By.XPATH, "//div[@class='results-container']/a")]
    time.sleep(0.5)
    for dependent in all_dependencies:
        print(f"Dependency for {mod_page}, {dependent}")
        download_mod(dependent, mod_loader, version)

with open('config.toml', 'r') as f:
    config = toml.load(f)

# Create mods folder to place downloaded mods into
if not os.path.exists(config['general']['modsFolder']):
    os.makedirs(config['general']['modsFolder'])

webscraper_options = Options()
prefs = {
    "download.prompt_for_download": False,
    "download.default_directory": os.path.join(os.getcwd(), config['general']['modsFolder']),
    "safebrowsing.enabled": True,  # Important: This must be true to allow bypass
    "safebrowsing.disable_download_protection": True, # Needed to download jar files
    "profile.default_content_setting_values.automatic_downloads": 1
}
webscraper_options.add_experimental_option("prefs", prefs)
webscraper_options.add_argument("--log-level=3")

driver = webdriver.Chrome(options=webscraper_options)

with open(config['general']['modListFile']) as mod_list:
    for line in mod_list:
        mod_page = config['general']['searchURL'] + line.strip().lower().replace('\'', '').replace(' ', '-')
        download_mod(mod_page, config['modProperties']['modLoader'], config['modProperties']['version'])