import pygame
import math
import random
from robot import Robot
import numpy as np


class Environment:
    def __init__(self,rows, cols, start, end, cell_size):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.height = rows * cell_size
        self.width = cols * cell_size
        self.start = start
        self.start_px = pygame.Vector2(start[0]*cell_size + cell_size/2, start[1]*cell_size + cell_size/2)
        self.end = end
        self.end_px = pygame.Vector2(end[0]*cell_size + cell_size/2, end[1]*cell_size + cell_size/2)
        self.max_steps = 1000
        self.steps = 0
        self.path = self.init_path(start, end, max_steps=self.max_steps)
        self.walls = self.init_walls()
        self.robot = Robot(self.start_px, 20)
        self.dt = 0.05
        self.goal = self.end_px
        self.max_range = 200
        self.prev_dist, _ = self._relative_goal(pygame.Vector2(self.robot.x, self.robot.y), self.robot.theta)
        self.progress_scale = 0.05
        self.step_penalty = 0.001
        self.proximity_penalty_scale = 0.5
        self.collision_penalty = 20.0
        self.goal_bonus = 15.0
        self.timeout_penalty = 1.0
        self.goal_radius = self.cell_size * 1.5
        self.collision_threshold = self.robot.w/2 * 1.1
        self.max_dist = math.sqrt(self.width ** 2 + self.height ** 2)

    def init_path(self, start, end, bias=0.2, max_steps=2000, corridor_rad=1):
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
                if (x, y) not in self.path]
        walls = [pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                for x, y in wall_cells]
        border_thickness = self.cell_size
        walls += [
            pygame.Rect(0, 0, self.width, border_thickness),  # top
            pygame.Rect(0, self.height - border_thickness, self.width, border_thickness),  # bottom
            pygame.Rect(0, 0, border_thickness, self.height),  # left
            pygame.Rect(self.width - border_thickness, 0, border_thickness, self.height),  # right
        ]
        return walls

    def reset(self):
        self.path = self.init_path(self.start, self.end)
        self.walls = self.init_walls()
        self.steps = 0
        self.start_px = pygame.Vector2(self.start[0] * self.cell_size + self.cell_size / 2,
                                  self.start[1] * self.cell_size + self.cell_size / 2)
        self.robot.reset(self.start_px)
        origin = pygame.Vector2(self.robot.x, self.robot.y)
        state = self.robot.get_state()
        ray_dists = [
            self.robot.cast_ray(origin, state["theta"] + offset, self.max_range, self.walls)
            for offset in self.robot.ray_offsets
        ]
        self.prev_dist, _ = self._relative_goal(origin, self.robot.theta)
        return self._get_obs(ray_dists)

    def _proximity_penalty(self, ray_dists):
        min_dist = min(ray_dists)
        if min_dist >= self.max_range / 2:
            return 0.0
        closeness = 1 - (min_dist / (self.max_range / 2))
        return closeness * self.proximity_penalty_scale

    def _relative_goal(self, origin, theta):
        to_goal = self.goal - origin
        distance = to_goal.length()

        goal_angle = math.atan2(-to_goal.y, to_goal.x)
        bearing = goal_angle - theta
        bearing = (bearing + math.pi) % (2 * math.pi) - math.pi

        return distance, bearing

    def _get_obs(self, ray_dists):
        state = self.robot.get_state()
        origin = pygame.Vector2(state["x"], state["y"])
        goal_dist, goal_bearing = self._relative_goal(origin, state["theta"])

        max_dist = math.sqrt(self.width ** 2 + self.height ** 2)
        goal_dist_norm = goal_dist / max_dist
        ray_dists_norm = [d / self.max_range for d in ray_dists]

        v = (state["vl"] + state["vr"]) / 2
        omega = (state["vr"] - state["vl"]) / self.robot.w
        return np.array([*ray_dists_norm, goal_dist_norm, goal_bearing, v, omega], dtype=np.float32)

    def crashed(self):
        if (self.robot.x < 0 or self.robot.x > self.width or
                self.robot.y < 0 or self.robot.y > self.height):
            return True
        for wall in self.walls:
            if wall.colliderect(self.robot.rect):
                return True
        return False

    def _get_reward_done(self, ray_dist):
        state = self.robot.get_state()
        origin = pygame.Vector2(state["x"], state["y"])
        new_dist, _ = self._relative_goal(origin, state["theta"])  # bearing unused here

        progress = self.prev_dist - new_dist
        self.prev_dist = new_dist

        reward = progress * self.progress_scale
        reward -= self.step_penalty
        reward -= self._proximity_penalty(ray_dist)

        done = False
        if self.crashed():
            reward -= self.collision_penalty
            done = True
        elif new_dist < self.goal_radius:
            time_bonus = (self.max_steps - self.steps) / self.max_steps * 5
            reward += self.goal_bonus + time_bonus
            done = True
        elif self.steps >= self.max_steps:
            reward -= self.timeout_penalty
            done = True

        return reward, done

    def step(self, action):
        self.robot.apply_action(action)
        self.robot.update(self.dt)
        state = self.robot.get_state()
        origin = pygame.Vector2(state["x"], state["y"])
        ray_dist = [
            self.robot.cast_ray(origin, state["theta"] + offset, self.max_range, self.walls)
            for offset in self.robot.ray_offsets
        ]
        obs = self._get_obs(ray_dist)
        reward, done = self._get_reward_done(ray_dist)
        self.steps += 1
        return obs, reward, done, {}


