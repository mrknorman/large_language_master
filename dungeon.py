
from enum import Enum
from typing import Tuple, List

from elements import (ElementType, NodeElementType, CapsuleType, 
                      NetworkElementType, Network, Vertex, Node, 
                      Capsule, APIConfig)
from dungeon_prompts import (ROOM_PROMPT_ARGUMENTS, ROOM_PROMPT, 
                             SURROUNDINGS_PROMPT_ARGUMENTS, SURROUNDINGS_PROMPT,
                             DUNGEON_PROMPT_ARGUMENTS, DUNGEON_PROMPT,
                             PORTAL_OUTLINE_PROMPT_ARGUMENTS, PORTAL_OUTLINE_PROMPT)

from verbs import Transitablity, Enterability, Exitablity

PORTAL = ElementType(
    name = "portal",
    summary_attributes=["name", "purpose", "flavour", "secrets", "story", "effect"],
    prompt_arguments=ROOM_PROMPT_ARGUMENTS,
    prompt_template=ROOM_PROMPT,
    affordances=[Transitablity]
)
class Portal(Vertex):

    def __init__(
            self,
            name : str,
            room_connections : Tuple[str],
            api_config : APIConfig, 
            **kwargs
        ):

        super().__init__(
            name=name, 
            type=PORTAL,
            room_connections=room_connections,
            api_config=api_config,
            **kwargs
        )

ROOM = NodeElementType(
    name = "room",
    summary_attributes=["name", "purpose", "flavour", "secrets", "story", "effect"],
    prompt_arguments=ROOM_PROMPT_ARGUMENTS,
    prompt_template=ROOM_PROMPT,
    vertex_key="portals",
    affordances=[Enterability, Exitablity]
)
class Room(Node):

    def __init__(
            self,
            name : str,
            connected_to : List[str],
            external_connection : bool, 
            api_config : APIConfig, 
            **kwargs
        ):

        super().__init__(
            name=name, 
            connected_to=connected_to,
            external_connection=external_connection,
            type=ROOM,
            api_config=api_config,
            **kwargs
        )

SURROUNDINGS = CapsuleType(
    name = "surroundings",
    summary_attributes=["name", "purpose", "flavour", "secrets", "story", "effect"],
    prompt_arguments=SURROUNDINGS_PROMPT_ARGUMENTS,
    prompt_template=SURROUNDINGS_PROMPT,
    vertex_key="portals",
    node_key="rooms",
    affordances=[Enterability, Exitablity, Transitablity]
)

class Surroundings(Capsule):
    def __init__(
        self,
        name : str,
        api_config : APIConfig, 
        **kwargs
    ):

        super().__init__(
            name=name, 
            type=SURROUNDINGS,
            api_config=api_config,
            **kwargs
        )

DUNGEON = NetworkElementType(
        name="dungeon", 
        summary_attributes=["name", "purpose", "flavour", "secrets", "story", "effect"],
        prompt_arguments=DUNGEON_PROMPT_ARGUMENTS,
        prompt_template=DUNGEON_PROMPT,
        child_element_dict = {
            "rooms" : Room
        },
        node_key="rooms",
        vertex_key="portals",
        capsule=Surroundings,
        verticies_prompt_arguments=PORTAL_OUTLINE_PROMPT_ARGUMENTS,
        verticies_prompt_template=PORTAL_OUTLINE_PROMPT,
        affordances=[Enterability, Exitablity]
    )
class Dungeon(Network):

    def __init__(
            self,
            name : str,
            num_rooms : int,
            api_config : APIConfig, 
            **kwargs
        ):

        self.num_rooms = num_rooms

        super().__init__(
            name=name, 
            type=DUNGEON,
            api_config=api_config,
            **kwargs
        )

    def assemble(self):
        super().assemble()
        self.affordances["enterability"].redirect = self.capsule

class ElementTypes(Enum):
    DUNGEON_PORTAL = Portal
    ROOM = Room 
    DUNGEON = Dungeon
    SURROUNDINGS = Surroundings