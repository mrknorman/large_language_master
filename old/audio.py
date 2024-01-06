from openai import OpenAI
from pathlib import Path 
import subprocess
import hashlib
import time
import pygame

from mutagen.mp3 import MP3

def get_mp3_length(filename):
    audio = MP3(filename)
    return audio.info.length

# Function to print a sentence with timing based on word length
def print_sentence_with_timing(sentence, mp3_path):
	duration = get_mp3_length(mp3_path)
	words = sentence.split()
	total_letters = sum(len(word) for word in words)
	time_per_letter = duration / total_letters

	for word in words:
		word_duration = len(word) * time_per_letter
		print(word, end=' ', flush=True)
		time.sleep(word_duration)
	
	print("")

def text_to_sha256_hash(text):
    encoded_text = text.encode()
    sha256_hash = hashlib.sha256(encoded_text).hexdigest()
    return sha256_hash

def play_mp3(path):
    pygame.mixer.init()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()

client = OpenAI(api_key=open('./api_key', 'r').read())

def read_text(text, skip = False):

	if not skip: 

		text_hash = text_to_sha256_hash(text)
		speech_file_path = Path(__file__).parent / f"./audio/{text_hash}.mp3"

		if not Path(speech_file_path).exists():
			response = client.audio.speech.create(
				model="tts-1",
				voice="alloy",
				input=text
			)

			response.stream_to_file(speech_file_path)

		play_mp3(speech_file_path)
		print_sentence_with_timing(text, speech_file_path)

	else:
		print(text)