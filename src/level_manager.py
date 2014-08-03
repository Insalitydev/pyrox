__author__ = 'Insality'

import generator.dungeon_gen
import level
from constants import *
from resource import *
from entities.map.tile import Tile
from random import randint

class LevelManager:
    def __init__(self):
        pass

    def generate_level(self, room_count):
        ascii_lvl = generator.dungeon_gen.generate(room_count)
        lvl = self.ascii_to_level(ascii_lvl)
        return lvl

    def load_level(self):
        pass

    def save_level(self):
        pass

    def get_level(self, level):
        pass

    def ascii_to_level(self, ascii_lvl):

        width = len(ascii_lvl[0])
        height = len(ascii_lvl)
        print ("Translate ascii to obj. %i:%i" % (width, height))
        dungeon = [[None for col in range(width)] for row in range(height)]

        for y in reversed(range(height)):
            for x in range(width):
                if ascii_lvl[y][x] == TILE_SOLID or ascii_lvl[y][x] ==TILE_EMPTY:
                    type = world_stone
                elif ascii_lvl[y][x] == TILE_FLOOR or ascii_lvl[y][x] == TILE_DOOR:
                    chance = randint(0, 1000)
                    if chance <= 5:
                        type = floor_dungeon_crack
                    else:
                        type = floor_dungeon
                elif ascii_lvl[y][x] == TILE_WALL:
                    type = wall_dungeon
                else:
                    type = None

                if not type==None:
                    position=(x*TILE_SIZE, TILE_ANCHOR[1] + y*TILE_SIZE)
                    tile = Tile(type, position[0], position[1])
                    dungeon[y][x] = tile

        return level.Level(dungeon)


_inst = LevelManager()
generate_level = _inst.generate_level
load_level = _inst.load_level
save_leve = _inst.save_level
get_level = _inst.get_level