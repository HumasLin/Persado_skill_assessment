import re
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from lib.utils import *
from lib.scraper import *
from lib.product import *

class Data:

	def __init__(self, scraper):
		self.scraper = scraper
		self.data = pd.DataFrame(columns=['id','time','text','image_link','image_flag',
										  'video_link','video_flag','products','product_flag'])
		self.product_data = pd.DataFrame(columns=['post_id','product_id','brand',
												  'product_name','price','details'])

	def get_video_link(self, post):
		try:
			video_module = post.find_element_by_css_selector("video")
			action = ActionChains(self.scraper.browser)
			action.move_to_element(video_module).move_by_offset(0, -120).context_click().perform()
			video_url = self.scraper.browser.find_element_by_link_text("Copy video URL at current time")
			video_element = video_url.find_elements_by_css_selector("span")[-1]
			video_link = video_element.get_attribute("value")
		except:
			video_link =  ""
		return video_link

	def get_product(self, post):
		try:
			product_button = post.find_element_by_xpath(".//*[text()='Click to View Products']")
			ActionChains(self.scraper.browser).move_to_element(product_button).move_by_offset(0, -185).click().perform()
			time.sleep(1.5)
			product_pages = self.scraper.browser.find_elements_by_xpath("//div[@class='fbPhotosPhotoTagboxBase tagBox']")
			product_urls = [product.find_element_by_css_selector("a").get_attribute("href") \
			                for product in product_pages]
			self.scraper.browser.back()
		except:
			product_urls = []
		return product_urls

	def get_info(self):
		for post in self.scraper.posts:
			analysis = []

			time_element = post.find_element_by_css_selector("abbr")
			utime = time_element.get_attribute("data-utime")
			post_id = self.scraper.brand+"_"+utime
			analysis.append(post_id)
			analysis.append(datetime.fromtimestamp(int(utime)).strftime('%Y-%m-%d'))

			text = post.find_element_by_class_name("userContent").text
			analysis.append(text)

			image_elements = post.find_elements_by_class_name("uiScaledImageContainer")
			image_url = [image.find_element_by_css_selector("img").get_attribute("src") \
						 for image in image_elements]
			if image_url == []:
				image_url = post.find_elements_by_css_selector("img")[1].get_attribute("src")
			analysis.append(image_url)
			image_flag = 'No' if image_url == [] else 'Yes'
			analysis.append(image_flag)

			video_url = self.get_video_link(post)
			analysis.append(video_url)
			video_flag = 'No' if video_url == '' else 'Yes'
			analysis.append(video_flag)

			products = self.get_product(post)
			analysis.append(products)
			product_flag = 'No' if products == [] else 'Yes'
			analysis.append(product_flag)

			self.data.loc[len(self.data.index)] = analysis

	def get_data(self):
		return self.data

	def get_product_data(self):
		for row_index in range(len(self.data)):
			post_id=self.data.iloc[row_index]['id']
			urls=self.data.iloc[row_index]['products']
			if len(urls) == 0:
				continue
			for url in urls:
				self.product_data.loc[len(self.product_data.index)] \
					= Product(post_id, url, self.scraper.browser).get_data()
		return self.product_data
