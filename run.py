# Recursive Backtracking maze generation algorithm, modified to create no dead ends.

import os
import random
import numpy as np
import pyxel


class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.go = {'N': np.array([0, 2]),
                   'E': np.array([2, 0]),
                   'S': np.array([0, -2]),
                   'W': np.array([-2, 0])}
        self.go_half = {key: (0.5 * value).astype(np.int) for key, value in self.go.items()}
        self.opposite = {'N': 'S', 'E': 'W', 'S': 'N', 'W': 'E'}

        # 0: path, 1: wall.
        self.data = np.ones((height, width), dtype=np.int)

    def generate(self):
        index = np.array([random.randint(0, self.height - 1),
                          random.randint(0, self.width - 1)])

        self.gen(index)

        self.random_break(index)

    def gen(self, index):
        end = True

        for direction in self.shuffle_directions():
            new_index = index + self.go[direction]

            if self.cell_valid(new_index) and not self.cell_visited(new_index):
                self.cell_move(index, new_index)
                self.gen(new_index)
                end = False

        # Remove dead ends.
        if end:
            self.random_break(index)

    def random_break(self, index):
        for direction in self.shuffle_directions():
            new_index = index + self.go[direction]

            if self.cell_valid(new_index) and self.cell_value(index + self.go_half[direction]) == 1:
                self.cell_move(index, new_index)
                break

    def cell_value(self, index):
        y, x = index
        return self.data[y, x]

    def cell_visited(self, index):
        return self.cell_value(index) != 1

    def cell_valid(self, index):
        y, x = index

        if y < 0 or y >= self.height or x < 0 or x >= self.width:
            return False

        return True

    def cell_move(self, index, new_index):
        y, x = new_index
        self.data[y, x] = 0

        y, x = (index + 0.5 * (new_index - index)).astype(np.int)
        self.data[y, x] = 0

    def shuffle_directions(self):
        return random.sample(self.go.keys(), len(self.go.keys()))

    def itermaze(self):
        return self.__iter2d__(self.data)

    @staticmethod
    def __iter2d__(data):
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                yield np.array([i, j]), data[i, j]

    def __str__(self):
        data = -1 * np.ones((self.height + 2, self.width + 2))

        out = ''

        wall = '#'
        path = '0'
        border = '+'

        data[1:-1, 1:-1] = self.data

        for index, value in self.__iter2d__(data):
            if index[1] == 0:
                out += os.linesep

            if value == -1:
                out += border
            elif value == 0:
                out += path
            elif value == 1:
                out += wall

        return out


class Pyxelapp():
    def __init__(self, maze):
        self.maze = maze

        self.things = []
        self.init_things(10)

    def init_things(self, num_things):
        for i in range(num_things):
            while True:
                pos = np.array([random.randint(0, self.maze.height - 1),
                                random.randint(0, self.maze.width - 1)])
                direction = random.sample(self.maze.go.keys(), 1)[0]

                if self.feasible(pos):
                    self.things.append([pos, direction])
                    break

    def update_things(self):
        for i in range(len(self.things)):
            pos = self.things[i][0]
            direction = self.things[i][1]

            newpos = pos + self.maze.go_half[direction]

            if self.feasible(newpos):
                self.things[i][0] = newpos
            else:
                for new_direction in self.maze.shuffle_directions():
                    if new_direction == self.maze.opposite[direction] or new_direction == direction:
                        continue

                    newpos = pos + self.maze.go_half[new_direction]

                    if self.feasible(newpos):
                        self.things[i][0] = newpos
                        self.things[i][1] = new_direction
                        break

    def feasible(self, pos):
        return self.maze.cell_valid(pos) and self.maze.cell_value(pos) == 0

    def draw_things(self):
        for i in self.things:
            y, x = i[0]
            pyxel.rect(x, y, x, y, 1)

    def draw_maze(self):
        for index, value in self.maze.itermaze():
            y, x = index
            if value == 0:
                pyxel.rect(x, y, x, y, 7)
            elif value == 1:
                pyxel.rect(x, y, x, y, 3)
            elif value == 2:
                pyxel.rect(x, y, x, y, 5)

    def run(self):
        pyxel.init(self.maze.width, self.maze.height, caption='Maze', scale=10)
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        self.update_things()

    def draw(self):
        pyxel.cls(0)

        self.draw_maze()
        self.draw_things()


def run():
    maze = Maze(81, 41)
    maze.generate()

    Pyxelapp(maze).run()


if __name__ == '__main__':
    run()
