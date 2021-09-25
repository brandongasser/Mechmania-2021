from networking.io import Logger
from game import Game
from api import game_util
from model.position import Position
from model.decisions.move_decision import MoveDecision
from model.decisions.action_decision import ActionDecision
from model.decisions.buy_decision import BuyDecision
from model.decisions.harvest_decision import HarvestDecision
from model.decisions.plant_decision import PlantDecision
from model.decisions.do_nothing_decision import DoNothingDecision
from model.tile_type import TileType
from model.item_type import ItemType
from model.crop_type import CropType
from model.upgrade_type import UpgradeType
from model.game_state import GameState
from model.player import Player
from api.constants import Constants

constants = Constants()

def clamp(val: int, lower_bound: int, upper_bound: int):
    return max(lower_bound, min(val, upper_bound))

def can_harvest_or_plant(game_state: GameState, my_player: Player, tile_pos: Position):
    player_number = 1
    if (my_player.name == game_state.player1.name):
        player_number == 0
    scarecrow_effect = game_state.tile_map.get_tile(tile_pos.x, tile_pos.y).scarecrow_effect
    return not (scarecrow_effect == 2 or (scarecrow_effect == 1 and player_number == 0 or scarecrow_effect == 1 and player_number == 0))

def find_next_pos(my_player: Player, target_position: Position):
    y_error = clamp(target_position.y - my_player.position.y, -my_player.max_movement, my_player.max_movement)
    x_error = clamp(target_position.x - my_player.position.x, -my_player.max_movement + abs(y_error), my_player.max_movement - abs(y_error))
    if not game_util.valid_position(Position(my_player.position.x + x_error, my_player.position.y + y_error)):
        return my_player.position
    return Position(my_player.position.x + x_error, my_player.position.y + y_error)

def is_carrying_crop(my_player: Player, crop_type: CropType):
    return my_player.harvested_inventory.__contains__(crop_type)

def within_plant_range(my_player: Player, target_pos: Position):
    return game_util.distance(my_player.position, target_pos) <= my_player.plant_radius

def within_harvest_range(my_player: Player, target_pos: Position):
    return game_util.distance(my_player.position, target_pos) <= my_player.harvest_radius

def get_plant_tiles(my_player: Player):
    positions = []
    for x in range(my_player.position.x - my_player.plant_radius, my_player.position.x + my_player.plant_radius):
        for y in range(my_player.position.y - my_player.plant_radius, my_player.position.y + my_player.plant_radius):
            position = Position(x, y)
            positions.append(position)
    
    for position in positions:
        if not game_util.valid_position(position):
            positions.remove(position)
    
    return positions

def get_harvest_tiles(my_player: Player):
    positions = []
    for x in range(my_player.position.x - my_player.harvest_radius, my_player.position.x + my_player.harvest_radius):
        for y in range(my_player.position.y - my_player.harvest_radius, my_player.position.y + my_player.harvest_radius):
            position = Position(x, y)
            positions.append(position)
    
    for position in positions:
        if not game_util.valid_position(position):
            positions.remove(position)
    
    return positions