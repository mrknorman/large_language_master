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

    def __init__(self, room_dict, dungeon):

        self.name         = room_dict["name"]
        self.connected_to = room_dict["connected_to"]
        self.has_entrance = room_dict["has_entrance"]

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

                The rooms is called {self.name} and is connected to {self.connected_to}.
                
                Respond with a brief outline in the following format imitating a python dictionary:
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
                                        'content': system_prompt
                                        
                                    },
                                    {
                                        'role':'user', 
                                        'content': room_string 
                                    }
                                ],
                            temperature=0.5
                            )

        return json.loads(response["choices"][0]["message"]["content"])

    def enter(self):
        print(self.flavour)

class Dungeon:

    def __init__(self, name=None):
        self.name = name
        plan = self.create_dungeon_plan(name)
        self.ingest(plan)
        self.create_rooms()
        self.find_entrances()

    def ingest(self, data):
        """Ingest room data from dictionary format."""
        self.purpose    = data.get('purpose', "")
        self.flavour    = data.get('flavour', "")
        self.secrets    = data.get('secrets', "")
        self.story      = data.get('story', "")
        self.effect     = data.get('effect', "")
        self.room_dicts = data.get('rooms', "")

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

        dungeon_string = \
            f"""
                You are designing a dungeon called {name} for your adventuring party to explore.

                The details of the rooms will be filled out by you later on, for now focus on the overall plan of 
                the dungeon, the story you\'d like it to tell, and how it will affect the player\'s journey.'
                Respond with a brief outline in the following format imitating a python dictionary:
                {{
                \"purpose\": \"the in universe purpose of the dungeon\", \n
                \"flavour\": \"a description of the dungeon that players might know before entering\"
                \"secrets\": \"any secrets the dungeon may hold\"
                \"story\": \"the underlying story you want the dungeon to tell.\"
                \"effect\": \"the effect you imagine this room will have on the players stories\"
                \"rooms\": [
                    {{\"name\": room_name, \"connected_to\": [ list_of_connecting_rooms ], 
                        \"has_entrance\": bool, true if room has dungon entrance/exit}}
                    ...
                    ]
                }}
            """

        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
                messages=[
                            {
                                'role':'system', 
                                'content': system_prompt
                            },
                            {
                                'role':'user', 
                                'content': dungeon_string
                            }
                        ],
                    temperature=0.5
                    )

        return json.loads(response["choices"][0]["message"]["content"])

    def check_connections(self, name):  
        for room_dict in self.room_dicts:
            for connected_dict in self.room_dicts.connected_to:
                pass # work on this at some point

    def create_rooms(self):
        self.rooms = {}
        for room_dict in self.room_dicts:
            self.rooms[room_dict["name"]] = Room(room_dict, self)

    def find_entrances(self):
        self.entrances = []
        for room in self.rooms.values():
            if room.has_entrance == True:
                self.entrances.append(room.name)

if __name__ == "__main__":
    # Example of an OpenAI ChatCompletion request
    # https://platform.openai.com/docs/guides/chat

    system_prompt = \
    f"""
        You are an expert dungeon master with many years of experience and a
        creative story-driven approach to constructing adventures. Your primary goal is to
        create a fun and engaging experience for all your players. Your responses will be 
        placed into a framework so try to generate outputs which are as close to the format 
        described as possible.
    """

    message_assembly = []
    
    openai.api_key_path = Path("./api_key")

    dungeon = Dungeon("The Tomb Urmouth Stormfather")

    print(f"{dungeon.name}\n {dungeon.flavour}")

    print(f"There are {len(dungeon.entrances)} entrances to the dungeon:\n")
        
    for index, entrance in enumerate(dungeon.entrances):
        print(f"{index}. {entrance}")

    choice = int(input("Which entrance do you want to use? Enter the number:"))

    current_room = dungeon.rooms[dungeon.entrances[choice]]

    while True:
        current_room.enter()

        print(f"There are {len(current_room.connected_to)} exits to this room:\n")
        
        for index, exit in enumerate(current_room.connected_to):
            print(f"{index}. {exit}")

        choice = int(input("Which room do you want to enter? Enter the number:"))

        current_room = dungeon.rooms[current_room.connected_to[choice]]







