#coding: UTF-8


import os

class YT_Videos_Info:

	config_file_name = "videos_config.txt"
	internal_dir = "youtube_scripts"
	video_separator = "\n"
	info_separator = "||"
	info_part_keys = ["title",
					  "video_code",
					  "volume_name",
					  "source_name",
					  "iteration_time",
					  "info_combination",
					  "main_color",
					  "background_color"]
	default_iteration_time = 300 # seconds
	default_info_combination = "vlc" # v - views, l - likes, c - comments

	@staticmethod
	def file_exists(file_name):
		return os.path.exists(file_name)

	@classmethod
	def get_raw_videos_info(self):
		config_file_name = os.path.join(self.internal_dir, self.config_file_name)
		if self.file_exists(os.path.join(config_file_name)):
			with open(config_file_name, 'r', encoding='utf-8') as file:
				return file.read()

	@classmethod
	def handle_raw_iteration_time(self, raw_time):

		def get_value(raw_text):
			alpha_list = []
			for symbol_index in range(len(raw_text)):
				if raw_text[symbol_index].isalpha():
					alpha_list.append(symbol_index)
			if len(alpha_list) > 0:
				return raw_text[alpha_list[-1]+1:]
			else:
				return 0

		def get_time(raw_time, time_separator, multiplier=1):
			if time_separator in raw_time:
				index = raw_time.find(time_separator)
				time = raw_time[0:index]
				if not time.isdigit():
					time = get_value(time)
				if time:
					return int(time) * multiplier
				else:
					return 0
			return 0

		seconds_total = 0

		for time_tuple in (('h', 3600), ('m', 60), ('s')):
			seconds_total += get_time(raw_time, *time_tuple)

		if seconds_total == 0:
			seconds_total = self.default_iteration_time

		return seconds_total

	@classmethod
	def get_info_list(self):
		raw_videos_info = self.get_raw_videos_info()
		if raw_videos_info:
			videos_info = []
			raw_videos_info_list = raw_videos_info.split(self.video_separator)
			for raw_video_info_index in range(len(raw_videos_info_list)):
				video_info = {}
				raw_video_info = raw_videos_info_list[raw_video_info_index]
				video_info_parts = raw_video_info.split(self.info_separator)

				info_parts_count = len(video_info_parts)
				if info_parts_count >= 4:

					for video_info_part_index in range(0, len(video_info_parts)):
						video_info_part_key = self.info_part_keys[video_info_part_index]
						video_info_part_value = video_info_parts[video_info_part_index]
						video_info[video_info_part_key] = video_info_part_value

					for video_info_part_index in range(len(video_info_parts), len(self.info_part_keys)):
						video_info_part_key = self.info_part_keys[video_info_part_index]
						if video_info_part_key == "iteration_time":
							video_info[video_info_part_key] = self.default_iteration_time
						elif video_info_part_key == "info_combination":
							video_info[video_info_part_key] = self.default_info_combination
						else:
							video_info[video_info_part_key] = None

					if not video_info["iteration_time"].isdigit():
						video_info["iteration_time"] = self.handle_raw_iteration_time(video_info["iteration_time"])
					else:
						video_info["iteration_time"] = int(video_info["iteration_time"])

					videos_info.append(video_info)

				elif info_parts_count == 0:
					print("Info string {} is empty in {}".format(raw_video_info_index + 1), self.config_file_name)

				else:
					video_title = video_info_parts[0]
					missing_parts = ", ".join([self.info_part_keys[video_info_part_index] for video_info_part_index in range(1, 4)])
					print("{} doesn't have params: {}". format(video_title, missing_parts))

			return videos_info

		else:
			print("Can't find or read the config file {}".format(self.config_file_name))
			return []

	@classmethod
	def get_pieces_info_list(self):
		videos_info_list = self.get_info_list()
		for video_info in videos_info_list:
			video_info["string"] = video_info["title"]
		return videos_info_list

class YT_Channels_Info(YT_Videos_Info):
	config_file_name = "channels_config.txt"
	video_separator = "\n"
	info_separator = "||"
	info_part_keys = ["title",
					  "channel_id",
					  "volume_name",
					  "source_name",
					  "iteration_time",
					  "info_combination",
					  "main_color",
					  "background_color"]
	default_iteration_time = 1800 # seconds
	default_info_combination = "vsw" # v - views, s - subscribres, w - videos