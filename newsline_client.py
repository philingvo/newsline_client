#coding: UTF-8

from basic_messages import *
from youtube_scripts.yt_video_pieces import YT_Videos_Queue
from youtube_scripts.yt_channel_pieces import YT_Channels_Queue
from config import Config


class Newsline_Client:
	config = Config
	messages = []

	@staticmethod
	def is_message_object(message_to_include):
		return isinstance(message_to_include, Message)

	def __init__(self):
		messages_to_include = [
								# Loop_Text_Piece(self,
								# 				loop_list=['JavaScript', 'Python', 'React', 'Django'],
								# 				name='plans',
								# 				volume="newsline",
								# 				iteration_time=10),
								# Date_Time_Piece(self, name='date_time', volume="newsline")
								YT_Videos_Queue(self).queue,
								YT_Channels_Queue(self).queue,
								]

		for message_to_include in messages_to_include:
			if self.is_message_object(message_to_include):
				self.messages.append(message_to_include)
			elif isinstance(message_to_include, list):
				for message_in_list in message_to_include:
					if self.is_message_object(message_in_list):
						self.messages.append(message_in_list)

	def run(self):
		for message in self.messages:
			message.run()

if __name__ == "__main__":
	server = Newsline_Client()
	server.run()
