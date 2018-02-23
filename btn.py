from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

from unidecode import unidecode
import pandas as pd
import time

class BehindTheName:

	def __init__(self, what_names, save_to_dir, webdriver_path):

		if isinstance(what_names, list):
			self.WHATKIND = what_names
		elif isinstance(what_names, str):
			self.WHATKIND = [what_names]
		else:
			raise TypeError	

		self.NAME_DIR = save_to_dir
		self.BASE_URL = "https://www.behindthename.com/submit/names/usage"

		self.driver = webdriver.Chrome(webdriver_path)
		self.driver.set_page_load_timeout(15)  # in seconds

	def _get_names(self, url):

		try:
			self.driver.get(url)
		except TimeoutException:
			# run this Java script to stop loading whatever it is
			self.driver.execute_script("window.stop();")

		name_gender_list = []

		next_ = True

		while next_:
			# now grab the name entries
			entries = self.driver.find_elements_by_xpath("//div[contains(@class,'browsename')]")
		
			for name_rec in entries:
		
				name = name_rec.find_element_by_xpath("./b").text.lower().strip()
				name = "".join([letter for letter in unidecode(name) if letter.isalpha()])
		
				try:
					gender = name_rec.find_element_by_xpath("./span[@class='masc' or @class='fem']").text.lower().strip()
				except:
					gender = None

				# look for the info class which is & - if found, it's a unisex name
				try:
					if (name_rec.find_element_by_xpath("./span[@class='info']").text.strip() == "&"):
						gender = "u"
				except:
					pass
		
				name_gender_list.append((name, gender))
	
			# now check if we can move to the next page
			try:	
				next_ = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Next")))
				next_.click()
				time.sleep(5)
			except:
				# apparently, there's only one page with names
				next_ = False
				break

		return name_gender_list

	def get_names(self):

		for i, k in enumerate(self.WHATKIND, 1):

			print(f'{i}: {k.upper()} names... ', end='')

			k_names = self._get_names(url=f'{self.BASE_URL}/{k}')

			print(len(k_names))

			pd.DataFrame.from_records(k_names, columns="name gender".split()).to_csv(f'{self.NAME_DIR}/names_{k}.txt', index=None)

		return self


	def quit(self):

		self.driver.quit()


if __name__ == '__main__':

	b = BehindTheName(what_names="""   Chewa
   Shona
   Tswana
   Xhosa
   Zulu
Western African
   Akan
   Igbo
   Urhobo
   Yoruba""".lower().split(), 
						save_to_dir='collected_names', 
							webdriver_path='/Users/ik/Data/webdrivers/chromedriver').get_names().quit()
