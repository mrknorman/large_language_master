import sys

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
    print("Heelo")