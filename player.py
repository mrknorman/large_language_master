from elements import ElementType, APIConfig
from stats import AbilityScores
from agents import Charater

PLAYER = ElementType(
    name = "player",
    summary_attributes=[],
    prompt_arguments=[],
    prompt_template="",
    prompt_focus="",
    prompt_story_length = "", 
    prompt_examples = "",
    child_element_dict={}
)

class Player(Charater):

    def __init__(
            self,
            name : str,
            ability : AbilityScores,
            api_config : APIConfig, 
            **kwargs
        ):

        super().__init__(
            name=name, 
            type=PLAYER,
            ability=ability,
            api_config=api_config,
            **kwargs
        )