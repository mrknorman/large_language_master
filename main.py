
from pathlib import Path

from openai import OpenAI

from dungeon import Dungeon
from elements import APIConfig
from dungeon_prompts import SYSTEM

from player import Player
from stats import AbilityScores, Check

from audio import read
from interaction import Enter, Enterable
from prompt import ElementPromptBuilder

if __name__ == "__main__":

    MODEL = "gpt-4-1106-preview"
    TEMPERATURE = 0.7

    client = OpenAI(api_key=open('./api_key', 'r').read())
    dungeon_arguments = {
        "name" : "Tombie's Funhouse",
        "num_rooms" : 3
    }

    api_config = APIConfig(
        system_prompt=SYSTEM,
        model=MODEL,
        temperature=TEMPERATURE,
        client=client,
    )
    
    dungeon = Dungeon(
        name="Tombie's Funhouse",
        num_rooms=3,
        api_config=api_config,
        path=Path("./elements/")
    )
    dungeon.assemble()

    player = Player(
        name="You",
        ability=AbilityScores(
            strength=10,
            dexterity=10,
            constitution=10,
            inteligence=10,
            wisdom=10,
            charisma=10
        ),
        api_config=api_config
    )

    # Example usage:
    builder = ElementPromptBuilder(
        type_name="dungeon",
        name="Mystic Caverns",
        focus="history and mysteries",
        num_children=10,
        child_name="room",
        node_name="room",
        story_length="few paragraphs",
        element_examples="a hidden sanctuary, a lost kingdom, a forgotten crypt",
        is_network=True,
        affordances=[Enterable(parent=dungeon, is_possible=True)]
    )

    # Building the prompt
    prompt = builder.build_prompt()
    print(prompt)

    quit()
    enter = Enter()
    enter(player, dungeon)
    player.roll(Check('strength', 'ability'))
    