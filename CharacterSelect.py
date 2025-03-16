# Here we are just selecting between the 2 characters
class CharacterSelector:
    def __init__(self):
        self.valid_characters = {'fox', 'mario'}
        self.selected_characters = {}

    # We just make sure the input is a correct character
    def validate_character(self, character_name):
        player_number = len(self.selected_characters) + 1
        if character_name in self.valid_characters:
            self.selected_characters[player_number] = character_name
            if character_name == 'mario':
                return f"Player {player_number} selected Mario."
            if character_name == 'fox':
                return f"Player {player_number} selected Fox."
        else:
            return f"Error: Invalid character '{character_name}' for Player {player_number}."

    # This runs the character selector
    def run(self):
        print('SELECT YOUR CHARACTERS')
        while True:
            print('Player 1 : Select Your Character')
            character_1 = input('SmashScript --> ')
            result = self.validate_character(character_1.lower())
            print(result)
            if 'Error' not in result:
                break
        while True:
            print('Player 2 : Select Your Character')
            character_2 = input('SmashScript --> ')
            result = self.validate_character(character_2.lower())
            print(result)
            if 'Error' not in result:
                break

    # We bring the selected characters over to our actual language using this
    def get_selected_characters(self):
        return self.selected_characters