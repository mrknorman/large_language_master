from elements import Element, ElementType, APIConfig
from stats import AbilityScores, Check

class Agent(Element):

    def __init__(
            self,
            name : str,
            type : ElementType,
            ability : AbilityScores,
            api_config : APIConfig, 
            **kwargs
        ):

        self.ability = ability

        super().__init__(
            name=name, 
            type=type,
            api_config=api_config,
            **kwargs
        )

    def roll(
            self,
            check : Check, 
            modifiers : dict = None,
            hidden : bool = False
        ):

            
            if not isinstance(check, Check):
                raise ValueError("Roll was expecting a stats.Check(attribute : str, category : str), e.g. Check('strength', 'ability')")

            score = getattr(self, check.category)

            roll = score.roll(check.attribute)

            if modifiers is None:
                modifiers = {f"{check.attribute} {check.category}" : roll["modifier"]}
            else:
                modifiers.update({f"{check.attribute} {check.category}" : roll["modifier"]})
            
            total_modifier = 0
            for key, value in modifiers.items():
                if value >= 0:
                    modifier_string = [f"+ {value} (from {key})"]
                else:
                    modifier_string = [f"- {value} (from {key})"]

                total_modifier += value
            
            modifiers_string = " ".join(modifier_string)

            total_roll = roll["total"] + total_modifier

            if not hidden:
                print(f"{self.name} rolled a {roll["roll"]} {modifiers_string} = {roll["total"]} {check.attribute} check!")

            return {
                "total" : total_roll,
                "modifiers" : modifiers
            }

class Charater(Agent):

    def __init__(
            self,
            name : str,
            type : ElementType,
            ability: AbilityScores,
            api_config : APIConfig, 
            **kwargs
        ):

        super().__init__(
            name=name, 
            type=type,
            ability=ability,
            api_config=api_config,
            **kwargs
        )