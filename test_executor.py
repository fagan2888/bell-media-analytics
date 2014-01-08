from time import sleep, strftime, localtime
from fiddler import fiddlerClass
from har_to_excel import harToExcel
from video_suite import videoSuite
from crawler import Crawler
import os, errno, math, time, auth

fiddling = fiddlerClass()
video = videoSuite()
xlsx = harToExcel()
crawled = Crawler()

########## Set-up functions and wrappers ##########
urls = []

def test_time():
	return strftime("%Y_%m_%d__%H.%M.%S", localtime())

def dir_exist(xlsx_dir, fiddler_logs):
	for i in xlsx_dir, fiddler_logs:
		try:
			os.makedirs(i)
		except:
			continue

def set_crawler_urls(show_name = False):
	global urls
	urls = crawled.video_crawler(auth.bravo_video_url,show_name)

def set_up_fiddler(filters="true"):
	fiddling.start_fiddler()
	sleep(10)
	if filters == "true": # filters are set by default
		fiddling.set_filter()
	fiddling.clear_all_sessions()
	print "Fiddler setup complete!"

def take_down_fiddler(start_time, fiddler_logs):
	print "export to", fiddler_logs+str(start_time)
	fiddling.export_all_sessions(fiddler_logs + str(start_time))
	sleep(1)
	fiddling.clear_all_sessions()
	sleep(1)
	fiddling.close_fiddler()
	print "Fiddler takedown complete!"

def social_networks_authenticate():
	video.twitter_login()
	video.facebook_login()
	video.google_login()

def social_networks_unauthenticate():
	video.twitter_logout()
	video.facebook_logout()
	video.google_logout()

def generic_video_test(url):
	try:
		print "Test url is", url
		video.set_driver()
		# notes, warnings
		print "Events 18, 20, and 21 are not tested, and 7 is not test explicitly."
		# event 3
		print "Testing event 3, authentication"
		video.authenticate()
		sleep(5)
		# event 5
		print "Testing event 5, video starts"
		video.get_video(url)
		sleep(5)
		# event 4, event 13
		print "Testing event 4, already authenticated"
		video.get_video(url)
		sleep(2)
		# event 6 (video completes)
		print "Testing event 6, 25; video completes and scrubbing"
		video.scrub(math.floor(video.video_duration()))
		sleep(2)
		# event 9 (20 seconds elapsed)
		print "Testing event 9, video 20 seconds elapsed"
		video.scrub(0)
		sleep(25)
		# event 10
		print "Testing event 10, video 80 percent complete" # this isn't working
		video.scrub(math.floor(video.video_duration()))
		sleep(2)
		# event 11 and 12
		print "Testing event 11, 12; preroll ad start, preroll ad complete"
		video.get_video(url, True)
		start_time = time.time()
		while video.is_ad():
			print "waiting for the ad(s) to end ... "
			print "is_error status", video.is_error()
			sleep(5)
			if time.time() - start_time > 80:
				print "Sorry, had to refresh the page because the video was stuck!"
				video.refresh()
				start_time = time.time()
		sleep(2)
		# event 16
		print "Testing event 16, pause"
		video.pause()
		sleep(1)
		# event 17
		print "Testing event 17, unpause"
		video.unpause()
		sleep(1)
		# event 14, episode complete
		print "Testing event 14"
		video.scrub(math.floor(video.episode_complete_num()))
		# event 18 ... related video clicks
		# event 20 ... favourite videos
		# event 21 ... info click
		sleep(2)
		video.close_browser()
	except:
	 	print "Something went wrong. Test aborted."


########## Setting up stuff ##########
dir_exist(auth.absolute_xlsx_dir, auth.absolute_fiddler_logs)


########## Tests go here ##########
def test_all_videos(show_name = False, site = auth.bravo_video_url):
	# If show_name == False, then the video hub will be crawled by show and each video will be tested.
	# If you specify a show_name (or just a substring of one (e.g. "uits" for "Suits"), it will only test "Suits").

	if show_name:
		print "Show being tested is", show_name
	if not urls: # for the first test
		try:
			set_crawler_urls(show_name)
			print "Crawler urls were set!"
		except:
			print "Couldn't set crawler urls! Aborting tests (because I cannot think of a better solution)!"

	for i in range(0, len(urls)):
		#for j in range(0, len(urls[i])):
		start_time = test_time()
		set_up_fiddler()
		print "Start time is", start_time

		# Creating custom directories for test suites based on show names
		if show_name:
			fiddler_logs = auth.absolute_fiddler_logs+show_name+"\\"
			xlsx_dir = auth.absolute_xlsx_dir+show_name+"\\"
			dir_exist(xlsx_dir, fiddler_logs)
		else:
			fiddler_logs = auth.absolute_fiddler_logs
			xlsx_dir = auth.absolute_xlsx_dir

		har_file = fiddler_logs+str(start_time)
		xlsx_file = xlsx_dir+str(start_time)+".xlsx"
		
		fiddling.clear_all_sessions()
		print "This test started at", start_time
		generic_video_test(urls[i])
		take_down_fiddler(start_time, fiddler_logs)
		fiddling.export_all_sessions(str(start_time))
		fiddling.clear_all_sessions()
		xlsx.create_document(har_file, xlsx_file)
	print "Test suite for", show_name, "is finished!"

def test_bravo_videos(showname = False, site = auth.bravo_video_url):
	test_all_videos(showname, site)

def test_ctv_videos(showname = False, site = auth.ctv_video_url):
	test_all_videos(showname, site)


########## Test Calls ##########
#test_bravo_videos()
test_bravo_videos("Disco")
test_bravo_videos("Graceland")
# test_bravo_videos("The First 48")
#test_bravo_videos("Cold Justice")