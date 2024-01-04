

from openai import OpenAI
client = OpenAI(api_key=open('./api_key', 'r').read())
import json
import random

SYSTEM = \
f"""
    As an expert dungeon master with extensive experience, your expertise lies in crafting creative, story-driven adventures. Your top priority is to ensure a fun and immersive experience for all players. Your responses will be integrated into a framework, so it is crucial to adhere closely to the prescribed format.

    Remember, while building the adventure, your creativity is key, but be cautious not to reveal secrets or traps in the flavor text. These elements should remain hidden, allowing players to discover them through exploration and interaction.

    IMPORTANT: All responses must be structured to be compatible with Python's json.loads function for seamless conversion into a Python dictionary. This ensures your creative content can be easily incorporated into the gaming framework.
"""

DUNGEON = """
    Design a dungeon named {name} for an adventuring party. It will have {num_rooms} rooms, focusing initially on the dungeon's layout and overarching narrative. 

    Think about the dungeon's theme, the story it tells, and its impact on the players' journey. Your outline should be detailed enough to ensure consistency and a cohesive story, considering future expansions.

    Ensure logical room connections, with each room having at least one entrance or exit. Include transitional spaces like corridors, particularly in larger dungeons, which can lead to multiple rooms and contain elements of interest.

    Your response should be in a JSON format compatible with python's json.loads function, like the example below. Highlight the dungeon's purpose, the information known to players beforehand, any secrets, the underlying story, and its anticipated effect on players.

    Each room in the "rooms" dictionary should include a "has_entrance" field. Set this to true if the room is an entry or exit point of the dungeon. Every dungeon should have at least one room with "has_entrance": true, indicating the main entrance or exit. You can also designate additional or secret entrances and exits in the same way.

    Example Format:
    {{
        "purpose": "example purpose",
        "flavour": "example flavour",
        "secrets": "example secrets",
        "story": "example story",
        "effect": "example effect",
        "rooms": {{
            "Room 1 Name": {{
                "connected_to": ["Room 2 Name", "Room 3 Name"],
                "has_entrance": true
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

    Your players will only see the name and the flavour text. The others are notes for your future self
    to use when generating the room's details, to ensure consistency. Ensure there is enough detail to avoid
    incosistencies and to tell a cohesive story.

    This room is called {room_name} and has the following traversable entrances/exits: {room_portals}.

    Attempt to match the description of the room, and investigation and perception findings, to the description
    of the entrances/exits given above. Aim for consistency to create a cohesive experience for your players.
    If a traversal-point has a certain visibility, perception information relating to that traversal-point
    should have a visibility difficulty less than or equal to that visibility. Similarly, if a traversal-point
    is has a high visibility difficulty, ensure it is not mentioned in the room flavour text.

    Respond with a brief outline in the following format imitating a JSON string that can be read by python's json.loads function:
    {{
        "purpose": str, # The in universe purpose of the room
        "flavour": dict = {{
            "0" : # A rich description the players first impressions when entering the room, note that this should not describe moving through any doors or passages, as that is handled seperately.
            "1" : # A description to read the second time the players enter the room, this could be noting an extra detail, a feeling of bordem, or a creeping sense of dread at the repetition, be creative with the desription.
            ... continue for as many as you desire, each time descibing the player's experience entering the room for the nth time.
        }},
        "secrets": str, # Any secrets the room may hold
        "story": str, # The underlying story you want the room to tell
        "effect": str, # The effect you imagine this room will have on the players' stories
        "investigation_text" : dict = {{ 
            # A dictionary showing intelligence roll required and revealed information
            # this should be information revealed by thoughtfull consideration not
            # perception.
            "0" : str # Generic information that is always revealed when investigated, giving an impression of the room 
            "roll_required : int as string (out of 30)" : str, #information revealed
            "higher_roll_required : int as string (out of 30)" : str, #more infomation revealed
            # more or less information as desired, could be none
        }},
        "perception_text": dict = {{
            # A dictionary showing perception roll required and revealed information
            # this should be information revealed by close inspection not
            # intellient investigation.
            "0" : str # Generic information that is always revealed when perceived, giving an impression of the room 
            "roll_required : int as string (out of 30)" : str, #information revealed
            "higher_roll_required : int as string (out of 30)" : str, #more infomation revealed
            # more or less information as desired, could be none
        }}
    }}
"""

ROOM_ITEMS = """
    You are designing items for your adventuring party to find.
    The items are located in a room named {room_name} which is 
    connected to these other rooms: [{room_connected_to}].
    Here is a description of the room. Use this in your creation of the list of items, especially if any 
    items are mentioned in the room description, try and make the descriptions coherent: 

    Purpose:{room_purpose}
    Flavour:{room_flavour}
    Secrets:{room_secrets}
    Story:{room_story}
    Effect:{room_effect}
    Perceptable Information (difficulty from 1 to 20): {room_perceptables}
    Investgatable Information (difficulty from 1 to 20): {room_investigables}

    Here is a description of the dungeon that contains the room:

    Name:{dungeon_name}
    Purpose:{dungeon_purpose}
    Flavour:{dungeon_flavour}
    Secrets:{dungeon_secrets}
    Story:{dungeon_story}
    Effect:{dungeon_effect}

    I would like you to respond with a list of items in this room, {room_name}.
    You should respond with small to medium items only. DO NOT: include doors, portals, or other entranceways,
    flooring or wall materials, or any animate animals, creatures, or intelligent agents. 

    Give your response in the following JSON format:
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
    As you design a dungeon for your adventuring party, focus on creating traversal points between rooms. These can be doors, tunnels, ladders, staircases, or other connectors. Mix mundane and extraordinary elements to keep the dungeon both grounded and exciting.

    For each traversal point, devise a descriptive name and a detailed description for consistency. Note any asymmetries where the experience of traversing differs based on direction.

    Use the provided list of connected pairs {portal_pairs} to structure your response. Format your response as a JSON string compatible with Python's json.loads function, with the following structure:
    {{
        "descriptive_traversal_point_name": {{
            "description": "Aesthetic and functional details",
            "hit_points": "Door health, with 10 as average for a wooden door",
            "asymmetries": {{
                "room_1_name": {{
                    "description": "Details from this room's perspective",
                    "visibility": "Visibility level (1-30)"
                }},
                "room_2_name": {{
                    "description": "Details from the other room's perspective",
                    "visibility": "Visibility level (1-30)"
                }}
            }},
            "conditions": "State of the traversal point (unobstructed, locked, blocked, barricaded)"
        }},
        ...
    }}

    Visibility Scale: 
    1 - Impossible to miss, 5 - Very easy to see, 10 - Easy to see, 15 - Could easily be overlooked,
    20 - Hard to see, 25 - Very hard to see, 30 - Almost impossible to see.
    Note: Choose any value between 1 and 30 for visibility, not limited to these examples.
"""

PORTAL_INSPECT = """
        You are designing an traversal-point between two areas of your dungeon.
        traversal-points include anything that a party member can use to transit between different 
        rooms in the dungeon. These could be doors, trapdoors, ladders, simple cracks in the wall,
        or magical portals. 

        Here is a description of the dungeon that contains the traversak point:

        Name:{dungeon_name}
        Purpose:{dungeon_purpose}
        Flavour:{dungeon_flavour}
        Secrets:{dungeon_secrets}
        Story:{dungeon_story}
        Effect:{dungeon_effect}

        This room is called {room_name}.
        Here is a description of the room containing the traversal-point:

        Purpose:{room_purpose}
        Flavour:{room_flavour}
        Secrets:{room_secrets}
        Story:{room_story}
        Effect:{room_effect}
        Perceptable Information (difficulty from 1 to 20): {room_perceptables_a}
        Investgatable Information (difficulty from 1 to 20): {room_investigables_a}

        Here is a description of the room. Use this in your description of the traveral point, especially if any 
        traversal poitns are mentioned in the room descriptions, try and make the descriptions coherent: 

        This is the room the traversal-point leads too {room_b_name}:

        Purpose:{room_b_purpose}
        Flavour:{room_b_flavour}
        Secrets:{room_b_secrets}
        Story:{room_b_story}
        Effect:{room_b_effect}
        Perceptable Information (difficulty from 1 to 20): {room_perceptables_b}
        Investgatable Information (difficulty from 1 to 20): {room_investigables_b}

        Here is the overall outline of the traversal-point:

        name : {portal_name}
        description : {portal_description}
        conditions : {portal_conditions}
        asymmetries : {portal_asymmetry}
        hit_pints : {portal_hit_points}
        visibility : {portal_visibility} # Assume the door has been discovered,
        although some addition about its difficulty in detection might be added 
        to the flavour for very high visibilities 15-30 (high visibility equals harder to see)

        I would like to to design some more detailed description of the
        traversal-point. Respond in the following JSON string that can be read by python's json.loads function.
        
        {{
            "flavour_text" : str, #paragraph to give to the player, adding to 
            the atmosphere and perhaps revealing something about the story.
            "failed_entry_text" : dict = {{ # given the traversal-point's condition, this should be text to show the player on a failed traversal attempt
                "0" : str, # This should be the text shown the first time the player attempts to enter the room
                "1" : str, # This should be the text shown the second time the player attempts to enter the room, NOTE: this should never hit at attempts to force or pick the lock, as these may not have happened.
                ... # As many attempts as you think is neccisary, no entries are neccisary if the door has no conditions.
            }},
            "is_pickable" : bool, # can you attempt to open this with a lockpick
            "not_pickable_text" :  dict = {{ # if the lock is not pickable this should be text to show the player's failed attempt to find a keyhole
                "0" : str, # This should be the text shown the first time the player attempts to find a way to pick the item
                "1" : str, # This should be the text shown the second time the player attempts to pick the item
                ... # As many attempts as you think is neccisary, no entries are neccisary if the door is not locked.
            }},
            "lockpick_results" : dict = {{   # Results of different lockpicking rolls, must be one failure at 0, and one success (unless impossible), and mabye intermediate levels which could damage the lock.
                "0" : dict = {{ # Worst failure case, only one case will be printed
                    "message" : str # text indicating result
                    "result" : str # one of [broken (lock becomes unpickable), damaged (lock harder to open in future), trap_triggered, nothing, success, loosened (lock easier to pick in future) ]
                }}, 
                ... Increasing levels of success, (between 1 and 30)
            }},
            "lock_broken_text" :  dict = {{ # as above, but because lock is broken rather than impossible
                "0" : str,
                "1" : str,
                ...
            }},
            "force_difficulty": int,
            "is_trapped": bool, #is the door trapped
            "entry_text": str, # atmospheric text to show the player on passing through
        }}
        """

"""
"investigation_text" : dict = {{ 
    # A dictionary showing inteligence roll required and revealed information
    # this should be information revealed by thoughtfull consideration not
    # perception
    roll_required (out of 30) : str #information revealed,
    higher_roll_required : #more infomation revealed,
    # more or less information as desired, could be none
}},
"perception_text": dict = {{
    # A dictionary showing perception roll required and revealed information
    # this should be information revealed by close inspection not
    # inteligent investigation
    roll_required (int) (out of 30) : str #information revealed,
    higher_roll_required (int) : str #more infomation revealed,
    # more or less information as desired, could be none
}}
"""

def system():
    return SYSTEM

def dungeon(
        name, 
        min_num_rooms, 
        max_num_rooms
    ):

    return DUNGEON.format(
        name=name,
        num_rooms=random.randint(min_num_rooms, max_num_rooms)
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
        room_effect=room.effect,
        room_perceptables = room.perceptables,
        room_investigables=room.investigables, 
    )

def room(room):

    dungeon = room.containing_dungeon
    room_portals = [
        portal.name + ": " + portal.description + " " + str(portal.asymmetries[room.name]) for portal in room.portal_dict.values()
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
        room_perceptables_a = room.perceptables,
        room_investigables_a=room.investigables, 
        room_perceptables_b = room_b.perceptables,
        room_investigables_b =room_b.investigables, 
        portal_name = portal.name,
        portal_description = portal.description,
        portal_conditions = portal.conditions,
        portal_asymmetry = portal.asymmetries[room.name],
        portal_hit_points = portal.hit_points,
        portal_visibility = portal.visibility
    )

def check_response(
    model,
    response, 
    prompt,
    temprature,
    system_prompt = SYSTEM
):
    try:
        response = json.loads(response.choices[0].message.content)
    except Exception as e:
        error_prompt = \
            (f"Your previous response: [{response}] to this prompt: [{prompt}], returned this error: [{e}], when attempting to convert it to a python"
            "dictionary with json.loads, please try again. Respond only in a format that can be read as a JSON by python's json.loads function,"
            " anything else will result in an error.")

        print(f"Error, trying again: {e}")

        response = prompt(
            error_prompt,
            model,
            temprature,
            system_prompt=system_prompt,
        )

    return response

def request_response(
    prompt,
    model,
    temprature,
    system_prompt = SYSTEM
):
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
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
        temperature=temprature
    )

    return check_response(
        model,
        response, 
        prompt,
        temprature,
        system_prompt=system_prompt,
    )