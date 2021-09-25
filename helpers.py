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

def can_harvest(game_state: GameState, my_player: Player, tile_pos: Position):
    player_number = 1
    if (my_player.name == game_state.player1.name):
        player_number == 0
    scarecrow_effect = game_state.tile_map.get_tile(tile_pos.x, tile_pos.y).scarecrow_effect
    return not (scarecrow_effect == 2 or (scarecrow_effect == 1 and player_number == 0 or scarecrow_effect == 1 and player_number == 0))