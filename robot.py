import pygame
import math
from SceneRandomization import Environment
import numpy as np

class Robot:
    def __init__(self, startpos, width):
        self.m2p=3779.52 #meters to pixel conversion
        self.w=width
        self.x=startpos[0]
        self.y=startpos[1]
        self.theta = 0
        self.vl=0.01*self.m2p #left velocity
        self.vr=0.01*self.m2p #right velocity
        self.maxspeed=0.02*self.m2p
        self.rect=pygame(center=(self.x,self.y))
        self.pos = (self.x, self.y)

    def trajectory(self, look_ahead_time=2.0):
        v = (self.vl+self.vr)/2
        forward = pygame.Vector2(math.cos(self.theta), -math.sin(self.theta))
        t_origin = pygame.Vector2(self.x, self.y)
        return t_origin + forward*v*look_ahead_time
    def update(self, dt):
        self.vl = max(min(self.vl, self.maxspeed), -self.maxspeed)
        self.vr = max(min(self.vr, self.maxspeed), -self.maxspeed)

        v = (self.vl + self.vr) / 2
        omega = (self.vr - self.vl) / self.w

        self.x += v * math.cos(self.theta) * dt
        self.y -= v * math.sin(self.theta) * dt
        self.theta += omega * dt
        self.rect.center = (self.x, self.y)

    def apply_action(self, action):
        self.vl = np.clip(action[0], -1, 1) * self.maxspeed
        self.vr = np.clip(action[1], -1, 1) * self.maxspeed

