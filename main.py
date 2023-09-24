# Built-In Libraries:
import sys
import time
import argparse
import json
import ast
import pickle
from dataclasses import dataclass
from pathlib import Path 

# External libraries:
import numpy as np
import openai
from tqdm import tqdm

# Internal Libraries:
import prompts
import commands

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

def check_response(response, prompt):
    try:
        response = json.loads(response["choices"][0]["message"]["content"])
    except Exception as e:
        error_prompt = \
            f"Your previous response: [{response}] to this prompt: [{prompt}], had this error: [{e}], please try again." \
            "Respond only in a format that can be read as a JSON, anything else will result in an error."

        print(f"Error, trying again: {e}")

        response = openai.ChatCompletion.create(
            model='gpt-4-0613',
                messages=[
                            {
                                'role':'system', 
                                'content': prompts.system()
                                
                            },
                            {
                                'role':'user', 
                                'content': error_prompt
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

        plan = self.plan()
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

    def plan(self):
        room_prompt = prompts.room(self)

        response = openai.ChatCompletion.create(
                    model='gpt-4-0613',
                        messages=[
                                    {
                                        'role':'system', 
                                        'content': prompts.system()
                                        
                                    },
                                    {
                                        'role':'user', 
                                        'content': room_prompt
                                    }
                                ],
                            temperature=0.5
                            )

        return check_response(response, room_prompt)

    def plan_items(self):

        room_items_prompt = prompts.room_items(self)
        response = openai.ChatCompletion.create(
            model='gpt-4-0613',
                messages=[
                            {
                                'role':'system', 
                                'content': prompts.system()
                                
                            },
                            {
                                'role':'user', 
                                'content': room_items_prompt
                            }
                        ],
                    temperature=0.5
                    )

        self.item_dict = check_response(response, room_items_prompt)


    def generate_item(self):
        pass

    def plan_egress(self):

        egress_prompt = prompts.egress(self)

        print(egress_prompt)

        response = openai.ChatCompletion.create(
            model='gpt-4-0613',
                messages=[
                            {
                                'role':'system', 
                                'content': prompts.system()
                                
                            },
                            {
                                'role':'user', 
                                'content': egress_prompt
                            }
                        ],
                    temperature=0.5
                    )

        self.egress_dict = check_response(response, egress_prompt)

    def enter(self, player):
        print(self.flavour)

        if (self.item_dict == {}):
            print("Generating item plan...")
            self.plan_items()
            print("Complete.")

        if (self.egress_dict == {}):
            print("Generating egress plan...")
            self.plan_egress()
            print("Complete.")

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
        plan = self.plan(name)
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

    def plan(self, name):

        dungeon_prompt = prompts.dungeon(name)
        response = openai.ChatCompletion.create(
            model='gpt-4-0613',
                messages=[
                            {
                                'role':'system', 
                                'content': prompts.system()
                            },
                            {
                                'role':'user', 
                                'content': dungeon_prompt
                            }
                        ],
                    temperature=0.5
                    )

        return check_response(response, dungeon_prompt)

    def check_connections(self):  

        for name, value in self.room_dicts.items():
            for connected_name in value["connected_to"]:
                if name not in self.room_dicts[connected_name]["connected_to"]:
                    self.room_dicts[connected_name]["connected_to"].append(name)

    def get_connected_pairs(self):
        """Returns a set containing all pairs of connected rooms."""
        connected_pairs = set()

        for room_name, room_data in self.room_dicts.items():
            for connected_room in room_data["connected_to"]:
                # Creating a sorted tuple to ensure uniqueness (e.g., (A, B) == (B, A))
                pair = tuple(sorted([room_name, connected_room]))
                connected_pairs.add(pair)

        return connected_pairs

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

def load_or_generate_dungeon(
    regenerate: bool, 
    filename: Path
    ) -> Dungeon:

    """
    Load or regenerate the dungeon based on the flag provided.

    Parameters
    ----------
    regenerate : bool
        Flag to regenerate the dungeon.
    filename : Path
        Path to the file where the dungeon is stored.

    Returns
    -------
    Dungeon
        The loaded or regenerated dungeon.
    """
    if not regenerate and filename.exists():
        with filename.open('rb') as handle:
            dungeon = pickle.load(handle)
    else:
        dungeon = Dungeon("The Temple of Old Ricky Bones")
        with filename.open('wb') as handle:
            pickle.dump(dungeon, handle)
    return dungeon

def cli_loop(dungeon, current_room, player):
    """Encapsulated command-line interaction loop."""

    commands_ = commands.initialize()
    while True:
        command_input = input("What would you like to do?")
        command_parts = command_input.split()
        command_name = command_parts[0]

        if command_name in commands_:
            command = commands_[command_name]
            current_room = command.execute(command_parts[1:], dungeon, current_room, player) or current_room
        elif command_name == "help":
            for cmd in commands_.values():
                print(f"{cmd.name}: {cmd.description}")
        elif command_name == "quit":
            break
        else:
            print("Invalid command. Type 'help' for a list of available commands.")

def main():

    parser = argparse.ArgumentParser(description="Dungeon master's main game loop.")
    parser.add_argument('--regenerate', action='store_true', help='Force regeneration of the dungeon.')
    args = parser.parse_args()

    openai.api_key_path = Path("./api_key")
    dungeon_filename = Path("dungeon.pickle")
    dungeon = load_or_generate_dungeon(args.regenerate, dungeon_filename)

    print(dungeon.get_connected_pairs())
    quit()

    player = Player()
    print(f"{dungeon.name}\n{dungeon.flavour}")
    print(f"There are {len(dungeon.entrances)} entrances to the dungeon:\n")

    for index, entrance in enumerate(dungeon.entrances):
        print(f"{index}. {entrance}")

    choice = int(input("Which entrance do you want to use? Enter the number:"))
    current_room = dungeon.rooms[dungeon.entrances[choice]]
    current_room.enter(player)

    commands.initialize()
    cli_loop(dungeon, current_room, player)

if __name__ == "__main__":
    main()







