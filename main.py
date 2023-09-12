import sys
import openai
import time
from pathlib import Path 
import numpy as np
import json
import ast

import pickle

from dataclasses import dataclass
from tqdm import tqdm
# Remember traps and secret levers

# Trapped       = will activate on interaction
# Discoverable  = can investigate to reveal other elements (roll investigate)
# Informational = can investigate to obtain information (roll investigate + history/religion/arcana/nature/survival)
# Interactable  = can interact to change state of the room (roll intelligence/strength/dex)
# Traversable   = can use to move around the room, i.e stairs, elevators.
# Exit          = can be used to leave room

"""
    {{
        "item_name":{{
            "purpose": "in universe purpose of the item",
            "flavour": "a decription of the item for the players",
            "secrets": "any secrets the room may hold",
            "story": "how the object adds to the room's story"
        }}

    }}
"""

def roll20():
    return np.random.randint(1, 21)

@dataclass
class Player():
    strength : int = 10
    dexterity : int = 10
    constitution : int = 10
    inteligence : int = 12
    wisdom : int = 10
    charisma : int = 10

    perception : int = inteligence
    perception_mod : int = ((perception - 10) // 2)

    passive_perception : int = perception

def check_response(response, system_prompt, prompt):
    try:
        response = json.loads(response["choices"][0]["message"]["content"])
    except exception as e:
        error_prompt = \
            item_string + f"Your previous response had this error: {e}, please try again."

        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
                messages=[
                            {
                                'role':'system', 
                                'content': system_prompt
                                
                            },
                            {
                                'role':'user', 
                                'content': prompt 
                            }
                        ],
                    temperature=0.5
                    )

    return response

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

    structure  = []
    characters = []

    egress_dict = {}
    item_dict = {}

    discovered_items = {}
    discovered_egress = {}

    perception_roll = 0

    def __init__(self, name, room_dict, dungeon):

        self.name         = name
        self.connected_to = room_dict["connected_to"]
        self.has_entrance = room_dict["has_entrance"]

        self.containing_dungeon = dungeon
        self.item_dict = {}
        self.egress_dict = {}

        self.discovered_items = {}
        self.discovered_egress = {}

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

        room_prompt = \
            f"""
                You are designing a new room for your adventuring party to explore.
                Here is a description of the dungeon that contains the room:
                
                Name: {dungeon.name}
                Purpose: {dungeon.purpose}
                Flavour: {dungeon.flavour}
                Secrets: {dungeon.secrets}
                Story: {dungeon.story}
                Effect: {dungeon.effect}

                The player will only see the name and the flavour text. The others are notes for the dungeon ai 
                to use when generating the room\'s details, to ensure consistency.

                This room is called {self.name} and is connected to: {self.connected_to}.
                
                Respond with a brief outline in the following format imitating a python dictionary:
                {{
                "purpose": "the in universe purpose of the room",
                "flavour": "a rich decription of the room for the players",
                "secrets": "any secrets the room may hold",
                "story": "the underlying story you want the room to tell",
                "effect": "the effect you imagine this room will have on the players stories"
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
                                        'content': room_prompt
                                    }
                                ],
                            temperature=0.5
                            )



        return check_response(response, system_prompt, room_prompt)

    def create_items(self):

        dungeon = self.containing_dungeon

        item_prompt = \
            f"""
                You are designing a new room for your adventuring party to explore.
                Here is a description of the dungeon that contains the room:
                
                Name:{dungeon.name}
                Purpose:{dungeon.purpose}
                Flavour:{dungeon.flavour}
                Secrets:{dungeon.secrets}
                Story:{dungeon.story}
                Effect:{dungeon.effect}

                This room is called {self.name} and is connected to: {self.connected_to}.
                Here is a description of the room:

                Purpose:{self.purpose}
                Flavour:{self.flavour}
                Secrets:{self.secrets}
                Story:{self.story}
                Effect:{self.effect}

                I would like you to respond with a list of items in the room. Do not include doors
                or other entranceways, or flooring or wall materials. Give your response in the following 
                json format:
                {{
                    "Item Name":{{
                        "purpose": str #in universe purpose of the item,
                        "story": str #how the object adds to the room's story,
                        "visibility:" int #see below
                    }}
                }}

                Given that visibility is mesured out of 30 where:
                1: Impossible to miss, 5: Very easy to see, 10: Easy to see, 15: Could easily be overlooked,
                20: Hard to see, 25: Very hard to see, 30: Almost impossible to see.
                Note: visibility can take any value between 1 and 30, not just these examples.
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
                                'content': item_prompt
                            }
                        ],
                    temperature=0.5
                    )

        self.item_dict = check_response(response, system_prompt, item_prompt)

    def create_egress(self):

        dungeon = self.containing_dungeon

        egress_prompt = \
            f"""
                You are designing a new room for your adventuring party to explore.
                Here is a description of the dungeon that contains the room:
                
                Name:{dungeon.name}
                Purpose:{dungeon.purpose}
                Flavour:{dungeon.flavour}
                Secrets:{dungeon.secrets}
                Story:{dungeon.story}
                Effect:{dungeon.effect}

                This room is called {self.name}.
                Here is a description of the room:

                Purpose:{self.purpose}
                Flavour:{self.flavour}
                Secrets:{self.secrets}
                Story:{self.story}
                Effect:{self.effect}

                I would like you to decide on the visibility of the room's egress points.
                This room connects to these rooms: {self.connected_to} each will require an egress entry.
                Come up with a desciptive name for each entrance point that will inform the player of its
                appearence.

                Respond in the following json ready format:
                {{
                    "Descriptive Egress Name":{{
                        "leads_to": str #room this point leads to, use exact name as listed above,
                        "purpose": str #in universe purpose of the entryway,
                        "visibility:" int #see below
                    }}
                }}

                Given that visibility is measured out of 30 where:
                1: Impossible to miss, 5: Very easy to see, 10: Easy to see, 15: Could easily be overlooked,
                20: Hard to see, 25: Very hard to see, 30: Almost impossible to see.
                Note: visibility can take any value between 1 and 30, not just these examples.
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
                                'content': egress_prompt
                            }
                        ],
                    temperature=0.5
                    )

        self.egress_dict = check_response(response, system_prompt, egress_prompt)


    def enter(self, player):
        print(current_room.flavour)

        if (self.item_dict == {}):
            self.create_items()

        if (self.egress_dict == {}):
            self.create_egress()

        for name, value in self.item_dict.items():
            if (value["visibility"] <= player.passive_perception):
                self.discovered_items[name] = value

        for name, value in self.egress_dict.items():
            if (value["visibility"] <= player.passive_perception):
                self.discovered_egress[name] = value

    def observe(self, player):

        if (self.perception_roll > 0):
            print("You have already observed this room!")
            return

        self.perception_roll = roll20() 
        print(f"You rolled a {self.perception_roll} + {player.perception_mod} perception check.")

        self.perception_roll += player.perception_mod

        for name, value in self.item_dict.items():
            if name not in self.discovered_items.keys():
                if (value["visibility"] <= self.perception_roll ):
                    self.discovered_items[name] = value
                    print(f"You discovered: {name}!")

        for name, value in self.egress_dict.items():
            if name not in self.discovered_egress.keys():
                if (value["visibility"] <= self.perception_roll):
                    self.discovered_egress[name] = value
                    print(f"You discovered: {name}!")

    def listAll(self):
        self.listItems()
        self.listEgress()

    def listItems(self):
        print("Discovered Items:")
        for index, (name, value) in enumerate(self.discovered_items.items()): 
            print(f"{index}. {name}")

    def listEgress(self):
        print("Discovered Egress Points:")
        for index, (name, value) in enumerate(self.discovered_egress.items()): 
            print(f"{index}. {name}")

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
        dungeon_prompt = \
            f"""
                You are designing a dungeon called {name} for your adventuring party to explore.

                The details of the rooms will be filled out by you later on, for now focus on the overall plan of 
                the dungeon, the story you'd like it to tell, and how it will affect the player's journey.
                Respond with a brief outline in the following format imitating a python dictionary:
                {{
                    "purpose": "the in universe purpose of the dungeon",
                    "flavour": "a description of the dungeon that players might know before entering",
                    "secrets": "any secrets the dungeon may hold",
                    "story": "the underlying story you want the dungeon to tell",
                    "effect": "the effect you imagine this room will have on the players stories"
                    "rooms": {{
                        "Room 1 Name":
                        {{
                            "connected_to": [ list_of_connecting_rooms ], 
                            "has_entrance": bool, true if room has dungon entrance/exit
                        }},
                    ...
                    }}
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
                                'content': dungeon_prompt
                            }
                        ],
                    temperature=0.5
                    )

        return check_response(response, system_prompt, dungeon_prompt)

    def check_connections(self):  
        for name, value in self.room_dicts.items():
            for connected_name in value["connected_to"]:
                if name not in self.room_dicts[connected_name]["connected_to"]:
                    self.room_dicts[connected_name]["connected_to"].append(name)

    def create_rooms(self):
        self.rooms = {}
        for name, value in tqdm(self.room_dicts.items()):
            self.rooms[name] = Room(name, value, self)

        self.check_connections()

    def find_entrances(self):
        self.entrances = []
        for room in self.rooms.values():
            if room.has_entrance == True:
                self.entrances.append(room.name)

    def save(self): 
        with open('dungeon.pickle', 'wb') as handle:
          pickle.dump(self, handle, protocol=pickle.HIGHEST_PROTOCOL)


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

    #dungeon = Dungeon("The Temple of Glob Blobulon")
    #dungeon.save()

    with open('filename.pickle', 'rb') as handle:
        dungeon = pickle.load(handle)

    player = Player()

    print(f"{dungeon.name}\n {dungeon.flavour}")
    print(f"There are {len(dungeon.entrances)} entrances to the dungeon:\n")
        
    for index, entrance in enumerate(dungeon.entrances):
        print(f"{index}. {entrance}")

    choice = int(input("Which entrance do you want to use? Enter the number:"))

    current_room = dungeon.rooms[dungeon.entrances[choice]]
    current_room.enter(player)

    while True:      
        commands = {
            "list" : {
                "all": current_room.listAll, 
                "items": current_room.listItems, 
                "egress": current_room.listEgress
            }
        }

        command = input("What would you like to do?").split()

        if (command[0] == "list"):
            commands["list"][command[1]]()
        elif (command[0] == "observe"):
            current_room.observe(player)
        elif (command[0] == "enter"):
            current_room = \
                dungeon.rooms[
                    current_room.discovered_egress[" ".join(command[1:])]["leads_to"]
                ]
            current_room.enter(player)
        elif (command[0] == "quit"):
            quit()

        #print(f"There are {len(current_room.connected_to)} exits to this room:\n")
        
        #for index, exit in enumerate(current_room.connected_to):
         #   print(f"{index}. {exit}")

        #current_room = dungeon.rooms[current_room.connected_to[choice]]







