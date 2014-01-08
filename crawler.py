from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from video_suite import videoSuite
import auth

## There are lots of try/catch statements because both selenium and the
## websites being tested are often broken.

class Crawler:

	list_of_urls = []

	driver = webdriver.Firefox()
	driver.implicitly_wait(20)

	def authenticate(self):
		# bell-affiliated and not using screen-door
		"""Attempts to authenticates on Bell all sites not using screen door. If it fails, it kills everything (intentional).
		IMPORTANT: does not trigger event3!"""
		try:
			self.driver.get(auth.universal_auth_url)
			sleep(5)
			self.driver.find_element_by_name("USER").send_keys(auth.bravo_username)
			sleep(1)
			self.driver.find_element_by_name("PASSWORD").send_keys(auth.bravo_password)
			sleep(1)
			print "Authenticated on Bell sites!"
		except:
			print "Authentication on Bell sites failed (probably because you were already authenticated)"
			print "quitting"
			exit()

	def episodes(self):
		"""A helper function which collect the URLs for each show and exists for re-factoring purposes."""
		num_of_episodes = len(self.driver.find_elements_by_class_name("vh-thumbnail"))
		while True:
			try: # navigate to the next page of episodes if there is one
				self.driver.find_element_by_class_name("server-next").click()
				num_of_episodes = num_of_episodes + len(self.driver.find_elements_by_class_name("vh-thumbnail"))
			except:
				# go back to first page
				try:
					self.driver.find_element_by_class_name("server-first").click()
				except:
					break
				break

		for j in range(0, num_of_episodes):
			if j % 25 == 0 and j != 0:
				try:
					sleep(2)
					self.driver.find_element_by_class_name("server-next").click()
				except:
					print "Couldn't click to the next set of episodes!"

			try:
				episodes = self.driver.find_elements_by_class_name("vh-thumbnail")
				episodes[j % 25].click() 
				print "j: {0}, current url: {1}".format(j, str(self.driver.current_url))
				self.list_of_urls.append(self.driver.current_url)
			except:
				self.driver.refresh()
				episodes = self.driver.find_elements_by_class_name("vh-thumbnail")
				episodes[j % 25].click() # I think 
				print "j: {0}, current url: {1}".format(j, str(self.driver.current_url))
				self.list_of_urls.append(self.driver.current_url)

			# select the back button ... it must be done this way until the
			# site stops randomly assigning names to back buttons ...
			try:
				e = self.driver.find_element_by_class_name("returnToIndex")
				e.click()
			except:
				try:
					e = self.driver.find_element_by_class_name("vh-back-btn")
					e.click()
				except:
					print "Whatever."

		return self.list_of_urls


	def video_crawler(self, url = auth.bravo_video_url, show_name = False):
		"""Will crawl the entire video hub of whatever site is specified with 'url'.
		If you specify a show, it will only collect the URLs for that show."""

		self.list_of_urls = [] # clearing potentially previously set values
		self.driver.get(url)

		# expanding side menus
		try:
			self.driver.find_element_by_class_name("expand-collection-title").click()
			self.driver.find_element_by_class_name("expand-collection-list-item").click()
		except:
			self.driver.refresh()
			self.driver.find_element_by_class_name("expand-collection-title").click()
			self.driver.find_element_by_class_name("expand-collection-list-item").click()

		if show_name == False:
			print "Crawling the entire video hub of", url
			list_of_shows = self.driver.find_elements_by_class_name("vh-thumbnail")
			num_of_shows = len(self.driver.find_elements_by_class_name("vh-thumbnail"))

			# calculating the total number of shows
			while True:
				try:
					self.driver.find_element_by_class_name("server-next").click()
					num_of_shows = num_of_shows + len(self.driver.find_elements_by_class_name("vh-thumbnail"))
				except:
					try:
						self.driver.find_element_by_class_name("server-first").click()
					except:
						break
					break

			print "num_of_shows is", num_of_shows

			for i in range(0, num_of_shows):
				print "i is", i

				for num_clicks in range(0, i / 25):
						sleep(5)
						self.driver.find_element_by_class_name("server-next").click()

				list_of_shows = self.driver.find_elements_by_class_name("vh-thumbnail")
				# this might not work, because there aren't always *exactly* 25 episodes on the page because of
				# larger advertisements ... TODO
				list_of_shows[i % 25].click()

				self.episodes()

				#select the back button (to return to the list of shows)
				print "list of urls is currently", self.list_of_urls, "\n"
				try:
					e = self.driver.find_element_by_class_name("vh-back-btn")
					e.click()
				except:
					try:
						e = self.driver.find_element_by_class_name("returnToIndex")
						e.click()
					except:
						print "More whatever."

				list_of_shows = self.driver.find_elements_by_class_name("vh-thumbnail")

			print "The length is", len(self.list_of_urls), "\n"
			print "The list_of_urls is", self.list_of_urls, "\n"

		else: ## looking for a specific show instead of crawling the entire site
			print "Only crawling the show", show_name
			# find the show page on the video hub
			show_found = False
			while show_found == False:
				try:
					self.driver.find_element_by_partial_link_text(show_name).click()
					show_found = True
				except: # go to next page of shows ...
					self.driver.find_element_by_class_name("server-next").click()

			# go back to the first page
			try:
				print "Trying to return to the first page!"
				self.driver.find_element_by_class_name("server-first").click()
			except:
				print "Already on first page!"
			
			list_of_urls = self.episodes()

		#print "List of urls gathered is:",self.list_of_urls
		return self.list_of_urls

# c = Crawler()
# c.authenticate()
# c.video_crawler(auth.ctv_video_url, "CTV Holiday Hub")

## Possible other examples on how to run this to get back a list of all video URLs:
# C = Crawler()
# c.authenticate() # not necessary
# c.video_crawler(auth.ctv_video_url) # will crawl the entire CTV video hub
# c.video_crawler(auth.bravo_video_url) # wil crawl the entire bravo video hub
# c.video_crawler(auth.ctv_video_url, "Marilyn") # will find the "Marilyn Dennis Show" and return its video URLs
# c.video_crawler(auth.ctv_video_url, "Borgias") # returns video url's of bravo's "The Borgias" series
