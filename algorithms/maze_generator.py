import heapq
import random
from typing import Callable, Optional

Point = tuple[int, int]
Grid = list[list[int]]

DIRS4 = [(0, -1), (1, 0), (0, 1), (-1, 0)]

def generate_maze(w: int, h: int, rng: random.Random) -> Grid:
    grid = [[1] * w for _ in range(h)]
    dirs = [(0, -2), (2, 0), (0, 2), (-2, 0)]
    stack = [(1, 1)]
    grid[1][1] = 0

    while stack:
        x, y = stack[-1]
        options = [
            (x + dx, y + dy , dx // 2, dy // 2)
            for dx, dy in dirs
            if 0 < x + dx < w - 1 and 0 < y + dy < h - 1
            and grid[y + dy][x + dx] == 1
        ]
        if not options:
            stack.pop()
            continue

        nx, ny, hx, hy = rng.choice(options)
        grid[y + hy][x + hx] = 0 # carve the wall between
        grid[ny][nx] = 0         # carve the next cell
        stack.append((nx, ny))
    return grid

def add_loops(grid: Grid, rng: random.Random, chance: float = 0.08) -> Grid:
    h, w = len(grid), len(grid[0])
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if grid[y][x] != 1 or rng.random() > chance:
                continue
            horizontal = grid[y][x - 1] == 0 and grid[y][x + 1] == 0
            vertical = grid[y - 1][x] == 0 and grid[y + 1][x] == 0
            if horizontal or vertical:
                grid[y][x] = 0
    return grid
    