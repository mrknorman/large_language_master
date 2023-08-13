import sys
import openai
import time
from pathlib import Path 

# Remember traps and secret levers

# Trapped       = will activate on interaction
# Discoverable  = can investigate to reveal other elements (roll investigate)
# Informational = can investigate to obtain information (roll investigate + history/religion/arcana/nature/survival)
# Interactable  = can interact to change state of the room (roll intelligence/strength/dex)
# Traversable   = can use to move around the room, i.e stairs, elevators.
# Exit          = can be used to leave room

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

class room():

    # Inital plan:

    name : str = "Dungeon"
    purpose : str = "To hold prisoners"
    flavour_text : str = "Default Text" 
    secrets : str = ""
    story : str = ""

    contemplation_of_purpose : str = ""
    
    structure = []
    characters = []
    items = []

    def create_new_encounter():
        print("NEW")

if __name__ == "__main__":
    # Example of an OpenAI ChatCompletion request
    # https://platform.openai.com/docs/guides/chat

    # record the time before the request is sent
    start_time = time.time()
    
    message_assembly = []
    
    system_prompt = []



    openai.api_key_path = Path("./api_key")

    # send a ChatCompletion request to count to 100
    response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                    messages=[
                                {'role': 'system', 
                                 'content': 'You are an expert dungeon master with many years of experience and a creative story-driven aproach to construting adventures. Your primary goal is to create a fun and engaging experience for all your players. Your responses will be ingested into a framework program so try to generate outputs which are as close to the format described as possible.'},
                                {'role': 'user', 'content': 'You are designing a new room for your adventuring party to explore. First reply with the name of the room only.'}
                                    ],
                        temperature=0,
                        )

    # calculate the time it took to receive the response
    response_time = time.time() - start_time

    # print the time delay and text received
    print(f"Full response received {response_time:.2f} seconds after request")
    print(f"Full response received:\n{response}")
