#coding: UTF-8

from threading import Thread
from urllib import request, parse
import json
from datetime import datetime


class Message:
	name = None
	refreshable = None
	cycles = 0
	raw_data = None
	text = ''
	main_color = False
	background_color = False
	message = None
	post_data = None

	def __init__(self, newsline_client, refreshable=True, iteration_time=60):
		self.message = {}
		self.led_server_url = newsline_client.config.led_server_url
		self.refreshable = refreshable # True - multiple sending, False - singular sending
		self.iteration_time = iteration_time # seconds, if "refreshable" is True, sending over the iteration time period
		self.previous_time = self.current_time
		if self.refreshable:
			self.thread = Thread(target=self.run_cycles)
			self.run = self.thread.start
		else:
			self.run = self.create_and_send

	@property
	def current_time(self):
		return datetime.now()

	def run_cycles(self):
		while True:
			if (self.current_time - self.previous_time).total_seconds() >= self.iteration_time or self.cycles == 0:
				self.create_and_send()
				self.cycles += 1

	def create_and_send(self):
		self.create_message_dict()
		self.convert_message_dict_to_post_data()
		self.send()

	def create_message_dict(self):
		self.message["string"] = self.text
		if self.main_color:
			self.message['main_color'] = self.main_color
		if self.background_color:
			self.message['background_color'] = self.background_color
		print(self.message)

	def convert_message_dict_to_post_data(self):
		self.post_data = str(json.dumps(self.message)).encode('utf-8')

	def send(self):
		req = request.Request(self.led_server_url, data=self.post_data) # this will make the method "POST"
		try:
			respond = request.urlopen(req)
		except:
			print("Can't send message to LED-server")
		self.previous_time = self.current_time

class Simple_Text_Message(Message):

	def __init__(self, newsline_client, text, refreshable=True, iteration_time=60):
		self.text = text
		super().__init__(newsline_client, refreshable, iteration_time)

class Piece(Message):
	# Piece is a refreshable message in a volume with a proper source address

	def __init__(self, newsline_client, name, volume, refreshable=True, iteration_time=60):
		self.name = name
		self.volume = volume
		super().__init__(newsline_client, refreshable, iteration_time)
		self.led_server_url += "/volumes"

	def create_message_dict(self):
		self.message["source"] = self.name
		self.message["volume"] = self.volume
		super().create_message_dict()

class Loop_Text_Message(Message):

	def __init__(self, newsline_client, loop_list, refreshable=True, iteration_time=60):
		self.loop_list = loop_list
		super().__init__(newsline_client, refreshable, iteration_time)

	def create_message_dict(self):
		if self.cycles == 0:
			self.i = 0

		item = self.loop_list[self.i]
		if isinstance(item, dict):
			self.text = item["string"]
			self.main_color = item.get("main_color")
			self.background_color = item.get("background_color")
		else:
			self.text = item

		self.i += 1
		if self.i >= len(self.loop_list):
			self.i = 0
		super().create_message_dict()

class Loop_Text_Piece(Loop_Text_Message, Piece):

	def __init__(self, newsline_client, loop_list, name, volume, iteration_time=60):
		Loop_Text_Message.__init__(self, newsline_client, loop_list)
		Piece.__init__(self, newsline_client, name, volume, iteration_time=iteration_time)

class Date_Time_Message(Message):
	main_color = 'blue'

	def create_message_dict(self):
		self.text = self.current_time.strftime("%H:%M:%S")
		super().create_message_dict()

class Date_Time_Piece(Piece, Date_Time_Message):

	def __init__(self, newsline_client, name, volume, iteration_time=30):
		super().__init__(newsline_client, name, volume, iteration_time=iteration_time)