import pygame
import math
import random
from robot import Robot
class Environment:
    def __init__(self,rows, cols, start, end, cell_size):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.height = rows * cell_size
        self.width = cols * cell_size
        self.start = start
        self.end = end
        self.path = self.init_path(start, end)
        self.walls = self.init_walls()
        self.robot = Robot(start, 20)
    def init_path(self, start, end, bias=0.75, max_steps=2000, corridor_rad=1):
        carved = set()
        cur = start
        steps = 0
        while cur != end and steps < max_steps:
            carved.add(cur)
            cx, cy = cur
            for dx in range(-corridor_rad, corridor_rad + 1):
                for dy in range(-corridor_rad, corridor_rad+1):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < self.cols and 0 <= ny < self.rows:
                        carved.add((nx, ny))
            dx_goal = end[0] - cur[0]
            dy_goal = end[1] - cur[1]
            goal_dirs = []
            if dx_goal > 0: goal_dirs.append((1, 0))
            if dx_goal < 0: goal_dirs.append((-1, 0))
            if dy_goal > 0: goal_dirs.append((0, 1))
            if dy_goal < 0: goal_dirs.append((0, -1))
            all_dirs = [(1,0), (-1,0), (0, 1), (0, -1)]
            if random.random() < bias and goal_dirs:
                dx, dy = random.choice(goal_dirs)
            else:
                dx, dy = random.choice(all_dirs)
            nx, ny = cur[0] + dx, cur[1] + dy
            nx = max(0, min(self.cols - 1, nx))
            ny = max(0, min(self.rows - 1, ny))
            cur = (nx, ny)
            steps += 1
        carved.add(end)
        return carved

    def init_walls(self):
        wall_cells = [(x, y) for x in range(self.cols) for y in range(self.rows)
                     if (x, y not in self.path)]
        return [pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                for x, y in wall_cells]
    def reset(self):
        self.path = self.init_path(self.start, self.end)
        self.walls = self.init_walls()

    def _get_obs(self):
        return None
    def _get_reward_done(self):
        return None
    def step(self, action):
        self.robot.apply_action(action)  # 1. set wheel speeds from policy's action
        self.robot.update(self.dt)  # 2. integrate motion using those speeds

        obs = self._get_obs()
        reward, done = self._get_reward_done()
        return obs, reward, done, {}

class Renderer:
    def __init__(self, env):
        pygame.display.set_caption("Robotic Simulation")
        self.screen = pygame.display.set_mode((env.grid_w, env.grid_h))
        self.colors = {}
