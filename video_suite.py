import pywinauto
from selenium import webdriver
from time import sleep, strftime, localtime
import math, time, auth

class videoSuite:

	driver = ""

	def check_if_logged_in():
		"""Checks if you are logged in by making sure the logout link is displayed."""
		if self.driver.find_element_by_class_name("vh-logout-link").is_displayed():
			return True
		else:
			return False

	def set_driver(self, browser="Firefox"):
		"""Sets the global webdriver instance to use a particular browser.

		Args:
			browser (string): defaults to Firefox, anything else will result in a PhantomJS browser.
		"""
		if browser == "Firefox":
			self.driver = webdriver.Firefox()
		else:
			self.driver = webdriver.PhantomJS(auth.phantomjs_path)

	def is_error(self): # this functionality doesn't exist yet!
		"""Returns whether or not the video's current state is in distress."""
		try:
			return self.driver.execute_script("return ETSPlayer.getAppInstanceByPlayerID('vplayer').getCurrentPlayerState().isError")
		except:
			return self.is_error() # more dangerous code

	def is_ad(self):
		"""Returns whether or not the video's current state is an advertisement."""
		try:
			return self.driver.execute_script("return ETSPlayer.getAppInstanceByPlayerID('vplayer').getCurrentPlayerState().isAd")
		except:
			return self.is_ad() # more dangerous code

	def no_ads(self):
		"""Attempts to disable ads on the currently active player."""
		self.driver.execute_script("etsapi.setAdrule('vplayer',{flashVars:{cms:'fortytwo'}, adRule:'none'})")
		print "Ads disabled!"	

	def get_video(self, site, ads = False):
		"""Navigates to a particular video with or without ads.

		Args:
			site (string): the url of the video hub of CTV or bravo
			ads (bool): set to by default False if you do not want advertisements to play, otherwise ads will play
		"""
		try:
			self.driver.get(site)
			sleep(2)
			if ads == False:
				self.no_ads()
				sleep(1)
				start_time = time.time()
				while self.is_ad():
					print "Paused--there's an ad!"
					sleep(5)
					# If the video is stuck or there's a problem with the site
					if time.time() - start_time > 80:
						print "Sorry, had to refresh!"
						self.refresh()
						start_time = time.time()
			print "... now the ads are gone for this episode :)"
		except:
			print "Couldn't get the video! (request was probably rejected by the server bc of maintenance) ... "
			print "This test was skipped. Please ignore everything up until the next test's start time is displayed ... "

	def authenticate(self, username = auth.bravo_username, password = auth.bravo_password):
		# Not using screen-door
		"""Attempts to authenticates on Bell all sites not using screen door. If it fails, it kills everything (intentional).
		Important: does not trigger event3!"""
		try:
			self.driver.get(auth.universal_auth_url)
			sleep(5)
			self.driver.find_element_by_name("USER").send_keys(username)
			sleep(1)
			self.driver.find_element_by_name("PASSWORD").send_keys(password)
			sleep(1)
			print "Authenticated on Bell sites!"
		except:
			print "Authentication on Bell sites failed (probably because you were already authenticated)"
			print "quitting"
			exit()

	def unauthenticate(self):
		"""Attemps to unauthenticate on Bell sites."""
		try:
			self.driver.find_element_by_class_name("vh-logout-link").click()
			sleep(1)
			print "Unauthenticated on Bell sites!"
		except:
			print "Unauthentication on Bell sites failed (maybe you weren't authenticated)."
	
	def refresh(self):
		"""Refreshes the page."""
		self.driver.refresh()
		print "Page refreshed!"

	def close_browser(self):
		"""Closes the browser."""
		self.driver.close()
		print "Browser closed!"

	def pause(self):
		"""Attempts to pause the currently playing video."""
		try:
			self.driver.execute_script("ETSPlayer.getAppInstanceByPlayerID('vplayer').pause()")
			print "Video paused"
		except:
			"Pausing video failed"

	def unpause(self):
		"""Attempts to unpause the currently playing video."""
		try:
			self.driver.execute_script("ETSPlayer.getAppInstanceByPlayerID('vplayer').unpause()")
			print "Video unpaused"
		except:
			print "Video unpausing failed."

	def video_duration(self):
		"""Attempts to return the duration of the currently playing video. Note that "video" means whichever particular subsection of
		the full episode the viewer currently sees. Does not tell you how long the entire episode is!"""
		try:
			d = self.driver.execute_script("return ETSPlayer.getAppInstanceByPlayerID('vplayer').getCurrentPlayerState().duration")
			print "Duration is", d
			return d
		except:
			print "Getting the duration failed! Returning 0"
			return 0

	def state(self):
		"""Attempts to return the state of the currently playing video."""
		try:
			s = self.driver.execute_script("return ETSPlayer.getAppInstanceByPlayerID('vplayer').getCurrentPlayerState().state")
			print "State is", s
			return s
		except:
			"State checking failed!"

	def scrub(self, num):
		"""Attempts to scrub to whatever number you pass in. Cannot scrub across video clips in an episode.

		Args:
			num (int): the location in seconds of the video clip you want
		"""
		try:
			self.driver.execute_script("ETSPlayer.getAppInstanceByPlayerID('vplayer').seek({0})".format(num))
			print "Seeked to", num
		except:
			print "Scrubbing failed!"

	def episode_complete_num(self):
		"""Returns the time stamp of when the current video is 85 percent complete."""
		return math.floor(self.video_duration() * 0.85)

	def eighty_percent(self):
		"""Returns the timestamp of when the video is 80 percent complete."""
		return math.floor(self.video_duration() * 0.8)

	def number_of_clips(self):
		"""Attempts tp return the number of clips in the episode which is playing."""
		try:
			num = self.driver.execute_script("return ETSPlayer.getPlayListInstanceByPlayerID('vplayer')._stackPlaylistObj._playlist.length")
			return num
		except:
			print "Checking number of clips failed! Returning 0"
			return 0

	# returns how long until the video is complete
	def get_episode_length(self):
		"""Attempts to return the length of the entire episode."""
		try:
			clips = self.number_of_clips()
			episode_length = 0
			for i in range(0,clips):
				d = self.video_duration()
				episode_length += d
				self.scrub(int(math.floor(d)))
				sleep(2)
				print "d is", d

			return episode_length
		except:
			print "Getting episode length failed! Returning 0"
			return 0

	def map_clips_to_id(self):
		"""Returns a dictionary mapping the number of a clip to its ID."""
		n = number_of_clips()
		clip_map = {}
		for i in range(0, n):
			clip_map[i] = self.driver.execute_script("return ETSPlayer.getPlayListInstanceByPlayerID('vplayer')._stackPlaylistObj._playlist[{0}].id".format(n))
		return clip_map

	def test_time(self):
		"""Returns the current date and time as a string."""
	 	return strftime("%Y_%m_%d__%H:%M:%S", localtime())

	def twitter_login(self):
		"""Attempts to log into Twitter."""
		try:
			self.driver.get("http://www.twitter.com/")
			self.driver.find_element_by_id("signin-email").send_keys(auth.email)
			self.driver.find_element_by_id("signin-password").send_keys(auth.email_password)
			print "Twitter authentication complete!"
		except:
			print "Twitter authentication failed, probably because they think I am a robot!"

	def google_login(self):
		"""Attempts to log into Google."""
		try:
			self.driver.get("https://accounts.google.com/ServiceLogin?service=oz&passive=1209600&continue=https://plus.google.com/?gpsrc%3Dgplp0%26partnerid%3Dgplp0")
			self.driver.find_element_by_id("Email").send_keys(auth.email)
			self.driver.find_element_by_id("Passwd").send_keys(auth.email_password)
			print "Google authentication complete!"
		except:
			print "Google authentication failed, probably because I can't handle captchas!"

	def facebook_login(self):
		"""Attempts to log into Facebook."""
		try:
			self.driver.get("http://www.facebook.com/login.php")
			self.driver.find_element_by_class_name("inputtext").send_keys(auth.email)
			self.driver.find_element_by_class_name("inputpassword").send_keys(auth.email_password)
			print "Facebook authentication complete!"
		except:
			print "Facebook authentication failed, probably because I failed the reverse Turing test :("

	def twitter_logout(self):
		"""Attempts to log out of Twitter."""
		try:
			self.driver.get("https://twitter.com/logout")
			self.driver.find_element_by_id("user-dropdown-toggle").click()
			self.driver.find_element_by_id("signout-button").click()
			print "No longer authenticated on Twitter!"
		except:
			print "Logging out of Twitter failed! Help ... I can't ... escape ... the Twitterverse ..."

	def google_logout(self):
		"""Attempts to log out of Google."""
		try:
			self.driver.get("https://www.google.ca/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&cad=rja&ved=0CCwQFjAA&url=http%3A%2F%2Fmail.google.com%2F%3Flogout&ei=2aUwUp_OJqakiQLg1IDgCg&usg=AFQjCNG-fTeQV2p4ntz3qPRhqE_ATd5TKg&bvm=bv.52109249,d.cGE")
			print "No longer authenticated on Google!"
		except:
			print "This is will never happen (but this message is here for symmetry's sake) ... Google unauthentication failed!"

	def facebook_logout(self):
		"""Attempts to log out of Facebook."""
		try:
			self.driver.get("http://www.facebook.com")
			self.driver.find_element_by_id("userNavigationLabel").click()
			self.driver.find_element_by_id("logout_form").submit()
			print "No longer authenticated on Facebook!"
		except:
			print "Facebook de-authentication failed 'cause they probably thought I was a robot earlier (which isn't false ...)"
