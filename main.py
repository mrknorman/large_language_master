import sys
import openai
import time
from pathlib import Path 
import json
import ast

# Remember traps and secret levers

# Trapped       = will activate on interaction
# Discoverable  = can investigate to reveal other elements (roll investigate)
# Informational = can investigate to obtain information (roll investigate + history/religion/arcana/nature/survival)
# Interactable  = can interact to change state of the room (roll intelligence/strength/dex)
# Traversable   = can use to move around the room, i.e stairs, elevators.
# Exit          = can be used to leave room

class boundary():
    verticies = []
    material = []
    exits = []
    traps = []
    secret_knowledge = []
    secret_buttons = []

class floor():
    main = []
    patches = []
    elevators = []
    traps = []
    secret_knowledge = []
    secret_buttons = []

class structure():
    boundary = []
    floor = []

class Room:

    structure = []
    characters = []
    items = []

    def __init__(self, name, connected_to, dungeon):

        self.name = name
        self.connected_to = connected_to

        plan = self.create_plan(dungeon)
        self.ingest(plan)

    def ingest(self, room_data):
        """Ingest room data from dictionary format."""
        self.purpose  = room_data.get('purpose', "")
        self.flavour  = room_data.get('flavour', "")
        self.secrets  = room_data.get('secrets', "")
        self.story    = room_data.get('story', "")
        self.effect   = room_data.get('effect', "")

    def display(self):
        """Display the details of the room."""
        print(f"""
            Name: {self.name}
            Purpose: {self.purpose}
            Flavour Text: {self.flavour}
            Secrets: {self.secrets}
            Overall Story: {self.story}
            Effect: {self.effect}
        """)

    def create_plan(self, dungeon):
        # send a ChatCompletion request to count to 100

        room_string = \
            f"""
                You are designing a new room for your adventuring party to explore.
                Here is a brief high-level description of the dungeon so far:
                
                Name: {dungeon.name}
                Purpose: {dungeon.purpose}
                Flavour Text: {dungeon.flavour}
                Secrets: {dungeon.secrets}
                Overall Story: {dungeon.story}
                Effect: {dungeon.effect}

                The player will only see the name and the flavour text. The others are notes for the dungeon ai 
                to use when generating the room\'s details, to ensure consistency.

                The rooms is called {self.name} and is connected to {self.connected_to}
                
                Respond with an brief outline in the following format imitating a python dictionary:
                {{
                \"purpose\": \"the in universe purpose of the room\",
                \"flavour\": \"an emotive decription of the room for the players\",
                \"secrets\": \"any secrets the room may hold\",
                \"story\": \"the underlying story you want the room to tell.\"',
                \"effect\": \"the effect you imagine this room will have on the players stories\"
                }}
            """

        response = openai.ChatCompletion.create(
                    model='gpt-3.5-turbo',
                        messages=[
                                    {
                                        'role':'system', 
                                        'content': 
                                        'You are an expert dungeon master with many years of experience and a'
                                        'creative story-driven approach to constructing adventures. Your primary goal is to '
                                        'create a fun and engaging experience for all your players. Your responses will be '
                                        'placed into a framework so try to generate outputs which are as close to the format '
                                        'described as possible.'
                                    },
                                    {
                                        'role':'user', 
                                        'content': room_string 
                                    }
                                ],
                            temperature=0
                            )

        return json.loads(response["choices"][0]["message"]["content"])

        def create_new_encounter():
            print("NEW")

class Dungeon:

    def __init__(self, name=None):
        self.name = name
        plan = self.create_dungeon_plan(name)
        self.ingest(plan)

    def ingest(self, data):
        """Ingest room data from dictionary format."""
        self.purpose  = data.get('purpose', "")
        self.flavour  = data.get('flavour', "")
        self.secrets  = data.get('secrets', "")
        self.story    = data.get('story', "")
        self.effect   = data.get('effect', "")
        self.rooms    = data.get('rooms', "")

    def display(self):
        """Display the details of the room."""
        print(f"""
            Name: {self.name}
            Purpose: {self.purpose}
            Flavour Text: {self.flavour}
            Secrets: {self.secrets}
            Overall Story: {self.story}
            Effect: {self.effect}
        """)

    def create_dungeon_plan(self, name):
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
                messages=[
                            {
                                'role':'system', 
                                'content': 
                                'You are an expert dungeon master with many years of experience and a'
                                'creative story-driven approach to constructing adventures. Your primary goal is to '
                                'create a fun and engaging experience for all your players. Your responses will be '
                                'placed into a framework so try to generate outputs which are as close to the format '
                                'described as possible.'
                            },
                            {
                                'role':'user', 
                                'content': 
                                f'You are designing a dungeon called {name} for your adventuring party to explore.'
                                'The details of the rooms will be filled out by you later on, for now focus on the overall plan of '
                                'the dungeon as well, the story you\'d like it to tell, and how it will effect the player\'s journey.'
                                'Respond with an brief outline in the following format imitating a python dictionary:' \
                                '\"purpose\": \"the in universe purpose of the dungeon\", \n'\
                                '\"flavour\": \"an emotive decription of the dungeon for the players\"' \
                                '\"secrets\": \"any secrets the dungeon may hold\"' \
                                '\"story\": \"the underlying story you want the dungeon to tell.\"' \
                                '\"effect\": \"the effect you imagine this room will have on the players stories\"'
                                '\"rooms\": ['
                                    '{\"name\": room_name, \"connected_to\": [ list_of_connecting_rooms ] }'
                                    '...'
                                ']}' 
                            }
                        ],
                    temperature=0
                    )

        return json.loads(response["choices"][0]["message"]["content"])


if __name__ == "__main__":
    # Example of an OpenAI ChatCompletion request
    # https://platform.openai.com/docs/guides/chat

    # record the time before the request is sent
    start_time = time.time()
    
    message_assembly = []
    
    system_prompt = []

    openai.api_key_path = Path("./api_key")

    dungeon = Dungeon("The Grand Palandatair of Old Sinhai")
    dungeon.display()

    rooms = []
    for r in dungeon.rooms:

        print("\n")
        new_room = Room(r['name'], r['connected_to'], dungeon)
        new_room.display()

        rooms.append(rooms)
