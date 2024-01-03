from openai import OpenAI
client = OpenAI(api_key=open('./api_key', 'r').read())
import json

SYSTEM = \
f"""
    You are an expert dungeon master with many years of experience and a
    creative story-driven approach to constructing adventures. Your primary goal is to
    create a fun and engaging experience for all your players. Your responses will be 
    placed into a framework so you must generate outputs which are as close to the format 
    described as possible. Be carefull never to reveal any information in flavour text about
    secrets or traps that the players should not know about untill they discover them. Allow them 
    to explore and find things on their own!

    IMPORTANT: All responses should be able to be converted into a python dictionary with python's json.loads function.
"""

DUNGEON = """
    You are designing a dungeon called {name} for your adventuring party to explore.

    The details of the rooms will be filled out by you later on, for now focus on the overall plan of 
    the dungeon, the story you'd like it to tell, and how it will affect the player's journey. Ensure that
    there is enough information in the plan for another instance of you to create a more detailed story
    when prompted for specific information. Ensure there is enough detail to avoid incosistencies and to tell 
    a cohesive story, even if your future self is not presnted with infomation about the other rooms.

    Respond with an outline in the following JSON format that can be converted into a python dictionary with python's json.loads function:
    {{
        "purpose" : str, # the in universe purpose of the dungeon
        "flavour" : str, # A description of the dungeon containing only information that your players would know before entering
        "secrets" : str, # any secrets the dungeon may hold
        "story" : str, # the underlying story you want the dungeon to tell
        "effect" : str, # the effect you imagine this room will have on the player's stories
        "rooms" : dict {{ # A plan of the rooms contained by this dungeon and the player-traversable connections between them
            "Room 1 Name" : dict
            {{
                "connected_to" : List[str], # list of rooms which connect to this one
                "has_entrance" : bool, # true if room has dungon entrance/exit (should be at least one per dungeon, but there can be alternative and secret entrances/exits)
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

    Respond with a brief outline in the following format imitating a JSON string that can be read by python's json.loads function:
    {{
        "purpose": str, # The in universe purpose of the room
        "flavour": str, # A rich description of the room for the players
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
        You are designing a dungeon for your adventuring party to explore.
        Here is a description of the dungeon:

        Name:{dungeon_name}
        Purpose:{dungeon_purpose}
        Flavour:{dungeon_flavour}
        Secrets:{dungeon_secrets}
        Story:{dungeon_story}
        Effect:{dungeon_effect}

        I have generated a list of the traversal-points between rooms present in this dungeon, these
        connections can be doors, tunnels, ladders, staircases or any other kind of connections. 
        traversal-points include anything that a party member can use to transit between different 
        rooms in the dungeon. Be creative but include sometime be mundane so the impressive travesal 
        points are more exciting to find.

        I would like you to come up with a desciptive name for each of these traversal-points and
        a brief description for you to use later when describing the traversal-point, 
        to ensure that the description is consistent from both directions. If the traversal-point is
        particularly asymetric, make a note of that in the asymmetries feild.

        Here is the list of connected pairs {portal_pairs}.

        Respond in a JSON string that can be read by python's json.loads function. In the same order as the traversal-point pairs appear:
        {{
            "descriptive_portal_name":
            {{
                "description: str, # aesthetic notes
                "asymmetries" : dict, # ALWAYS create both entry even if the door is symmetric.
                {{
                    "room_1_name" : str {{
                        "description" : str, # description of this rooms side of the traversal-point, empty if symetric
                        "visibility" : int #visibility of this room's side of the poral, see below,
                    }} : dict,
                    "room_2_name" : str {{
                        # as with first room name
                    }} : dict,
                }}
                "conditions" : str # one of [unobstructed, locked, blocked, or barricaded] and no more
            }}
        }}

        Given that visibility is measured out of 30 where:
        1: Impossible to miss, 5: Very easy to see, 10: Easy to see, 15: Could easily be overlooked,
        20: Hard to see, 25: Very hard to see, 30: Almost impossible to see.
        Note: visibility can take any value between 1 and 30, not just these examples.
    """   

PORTAL = \
    """
        You are designing an traversal-point between to areas of your dungeon.
        These could be doors, trapdoors, ladders, simple cracks in the wall,
        or magical portals. 

        Here is a description of the dungeon that contains the traversal-point:
        
        Name:{dungeon_name}
        Purpose:{dungeon_purpose}
        Flavour:{dungeon_flavour}
        Secrets:{dungeon_secrets}
        Story:{dungeon_story}
        Effect:{dungeon_effect}

        This room is called {room_name}.
        Here is a description of the specific room containing the traversal-point. 
        Use this in your creation of the traversal-points, especially if a traversal-point is
        mentioned in the room description, try and make the descriptions coherent

        Purpose:{room_purpose}
        Flavour:{room_flavour}
        Secrets:{room_secrets}
        Story:{room_story}
        Effect:{room_effect}
        Perceptable Information (difficulty from 1 to 20): {room_perceptables}
        Investgatable Information (difficulty from 1 to 20): {room_investigables}

        Here is the overall outline of the traversal-point:

        name : {portal_name}
        description : {portal_description}
        conditions : {portal_conditions}
        asymmetries : {portal_asymmetry}

        I would like you to decide on the visibility and hit points of this traversal-point.

        Respond in the following JSON ready format that can be read by python's json.loads function.
        {{
            "visibility:" int #see below,
            "hit_points:" int, #door health where 10 is an average wooden door
        }}
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
            "failed_entry_text" : str, # given the traversal-point's condition, this should be text to 
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

        2. If the door is baracaded or locked, this is a mesure of the difficulty required to brute 
        force it open:
        1: Easy as tissue paper to open, 5: Very easy to force, 10: Easy to force, 
        15: Average door strength, 20: Strong Door, 25: Very strong door, 30: Almost impregnable door.
        Note: force_difficulty can take any value between 1 and 30, not just these examples.

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
        room_perceptables = room.perceptables,
        room_investigables=room.investigables, 
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

def prompt(
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