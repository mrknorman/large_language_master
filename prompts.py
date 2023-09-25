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

    This room is called {room_name} and has the following portals: {room_portals}.
    Portal here refers to the architectural feature that allows for traversal, not neccisarily magical, 
    although it could be.

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

    I would like you to respond with a list of items in the room.

    DO NOT: include doors, portals, or other entranceways, flooring or wall materials, 
    or any animate animals, creatures, or intelligent agents. 

    Give your response in the following json format:
    {{
        "Item Name":{{
            "purpose": str,  # in uni verse purpose of the item
            "story": str,  # how the object adds to the room's story
            "visibility": int  # see below
        }}
    }}

    Given that visibility is measured out of 30 where:
    1: Impossible to miss, 5: Very easy to see, 10: Easy to see, 15: Could easily be overlooked,
    20: Hard to see, 25: Very hard to see, 30: Almost impossible to see.
    Note: visibility can take any value between 1 and 30, not just these examples.
"""

PLAN_PORTAL = \
    """
        You are designing dungeon for your adventuring party to explore.
        Here is a description of the dungeon:

        Portal here refers to the architectural feature that allows for traversal,
        not neccisarily magical, although it could be.
        
        Name:{dungeon_name}
        Purpose:{dungeon_purpose}
        Flavour:{dungeon_flavour}
        Secrets:{dungeon_secrets}
        Story:{dungeon_story}
        Effect:{dungeon_effect}

        I have generated a list of the connections between rooms present in this dungeon, these
        connections can be doors, tunnels, ladders, staircases or any other kind of connections.
        I would like you to come up with a desciptive name for each of these portal points and
        a brief description for the dungeon master to use later when describing the portal, to
        ensure that the description is consistent from both directions. If the portal is
        particularly asymetric, make a note of that in the asymmetries feils

        Here is the list of connected pairs {portal_pairs}.

        Respond in the following json ready format, in the same order as portal pairs appears
        {{
            "descriptive_portal_name":
            {{
                "description: str, # aesthetic notes
                "asymmetries" : dict = 
                {{
                    "room_1_name" : str {{
                        "description" : str, # description of this rooms side of the portal, empty if symetric
                        "visibility" : int #visibility of this room's side of the poral, see below,
                    }} : dict,
                    "room_2_name" : str {{
                        # as with first room name
                    }} : dict,
                }}
                "conditions" : str # one of [unobstructed, locked, blocked or barricaded] and no more
            }}
        }}

        Given that visibility is measured out of 30 where:
        1: Impossible to miss, 5: Very easy to see, 10: Easy to see, 15: Could easily be overlooked,
        20: Hard to see, 25: Very hard to see, 30: Almost impossible to see.
        Note: visibility can take any value between 1 and 30, not just these examples.
    """   

PORTAL = \
    """
        You are designing an portal point between to areas of your dungeon.
        Here is a description of the dungeon that contains the portal:

        Portal here refers to the architectural feature that allows for traversal,
        not neccisarily magical, although it could be.
        
        Name:{dungeon_name}
        Purpose:{dungeon_purpose}
        Flavour:{dungeon_flavour}
        Secrets:{dungeon_secrets}
        Story:{dungeon_story}
        Effect:{dungeon_effect}

        This room is called {room_name}.
        Here is a description of the room containing the portal:

        Purpose:{room_purpose}
        Flavour:{room_flavour}
        Secrets:{room_secrets}
        Story:{room_story}
        Effect:{room_effect}

        Here is the overall outline of the portal:

        name : {portal_name}
        description : {portal_description}
        conditions : {portal_conditions}
        asymmetries : {portal_asymmetry}

        I would like you to decide on the visibility and hit points of this portal.

        Respond in the following json ready format:
        {{
            "visibility:" int #see below,
            "hit_points:" int, #door health where 10 is an average wooden door
        }}


        }}
    """   

PORTAL_INSPECT = """
        You are designing an portal point between to areas of your dungeon.
        Here is a description of the dungeon that contains the portal:

        Portal here refers to the architectural feature that allows for traversal,
        not neccisarily magical, although it could be.
        
        Name:{dungeon_name}
        Purpose:{dungeon_purpose}
        Flavour:{dungeon_flavour}
        Secrets:{dungeon_secrets}
        Story:{dungeon_story}
        Effect:{dungeon_effect}

        This room is called {room_name}.
        Here is a description of the room containing the portal:

        Purpose:{room_purpose}
        Flavour:{room_flavour}
        Secrets:{room_secrets}
        Story:{room_story}
        Effect:{room_effect}

        This is the room the portal leads too {room_b_name}:

        Purpose:{room_b_purpose}
        Flavour:{room_b_flavour}
        Secrets:{room_b_secrets}
        Story:{room_b_story}
        Effect:{room_b_effect}

        Here is the overall outline of the portal:

        name : {portal_name}
        description : {portal_description}
        conditions : {portal_conditions}
        asymmetries : {portal_asymmetry}
        hit_pints : {portal_hit_points}
        visibility : {portal_visibility} # Assume the door has been discovered,
        although some addition about its difficulty in detection might be added 
        to the flavour for very high visibilities 15-30 (high visiblity equals harder to see)

        I would like to to design some more detailed description of the
        portal. Respond in the following json ready format:

        {{
            "flavour_text" : str, #paragraph to give to the player, adding to 
            the atmosphere and perhaps revealing something about the story.
            "failed_entry_text" : str, # given the portals condition, this should be text to 
            show the player on a failed traversal attempt
            "lock_difficulty": int, #see 1. below
            "force_difficulty": int, #see 2. below
            "is_trapped": bool, #is the door trapped
            "entry_text": str, # atmospheric text to show the player on passing through
        }}

        1. Given that lock difficulty is a mesure of lock picking difficulty where:
        1: Unlocks instantly, 5: Very easy to unlock, 10: Easy to unlock, 15: Average lock difficulty,
        20: Hard to unlock, 25: Very hard to unlock, 30: Almost impossible to unlock.
        Note: lock_difficulty can take any value between 1 and 30, not just these examples.

        2. If the door is baracaded or locked, this is a mesure of the diffculty to brute 
        force it open, given:
        1: Easy as tissue paper to open, 5: Very easy to force, 10: Easy to force, 
        15: Average door strength, 20: Strong Door, 25: Very stron door, 30: Almost impregnable door.
        Note: force_difficulty can take any value between 1 and 30, not just these examples.

        """

"""
"investigation_text" : dict = {{ 
    # A dictionary showing inteligence roll required and revealed information
    # this should be information revealed by thoughtfull consideration not
    # perception
    roll_required (out of 20) : str #information revealed,
    higher_roll_required : #more infomation revealed,
    # more or less information as desired, could be none
}},
"perception_text": dict = {{
    # A dictionary showing perception roll required and revealed information
    # this should be information revealed by close inspection not
    # inteligent investigation
    roll_required (int) (out of 20) : str #information revealed,
    higher_roll_required (int) : str #more infomation revealed,
    # more or less information as desired, could be none
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
    room_portals = [
        portal.name + ": " + portal.description + " " + portal.asymmetries[room.name] for portal in room.portal_dict.values()
    ]

    return ROOM.format(
        dungeon_name=dungeon.name,
        dungeon_purpose=dungeon.purpose,
        dungeon_flavour=dungeon.flavour,
        dungeon_secrets=dungeon.secrets,
        dungeon_story=dungeon.story,
        dungeon_effect=dungeon.effect,
        room_name=room.name,
        room_portals=room_portals
    )

def plan_portal(dungeon):

    return PLAN_PORTAL.format(
        dungeon_name=dungeon.name,
        dungeon_purpose=dungeon.purpose,
        dungeon_flavour=dungeon.flavour,
        dungeon_secrets=dungeon.secrets,
        dungeon_story=dungeon.story,
        dungeon_effect=dungeon.effect,
        portal_pairs=dungeon.portal_pairs
    )

def portal(room, portal):

    dungeon = room.containing_dungeon
    return PORTAL.format(
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
        room_effect=room.effect,
        portal_name = portal.name,
        portal_description = portal.description,
        portal_conditions = portal.conditions,
        portal_asymmetry = portal.asymmetries[room.name]
    )

def portal_inspect(room, room_b, portal):

    dungeon = room.containing_dungeon
    return PORTAL_INSPECT.format(
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
        room_effect=room.effect,
        room_b_name=room_b.name,
        room_b_purpose=room_b.purpose,
        room_b_flavour=room_b.flavour,
        room_b_secrets=room_b.secrets,
        room_b_story=room_b.story,
        room_b_effect=room_b.effect,
        portal_name = portal.name,
        portal_description = portal.description,
        portal_conditions = portal.conditions,
        portal_asymmetry = portal.asymmetries[room.name],
        portal_hit_points = portal.hit_points,
        portal_visibility = portal.visibility
    )
