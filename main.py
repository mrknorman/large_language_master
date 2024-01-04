# Built-In Libraries:
import argparse
import json
import pickle
from dataclasses import dataclass
from pathlib import Path 
import re

# External libraries:
import numpy as np
from openai import OpenAI

client = OpenAI(api_key=open('./api_key', 'r').read())

MODEL = "gpt-4-1106-preview"
TEMP = 0.7
from tqdm import tqdm

# Internal Libraries:
import prompts
import commands
import audio

# Remember traps and secret levers

# Trapped       = will activate on interaction
# Discoverable  = can investigate to reveal other elements (roll investigate)
# Informational = can investigate to obtain information (roll investigate + history/religion/arcana/nature/survival)
# Interactable  = can interact to change state of the room (roll intelligence/strength/dex)
# Traversable   = can use to move around the room, i.e stairs, elevators.
# Exit          = can be used to leave room

def roll20():
    return np.random.randint(1, 21)

def find_nearest_lower_np(arr, num):
    arr = np.array(arr)
    filtered_arr = arr[arr <= num]
    if filtered_arr.size > 0:
        return filtered_arr.max()
    else:
        return None

@dataclass
class Player():
    strength : int = 10
    dexterity : int = 100
    constitution : int = 10
    inteligence : int = 12
    wisdom : int = 10
    charisma : int = 10

    perception : int = wisdom
    perception_mod : int = ((perception - 10) // 2)

    lockpick : int = dexterity
    lockpick_mod : int = ((dexterity - 10) // 2)

    passive_perception : int = perception

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

#class Area:


class Room:

    structure  = None
    characters = None

    portal_dict = None
    item_dict = None

    discovered_items = None
    discovered_portals = None

    planned = None
    perceived = None

    perception_roll = 0
    times_visited = 0
    unexplored = True

    def __init__(self, name, room_dict, dungeon):

        self.name         = name
        self.connected_to = room_dict["connected_to"]
        self.has_entrance = room_dict["has_entrance"]

        self.discovered_items = {}
        self.perception_roll = 0
        self.containing_dungeon = dungeon

        if self.portal_dict is None:
            self.portal_dict = {}

        self.discovered_items = {}
        self.discovered_portals = {}

        self.get_portals()

        if self.planned is None:
            plan = self.plan()
            self.ingest(plan)
            self.planned = True
            self.containing_dungeon.save()

    def get_portals(self):
        for key, value in self.containing_dungeon.portals.items():
            if (value.connection_a == self.name):
                self.portal_dict[key] = value
            elif (value.connection_b == self.name):
                self.portal_dict[key] = value

    def ingest(self, room_data):
        """Ingest room data from dictionary format."""
        self.purpose  = room_data.get('purpose', "")
        self.flavour  = room_data.get('flavour', "")
        self.secrets  = room_data.get('secrets', "")
        self.story    = room_data.get('story', "")
        self.effect   = room_data.get('effect', "")
        self.perceptables = room_data.get('perception_text', "")
        self.investigables = room_data.get('investigation_text', "")

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
        return prompts.request_response(
            prompts.room(self),
            MODEL,
            TEMP,
        )

    def plan_items(self):
        if self.item_dict is None:
            
            self.item_dict = prompts.request_response(
                prompts.room_items(self),
                MODEL,
                TEMP,
            )
            self.containing_dungeon.save()

    def generate_item(self):
        pass

    def expand_portals(self):
        for value in self.portal_dict.values():
            value.expand()

    def enter(self, player, entrance = None):
        try:
            audio.read_text(self.flavour[str(self.times_visited)])
        except:
            audio.read_text(list(sorted(self.flavour).values())[-1])
        
        self.times_visited += 1

        if self.unexplored == True:
            print("Generating item plan...")
            self.plan_items()
            print("Complete.")

            print("Expanding portals...")
            self.expand_portals()
            print("Complete.")

        if self.discovered_portals is None:
            self.discovered_portals = {}
        
        if self.discovered_items is None:
            self.discovered_items = {}

        if entrance is not None:
            self.discovered_portals[entrance.name] = entrance

        for name, value in self.item_dict.items():
            if (value["visibility"] <= player.passive_perception):
                self.discovered_items[name] = value

        for name, value in self.portal_dict.items():
            if (value.visibility[self.name] <= player.passive_perception):
                self.discovered_portals[name] = value

        if self.unexplored == True:

            if len(self.discovered_portals) > 1 and entrance is not None:
                audio.read_text("On first entrance you note several exits to the room, including the passage you entered through, these are:")
                for index, name in enumerate(sorted(self.discovered_portals)):
                    audio.read_text(f"{index}. {name}") 
            else:
                audio.read_text("There do not seem to be any further exits to the room, perhaps closer investigation would reveal a path forward, perhaps not.")

            if len(self.discovered_items) > 0 or entrance is None:
                if len(self.discovered_portals) > 1:
                    audio.read_text("You also note some items of interest:")
                else:
                    audio.read_text("Despite this, you note some items of interest:")

                for index, name in enumerate(sorted(self.discovered_items)):
                    audio.read_text(f"{index}. {name}") 
            
            self.unexplored = False

    def observe(self, player):

        if (self.perception_roll > 0):
            print("You have already observed this room!")
            return

        self.perception_roll = roll20() 
        print(f"You rolled a {self.perception_roll} + {player.perception_mod} perception check.")

        self.perception_roll += player.perception_mod

        if self.perceived is None:
            self.perceived = {}

        for name, value in self.perceptables.items():
            if (int(name) <= self.perception_roll):
                self.perceived[int(name)] = value

        for difficulty in sorted(self.perceived):
            value = self.perceived[difficulty]
            audio.read_text(value)
        
        for name, value in self.item_dict.items():
            if name not in self.discovered_items.keys():
                if (value["visibility"] <= self.perception_roll ):
                    self.discovered_items[name] = value
                    audio.read_text(f"You discovered: {name}!")

        for name, value in self.portal_dict.items():
            if name not in self.discovered_portals.keys():
                if (value.visibility[self.name] <= self.perception_roll):
                    self.discovered_portals[name] = value
                    audio.read_text(f"You discovered: {name}!")

    def investigate(self, player):

        if (self.investigate_roll > 0):
            print("You have already observed this room!")
            return

        self.investigate_roll = roll20() 
        print(f"You rolled a {self.perception_roll} + {player.perception_mod} perception check.")

        self.investigate_roll += player.perception_mod

        if self.perceived is None:
            self.perceived = {}

        for name, value in self.perceptables.items():
            if (int(name) <= self.perception_roll ):
                self.perceived[int(name)] = value

        for difficulty in sorted(self.perceived):
            value = self.perceived[difficulty]
            audio.read_text(value)
        
        for name, value in self.item_dict.items():
            if name not in self.discovered_items.keys():
                if (value["visibility"] <= self.perception_roll ):
                    self.discovered_items[name] = value
                    audio.read_text(f"You discovered: {name}!")

        for name, value in self.portal_dict.items():
            if name not in self.discovered_portals.keys():
                if (value.visibility <= self.perception_roll):
                    self.discovered_portals[name] = value
                    audio.read_text(f"You discovered: {name}!")

    def listAll(self):
        self.listItems()
        self.listEgress()

    def listItems(self):
        print("Discovered Items:")
        sorted_items = sorted(self.discovered_items.items())
        for index, (name, value) in enumerate(sorted_items): 
            print(f"{index}. {name}")

    def listEgress(self):
        print("Discovered Entrances/Exits:")
        sorted_egress = sorted(self.discovered_portals.items())
        for index, (name, value) in enumerate(sorted_egress): 
            print(f"{index}. {name}")
    
    def getItemByIndex(self, index):
        """Return the item at the specified index."""
        sorted_items = sorted(self.discovered_items.items())
        if 0 <= index < len(sorted_items):
            item_name, item_value = sorted_items[index]
            return item_value
        else:
            print("No item of that name is known.")
            return None

    def getEgressByIndex(self, index):
        """Return the egress point at the specified index."""
        sorted_egress = sorted(self.discovered_portals.items())
        if 0 <= index < len(sorted_egress):
            egress_name, egress_value = sorted_egress[index]
            return egress_name, egress_value
        else:
            print("No exit/entrance of that name is known.")
            return None, None
    
    def reset(self):
        self.perceived = None
        self.perception_roll = 0
        self.unexplored = True
        self.discovered_items = None
        self.discovered_portals = None
        self.times_visited = 0
        
class Dungeon:

    def __init__(self, name=None):
        self.name = name
        self.path = Path(f"./dungeons/{to_snake_case(name)}")

        plan = self.plan(name)
        self.ingest(plan)
        self.check_connections()
        self.generate_portals()
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

        return prompts.request_response(
            prompts.dungeon(name, 15, 20),
            MODEL,
            TEMP,
        )

    def generate_portals(self):

        self.portal_pairs = self.get_connected_pairs()
        self.portal_plan = prompts.request_response(
            prompts.plan_portal(self),
            MODEL,
            TEMP,
        )
        self.ingest_portals()

    def ingest_portals(self):

        self.portals = {}
        for key, value in self.portal_plan.items():
            self.portals[key] = Portal(
                name=key,
                description=value["description"],
                hit_points=value["hit_points"],
                conditions=value["conditions"],
                connection_a=list(value["asymmetries"].keys())[0],
                connection_b=list(value["asymmetries"].keys())[1],
                asymmetries=value["asymmetries"],
                containing_dungeon=self
            )

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

    def find_entrances(self):
        self.entrances = []
        for room in self.rooms.values():
            if room.has_entrance == True:
                self.entrances.append(room.name)

    def save(self): 
        with open(self.path, 'wb') as handle:
          pickle.dump(self, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def reset(self):
        for room in self.rooms.values():
            room.reset()

        self.ingest_portals()

        for portal in self.portals.values():
            portal.reset()

@dataclass
class Portal():

    name : str
    description : str
    hit_points : int
    conditions : str

    connection_a : str
    connection_b : str

    asymmetries : dict

    containing_dungeon : Dungeon

    inspected : bool = False
    used : bool = False

    visibility : int = -1
    lock_difficulty : int = -1
    failed_attempts = 0 
    
    is_locked : bool = False
    is_blocked : bool = False
    is_barricaded : bool = False

    lock_damage_mod = 0 
    lock_broken = False
    broken_attempts = 0

    failed_entry_text = None

    pick_attempts = 0

    room_info = {}

    def __post_init__(self):
        self.inital_conditions = self.conditions

    def reset(self):
        self.conditions = self.inital_conditions

    def expand(self):

        self.failed_attempts = 0
                
        self.visibility = {}
        for name, value in self.asymmetries.items():
            self.visibility[name] = value["visibility"]
        if self.conditions == "locked":
            self.is_locked = True
        elif self.conditions == "blocked":
            self.is_blocked = True
        elif self.conditions == "barricaded":
            self.is_barricaded = True

        self.is_passable = not (self.is_locked or self.is_barricaded or self.is_barricaded)

    def inspect(self, room, room_b):

        try:
            if self.failed_entry_text is None:
                pass
        except:
            self.failed_entry_text is None

        if self.failed_entry_text is None:
            
            extra_dict = prompts.request_response(
                prompts.portal_inspect(room, room_b, self),
                MODEL,
                TEMP
            )

            self.flavour_text = extra_dict["flavour_text"]
            self.failed_entry_text = extra_dict["failed_entry_text"]
            self.entry_text = extra_dict["entry_text"]

            self.is_pickable = extra_dict["is_pickable"]
            self.not_pickable_text = extra_dict["not_pickable_text"]
            self.lockpick_results = extra_dict["lockpick_results"]
            self.lock_broken_results = extra_dict["lock_broken_text"]

            self.force_difficulty = extra_dict["force_difficulty"] 
            self.is_trapped = extra_dict["is_trapped"]

            self.inspected = True
        
            self.containing_dungeon.save()

    def pick(self, player):

        if self.lock_broken:
            self.broken_attempts += 1
            try:
                audio.read_text(self.lock_broken_text[str(self.broken_attempts)])
            except:
                audio.read_text(list(sorted(self.lock_broken_text).values())[-1])
        
        elif not self.is_pickable:
            self.pick_attempts += 1

            try:
                audio.read_text(self.not_pickable_text[str(self.pick_attempts)])
            except:
                audio.read_text(list(sorted(self.not_pickable_text).values())[-1])

        else:
            lockpick_roll = roll20()
            print(f"You rolled a {lockpick_roll} + {player.lockpick_mod} + {self.lock_damage_mod} lockpick check.")  
            lockpick_roll += player.lockpick_mod + self.lock_damage_mod

            int_ranges = [int(value) for value in self.lockpick_results]
            
            value = find_nearest_lower_np(int_ranges, lockpick_roll)

            audio.read_text(self.lockpick_results[str(value)]["message"])

            if self.lockpick_results[str(value)]["result"] == "success":
                self.is_locked = False
                if self.conditions == "locked":
                    self.conditions = "unobstructed"
            elif self.lockpick_results[str(value)]["result"] == "damaged":
                self.lock_damage_mod -= 5
            elif self.lockpick_results[str(value)]["result"] == "broken":
                self.lock_damage_mod -= 500
                self.lock_broken = True
                self.is_pickable = False
            elif self.lockpick_results[str(value)]["result"] == "loosened":
                self.lock_damage_mod += 5


def to_snake_case(input_string):
    # Replace non-alphanumeric characters with an underscore
    s = re.sub(r'\W+', '_', input_string)

    # Convert to lowercase
    return s.lower()

def load_or_generate_dungeon(
    name: bool, 
    force_regenerate: bool = False
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
    dungeon_file_name = Path(f"./dungeons/{to_snake_case(name)}")

    if dungeon_file_name.exists() and not force_regenerate:
        with dungeon_file_name.open('rb') as handle:
            dungeon = pickle.load(handle)
    else:
        dungeon = Dungeon(name)
        with dungeon_file_name.open('wb') as handle:
            pickle.dump(dungeon, handle)

    dungeon.reset()
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
    parser.add_argument('--name', type=str, help='Name the dungeon.')

    args = parser.parse_args()
    dungeon = load_or_generate_dungeon(args.name)

    player = Player()
    audio.read_text(f"{dungeon.name}\n{dungeon.flavour}")

    if len(dungeon.entrances) > 1: 
        audio.read_text(f"There are {len(dungeon.entrances)} entrances to the dungeon:\n")
    else:
        audio.read_text(f"There is only one entrance to the dungeon:\n")

    for index, entrance in enumerate(dungeon.entrances):
        audio.read_text(f"{index}. {entrance}")

    audio.read_text("Which entrance would you like to use?")

    choice = int(input("Enter the number:"))
    current_room = dungeon.rooms[dungeon.entrances[choice]]
    current_room.enter(player)

    commands.initialize()
    cli_loop(dungeon, current_room, player)

if __name__ == "__main__":
    main()