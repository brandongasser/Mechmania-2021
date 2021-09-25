from model.decisions import do_nothing_decision
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

import random

logger = Logger()
constants = Constants()

GREEN_GROCER_POS = Position((constants.BOARD_WIDTH // 2), 0)

def can_harvest(game_state: GameState, pos: Position, my_player_number: int):
    scarecrow_effect = game_state.tile_map.get_tile(pos.x, pos.y).scarecrow_effect
    return not (scarecrow_effect == 2 or (scarecrow_effect == 1 and my_player_number == 0 or scarecrow_effect == 0 and my_player_number == 1))

def find_harvest_positions(my_player: Player):
    harvest_positions = []
    for x in range((my_player.position.x - my_player.harvest_radius), (my_player.position.x + my_player.harvest_radius)):
        for y in range((my_player.position.y - my_player.harvest_radius), (my_player.position.y + my_player.harvest_radius)):
            harvest_positions.append(Position(x, y))
    return harvest_positions

def find_next_pos(my_pos: Position, target_pos: Position):
    if (my_pos.x == target_pos.x and my_pos.y == target_pos.y):
        return target_pos
    if (game_util.distance(my_pos, target_pos) <= 10):
        return target_pos
    else:
        if (my_pos.y > target_pos.y):
            if (my_pos.y - target_pos.y <= 10):
                return Position(my_pos.x, target_pos.y)
            else:
                return Position(my_pos.x, (my_pos.y - 10))
        elif (my_pos.y < target_pos.y):
            if (target_pos.y - my_pos.y <= 10):
                return Position(my_pos.x, target_pos.y)
            else:
                return Position(my_pos.x, (my_pos.y + 10))
        elif (my_pos.x > target_pos.x):
            if (my_pos.x - target_pos.x <= 10):
                return Position(target_pos.x, my_pos.y)
            else:
                return Position((my_pos.x - 10), my_pos.y)
        elif (my_pos.x < target_pos.x):
            if (target_pos.x - my_pos.x <= 10):
                return Position(target_pos.x, my_pos.y)
            else:
                return Position((my_pos + 10), my_pos.y)

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
    my_player_number = 0
    if (my_player.name == game_state.player1.name):
        my_player_number = 0
    else:
        my_player_number = 1
    opponent_player: Player = game_state.get_opponent_player()
    pos: Position = my_player.position
    logger.info(f"Currently at {my_player.position}")

    decision = DoNothingDecision()

    if my_player.harvested_inventory.__contains__(CropType.GRAPE):
        decision = MoveDecision(find_next_pos(pos, GREEN_GROCER_POS))
    else:
        grape_tiles = []
        for x in range(constants.BOARD_WIDTH):
            for y in range(constants.BOARD_HEIGHT):
                if game_state.tile_map.get_tile(x, y).crop == CropType.GRAPE:
                    grape_tiles.append(Position(x, y))

        best_pos = pos
        for grape_pos in grape_tiles:
            if best_pos == pos and can_harvest(game_state, grape_pos, my_player_number):
                best_pos = grape_pos
            if game_util.distance(pos, grape_pos) < game_util.distance(pos, best_pos) and can_harvest(game_state, grape_pos, my_player_number):
                best_pos = grape_pos

        decision = MoveDecision(find_next_pos(pos, best_pos))

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

    decision = HarvestDecision(find_harvest_positions(my_player))

    logger.debug(f"[Turn {game_state.turn}] Sending ActionDecision: {decision}")
    return decision


def main():
    """
    Competitor TODO: choose an item and upgrade for your bot
    """
    game = Game(ItemType.COFFEE_THERMOS, UpgradeType.SCYTHE)

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
