#coding: UTF-8

import json
import urllib.request
from basic_messages import Piece
from .yt_info_generator import YT_Videos_Info


class YT_Video_Info(Piece):
	# https://developers.google.com/youtube/v3/docs/videos/list

	previous_views_value = None
	previous_likes_value = None
	previous_comments_value = None

	url_template = "https://www.googleapis.com/youtube/v3/videos?part=statistics&id={}&key={}"

	def __init__(self, yt_queue, video_settings):

		newsline_client = yt_queue.newsline_client
		self.api_key = yt_queue.api_key

		source_name = video_settings["source_name"]
		volume_name = video_settings["volume_name"]
		iteration_time = video_settings["iteration_time"]

		self.video_code = self.get_video_code(video_settings["video_code"])
		self.title = video_settings["title"]
		self.info_combination = video_settings["info_combination"].lower()
		self.main_color = video_settings["main_color"]
		self.background_color = video_settings["background_color"]

		super().__init__(newsline_client, source_name, volume_name, iteration_time=iteration_time)

	def get_video_code(self, raw_video_code):
		if "youtube.com" in raw_video_code:
			code_index = raw_video_code.find("watch?v=") + len("watch?v=")
			return raw_video_code[code_index:]
		elif "youtu.be" in raw_video_code:
			code_index = raw_video_code.rfind("/") + 1
			return raw_video_code[code_index:]
		else:
			return raw_video_code

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

		video_statistic = self.get_video_statistic()
		if len(video_statistic) == 3:
			views_value, likes_value, comments_value = video_statistic[0], video_statistic[1], video_statistic[2]
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

			if "l" in self.info_combination:
				likes_text, likes_difference_color = self.get_values_text(likes_value, self.previous_likes_value)
				likes_text = "❤" + likes_text
				self.text += " {}".format(likes_text)
				self.previous_likes_value = likes_value

				end_index = start_index + len(likes_text) - 1
				likes_text_range = "{}-{}".format(start_index, end_index)

				if likes_difference_color in letters_colors_dict:
					letters_colors_dict[likes_difference_color].append(likes_text_range)
				else:
					letters_colors_dict.update({likes_difference_color: [likes_text_range]})
				start_index = end_index + 2

			if "c" in self.info_combination:
				comments_text, comments_difference_color = self.get_values_text(comments_value, self.previous_comments_value)
				comments_text = "💬" + comments_text
				self.text += " {}".format(comments_text)
				self.previous_comments_value = comments_value

				end_index = start_index + len(comments_text)
				comments_text_range = "{}-{}".format(start_index, end_index)

				if comments_difference_color in letters_colors_dict:
					letters_colors_dict[comments_difference_color].append(comments_text_range)
				else:
					letters_colors_dict.update({comments_difference_color: [comments_text_range]})

			self.message["letters_colors"] = {"main_color": letters_colors_dict}

		else:
			self.text = "{} !{}!".format(self.title, video_statistic[0])
			self.message["letters_colors"] = {"main_color": {"red": ["{}-{}".format(len(self.title) + 1, len(self.text) - 1)]}}

		super().create_message_dict()

	def get_video_statistic(self):
		request_url = self.url_template.format(self.video_code, self.api_key)

		try:
			connection = urllib.request.urlopen(request_url)
			body = connection.read().decode("utf-8")
		except:
			return ["Connection Error"]
		else:
			if connection.status == 200 and 'application/json' in connection.headers['content-type']:
				video_info = json.loads(body)
				views_value = int(video_info["items"][0]["statistics"]["viewCount"])
				likes_value = int(video_info["items"][0]["statistics"]["likeCount"])
				comments_value = int(video_info["items"][0]["statistics"]["commentCount"])
				return views_value, likes_value, comments_value
			elif connection.status == 404:
				return ["Video can't be found"]
			else:
				return ["Response can't be handled"]

class YT_Videos_Queue:

	queue = []

	def __init__(self, newsline_client):
		self.newsline_client = newsline_client
		self.api_key = self.newsline_client.config.yt_api_key
		videos_info = YT_Videos_Info.get_info_list()

		for video_info in videos_info:
			self.queue.append(YT_Video_Info(self, video_info))