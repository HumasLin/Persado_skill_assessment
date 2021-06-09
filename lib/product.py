import re 
import time
import numpy as np
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class Product:

	def __init__(self, post_id, url, browser):
		self.post_id = post_id
		self.product_id = url.split('/')[-2].strip('/')
		self.brand = post_id.split("_")[0]
		self.browser = browser

		self.browser.get(url)
		time.sleep(np.random.uniform(1,2))

		self.product_name = self.browser.find_elements_by_class_name("n851cfcs")[1].text

		self.price = self.browser.find_element_by_xpath("//div[@class='btwxx1t3 j83agx80']").text
		self.price = re.findall(r"\$[^\]]+",self.price)[0].split()[0]

		expand = self.browser.find_element_by_xpath("//div[@aria-label='expand section']")
		expand.click()

		details_module = self.browser.find_element_by_xpath("//div[@class='dati1w0a qt6c0cv9 hv4rvrfc jb3vyjys']")
		self.details = details_module.text.lstrip("Details ")
	
	def get_data(self):
		return [self.post_id, self.product_id, self.brand, self.product_name, self.price, self.details]
		