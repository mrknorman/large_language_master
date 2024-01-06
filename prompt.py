import textwrap
from typing import List
from interaction import Affordance

class ElementPromptBuilder:
    # Class constants for template strings
    ELEMENT_MAIN = textwrap.dedent("""\
        Design a {type_name} named {name} for an adventuring party, focusing initially on the {focus}.
        Think about the {type_name}'s theme, the story it tells, and its impact on the players' journey. Your outline should be detailed enough to ensure consistency and a cohesive story, considering future expansions.\n""")

    CHILDREN_NUMBER = "It should have {num_children} {child_name}s.\n"

    NETWORK_MAIN = textwrap.dedent("""\
        Your response should include a field named : {node_name}s. These {node_name}s should form a network, with connections to other {node_name}s listed in the "connected_to" field of each {node_name}.
        Ensure logical connections between {node_name}s. With each {node_name} having at least one connection to another {node_name}.\n""")

    NETWORK_EXTERNAL = textwrap.dedent("""\
        Each {node_name} in the "{node_name}s" dictionary should include a "external_connection" field. Set this to true if the room is an entry or exit point of the {type_name}.
        The {type_name} should have at least one {node_name} with "external_connection": true, indicating the main entrance or exit. You can also designate additional or secret entrances and exits in the same way.""")

    NETWORK_EXAMPLE = textwrap.dedent("""\
        "{node_name}s_outline": {{ # A plan of the {node_name}s contained by this {type_name} and the player-traversable connections between them.
            "{node_name}_1_name": {{
                "name" : "{node_name_capitalized} 1 Name"
                "connected_to": ["{node_name}_2_name", ...], # A list of {node_name}s which connect to this one.
                "external_connection": true,
                "description" : # A brief description of this {node_name}
            }},
            ...
        }}""")
    
    AFFORDANCE_HEADER = textwrap.dedent("""\
        There is an affordances for every action that can be performed on this {type_name} by another element. For example a room can be entered, giving it the affordance of enterable.
        There are two types of affordance. Ones that automatically fail or succeed without any checks, and ones that have levels of success and failure.
        This is a list of all affordances for this {type_name}: {affordances_list}. For each affordance, add an item the response dictionary item "affordances_text". See the example for details.\n"""
    )
    AFFORDANCE_EXAMPLE = textwrap.dedent("""\
        "affordances_text" : dict {{
            "{first_affordance}" : dict {{ 
                "is_possible" : bool, # true if affordance is in any way possible
                "check_required" : bool, # true if check required to perform succesfully
                "cumulative_checks" : bool # if true all check results below roll are read, if false next lowest check result to roll is read
                # IF auto-successful (is_possible = true, and check_required = false) list results of repetitions of this action:
                "success_text" : [ # list
                    "first_success_text" : str, # e.g text to be read when action is first performed on this {type_name}, this should be descriptive, and the longest text output.    
                    "second_success_text" : str,  # e.g text to be read the second {type_name}, perhaps it is more ominous the second time, or more calming.   
                    ... As many as desired
                ]
                # ELSE IF auto-failure (is_possible = false): list results of repetitions of this action:
                "failure_text" : [ # list 
                    ... similar to success but describing failure                             
                ]
                # ELSE IF check-required (check_required = true): instead generate a dictionary showing results of different rolls (0: auto-success, 30: almost impossible)
                "check_results" : {{
                    0 : str, # Worst possible result
                    5 : str, # Various results at different difficulties.
                }}
            ... repeat for each affordance listed above.
        }}"""
    )

    EXAMPLE_HEADER = "Format your response as a JSON string compatible with Python's json.loads function, with the following structure:"
    EXAMPLE_MAIN = textwrap.dedent("""\
        "purpose" : str, # The in-universe purpose of this structure, was it {element_examples}, be creative, but cohesive.
        "description" : str, # A brief description of the {type_name}, that can be used to generate more details later on.
        "secrets" : str, # A description of the secrets hidden in this {type_name}.
        "story" : str, # A {story_length} explaining the story of the dungeon, to help build a strong narrative.
        "effect" : str, # The effect this dungeon will have on your players' story and character development.""")

    def __init__(
            self, 
            type_name : str = "", 
            name : str = "", 
            focus : str = "", 
            num_children : int = 0, 
            child_name : str = "", 
            node_name : str = "", 
            story_length : str = "", 
            element_examples : str = "", 
            is_network : str = False, 
            network_extra : str = "",
            affordances : List[Affordance] = None
        ):
        # Initialize with provided values
        self.type_name = type_name
        self.name = name
        self.focus = focus
        self.num_children = num_children
        self.child_name = child_name
        self.node_name = node_name
        self.story_length = story_length
        self.element_examples = element_examples
        self.is_network = is_network
        self.network_extra = network_extra
        self.affordances = affordances

    def build_prompt(self):
        # Building the prompt using list comprehensions
        prompt_parts = [
            self.ELEMENT_MAIN.format(type_name=self.type_name, name=self.name, focus=self.focus),
            self.CHILDREN_NUMBER.format(num_children=self.num_children, child_name=self.child_name)
        ]

        if self.is_network:
            prompt_parts.extend([
                self.NETWORK_MAIN.format(node_name=self.node_name),
                self.NETWORK_EXTERNAL.format(node_name=self.node_name, type_name=self.type_name),
                self.network_extra
            ])
        if self.affordances is not None:
            affordances_list = [affordance.name for affordance in self.affordances]
            prompt_parts.append(
                self.AFFORDANCE_HEADER.format(type_name=self.type_name, affordances_list=affordances_list)
            )

        prompt_parts.extend([
            self.EXAMPLE_HEADER,
            "{",
            self.EXAMPLE_MAIN.format(element_examples=self.element_examples, story_length=self.story_length, type_name=self.type_name)
        ])

        if self.is_network:
            prompt_parts.append(
                self.NETWORK_EXAMPLE.format(node_name=self.node_name, node_name_capitalized=self.node_name.capitalize(), type_name=self.type_name)
            )
        if self.affordances is not None:
            affordances_list = [affordance.name for affordance in self.affordances]
            prompt_parts.append(
                self.AFFORDANCE_EXAMPLE.format(first_affordance=affordances_list[0], type_name=self.type_name)
            )
 

        prompt_parts.append("}")
        return "\n".join(prompt_parts)
