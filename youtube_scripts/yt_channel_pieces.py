#coding: UTF-8

import json
import urllib.request
from basic_messages import Piece
from .yt_info_generator import YT_Channels_Info


class YT_Channel_Info(Piece):
	# https://developers.google.com/youtube/v3/docs/channels/list
	# https://commentpicker.com/youtube-channel-id.php
	# https://www.youtube.com/watch?v=D12v4rTtiYM # find in html <meta itemprop="channelId" content="UC4e_XPBiiIO4fo4_CucxQeg">

	previous_views_value = None
	previous_subscribers_value = None
	previous_videos_value = None

	url_template = "https://www.googleapis.com/youtube/v3/channels?part=statistics&id={}&key={}"	

	def __init__(self, yt_queue, channel_settings):

		newsline_client = yt_queue.newsline_client
		self.api_key = yt_queue.api_key

		source_name = channel_settings["source_name"]
		volume_name = channel_settings["volume_name"]
		iteration_time = channel_settings["iteration_time"]

		self.channel_id = channel_settings["channel_id"]
		self.title = channel_settings["title"]
		self.info_combination = channel_settings["info_combination"].lower()
		self.main_color = channel_settings["main_color"]
		self.background_color = channel_settings["background_color"]

		super().__init__(newsline_client, source_name, volume_name, iteration_time=iteration_time)

	@staticmethod
	def get_values_text(current_value, previous_value):

		def make_value_readable(value):
			value = str(value)
			split = lambda value, n: [value[i - n:i] if i - n > 0 else value[:i] for i in range(len(value), 0, -1 * n)]
			value_list = split(value, 3)
			value_list.reverse()
			return ".".join(value_list)

		if previous_value:
			difference = current_value - previous_value

			if difference == 0:
				return "{} =".format(make_value_readable(current_value)), "blue"
			else:
				if difference > 0:
					difference_color = "green"
					difference_symbol = "▲"
				elif difference < 0:
					difference_color = "red"
					difference_symbol = "▼"
				return "{} {}{}".format(make_value_readable(current_value),
										make_value_readable(difference_symbol),
										make_value_readable(abs(difference))), difference_color
		else:
			return make_value_readable(current_value), "blue"

	def create_message_dict(self):
		channel_statistic = self.get_channel_statistic()

		if len(channel_statistic) == 3:
			views_value, subscribers_value, videos_value = channel_statistic[0], channel_statistic[1], channel_statistic[2]
			letters_colors_dict = {}

			self.text = self.title
			start_index = len(self.title) + 1

			if "v" in self.info_combination:
				views_text, views_difference_color = self.get_values_text(views_value, self.previous_views_value)
				views_text = "👀" + views_text
				self.text += " {}".format(views_text)
				self.previous_views_value = views_value

				end_index = start_index + len(views_text)
				letters_colors_dict.update({views_difference_color: ["{}-{}".format(start_index, end_index)]})
				start_index = end_index + 1

			if "s" in self.info_combination:
				subscribers_text, subscribers_difference_color = self.get_values_text(subscribers_value, self.previous_subscribers_value)
				subscribers_text = "👤" + subscribers_text
				self.text += " {}".format(subscribers_text)
				self.previous_subscribers_value = subscribers_value

				end_index = start_index + len(subscribers_text) - 1
				subscribers_text_range = "{}-{}".format(start_index, end_index)

				if subscribers_difference_color in letters_colors_dict:
					letters_colors_dict[subscribers_difference_color].append(subscribers_text_range)
				else:
					letters_colors_dict.update({subscribers_difference_color: [subscribers_text_range]})
				start_index = end_index + 1

			if "w" in self.info_combination:
				videos_text, videos_difference_color = self.get_values_text(videos_value, self.previous_videos_value)
				videos_text = "▶" + videos_text
				self.text += " {}".format(videos_text)
				self.previous_videos_value = videos_value

				end_index = start_index + len(videos_text)
				videos_text_range = "{}-{}".format(start_index, end_index)

				if videos_difference_color in letters_colors_dict:
					letters_colors_dict[videos_difference_color].append(videos_text_range)
				else:
					letters_colors_dict.update({videos_difference_color: [videos_text_range]})

			self.message["letters_colors"] = {"main_color": letters_colors_dict}

		else:
			self.text = "{} !{}!".format(self.title, channel_statistic[0])
			self.message["letters_colors"] = {"main_color": {"red": ["{}-{}".format(len(self.title) + 1, len(self.text) - 1)]}}

		super().create_message_dict()

	def get_channel_statistic(self):
		request_url = self.url_template.format(self.channel_id, self.api_key)

		try:
			connection = urllib.request.urlopen(request_url)
			body = connection.read().decode("utf-8")
		except:
			return ["Connection Error"]
		else:
			if connection.status == 200 and 'application/json' in connection.headers['content-type']:
				video_info = json.loads(body)
				views_value = int(video_info["items"][0]["statistics"]["viewCount"])
				subscribers_value = int(video_info["items"][0]["statistics"]["subscriberCount"])
				videos_value = int(video_info["items"][0]["statistics"]["videoCount"])
				return views_value, subscribers_value, videos_value
			elif connection.status == 404:
				return ["Channel can't be found"]
			else:
				return ["Response can't be handled"]

class YT_Channels_Queue:

	queue = []

	def __init__(self, newsline_client):
		self.newsline_client = newsline_client
		self.api_key = self.newsline_client.config.yt_api_key

		channels_info = YT_Channels_Info.get_info_list()
		for video_info in channels_info:
			self.queue.append(YT_Channel_Info(self, video_info))