#coding: UTF-8

import os
import json
from youtube_scripts.yt_info_generator import YT_Videos_Info
from youtube_scripts.yt_info_generator import YT_Channels_Info
from config import Config


class Volume_File_Generator:
	volumes_dir = Config.led_volumes_dir
	filename = None

	@classmethod
	def get_volume_filename(self):
		self.volume_filepath = os.path.join(self.volumes_dir, self.filename)

	@staticmethod
	def file_exists(file_name):
		return os.path.exists(file_name)

	@classmethod
	def get_saved_pieces_list(self):
		self.get_volume_filename()
		if self.file_exists(self.volume_filepath):
			with open(self.volume_filepath, 'r', encoding='utf-8') as file:
				return self.handle_saved_pieces(json.load(file))
		else:
			print("Can't find {}".format(self.volume_filepath))

	@classmethod
	def handle_saved_pieces(self):
		pass

	@classmethod
	def save(self, pieces_to_save):
		with open(self.volume_filepath, 'w', encoding='utf-8') as file:
			json.dump(pieces_to_save, file, ensure_ascii=False)
		print('Volume \"{}\" has been saved with content \"{}\"'.format(self.filename, pieces_to_save))

class Newsline_Volume_File_Generator(Volume_File_Generator):
	filename = "newsline.json"

	@classmethod
	def handle_saved_pieces(self, newsline_dict):
		saved_pieces = []
		for source_name, piece_dict in newsline_dict.items():
			piece_dict["volume_name"] = "newsline"
			piece_dict["source_name"] = source_name
			saved_pieces.append(piece_dict)
		return saved_pieces

class Notes_Volume_File_Generator(Volume_File_Generator):
	filename = "notes.json"

	@classmethod
	def handle_saved_pieces(self, notes_dict):
		saved_pieces = []
		for piece_dict_index in range(len(notes_dict)):
			piece_dict = notes_dict[piece_dict_index]
			piece_dict["volume_name"] = "notes"
			piece_dict["source_name"] = str(piece_dict_index)
			saved_pieces.append(piece_dict)
		return saved_pieces

class Volume_Files_Generator:	
	newsline_sources_list_filename = Config.newsline_sources_list_filename
	pieces_to_include = [Newsline_Volume_File_Generator.get_saved_pieces_list(),
						 Notes_Volume_File_Generator.get_saved_pieces_list(),
						 YT_Channels_Info.get_pieces_info_list(),
						 YT_Videos_Info.get_pieces_info_list()]

	@staticmethod
	def is_volume_piece(volume_piece):
		if isinstance(volume_piece, dict) and "volume_name" in volume_piece and "source_name" in volume_piece:
			return True

	@classmethod
	def generate(self):
		pieces = []
		for piece_to_include in self.pieces_to_include:
			if self.is_volume_piece(piece_to_include):
				pieces.append(piece_to_include)
			elif isinstance(piece_to_include, list):
				for piece_in_list in piece_to_include:
					if self.is_volume_piece(piece_in_list):
						pieces.append(piece_in_list)

		newsline_dict = {}
		notes_dict = {}
		notes_list = []

		for piece in pieces:
			piece_dict = {}
			piece_dict["string"] = piece.get("string", "No text for a piece with the \"{}\" source in the \"{}\" volume".format(piece["source_name"], piece["volume_name"]))
			for key in ["main_color", "background_color"]:
				value = piece.get(key)
				if value:
					piece_dict[key] = value

			if piece["volume_name"] == "newsline":
				volume_dict = newsline_dict
			elif piece["volume_name"] == "notes":
				volume_dict = notes_dict

			if piece["source_name"] in volume_dict:
				print("Volume \"{}\" already has a piece with the source \"{}\". Left this {}".format(piece["volume_name"],
																								piece["source_name"],
																								piece_dict))
			volume_dict[piece["source_name"]] = piece_dict


		if len(notes_dict) > 0:
			valid_indexes = []
			invalid_indexes = []
			for note_index in sorted(notes_dict.keys()):
				if note_index.isdigit():
					valid_indexes.append(int(note_index))
				else:
					invalid_indexes.append(note_index)

			valid_indexes.sort()
			outranged_indexes = []
			for valid_index in valid_indexes:
				if len(notes_list) == valid_index:
					notes_list.append(notes_dict[str(valid_index)])
				else:
					outranged_indexes.append(valid_index)

			for outranged_index in outranged_indexes:
				notes_list.append(notes_dict[str(outranged_index)])
				print("Note piece with the source \"{}\" is out of range. You can send messages using the source \"{}\"".format(outranged_index, len(notes_list)-1))

			for invalid_index in invalid_indexes:
				notes_list.append(notes_dict[invalid_index])
				print("Note piece with the source \"{}\" is not valid. You can send messages using the source \"{}\"".format(invalid_index, len(notes_list)-1))

		if len(newsline_dict) > 0:
			Newsline_Volume_File_Generator.save(newsline_dict)
			self.save_newsline_sources_list_file(list(newsline_dict.keys()))

		if len(notes_list) > 0:
			Notes_Volume_File_Generator.save(notes_list)

	@classmethod
	def save_newsline_sources_list_file(self, newsline_sources_list):
		with open(self.newsline_sources_list_filename, 'w', encoding='utf-8') as file:
			file.write(str(newsline_sources_list))

		print('-----------------------')
		print('Newsline sources names:')
		for newsline_source in newsline_sources_list:
			print(newsline_source)
		print('-----------------------')
		print("Insert this names in the sources attribute of the class Newsline_saved_messages. File \"saved_messages_library.py\"")
		print("Example:\n")
		print("class Newsline_saved_messages(Saved_Messages_Volume_Dict):\n")
		print("    volume_name = 'newsline'")
		print("    volume_filename = 'data/saves/newsline.json'")
		for newsline_source_index in range(len(newsline_sources_list)):
			newsline_source = newsline_sources_list[newsline_source_index]
			if newsline_source_index == 0:
				print("    sources = [{},".format(newsline_source))
			elif newsline_source_index == len(newsline_sources_list) - 1:
				print("               {}".format(newsline_source))
			else:
				print("               {},".format(newsline_source))
		print('\n-----------------------')
		print('Newsline sources names has been saved in the file \"{}\" you can copy and insert them'.format(self.newsline_sources_list_filename))

if __name__ == "__main__":
	Volume_Files_Generator.generate()