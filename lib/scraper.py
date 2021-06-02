import re
import time
import numpy as np
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class Scraper:

	def __init__(self, brand, depth, browser, account="", num_follow=0, posts=[]):
		self.brand = brand
		self.depth = depth
		self.browser = browser
		self.account = account
		self.num_follow = num_follow
		self.posts = posts

	def get_posts(self):
		# Go to desired website	
		self.browser.get('https://www.facebook.com/' + self.brand + '/')

		profile = self.browser.find_element_by_xpath("//div[@id='PagesProfileHomeSecondaryColumnPagelet']").text
		num_follow_text = [text for text in profile.split('\n') if 'people follow this' in text]
		self.num_follow = int(re.sub(",","",num_follow_text[0].split()[0]))

		bio = self.browser.find_element_by_xpath("//div[@role='navigation']")
		self.account = bio.text.split('\n')[0].strip()

		while True:
			# Scroll down to bottom
			self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			time.sleep(np.random.uniform(2,3))
			depth = len(self.browser.find_elements_by_class_name("userContentWrapper"))
			if depth>self.depth:
			    break
			if depth==0:
				self.browser.get('https://www.facebook.com/' + self.brand + '/')
				self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		
		clear_screen = self.browser.find_element_by_link_text("Not Now")
		clear_screen.click()

		links = self.browser.find_elements_by_link_text("See more")
		for link in links:
		    link.click()
		
		self.posts = self.browser.find_elements_by_class_name("userContentWrapper")
