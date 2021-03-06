# coding: utf-8
__author__ = 'Insality'

from src.constants import *
from random import randint, choice
from src.log import log


class Hall:
    def __init__(self, from_point, to_point):
        self.x_from, self.y_from = from_point
        self.x_to, self.y_to = to_point


class Room:
    def __init__(self, pos_x, pos_y, width, height):
        self.x = 0
        self.y = 0
        # pos in general map
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.width = width
        self.height = height

        self.center = (self.pos_x + self.width // 2, self.pos_y - self.height // 2)

        self.free_direction = DIRECTIONS[:]
        self.make_room()

    def make_room(self):
        self.room = [[TILE_SOLID for col in range(self.width)] for row in range(self.height)]
        _fill_with(self.room, self.x, self.y, self.width, self.height, TILE_WALL)
        _fill_with(self.room, self.x + 1, self.y + 1, self.width - 2, self.height - 2, TILE_FLOOR)

    def place_tile(self, x, y, tile):
        self.room[y][x] = tile

    def get_random_wall_pos(self, direction):
        dx, dy = 0, 0
        if (direction == UP or direction == DOWN):
            rnd = randint(1, self.width - 2)
        else:
            rnd = randint(1, self.height - 2)

        if direction == UP:
            dx, dy = rnd, 0
        elif direction == DOWN:
            dx, dy = rnd, self.height - 1
        elif direction == RIGHT:
            dx, dy = self.width - 1, rnd
        elif direction == LEFT:
            dx, dy = 0, rnd

        return dx + self.pos_x, dy + self.pos_y

    def get_random_pos(self):
        x = randint(1, self.width-2) + self.pos_x
        y = randint(1, self.height-2) + self.pos_y
        return x, y

    def overlaps(self, other):
        return ( abs(self.center[0] - other.center[0]) < (self.width // 2) + (other.width // 2) and
                 abs(self.center[1] - other.center[1]) < (self.width // 2) + (other.height // 2) )


class Dungeon:
    def __init__(self, room_count):

        # random.seed(10)
        self.room_count = room_count
        self.width = 0
        self.height = 0

        self.rooms = []
        self.halls = []
        self.dungeon = []

    def generate(self):
        if len(self.rooms) <= 0:
            self.make_first_room(0, 0, randint(ROOM_MIN_WIDTH, ROOM_MAX_WIDTH),
                                 randint(ROOM_MIN_HEIGHT, ROOM_MAX_HEIGHT))

        while (len(self.rooms) < self.room_count):
            self.make_random_room()

        self.compile()

    def make_random_room(self):
        assert len(self.rooms) > 0, "A main room must me created"

        prefer_direction = set()
        if (self.width > self.height):
            prefer_direction.add(UP)
            prefer_direction.add(DOWN)
        else:
            prefer_direction.add(RIGHT)
            prefer_direction.add(LEFT)

        rooms = filter(lambda x: len(x.free_direction) > 0 and len(set(x.free_direction) & prefer_direction) > 0,
                       self.rooms)
        # TODO: ставить комнату в непредпочтитетльную сторону при остутствии предпочтительных?

        room_from = choice(rooms)
        dirs = set(room_from.free_direction) & prefer_direction
        direction = choice(list(dirs))
        door_from = room_from.get_random_wall_pos(direction)

        room_new = None
        for i in range(GEN_MAX_TRY_PLACE_ROOM):
            hall_len = randint(HALL_MIN_LENGTH, HALL_MAX_LENGTH)
            door_new = get_new_pos_by_direction(door_from[0], door_from[1], hall_len, direction)

            room_width = randint(ROOM_MIN_WIDTH, ROOM_MAX_WIDTH)
            # if (room_width == 3):
            #     room_height = 3
            # else:
            room_height = randint(ROOM_MIN_HEIGHT, ROOM_MAX_HEIGHT)
            room_x = door_new[0]
            room_y = door_new[1]
            if (direction == UP):
                room_x -= room_width // 2
                room_y -= room_height - 1
            elif (direction == RIGHT):
                room_y -= room_height // 2
            elif (direction == DOWN):
                room_x -= room_width // 2
            elif (direction == LEFT):
                room_y -= room_height // 2
                room_x -= room_width - 1

            room_new = Room(room_x, room_y, room_width, room_height)
            hall_new = Hall(door_from, door_new)

            for room in self.rooms:
                if room_new.overlaps(room):
                    room_new = None
                    break

        # If new room was not created
        if (room_new == None):
            log("Cannot create new room, remove aviable direction")
            room_from.free_direction.remove(direction)
            return

        room_from.free_direction.remove(direction)
        room_new.free_direction.remove((direction + 2) % 4)

        self.halls.append(hall_new)
        self.rooms.append(room_new)
        self.compile()

    def make_dungeon(self):
        self.dungeon = [[TILE_SOLID for col in range(self.width)] for row in range(self.height)]

    def make_first_room(self, x, y, width, height):
        self.rooms.append(Room(x, y, width, height))
        self.compile()

    def _is_empty(self, x, y, width, height):
        for i in range(y, y + height):
            for j in range(x, x + width):
                if (not self.dungeon[i][j] == TILE_EMPTY):
                    return False
        return True

    def place_room(self, room):
        offset_x = self.room_offset_x + room.pos_x
        offset_y = self.room_offset_y +room.pos_y
        for i in range(room.height):
            for j in range(room.width):
                self.dungeon[i + offset_y][j + offset_x] = room.room[i][j]

    def place_hall(self, hall):
        from_x = hall.x_from + self.room_offset_x
        from_y = hall.y_from + self.room_offset_y
        to_y = hall.y_to + self.room_offset_y
        to_x = hall.x_to + self.room_offset_x

        from_pos = (from_x, from_y)
        to_pos = (to_x, to_y)

        if (from_pos > to_pos):
            from_pos, to_pos = to_pos, from_pos

        # placing wall with width = 3 between points
        for x in range(from_pos[0], to_pos[0] + 1):
            for y in range(from_pos[1], to_pos[1] + 1):
                if (x > from_pos[0] and x < to_pos[0] or y > from_pos[1] and y < to_pos[1]):
                    self.dungeon[y-1][x] = TILE_WALL
                    self.dungeon[y+1][x] = TILE_WALL
                    self.dungeon[y][x-1] = TILE_WALL
                    self.dungeon[y][x+1] = TILE_WALL

        # placing floor between two points
        for x in range(from_pos[0], to_pos[0] + 1):
            for y in range(from_pos[1], to_pos[1] + 1):
                self.dungeon[y][x] = TILE_FLOOR

        self.dungeon[from_y][from_x] = TILE_DOOR
        self.dungeon[to_y][to_x] = TILE_DOOR

    def compile(self):
        assert len(self.rooms) > 0

        # Calculating borders of all rooms
        min_x, max_x = self.rooms[0].pos_x, self.rooms[0].pos_x + self.rooms[0].width
        min_y, max_y = self.rooms[0].pos_y, self.rooms[0].pos_y + self.rooms[0].height

        for room in self.rooms:
            if min_x > room.pos_x:
                min_x = room.pos_x
            if min_y > room.pos_y:
                min_y = room.pos_y
            if max_x < room.pos_x + room.width:
                max_x = room.pos_x + room.width
            if max_y < room.pos_y + room.height:
                max_y = room.pos_y + room.height

        # +2 - add one-width WORLD_STONE around map
        self.width = max_x - min_x + 2
        self.height = max_y - min_y + 2

        # offsets for start with (0,0), +1 - world-stone border
        self.room_offset_x = -min_x + 1
        self.room_offset_y = -min_y + 1

        self.make_dungeon()


        for room in self.rooms:
            self.place_room(room)

        for hall in self.halls:
            self.place_hall(hall)
    #    selecting start and exit pos:
    #     TODO: rework this +offset pos
        pos = self.rooms[0].get_random_pos()
        self.dungeon[pos[1] + self.room_offset_y][pos[0] + self.room_offset_x] = TILE_ENTER
        pos = self.rooms[-1].get_random_pos()
        self.dungeon[pos[1] + self.room_offset_y][pos[0] + self.room_offset_x] = TILE_EXIT

        for room in self.rooms[1:]:
            self.place_enemy(room)
        # self.crop_solid()

    def place_enemy(self, room):
        for i in range(2):
            pos = room.get_random_pos()
            self.dungeon[pos[1] + self.room_offset_y][pos[0] + self.room_offset_x] = TILE_ENEMY

    def crop_solid(self):
        for y in range(1, self.height-1):
            for x in range(1, self.width-1):
                if (not TILE_WALL in self.get_neighbors8(x, y)):
                    if (self.dungeon[y][x] == TILE_SOLID):
                        self.dungeon[y][x] = TILE_EMPTY

    def get_neighbors8(self, x, y):
        neightbors = []
        neightbors.append(self.dungeon[y+1][x-1])
        neightbors.append(self.dungeon[y+1][x])
        neightbors.append(self.dungeon[y+1][x+1])
        neightbors.append(self.dungeon[y][x-1])
        neightbors.append(self.dungeon[y][x+1])
        neightbors.append(self.dungeon[y-1][x-1])
        neightbors.append(self.dungeon[y-1][x])
        neightbors.append(self.dungeon[y-1][x+1])
        return neightbors

    def draw(self):
        for row in self.dungeon:
            print(''.join(row))


def _fill_with(source, x, y, width, height, type):
    for i in range(y, y + height):
        for j in range(x, x + width):
            source[i][j] = type


def get_new_pos_by_direction(x, y, len, direction):
    if (direction == RIGHT):
        x += len
    elif (direction == UP):
        y -= len
    elif (direction == LEFT):
        x -= len
    elif (direction == DOWN):
        y += len
    return x, y


def test_generator(room_count):
    assert room_count >= 2, "Room_count must be more than 2"

    dungeon = Dungeon(room_count)

    dungeon.generate()
    dungeon.draw()
    print(dungeon.width, dungeon.height)

def generate(room_count):
    assert room_count >= 2, "Room_count must be more than 2"
    dungeon = Dungeon(room_count)

    dungeon.generate()
    return dungeon.dungeon

if __name__ == "__main__":
    test_generator(6)
