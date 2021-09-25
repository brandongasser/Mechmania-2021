from model import crop
from model.crop import Crop
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
import helpers

import random

logger = Logger()
constants = Constants()
moving_to_sell = True
has_planted = False
plant_pos = Position(constants.BOARD_WIDTH // 2, 1)

def get_move_decision(game: Game) -> MoveDecision:
    """
    Returns a move decision for the turn given the current game state.
    This is part 1 of 2 of the turn.

    Remember, you can only sell crops once you get to a Green Grocer tile,
    and you can only harvest or plant within your harvest or plant radius.

    After moving (and submitting the move decision), you will be given a new
    game state with both players in their updated positions.

    :param: game The object that contains the game state and other related information
    :returns: MoveDecision A location for the bot to move to this turn
    """
    game_state: GameState = game.get_game_state()
    logger.debug(f"[Turn {game_state.turn}] Feedback received from engine: {game_state.feedback}")

    # Select your decision here!
    my_player: Player = game_state.get_my_player()
    pos: Position = my_player.position

    decision = MoveDecision(pos)

    if (moving_to_sell):
        decision = MoveDecision(helpers.find_next_pos(my_player, Position((constants.BOARD_WIDTH // 2), 0)))
    elif (not pos.y == plant_pos.y):
        decision = MoveDecision(helpers.find_next_pos(my_player, plant_pos))

    logger.debug(f"[Turn {game_state.turn}] Sending MoveDecision: {decision}")
    return decision

def get_action_decision(game: Game) -> ActionDecision:
    """
    Returns an action decision for the turn given the current game state.
    This is part 2 of 2 of the turn.

    There are multiple action decisions that you can return here: BuyDecision,
    HarvestDecision, PlantDecision, or UseItemDecision.

    After this action, the next turn will begin.

    :param: game The object that contains the game state and other related information
    :returns: ActionDecision A decision for the bot to make this turn
    """
    game_state: GameState = game.get_game_state()
    logger.debug(f"[Turn {game_state.turn}] Feedback received from engine: {game_state.feedback}")

    # Select your decision here!
    my_player: Player = game_state.get_my_player()
    pos: Position = my_player.position
    # Let the crop of focus be the one we have a seed for, if not just choose a random crop

    decision = DoNothingDecision()
    global moving_to_sell, has_planted, plant_pos

    if (not game_util.valid_position(plant_pos)):
        return decision
    
    if (pos.x == constants.BOARD_WIDTH // 2 and pos.y == 0 and moving_to_sell):
        decision = BuyDecision([CropType.POTATO], [5])
        moving_to_sell = False
    elif (pos.y == plant_pos.y and not has_planted):
        plants = [CropType.POTATO, CropType.POTATO, CropType.POTATO, CropType.POTATO, CropType.POTATO]
        plant_tiles = [Position(pos.x, pos.y), Position(pos.x - 1, pos.y), Position(pos.x + 1, pos.y), Position(pos.x, pos.y - 1), Position(pos.x, pos.y + 1)]
        for pos in plant_tiles:
            if not game_util.valid_position(pos):
                plant_tiles.remove(pos)
                del plants[0]
        decision = PlantDecision(plants, plant_tiles)
        has_planted = True
    elif (game_state.tile_map.get_tile(pos.x, pos.y).crop.growth_timer == 0 and has_planted):
        harvest_tiles = [Position(pos.x, pos.y), Position(pos.x - 1, pos.y), Position(pos.x + 1, pos.y), Position(pos.x, pos.y - 1), Position(pos.x, pos.y + 1)]
        for pos in harvest_tiles:
            if not game_util.valid_position(pos):
                harvest_tiles.remove(pos)
        decision = HarvestDecision(harvest_tiles)
        moving_to_sell = True
        has_planted = False
        plant_pos = Position(plant_pos.x, plant_pos.y + 3)

    logger.debug(f"[Turn {game_state.turn}] Sending ActionDecision: {decision}")
    return decision


def main():
    """
    Competitor TODO: choose an item and upgrade for your bot
    """
    game = Game(ItemType.COFFEE_THERMOS, UpgradeType.RABBITS_FOOT)

    while (True):
        try:
            game.update_game()
        except IOError:
            exit(-1)
        game.send_move_decision(get_move_decision(game))

        try:
            game.update_game()
        except IOError:
            exit(-1)
        game.send_action_decision(get_action_decision(game))


if __name__ == "__main__":
    main()
