import audio

class Command:
    def __init__(self, name, description, func):
        self.name = name
        self.description = description
        self.func = func

    def execute(self, args, dungeon, current_room, player):
        return self.func(args, dungeon, current_room, player)

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

        portal_name = " ".join(args)
        if portal_name in current_room.discovered_portals:

            portal = current_room.discovered_portals[portal_name]

            if current_room.name != portal.connection_a:
                new_room_name = portal.connection_a
            else:
                new_room_name = portal.connection_b

            new_room = dungeon.rooms[new_room_name]

            if not portal.inspected:
                portal.inspect(current_room, new_room)

            if not portal.is_passable:
                audio.read_text(portal.failed_entry_text)
                return current_room
            else:
                audio.read_text(portal.entry_text)

                new_room.enter(player, portal)
                return new_room
        else:
            print(f"There is no entryway named {portal_name} found in the current room.")
            return current_room

    def pick_func(args, dungeon, current_room, player):

        if not args:
            audio.read_text("Specify what you'd like to pick.")

        portal_name = " ".join(args)

        if portal_name in current_room.discovered_portals:

            portal = current_room.discovered_portals[portal_name]

            if not portal.is_locked:
                audio.read_text("Door not locked.")
                return current_room
            else:
                audio.read_text(portal.entry_text)

                new_room.enter(player, current_room)
                return new_room
        else:
            audio.read_text(f"This is no entryway named {portal_name} found in the current room.")
            return current_room


    list_command = Command("list", "List details. Use: list <all/items/portal>", list_func)
    observe_command = Command("observe", "Observe the current room.", observe_func)
    enter_command = Command("enter", "Enter a specified portal. Use: enter <portal_name>", enter_func)

    return {
        list_command.name: list_command,
        observe_command.name: observe_command,
        enter_command.name: enter_command
    }