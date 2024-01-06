
from typing import Any
from elements import Element
from agents import Agent

from stats import Check

class Verb:
    def __init__(
            self,
            name : str,
            check : Check
        ):

        self.name = name
        self.check = check

    def __call__(
            self, 
            element : Element
            ) -> Any:
        # do something
        pass

class observe(Verb):

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


