SYSTEM = \
f"""
    You are an expert dungeon master with many years of experience and a
    creative story-driven approach to constructing adventures. Your primary goal is to
    create a fun and engaging experience for all your players. Your responses will be 
    placed into a framework so you must generate outputs which are as close to the format 
    described as possible.
"""

DUNGEON = """
    You are designing a dungeon called {name} for your adventuring party to explore.

    The details of the rooms will be filled out by you later on, for now focus on the overall plan of 
    the dungeon, the story you'd like it to tell, and how it will affect the player's journey. Ensure that
    there is enough information in the plan for another instance of you to create a more detailed story
    when prompted for specific information.

    Respond with a brief outline in the following json format imitating a python dictionary:
    {{
        "purpose" : str # the in universe purpose of the dungeon,
        "flavour" : str # a description of the dungeon that players might know before entering,
        "secrets" : str # any secrets the dungeon may hold,
        "story" : str # the underlying story you want the dungeon to tell,
        "effect" : str # the effect you imagine this room will have on the players stories,
        "rooms" : {{
            "Room 1 Name":
            {{
                "connected_to" : List[str] # list of connecting rooms, 
                "has_entrance": bool # true if room has dungon entrance/exit
            }},
        ...
        }}
    }}
    """

ROOM = """
    You are designing a new room for your adventuring party to explore.
    Here is a description of the dungeon that contains the room:

    Name: {dungeon_name}
    Purpose: {dungeon_purpose}
    Flavour: {dungeon_flavour}
    Secrets: {dungeon_secrets}
    Story: {dungeon_story}
    Effect: {dungeon_effect}

    The player will only see the name and the flavour text. The others are notes for the dungeon ai 
    to use when generating the room's details, to ensure consistency.

    This room is called {room_name} and is connected to: {room_connected_to}.

    Respond with a brief outline in the following format imitating a python dictionary:
    {{
        "purpose": "the in universe purpose of the room",
        "flavour": "a rich description of the room for the players",
        "secrets": "any secrets the room may hold",
        "story": "the underlying story you want the room to tell",
        "effect": "the effect you imagine this room will have on the players' stories"
    }}
"""

ROOM_ITEMS = """
    You are designing a new room for your adventuring party to explore.
    Here is a description of the dungeon that contains the room:

    Name:{dungeon_name}
    Purpose:{dungeon_purpose}
    Flavour:{dungeon_flavour}
    Secrets:{dungeon_secrets}
    Story:{dungeon_story}
    Effect:{dungeon_effect}

    This room is called {room_name} and is connected to: [{room_connected_to}].
    Here is a description of the room:

    Purpose:{room_purpose}
    Flavour:{room_flavour}
    Secrets:{room_secrets}
    Story:{room_story}
    Effect:{room_effect}

    I would like you to respond with a list of items in the room. Do not include doors
    or other entranceways, flooring or wall materials, or any animate animals, creatures, or
    intelligent agents. Give your response in the following json format:
    {{
        "Item Name":{{
            "purpose": str,  # in universe purpose of the item
            "story": str,  # how the object adds to the room's story
            "visibility": int  # see below
        }}
    }}

    Given that visibility is measured out of 30 where:
    1: Impossible to miss, 5: Very easy to see, 10: Easy to see, 15: Could easily be overlooked,
    20: Hard to see, 25: Very hard to see, 30: Almost impossible to see.
    Note: visibility can take any value between 1 and 30, not just these examples.
"""

EGRESS = \
    """
        You are designing a new room for your adventuring party to explore.
        Here is a description of the dungeon that contains the room:
        
        Name:{dungeon_name}
        Purpose:{dungeon_purpose}
        Flavour:{dungeon_flavour}
        Secrets:{dungeon_secrets}
        Story:{dungeon_story}
        Effect:{dungeon_effect}

        This room is called {room_name}.
        Here is a description of the room:

        Purpose:{room_purpose}
        Flavour:{room_flavour}
        Secrets:{room_secrets}
        Story:{room_story}
        Effect:{room_effect}

        I would like you to decide on the visibility of the room's egress points.
        This room connects to these rooms: {room_connected_to} each will require an egress entry.
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

def system():
    return SYSTEM

def dungeon(name):

    return DUNGEON.format(
        name=name
        )

def room_items(room):

    dungeon = room.containing_dungeon

    return ROOM_ITEMS.format(
        dungeon_name=dungeon.name,
        dungeon_purpose=dungeon.purpose,
        dungeon_flavour=dungeon.flavour,
        dungeon_secrets=dungeon.secrets,
        dungeon_story=dungeon.story,
        dungeon_effect=dungeon.effect,
        room_name=room.name,
        room_connected_to=", ".join(room.connected_to),
        room_purpose=room.purpose,
        room_flavour=room.flavour,
        room_secrets=room.secrets,
        room_story=room.story,
        room_effect=room.effect
    )

def room(room):

    dungeon = room.containing_dungeon
    return ROOM.format(
        dungeon_name=dungeon.name,
        dungeon_purpose=dungeon.purpose,
        dungeon_flavour=dungeon.flavour,
        dungeon_secrets=dungeon.secrets,
        dungeon_story=dungeon.story,
        dungeon_effect=dungeon.effect,
        room_name=room.name,
        room_connected_to=", ".join(room.connected_to)
    )

def egress(room):

    dungeon = room.containing_dungeon
    return EGRESS.format(
        dungeon_name=dungeon.name,
        dungeon_purpose=dungeon.purpose,
        dungeon_flavour=dungeon.flavour,
        dungeon_secrets=dungeon.secrets,
        dungeon_story=dungeon.story,
        dungeon_effect=dungeon.effect,
        room_name=room.name,
        room_connected_to=", ".join(room.connected_to),
        room_purpose=room.purpose,
        room_flavour=room.flavour,
        room_secrets=room.secrets,
        room_story=room.story,
        room_effect=room.effect
    )
