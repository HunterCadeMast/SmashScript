import CharacterSelect
import re
import random
import sys

##################################################################################################################################################
# Here is SmashScript
# grammar.txt has the grammar for the langauge
# Current characters to select from: [Mario, Fox]
#
# How to Run:
#   - All that is needed to run the program is to just run this script in Python and it should take you through the steps
#
# Known Bugs:
#   - Grab does not seem to read properly
#   - Tokens are not fully read correctly and will accept certain incorrect inputs
#
# Have fun!
#
# Created By: Hunter Mast
# Date: 11/30/23
####################################################################################################################################################

# This runs the character selector for either 'Mario' or 'Fox'
character_selector = CharacterSelect.CharacterSelector()
character_selector.run()
player_1_character = character_selector.get_selected_characters().get(1)
player_2_character = character_selector.get_selected_characters().get(2)

# Everything below should be the lexer of the language (Up to the parser, of course)

# Token Types
PLAYER = 'PLAYER'
INTEGER = 'INTEGER'
MOVE = 'MOVE'
ATTACK = 'ATTACK'
SPECIAL = 'SPECIAL'
SMASH = 'SMASH'
TILT = 'TILT'
GRAB = 'GRAB'
THROW = 'THROW'
UP = 'UP'
DOWN = 'DOWN'
LEFT = 'LEFT'
RIGHT = 'RIGHT'
NEUTRAL = 'NEUTRAL'
THEN = 'THEN'

# This will run RegEx to parse whatever input is given to it's correct length
patterns = [
    (re.compile(r'Player'), PLAYER),
    (re.compile(r'\d+'), INTEGER),
    (re.compile(r'move'), MOVE),
    (re.compile(r'attack'), ATTACK),
    (re.compile(r'special'), SPECIAL),
    (re.compile(r'smash'), SMASH),
    (re.compile(r'tilt'), TILT),
    (re.compile(r'grab'), GRAB),
    (re.compile(r'throw'), THROW),
    (re.compile(r'up'), UP),
    (re.compile(r'down'), DOWN),
    (re.compile(r'left'), LEFT),
    (re.compile(r'right'), RIGHT),
    (re.compile(r'neutral'), NEUTRAL),
    (re.compile(r'then'), THEN),
]

# This class intitializes the tokens and acts like an object keeping the type and value together
class Token:
    def __init__(self, type, value, line_num):
        self.type = type
        self.value = value
        self.line_num = line_num

    def __repr__(self):
        return f'{self.type}: {self.value}'

# This uses the 'Token' class to search for patterns for each length of word and then tries to match it, setting the given input as a new token
def tokenize(text):
    tokens = []
    for pattern, token_type in patterns:
        match = pattern.search(text)
        if match:
            value = match.group()
            tokens.append(Token(token_type, value, 1))
    return tokens

# This class parses the strings to go through our tokens and make sure it is correct according to the grammar
class SmashScriptParser:
    def __init__(self):
        self.characters = {}
        self.player_num = 0
        self.player_1_damage = 0
        self.player_2_damage = 0

    # This is where the actual parsing takes place of the tokens given
    def parse(self, tokens):
        i = 0
        while i < len(tokens):
            if (tokens[i].type == PLAYER and i + 3 < len(tokens) and tokens[i + 1].type == INTEGER and tokens[i + 2].type == MOVE):
                self.player_num = int(tokens[i + 1].value)
                self.parse_move(i + 3, tokens, self.player_num)
                break
            else:
                print(f"Error: Unexpected token {tokens[i].type} at line {tokens[i].line_num}")
                i += 1

    # Here we deal with the move given by the parser and we figure out what damage to deal
    def parse_move(self, i, tokens, player_num):
        damage_dealt = 0
        if i < len(tokens):
            token = tokens[i]
            token_type = token.type.upper()
            # We check the token types to see which attack we are performing
            if token_type == ATTACK:
                direction = 'NULL'
                damage_dealt = self.calculate_damage(token_type, direction)
            elif token_type == SPECIAL:
                direction = self.parse_smash_direction(i + 1, tokens)
                if direction == UP or direction == LEFT or direction == RIGHT or direction == DOWN or direction == NEUTRAL:
                    damage_dealt = self.calculate_damage(token_type, direction)
                else:
                    print(f"Error: Invalid direction '{direction}' for special move.")
            elif token_type == SMASH:
                direction = self.parse_smash_direction(i + 1, tokens)
                if direction == UP or direction == LEFT or direction == RIGHT or direction == DOWN:
                    damage_dealt = self.calculate_damage(token_type, direction)
                else:
                    print(f"Error: Invalid direction '{direction}' for smash move.")
            elif token_type == TILT:
                direction = self.parse_smash_direction(i + 1, tokens)
                if direction == UP or direction == LEFT or direction == RIGHT or direction == DOWN:
                    damage_dealt = self.calculate_damage(token_type, direction)
                else:
                    print(f"Error: Invalid direction '{direction}' for tilt move.")
            elif token_type == GRAB:
                direction = self.parse_smash_direction(i + 1, tokens)
                if direction == ATTACK:
                    direction = self.parse_smash_direction(i + 1, tokens)
                    if direction == THEN:
                        direction = self.parse_smash_direction(i + 1, tokens)
                        if direction == THROW:
                            direction = self.parse_smash_direction(i + 1, tokens)
                            if direction == UP or direction == LEFT or direction == RIGHT or direction == DOWN:
                                damage_dealt = self.calculate_damage('ATT', direction)
                            else:
                                print(f"Error: Invalid direction '{direction}' for throw move.")
                        else:
                            print(f"Error: Invalid action '{direction}' for grab move.")
                    else:
                        direction = 'NULL'
                        damage_dealt = self.calculate_damage('ATTACK', direction)
                elif direction == THROW:
                    direction = self.parse_smash_direction(i + 1, tokens)
                    if direction == UP or direction == LEFT or direction == RIGHT or direction == DOWN:
                        damage_dealt = self.calculate_damage('THROW', direction)
                    else:
                        print(f"Error: Invalid direction '{direction}' for throw move.")
                else:
                    print(f"Error: Invalid action '{direction}' for grab move.")
            elif token_type == THROW:
                return token_type
            elif token_type == THEN:
                return token_type
            elif token_type == UP:
                return token_type
            elif token_type == DOWN:
                return token_type
            elif token_type == LEFT:
                return token_type
            elif token_type == RIGHT:
                return token_type
            elif token_type == NEUTRAL:
                return token_type
            # After reciving our damage dealt, we then try and see if it is enough to win and if so, end the game
            try:
                self.stock_check(damage_dealt)
                return token_type
            except GameOverException as e:
                print(e)
                sys.exit()
            return token_type
    
    # Here we calculate the damage deal by each character through their selected characters.
    def calculate_damage(self, attack_name, direction):
        opposite_player_num = 0
        character = 'NULL'
        attack_hits = random.choice([1, 2, 3])
        damage_dealt = 0
        if self.player_num == 1:
            opposite_player_num = 2
            character = player_1_character
            player_damage = self.player_1_damage
        elif self.player_num == 2:
            opposite_player_num = 1
            character = player_2_character
            player_damage = self.player_2_damage
        # Each character has it's own specific attack damage, so it is calculated through this
        if character.upper() == "MARIO":
            attack_damage = 3 * attack_hits
            special_damage_neutral = 6
            special_damage_up = 3
            special_damage_left = 8
            special_damage_right = 8
            special_damage_down = 3
            smash_damage_charge = random.randrange(0, 5, 3)
            smash_damage_up = 15 * smash_damage_charge
            smash_damage_left = 15 * smash_damage_charge
            smash_damage_right = 15 * smash_damage_charge
            smash_damage_down = 15 * smash_damage_charge
            tilt_damage_up = 8
            tilt_damage_left = 9
            tilt_damage_right = 9
            tilt_damage_down = 8
            throw_damage_up = 8
            throw_damage_left = 8
            throw_damage_right = 8
            throw_damage_down = 8
            if attack_name == ATTACK:
                damage_dealt += attack_damage
            elif attack_name == SPECIAL:
                if direction == NEUTRAL:
                    damage_dealt += special_damage_neutral
                elif direction == UP:
                    damage_dealt += special_damage_up
                elif direction == LEFT:
                    damage_dealt += special_damage_left
                elif direction == RIGHT:
                    damage_dealt += special_damage_right
                elif direction == DOWN:
                    damage_dealt += special_damage_down
            elif attack_name == SMASH:
                if direction == UP:
                    damage_dealt += smash_damage_up
                elif direction == LEFT:
                    damage_dealt += smash_damage_left
                elif direction == RIGHT:
                    damage_dealt += smash_damage_right
                elif direction == DOWN:
                    damage_dealt += smash_damage_down
            elif attack_name == TILT:
                if direction == UP:
                    damage_dealt += tilt_damage_up
                elif direction == LEFT:
                    damage_dealt += tilt_damage_left
                elif direction == RIGHT:
                    damage_dealt += tilt_damage_right
                elif direction == DOWN:
                    damage_dealt += tilt_damage_down
            elif attack_name == THROW:
                if direction == UP:
                    damage_dealt += throw_damage_up
                elif direction == LEFT:
                    damage_dealt += throw_damage_left
                elif direction == RIGHT:
                    damage_dealt += throw_damage_right
                elif direction == DOWN:
                    damage_dealt += throw_damage_down
            elif attack_name == ATT:
                damage_dealt += attack_damage
                if direction == UP:
                    damage_dealt += throw_damage_up
                elif direction == LEFT:
                    damage_dealt += throw_damage_left
                elif direction == RIGHT:
                    damage_dealt += throw_damage_right
                elif direction == DOWN:
                    damage_dealt += throw_damage_down
        # Same is done here as above, but for the other character
        elif character.upper() == "FOX":
            attack_damage = 4 * attack_hits
            special_damage_neutral = 3
            special_damage_up = 9
            special_damage_left = 7
            special_damage_right = 7
            special_damage_down = 5
            smash_damage_charge = random.randrange(0, 5, 3)
            smash_damage_up = 13 * smash_damage_charge
            smash_damage_left = 12 * smash_damage_charge
            smash_damage_right = 12 * smash_damage_charge
            smash_damage_down = 12 * smash_damage_charge
            tilt_damage_up = 9
            tilt_damage_left = 9
            tilt_damage_right = 9
            tilt_damage_down = 10
            throw_damage_up = 2
            throw_damage_left = 3
            throw_damage_right = 3
            throw_damage_down = 2
            if attack_name == ATTACK:
                damage_dealt += attack_damage
            elif attack_name == SPECIAL:
                if direction == NEUTRAL:
                    damage_dealt += special_damage_neutral
                elif direction == UP:
                    damage_dealt += special_damage_up
                elif direction == LEFT:
                    damage_dealt += special_damage_left
                elif direction == RIGHT:
                    damage_dealt += special_damage_right
                elif direction == DOWN:
                    damage_dealt += special_damage_down
            elif attack_name == SMASH:
                if direction == UP:
                    damage_dealt += smash_damage_up
                elif direction == LEFT:
                    damage_dealt += smash_damage_left
                elif direction == RIGHT:
                    damage_dealt += smash_damage_right
                elif direction == DOWN:
                    damage_dealt += smash_damage_down
            elif attack_name == TILT:
                if direction == UP:
                    damage_dealt += tilt_damage_up
                elif direction == LEFT:
                    damage_dealt += tilt_damage_left
                elif direction == RIGHT:
                    damage_dealt += tilt_damage_right
                elif direction == DOWN:
                    damage_dealt += tilt_damage_down
            elif attack_name == THROW:
                if direction == UP:
                    damage_dealt += throw_damage_up
                elif direction == LEFT:
                    damage_dealt += throw_damage_left
                elif direction == RIGHT:
                    damage_dealt += throw_damage_right
                elif direction == DOWN:
                    damage_dealt += throw_damage_down
            elif attack_name == ATT:
                damage_dealt += attack_damage
                if direction == UP:
                    damage_dealt += throw_damage_up
                elif direction == LEFT:
                    damage_dealt += throw_damage_left
                elif direction == RIGHT:
                    damage_dealt += throw_damage_right
                elif direction == DOWN:
                    damage_dealt += throw_damage_down
        # There is most likely a better way to find damage by each character, but this is the easiet for only having 2 characters
        # More characters I would most likely have multiple files, a new one for each character
        # Below damage is calculated and reported
        player_damage += damage_dealt
        if self.player_num == 1:
            self.player_1_damage = player_damage
        elif self.player_num == 2:
            self.player_2_damage = player_damage            
        print(f"Player {self.player_num} dealt {damage_dealt} damage to Player {opposite_player_num}!")
        print(f"Player {opposite_player_num} Percentage: {player_damage}")
        return player_damage

    # Here we check if the move happens to be enough to win the game
    def stock_check(self, damage):
        if damage >= 150 and self.player_num == 2:
            death_chance = random.randrange(0, 100, 3)
            if death_chance >= 50:
                raise GameOverException("Player 1 has been defeated! Player 2 wins!")
        if damage >= 150 and self.player_num == 1:
            death_chance = random.randrange(0, 100, 3)
            print(death_chance)
            if death_chance >= 50:
                raise GameOverException("Player 2 has been defeated! Player 1 wins!")

    # We also just check on the direction that moves use here
    def parse_smash_direction(self, i, tokens):
        if i < len(tokens):
            direction = tokens[i].value.upper()
            return direction
        else:
            return None

# Ends the game
class GameOverException(Exception):
    pass

# This is where the game starts at and how we start inputting text for the actual match
print('READY...')
print('GO!')
parser = SmashScriptParser()
while True:
    text = input('SmashScript --> ')
    random.seed()
    tokens = tokenize(text)
    parser.parse(tokens)