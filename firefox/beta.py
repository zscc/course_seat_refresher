from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import datetime
import time
import os
from twilio.rest import Client
import sys
import json

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException

class CourseSelector:

	def __init__(self, username, password, course_code, refresh_rate, first_login_enabled):

		self.course_code = course_code
		self.username = username
		self.password = password
		self.refresh_rate = refresh_rate
		self.first_login_enabled = first_login_enabled

		self.course_address = ''

		self.subj = ''
		self.crsno = ''
		self.sectno = ''

		# account_sid = '``'
		# auth_token = '``'
		self.account_sid = '00'
		self.auth_token = '00'
		self.client = Client(self.account_sid, self.auth_token)

		self.driver = self.init_driver()


	def init_driver(self):
		caps = DesiredCapabilities().FIREFOX
		caps["pageLoadStrategy"] = "eager"  #  interactive
		options = webdriver.FirefoxOptions()
		options.add_argument('--ignore-certificate-errors')
		driver = webdriver.Firefox(options=options, desired_capabilities=caps)
		driver.set_page_load_timeout(30)
		return driver

	def initialize(self):
		if self.first_login_enabled == 'y':
			self.first_login()
		else:
			self.first_login()
			self.logout()

		self.navigate_to_course_page()
		self.request_loop()

	def logout(self):
		while True:
			try:
				self.driver.find_element_by_name("logout").click()
				break
			except Exception as e:
				self.exception_handler('Exception - logout()', e, 900)



	def send_sms(self, msg):
		print('sending sms')
		message = self.client.messages.create(
			body=msg,
			from_='+17787196053',
			to='+17786820686'
			)

	def twilio_call(self):
		print('calling')
		message = self.client.calls.create(
			url='http://demo.twilio.com/docs/voice.xml',
			from_='+17787196053',
			to='+17786820686'
			)

	def exception_handler(self, msg, e, seconds):
		file_name = 'error_log.txt'
		whole_msg = self.course_code + ': ' + msg + ', retrying after ' + str(seconds) + \
					' seconds. Time: ' + str(datetime.datetime.now()) + str(e)
		print(whole_msg)
		screenshot_name = 'screenshots/' + self.course_code +' '+ str(datetime.datetime.now()) + '.png'
		self.driver.save_screenshot(screenshot_name)
		with open(file_name, 'a') as f:
			print(whole_msg, file=f)
		time.sleep(seconds)



	def success_notify(self):
		file_name = 'success_log.txt'
		whole_msg = self.course_code + ': registered at ' + str(datetime.datetime.now())
		print(whole_msg)
		with open(file_name, 'a') as f:
			print(whole_msg, file=f)
		time.sleep(seconds)
	


	def first_login(self):
		try:
			self.driver.get("https://cas.id.ubc.ca/ubc-cas/login?TARGET=https%3A%2F%2Fcourses.students.ubc.ca%2Fcs%2Fsecure%2Flogin")
		except Exception as e:
			exception_handler('Exception - first_login()', e, 0)
			self.driver.quit()
		print("now in first_login page")
		self.login()


	def re_login(self):
		print('in method:re_login')
		print('finding IMGSUBMIT')
		self.driver.find_element_by_name("IMGSUBMIT").click()
		print("clicked IMGSUBMIT, now calling method:login")
		self.login()


	def login(self):
		while True:
			try:
				username_field = self.driver.find_element_by_id("username")
				username_field.send_keys(self.username)
				password_field = self.driver.find_element_by_id("password")
				password_field.send_keys(self.password)
				print("finished typing log in info")
				t1 = time.time()
				self.driver.find_element_by_name("submit").click()
				
				print("submitted log in info") # this is only printed after navigating to course page
				break
			except NoSuchElementException:
				break
				
			except Exception as e:
				self.exception_handler('Exception - login()', e, 900)


	def logged_in(self):
		try:
			# t11 = time.time()
			self.driver.find_element_by_name("logout")
			# print ('checking logout button:', time.time() - t11)
		except Exception as e:
			print("not logged in. Log out button not found")
			# print ('checking logout button:', time.time() - t11) # 0.01
			return False
		return True


	def navigate_to_course_page(self):
		while True:
			try:
				self.driver.get("https://courses.students.ubc.ca/cs/courseschedule?pname=subjarea&tname=sectsearch")
				print("in search page")
				break
			except TimeoutException as e:
				self.exception_handler('TimeoutException - navigate_to_course_page(): loading search page', e, 900)
			except Exception as e:
				self.exception_handler('Exception - navigate_to_course_page(): loading search page', e, 900)

		while True:
			try:
				course_code_in_array_form = self.course_code.split(" ")
				self.subj = course_code_in_array_form[0]
				self.crsno = course_code_in_array_form[1]
				self.sectno = course_code_in_array_form[2]
				subj_field = self.driver.find_element_by_id('subj')
				subj_field.clear()
				subj_field.send_keys(self.subj)
				crsno_field = self.driver.find_element_by_id('crsno')
				crsno_field.clear()
				crsno_field.send_keys(self.crsno)
				break
			except NoSuchElementException as e:
				self.exception_handler('NoSuchElementException - navigate_to_course_page(): filling subj and crsno', e, 300)

		while True:
			try:
				print("filled in subj and crsno, clicking submit")
				self.driver.find_element_by_name("submit").click()
				print("in search result page, clicking course code")
				self.driver.find_element_by_link_text(self.course_code).click()
				self.course_address = self.driver.current_url
				break
			except NoSuchElementException as e:
				self.exception_handler('NoSuchElementException - navigate_to_course_page(): submitting.', e, 300)



	def request_loop(self):

		while True:
			t0 = time.time()

			while True:
				t3 = time.time()
				try:
					available_seats = int(self.driver.find_element_by_xpath( \
					"/html/body/div[2]/div[4]/table[4]/tbody/tr[3]/td[2]/strong").text) # 0.08
					break
				except NoSuchElementException as e:
					self.exception_handler('NoSuchElementException - request_loop(): parsing available_seats', e, 10)
					self.driver.refresh()
				except WebDriverException as e:
					self.exception_handler('WebDriverException - request_loop(): parsing available_seats', e, 10)
					self.driver.refresh()
				except ValueError as e:
					self.exception_handler('ValueError - request_loop(): parsing available_seats', e, 1)
					self.driver.refresh()




			print(datetime.datetime.now(), "Available seat(s):" , available_seats, "for", self.course_code) 
			
			if available_seats > 0:
				print("Found it! Registering now...")
				
				if not self.logged_in(): # 0.01
					
					print("calling method:re_login")
					t3 = time.time()
					self.re_login()
					print ('calling re_login():', time.time() - t3)
					print("going to course page")
					self.driver.get(self.course_address)
					print("back from navigate_to_course_page")

				# ----------------------------
				print("clicking 'Register Section'")
				while True:
					try:
						t2 = time.time()
						
						# register_button = self.driver.find_element_by_xpath('/html/body/div[2]/div[4]/a[2]')
						register_button = self.driver.find_element_by_css_selector('body > div.container > div.content.expand > a:nth-child(7)')
						
						register_button.click()

						print ('finding Register Section:', time.time() - t2)
						print ('total time:', time.time() - t0)
						break
					except NoSuchElementException as e:
						self.exception_handler("NoSuchElementException - request_loop(): clicking 'Register Section'", e, 2)
				# ----------------------------

				if self.check_registration() == True:
					self.success_notify()
					self.driver.quit()
				else:
					self.twilio_call()
					self.driver.get(self.course_address)

			else:
				time.sleep(self.refresh_rate)
				print("Keep refreshing...")
				while True:
					try:
						self.driver.refresh()
						break
					except Exception as e:
						self.exception_handler("Exception - request_loop(): refreshing", e, 120)



	def check_registration(self):
		while True:
			try:
				self.driver.get("https://courses.students.ubc.ca/cs/courseschedule?pname=regi_sections&tname=regi_sections")
				print('loaded Registered Courses page')
				self.driver.find_element_by_link_text(self.course_code)
				
			except TimeoutException as e:
				self.exception_handler("TimeoutException - check_registration(): loading Registered Courses page", e, 20)
			except NoSuchElementException as e:
				self.exception_handler("NoSuchElementException - check_registration(): cannot find course in Registered Courses page", e, 5)
				return False
			return True
			



def main():
	print("Starting course seats checker at", datetime.datetime.now())
	print("--------------------")

	# with open('courses.json') as json_file:
	# 	data = json.load(json_file)

	# number_to_run = input('Course: ')
	# course_data = data[number_to_run]

	user = input('Your username: ')
	password = input('Your password: ')
	course = input('The course you want (i.e. COMM 110 101): ')
	refresh_time =input('How frequent do you want to check the seat (in seconds): ')
	log_in = "y"
	# cs = CourseSelector(course_data[0], course_data[1], course_data[2], course_data[3], course_data[4])
	cs = CourseSelector(user, password, course, refresh_time, log_in)
	cs.initialize()
	

main()

