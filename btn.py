from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
from unidecode import unidecode
import pandas as pd

WHATKIND = "serbian"
NAME_DIR = "collected_names/"

# page where they have the full list of name types by letter, gender or usage
BASE_URL = "https://www.behindthename.com/names/usage/"

# full path to the webdriver to use; use webdriver.PhantomJS() for invisible browsing
driver = webdriver.Chrome('webdriver/chromedriver')
driver.set_page_load_timeout(10)

name_gender_list = []

# there seems to be a pending script running on that page, so we need to
# avoid stucking 
try:
	driver.get(BASE_URL + WHATKIND)
except TimeoutException:
	# run this java script to stop loading wahtever it is
	driver.execute_script("window.stop();")

possible_next_page = True

while possible_next_page:
	# now grab the name entries
	entries = driver.find_elements_by_xpath("//div[contains(@class,'browsename')]")
	print("total entries on this page {}".format(len(entries)))
	
	for name_rec in entries:

		name = name_rec.find_element_by_xpath("./b").text.lower().strip()
		name = "".join([letter for letter in unidecode(name) if letter.isalpha()])

		try:
			gender = name_rec.find_element_by_xpath("./span[@class='masc' or @class='fem']").text.lower().strip()
		except:
			print("couldn\'t find gender for name {}! exiting...".format(name))
		# look for the info class which is & - if found, it's a unisex name
		try:
			if (name_rec.find_element_by_xpath("./span[@class='info']").text.strip() == "&"):
				gender = "u"
		except:
			pass

		name_gender_list.append((name, gender))

	# check if we can move to the next page
	try:
		print("trying to click next page...")
		possible_next_page = WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Next")))
		possible_next_page.click()
		time.sleep(3)
	except:
		# apparently, there's only one page with names
		print("no next page found...")
		possible_next_page = None

driver.quit()
print("saving results to file...")
# done with collecting nemas, now save them to a file
pd.DataFrame.from_records(name_gender_list, columns="name gender".split()).to_csv(NAME_DIR + "names_" + WHATKIND + ".txt", index=None)






