import audio

class Command:
    def __init__(self, name, description, func):
        self.name = name
        self.description = description
        self.func = func

    def execute(self, args, dungeon, current_room, player):
        return self.func(args, dungeon, current_room, player)

def roll20():
    return np.random.randint(1, 21)

def initialize():
    """Initialize and return the dictionary of command instances."""

    def list_func(args, _, current_room, player):
        if not args:
            current_room.listAll()
            return

        subcommands = {
            "all": current_room.listAll,
            "items": current_room.listItems,
            "portal": current_room.listEgress
        }

        if args and args[0] in subcommands:
            subcommands[args[0]]()
        else:
            print(f"Invalid sub-command for list. Available options are: {list[subcommands.keys()]}.")

    def observe_func(args, _, current_room, player):
        if not args:
            current_room.observe(player)
            return

        subcommands = {
            'room' : current_room.observe(player),
        }        

        if args and args[0] in subcommands:
            subcommands[args[0]]()
        else:
            print(f"Invalid sub-command for list. Available options are: {list(subcommands.keys())}.")

    def enter_func(args, dungeon, current_room, player):
        if not args:
            audio.read_text("Specify the door you'd like to enter.")
            return current_room

        # Check if the argument is a number (index)
        if args[0].isdigit():
            index = int(args[0])
            portal_name, portal = current_room.getEgressByIndex(index)
            if not portal:
                print(f"No entryway found at index {index}.")
                return current_room
        else:
            portal_name = " ".join(args)
            if portal_name not in current_room.discovered_portals:
                print(f"There is no entryway named {portal_name} found in the current room.")
                return current_room
            portal = current_room.discovered_portals[portal_name]
        
        # Remaining logic for entering the portal
        if current_room.name != portal.connection_a:
            new_room_name = portal.connection_a
        else:
            new_room_name = portal.connection_b

        new_room = dungeon.rooms[new_room_name]

        first_time = False
        if not portal.used:
            first_time = True
            portal.inspect(current_room, new_room)

        portal.is_passable = not (portal.is_locked or portal.is_barricaded or portal.is_barricaded)        
        if not portal.is_passable:
            try:
                audio.read_text(portal.failed_entry_text[str(portal.failed_attempts)])
            except:
                max_tries = list(sorted(portal.failed_entry_text))[-1]
                audio.read_text(max_tries)

            portal.failed_attempts += 1
            return current_room
        else:
            if first_time:
                audio.read_text(portal.entry_text)
            new_room.enter(player, portal)
            portal.used = True
            return new_room

    def pick_func(args, dungeon, current_room, player):

        if not args:
            audio.read_text("Specify what you'd like to pick.")

        # Check if the argument is a number (index)
        if args[0].isdigit():
            index = int(args[0])
            portal_name, portal = current_room.getEgressByIndex(index)
            if not portal:
                print(f"No entryway found at index {index}.")
        else:
            portal_name = " ".join(args)
            if portal_name not in current_room.discovered_portals:
                print(f"There is no entryway named {portal_name} found in the current room.")
            
            portal = current_room.discovered_portals[portal_name]

        # Remaining logic for entering the portal
        if current_room.name != portal.connection_a:
            new_room_name = portal.connection_a
        else:
            new_room_name = portal.connection_b

        new_room = dungeon.rooms[new_room_name]

        first_time = False
        if not portal.used:
            first_time = True
            portal.inspect(current_room, new_room)

        if portal_name in current_room.discovered_portals:

            portal = current_room.discovered_portals[portal_name]
            portal.pick(player)

        else:
            audio.read_text(f"This is no entryway named {portal_name} found in the current room.")

    list_command = Command("list", "List details. Use: list <all/items/portal>", list_func)
    observe_command = Command("observe", "Observe the current room.", observe_func)
    enter_command = Command("enter", "Enter a specified portal. Use: enter <portal_name>", enter_func)
    pick_command = Command("pick", "Enter a specified portal. Use: enter <portal_name>", pick_func)

    return {
        list_command.name: list_command,
        observe_command.name: observe_command,
        enter_command.name: enter_command,
        pick_command.name: pick_command
    }