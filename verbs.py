
from typing import Any
from elements import Element
from agents import Agent

from stats import Check

from audio import read

class Verb:

    def __init__(
            self,
            name : str,
            affordance_name : str,
            check : Check
        ):

        self.name = name
        self.check = check
        self.affordance_name = affordance_name
        
        self.count = 0

    def __call__(
            self, 
            element : Element
            ) -> Any:
        
        count += 1

class Affordance:

    def __init__(
        self,
        parent : Element,
        is_possible : bool,
        name : str,
        verb_name : str
    ):
        self.name = name
        self.parent = parent
        self.verb_name = verb_name
        self.is_possible = is_possible
        self.success_text = None
        self.count_element = {}

class Enterability(Affordance):

    def __init__(
            self, 
            parent : Element,  
            is_possible : bool,
            redirect : Element = None
        ):

        self.redirect = redirect

        super().__init__(
            parent=parent,
            is_possible=is_possible,
            name="enterability",
            verb_name="enter", 
        )
class Enter(Verb): 

    def __init__(
            self,
        ):
        
        super().__init__(
            name="enter",
            affordance_name="enterability",
            check=Check(
                attribute="dexterity", 
                category="ability"
            )
        )

    def __call__(
            self,
            element : Element,
            container : Element,
            modifiers : dict = None
        ):

        if modifiers is None:
            modifiers = {}

        # Can enter check            
        if not hasattr(container, "affordances"):
            raise AttributeError("Element does not have affordances dict!")
        elif self.affordance_name not in container.affordances:
            read("You cannot do that!")
        else:
            affordance = container.affordances[self.affordance_name]
            if affordance.is_possible:
                
                if element.parent is not None:
                    element.parent.children.pop(element.name, None)

                if element.name not in affordance.count_element:
                    affordance.count_element[element.name] = 0

                read(container.entry_text)
                
                if affordance.success_text is not None:
                    if affordance.count_element[element.name] >= len(affordance.success_text):
                        read(affordance.success_text[-1])
                    else:
                        read(affordance.success_text[affordance.count_element[element.name]])          
                
                if affordance.redirect is not None:
                    self(element, affordance.redirect)
                else:
                    container.children.update({element.name : element})      
                
            else:
                read("That does not seem possible...")
class Transitablity(Affordance):

    num_of_applications = 0
    num_succesfull_applications = 0
    num_failed_applications = 0

    def __init__(self, parent : Element, is_possible : bool):

        super().__init__(
            parent=parent,
            is_possible=is_possible,
            name="transitablity",
            verb_name="transit"
        )

class Transit(Verb):
    def __init__(self):
        
        super().__init__(
            name="transit",
            affordance_name="transitablity",
            check=Check(
                attribute="dexterity", 
                category="ability"
            )
        )

    def __call__(
            self,
            agent : Element,
            element : Element,
            modifiers : dict = None
        ):

        if modifiers is None:
            modifiers = {}

        # Can enter check

        if hasattr(element, "is_enterable"):
            if element.is_enterable == True:
                read("transit")

class Exitablity(Affordance):

    num_of_applications = 0
    num_succesfull_applications = 0
    num_failed_applications = 0

    def __init__(self, parent : Element, is_possible : bool):

        super().__init__(
            parent=parent,
            is_possible=is_possible,
            name="exitablity",
            verb_name="exit"
        )
class Exit(Verb):
    def __init__(self):
        
        super().__init__(
            name="exit",
            affordance_name="exitability",
            check=Check(
                attribute="dexterity", 
                category="ability"
            )
        )

    def __call__(
            self,
            agent : Element,
            element : Element,
            modifiers : dict = None
        ):
        pass
class Observe(Verb):

    def __init__(self):
        
        super().__init__(
            name="enter",
            check=Check(
                attribute="wisdom", 
                category="ability"
            )
        )

    def __call__(
            self,
            agent : Agent,
            element : Element,
            modifiers : dict = None
        ):

        if modifiers is None:
            modifiers = {}

        if hasattr(element, "observables"):
            value = agent.roll(self.check)


