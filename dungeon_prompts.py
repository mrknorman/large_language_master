SYSTEM = \
f"""
    As an expert dungeon master with extensive experience, your expertise lies in crafting creative, story-driven adventures. Your top priority is to ensure a fun and immersive experience for all players. Your responses will be integrated into a framework, so it is crucial to adhere closely to the prescribed format.

    Remember, while building the adventure, your creativity is key, but be cautious not to reveal secrets or traps in the flavor text. These elements should remain hidden, allowing players to discover them through exploration and interaction.

    IMPORTANT: All responses must be structured to be compatible with Python's json.loads function for seamless conversion into a Python dictionary. This ensures your creative content can be easily incorporated into the gaming framework.
"""

DUNGEON_PROMPT_ARGUMENTS = ["name", "num_rooms"]
DUNGEON_PROMPT = """
    Design a dungeon named {name} for an adventuring party. It will have {num_rooms} rooms, focusing initially on the dungeon's layout and overarching narrative. 

    Think about the dungeon's theme, the story it tells, and its impact on the players' journey. Your outline should be detailed enough to ensure consistency and a cohesive story, considering future expansions.

    Ensure logical room connections, with each room having at least one entrance or exit. Include transitional spaces like corridors, particularly in larger dungeons, which can lead to multiple rooms and contain elements of interest.

    Your response should be in a JSON format compatible with python's json.loads function, like the example below. Highlight the dungeon's purpose, the information known to players beforehand, any secrets, the underlying story, and its anticipated effect on players.

    Each room in the "rooms" dictionary should include a "external_connection" field. Set this to true if the room is an entry or exit point of the dungeon. Every dungeon should have at least one room with "external_connection": true, indicating the main entrance or exit. You can also designate additional or secret entrances and exits in the same way.

    Example Format:
    {{
        "purpose": "The in universe purpose of this structure, was it a prison, a fortress, a temple in honour of a mad god, be creative, but cohesive.",
        "entry_text": "This text will be read before your party members enter the dungeon. It should set the scene and prepare your party members for what is to come. Do not mention specific details about the party aproaching the dungeon, as this will be covered later.",
        "secrets": "A description of the secrets hidden in the dungeon",
        "story": "example story",
        "effect": "example effect",
        "rooms_outline": {{ # A plan of the rooms contained by this dungeon and the player-traversable connections between them.
            "Room 1 Name": {{
                "connected_to": ["Room 2 Name", ...], # A list of rooms which connect to this one.
                "external_connection": true,
                "description" : "description of the room"
            }},
            ...
        }}
    }}
"""

PORTAL_OUTLINE_PROMPT_ARGUMENTS = ["context", "portals_map"]
PORTAL_OUTLINE_PROMPT = \
"""
    As you design a dungeon for your adventuring party, focus on creating traversal points between rooms. These can be doors, tunnels, ladders, staircases, or other connectors. Mix mundane and extraordinary elements to keep the dungeon both grounded and exciting.

    Here is some contextual infomation about the dungeon:

    {context}

    And here is a list of connected pairs of rooms, each of which require a traversal point:

    {portals_map}

    For each traversal point, devise a descriptive name and a detailed description for consistency. Note any asymmetries where the experience of traversing differs based on direction.

    Format your response as a JSON string compatible with Python's json.loads function, with the following structure:
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

SURROUNDINGS_PROMPT_ARGUMENTS = ["lineage", "connected_to"]
SURROUNDINGS_PROMPT = \
"""
    As you design a dungeon for your adventuring party, focus on creating the area surrouding the dungeon. This could be a dense jungle, or a towering abandoned cityscape, or perhaps a strange otherworldly dimension. Mix mundane and extraordinary elements to keep the dungeon both grounded and exciting.

    Here is some contextual infomation about the dungeon:

    {lineage}

    And here is a list of dungeon rooms which have an exterior entrance:

    {connected_to}

    Highlight the information known to players beforehand, any secrets, the underlying story, and its anticipated effect on players. Perhaps hint at how the players are feeling as they await there expidition.

    Format your response as a JSON string compatible with Python's json.loads function, with the following structure:
    {{
        "name" : "Descpiptive name of the dungeons surroundings e.g. Dense Jungle, Alien Planescape..."
        "flavour": "First impression description. This should be the longest and set the scene as your players arrive in the area surrouding the jungle entrance.",
        "success_exit_text" : "This should describe how the area feels to the players after they exit the dungeon after a sucesfull mission.",
        "failed_exit_text" : "This should describe how the area feels to the players after they exit the dungeon after a failed mission.",
        "early_exit_text" : [
            "Sometimes your players might exit the dungeon early. The first time they do so, this will be read.",
            "The second time they do so, this will be read."
            ... # Additional information as needed

        ]
        "secrets": "Secretes of the surrounding area",
        "story": "Underlying story",
        "effect": "Effect on players",
        "investigation_text": {{
            "0": "Basic investigation information",
            "roll_required (out of 30)": "Information for a specific intelligence roll",
            ... # Additional information as needed
        }},
        "perception_text": {{
            "0": "Basic perception information",
            "roll_required (out of 30)": "Information for a specific wisdom roll",
            ... # Additional information as needed
        }}
        "entrances" : {{ #  For each entrance, devise a descriptive name and a detailed description for consistency. Note any asymmetries where the experience of entering the dungeon differs from exiting.
            "descriptive_dungeon_entrance_name": {{
                "description": "Aesthetic and functional details",
                "hit_points": "Door health, with 10 as average for a wooden door",
                "asymmetries": {{
                    "Dense Jungle": {{ # Exterior name
                        "description": "Details from the dungeon's exterior.",
                        "visibility": "Visibility level (1-30)"
                    }},
                    "dungeon_room_name": {{
                        "description": "Details from the inside the dungeon.",
                        "visibility": "Visibility level (1-30)"
                    }}
                }},
                "conditions": "State of the entrance (unobstructed, locked, blocked, barricaded)" # Ensure at least one is unobstructed or locked per dungeon.
            }},
            ...
        }},
    }}

    Visibility Scale: 
    1 - Impossible to miss, 5 - Very easy to see, 10 - Easy to see, 15 - Could easily be overlooked,
    20 - Hard to see, 25 - Very hard to see, 30 - Almost impossible to see.
    Note: Choose any value between 1 and 30 for visibility, not limited to these examples.
"""


ROOM_PROMPT_ARGUMENTS = ["name", "lineage", "connected_verticies"]
ROOM_PROMPT = """
    Design a new room, {name}, for your dungeon. This room is part of a larger dungeon.

    Here is some contextual infomation about the dungeon:

    {lineage}

    Initially, players will encounter only the room's name and flavour text. Use the other details to guide the room's design, ensuring consistency with the dungeon's overall story and theme.

    Traversable Entrances/Exits: 
    
    {connected_verticies}

    Align the room's description, investigation, and perception details with these entrances/exits for a cohesive player experience. The visibility of traversal points should match the difficulty of perceiving them. If a traversal point is less visible, it should not be easily detected in the room's flavour text.

    Format your response as a JSON-like string for Python's json.loads function:
    {{
        "purpose": "In-universe purpose",
        "flavour": [
            "First impression description. This should be the longest and reveal everything noticable on first entry to the room.",
            "Second entry description",
            ... # Additional entries as desired
        ],
        "secrets": "Room secrets",
        "story": "Underlying story",
        "effect": "Effect on players",
        "investigation_text": {{
            "0": "Basic investigation information",
            "roll_required (out of 30)": "Information for a specific intelligence roll",
            ... # Additional information as needed
        }},
        "perception_text": {{
            "0": "Basic perception information",
            "roll_required (out of 30)": "Information for a specific wisdom roll",
            ... # Additional information as needed
        }}
    }}
"""

#Old:
PORTAL_ARGUMENTS = [""]
PORTAL = """
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