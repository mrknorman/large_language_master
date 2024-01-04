import logging
import json

from dataclasses import dataclass
from typing import List, Tuple
from pathlib import Path
from time import sleep

from openai import OpenAI

import prompts

class Verbs():
	pass

@dataclass
class APIConfig():
	system_prompt : str
	model : str
	temperature : float
	client : OpenAI

	def __post_init__(self):
		if not isinstance(self.system_prompt, str):
			raise ValueError("system_prompt is wrong type!")
		if not isinstance(self.model, str):
			raise ValueError("model is wrong type!")
		if not isinstance(self.temperature, float):
			raise ValueError("temperature is wrong type!")

class ElementPrompt:
	arguments : dict = None
	template : str = None
	prompt : str = None
	response : str = None 

	api_config : APIConfig = None

	num_prompt_retries : int = 0
	max_num_prompt_retries : int = 10

	def __init__(
			self,
			arguments : dict,
			template : str,
			api_config : APIConfig,
			max_num_prompt_retries : int = 10
		) -> None:

		self.logger = logging.getLogger(__name__)

		self.arguments = arguments
		self.template = template

		self.api_config = api_config

		self.num_prompt_retries = 0
		self.max_num_prompt_retries = max_num_prompt_retries

		self.generate_prompt()
		self.acquire_response(self.prompt)

	def generate_prompt(
		self
		) -> None:

		if not isinstance(self.arguments, dict):
			raise ValueError("prompt_arguments is wrong type!")
		elif not isinstance(self.template, str):
			raise ValueError("prompt_template is wrong type!")
		else:
			self.prompt = self.template.format(
				**self.arguments
			)

	def acquire_response(
			self,
			prompt : str
		) -> None:

		if not isinstance(self.api_config, APIConfig):
			raise ValueError("Argument 'api_config' should be APIConfig!")
		else:
			self.response = self.check_response(
				self.get_response(prompt), 
				prompt,
			)
	
	def get_response(
			self, 
			prompt : str,
			num_retries : int = 0,
			retry_sleep_duration_seconds : float = 1.0,
			maximum_num_retries : int = 10
		) -> str:

		try:
			response = self.api_config.client.chat.completions.create(
				model=self.api_config.model,
				response_format={"type": "json_object"},
				messages=[
					{
						'role':'system', 
						'content': self.api_config.system_prompt
						
					},
					{
						'role':'user', 
						'content': prompt
					}
				],
				temperature=self.api_config.temperature
			)

			return response
		except Exception as e:
			num_retries += 1

			if num_retries > maximum_num_retries:
				raise TimeoutError("Maximum num API requests reached.")
			
			self.logger.warning(
				(f"Call to API failed, because of {e} retrying for the "
				f"{num_retries} time in {retry_sleep_duration_seconds} s")
			)
			sleep(retry_sleep_duration_seconds)

			return self.get_response(prompt, num_retries)

	def check_response(
		self,
		response : str,
		prompt : str
	):
		try:
			response = json.loads(
				response.choices[0].message.content
			)
		except Exception as e:
			self.logger.warning("Error occoured coverting API response to json. Retrying")
			self.num_prompt_retries += 1

			if self.num_prompt_retries > self.max_num_prompt_retries:
				raise TimeoutError((
					"API failed return request in required format"
					f"after {self.max_num_prompt_retries} retries!"
				))

			response = self.get_response(
				(f"Error in previous response: '{response}' for prompt: '{prompt}'."
				f" Issue: '{e}'."
				" Please provide a response in valid JSON format as required by python's json.loads function."
				" Non-JSON responses will lead to an error."
				)
			)

		return response

class Element():
	name : str = None
	description : str = None
	path : Path = None

	api_config : APIConfig = None
	prompt_arguments : dict = None
	prompt_template : str = None

	parents : List = None
	children : List = None
	verbs : List = None

	prompt : str = None
	outline : dict = None
	header : dict = None

	def __init__(
			self,
			name: str, 
			prompt_template : str,
			prompt_arguments : List[str], 
			header_attributes : List[str],
			api_config : APIConfig,
			verbs : List = None,
			parents : List = None,
		):

		self.name = name
		self.parents = parents
		self.verbs = verbs
		self.api_config = api_config

		self.prompt_arguments = {
			key : getattr(self, key) for key in prompt_arguments
		}
		self.prompt_template = prompt_template

		self.header_attributes = header_attributes

	def save(self):
		pass

	def load(self):
		pass

	def initilize(self):
		self.generate_primary_outline()
		self.encorporate_outline()
		self.create_header()

	def generate_primary_outline(self):
		self.prompt = ElementPrompt(
			arguments=self.prompt_arguments,
			template=self.prompt_template,
			api_config=self.api_config
		)
		self.outline = self.prompt.response

	def encorporate_outline(self):
		for key, value in self.outline.items():
			setattr(self, key, value)

	def create_header(self):
		extracted_attibute_values= {
			attr: getattr(self, attr) for attr in self.header_attributes if hasattr(self, attr)}
		
		self.header = ""
		for attr, value in extracted_attibute_values.items():
			self.header += f' - {attr}: {value}\n'

class ElementNetwork(Element):

	def __init__(
			self,
			name : str,
			prompt_template : str,
			prompt_arguments : List[str], 
			header_attrubutes : List[str],
			node_key : str,
			vertex_key : str,
			verticies_prompt_template : str,
			verticies_prompt_arguments : dict,
			api_config : APIConfig, 
			verbs : List = None, 
			parents : List =None,
		):

		self.node_key = node_key
		self.vertex_key = vertex_key
		self.verticies_prompt_template = verticies_prompt_template
		self.verticies_prompt_arguments = verticies_prompt_arguments

		super().__init__(
			name, 
			prompt_template, 
			prompt_arguments,
			header_attrubutes,
			api_config,
			verbs=verbs,
			parents=parents
		)

	def initilize(self):
		super().initilize()
		self.generate_vertices()
		self.verticies_prompt_arguments = {
			key : getattr(self, key) for key in self.verticies_prompt_arguments
		}
		self.generate_vertices_outline()

	def ensure_connections(self):  
		network_dict = getattr(self, self.node_key)

		for key, value in network_dict.items():
			for connected_key in value["connected_to"]:
				if key not in network_dict[connected_key]["connected_to"]:
					network_dict[connected_key]["connected_to"].append(key)

	def get_all_verticies(self):
		"""Returns a set containing all pairs of connected rooms."""
		network_dict = getattr(self, self.node_key)
		verticies = set()

		for key, node in network_dict.items():
			for connected_key in node["connected_to"]:
				# Creating a sorted tuple to ensure uniqueness (e.g., (A, B) == (B, A))
				pair = tuple(sorted([key, connected_key]))
				verticies.add(pair)
		
		setattr(self, self.vertex_key, verticies)
	
	def generate_vertices(self):
		self.ensure_connections()
		self.get_all_verticies()

	def generate_vertices_outline(self):
		self.verticies_prompt = ElementPrompt(
			arguments=self.verticies_prompt_arguments,
			template=self.verticies_prompt_template,
			api_config=self.api_config
		)
		setattr(
			self, 
			f"{self.vertex_key}_outline", 
			self.verticies_prompt.response
		)
	
	def initilize_nodes(self):
		pass

class ElementVertex(Element):

	def __init__(
			self,
			name : str,
			prompt_template : str,
			prompt_arguments : List[str], 
			header_attrubutes : List[str],
			node_key : str,
			connections : Tuple[str],
			api_config : APIConfig, 
			verbs : List = None, 
			parents : List =None,
		):

		self.node_key = node_key
		self.connections = connections 
		
		super().__init__(
			name, 
			prompt_template, 
			prompt_arguments,
			header_attrubutes,
			api_config,
			verbs=verbs,
			parents=parents
		)

class Dungeon(ElementNetwork):

	def __init__(
			self,
			name : str,
			num_rooms : int,
			api_config : APIConfig, 
			verbs : List = None, 
			parents : List =None,
		):

		self.num_rooms = num_rooms

		super().__init__(
			name, 
			prompts.DUNGEON, 
			prompts.DUNGEON_ARGUMENTS,
			prompts.DUNGEON_ATTRIBUTES,
			"rooms",
			"portals",
			prompts.DUNGEON_PORTALS,
			prompts.DUNGEON_PORTALS_ARGUMENTS,
			api_config,
			verbs,
			parents
		)

class Room(Element):

	def __init__(
			self,
			name : str,
			api_config : APIConfig, 
			verbs : List = None, 
			parents : List =None,
		):

		super().__init__(
			name, 
			prompts.ROOM, 
			prompts.ROOM_ARGUMENTS,
			prompts.ROOM_ATTRIBUTES,
			api_config,
			verbs,
			parents
		)


class Portal(ElementVertex):

	def __init__(
			self,
			name : str,
			room_connections : Tuple(str),
			api_config : APIConfig, 
			verbs : List = None, 
			parents : List =None,
		):

		super().__init__(
			name, 
			prompts.PORTAL, 
			prompts.PORTAL_ARGUMENTS,
			prompts.PORTAL_ATTRIBUTES,
			"rooms",
			room_connections,
			api_config,
			verbs,
			parents
		)

if __name__ == "__main__":

	MODEL = "gpt-4-1106-preview"
	TEMPERATURE = 0.7

	client = OpenAI(api_key=open('./api_key', 'r').read())
	dungeon_arguments = {
		"name" : "Tombie's Funhouse",
		"num_rooms" : 3
	}

	api_config = APIConfig(
		system_prompt=prompts.SYSTEM,
		model=MODEL,
		temperature=TEMPERATURE,
		client=client,
	)

	dungeon = Dungeon(
		name="Tombie's Funhouse",
		num_rooms=3,
		api_config=api_config
	)
	dungeon.initilize()

	print(dungeon.header)
	print(dungeon.portals)
	print(dungeon.portals_outline)

