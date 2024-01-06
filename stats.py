from numpy.random import randint

from dataclasses import dataclass
from typing import List

@dataclass
class Check:
    attribute : str
    category : str

class Die:
    def __init__(
            self, 
            num_sides : int = 20,
            weightings : List[float] = None
        ):

        self.num_sides = num_sides
        self.weightings = weightings

    def roll(self):
        self.value = randint(1, self.num_sides+1)
        return self.value      

class AbilityScore:
    value : int
    
    def __init__(self, value : int):
        self.value = value
        self.modifier = self.calculate_modifier(value)
        self.die = Die(20)

    def calculate_modifier(self, value):
        return ((value - 10) // 2)

    def roll(self):
        self.die.roll()
        return {
            "total" : self.die.value + self.modifier,
            "roll" : self.die.value,
            "modifier" : self.modifier
        }

class AbilityScores:

    def __init__(
            self,
            strength : int = 10,
            dexterity : int = 10,
            constitution : int = 10,
            inteligence : int = 10,
            wisdom : int = 10,
            charisma : int = 10
        ):
        self.strength = AbilityScore(strength)
        self.dexterity = AbilityScore(dexterity)
        self.constitution = AbilityScore(constitution)
        self.inteligence = AbilityScore(inteligence)
        self.wisdom = AbilityScore(wisdom)
        self.charisma = AbilityScore(charisma)

    def roll(
            self,
            ability_name : str
        ):
        
        return getattr(self, ability_name).roll()