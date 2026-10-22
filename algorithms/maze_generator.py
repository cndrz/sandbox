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

def manhattan(a: Point, b: Point) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def zero(a: Point, b: Point) -> int:
    return 0

def reconstruct(came_from: dict[Point, Point], end: Point) -> list[Point]:
    path = [end]
    while path[-1] in came_from:
        path.append(came_from[path[-1]])
    return path[::-1]

def astar(
    grid: Grid,
    start: Point,
    goal: Point,
    heuristic: Callable[[Point, Point], int] = manhattan,
) -> dict:
    h, w = len(grid), len(grid[0])
    g_score: dict[Point, int] = {start: 0}
    came_from: dict[Point, Point] = {}
    closed: set[Point] = set()
    open_heap = [(heuristic(start, goal), 0, start)]

    while open_heap:
        _, neg_g, cur = heapq.heappop(open_heap)
        if cur in closed:
            continue
        closed.add(cur)

    if cur == goal:
        return{"path": reconstruct(came_from, cur), "closed": closed}

    g = -neg_g
    for dx, dy in DIRS4:
        nx, ny = cur[0] + dx, cur[1] + dy
        nxt = (nx, ny)
        if not (0 <= nx < w and 0 <= ny < h) or grid[ny][nx] == 1:
            continue
        if nxt in closed:
            continue

        tentative = g + 1
        if tentative < g_score.get(nxt, float("inf")):
            g_score[nxt] = tentative
            came_from[nxt] = cur
            f = tentative + heuristic(nxt, goal)
            heapq.heappush(open_heap, (f, -tentative, nxt))

    return {"path": None, "closed": closed}
