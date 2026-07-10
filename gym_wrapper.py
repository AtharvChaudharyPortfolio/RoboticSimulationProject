import pygame
pygame.init()

import gymnasium as gym
import numpy as np
from gymnasium import spaces
from SceneRandomization import Environment


class RobotEnv(gym.Env):
    def __init__(self, rows=15, cols=15, start=(2, 1), end=(12, 12), cell_size=40):
        super().__init__()
        self.env = Environment(rows, cols, start, end, cell_size)
        self.observation_space = spaces.Box(
            low=np.array([0]*7 + [0, -np.pi, -np.inf, -np.inf], dtype=np.float32),
            high=np.array([self.env.max_range]*7 + [np.inf, np.pi, np.inf, np.inf], dtype=np.float32),
            dtype=np.float32
        )
        self.action_space = spaces.Box(
            low=np.float32(-1),
            high=np.float32(1),
            shape=(2,),
            dtype=np.float32
        )
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        obs=self.env.reset()
        return obs, {}
    def step(self, action):
        obs, reward, done, info = self.env.step(action)
        print(f"done: {done}, steps: {self.env.steps}, reward: {reward:.3f}")
        return obs, reward, done, False, info
    def render(self):
        pass


