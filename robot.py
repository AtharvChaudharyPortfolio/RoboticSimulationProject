import pygame
import math
import numpy as np

class Robot:
    def __init__(self, startpos, width):
        self.m2p = 3779.52 #meters to pixel conversion
        self.w = width
        self.x = startpos[0]
        self.y = startpos[1]
        self.theta = 0
        self.vl = 0.01*self.m2p #left velocity
        self.vr = 0.01*self.m2p #right velocity
        self.maxspeed = 0.02*self.m2p
        self.rect = pygame.Rect(self.x - self.w/2, self.y - self.w/2, self.w, self.w)
        self.pos = (self.x, self.y)
        self.num_rays = 7
        self.ray_fov = math.radians(180)
        self.ray_offsets = self._compute_ray_offsets()

    def _compute_ray_offsets(self):
        start = -self.ray_fov / 2
        step = self.ray_fov / (self.num_rays - 1)
        return [start + i * step for i in range(self.num_rays)]

    def trajectory(self, look_ahead_time=2.0):
        v = (self.vl+self.vr)/2
        forward = pygame.Vector2(math.cos(self.theta), -math.sin(self.theta))
        t_origin = pygame.Vector2(self.x, self.y)
        return t_origin + forward*v*look_ahead_time

    def get_state(self):
        return {
            "x": self.x, "y": self.y, "theta": self.theta,
            "vl": self.vl, "vr": self.vr,
        }
    def update(self, dt):
        self.vl = max(min(self.vl, self.maxspeed), -self.maxspeed)
        self.vr = max(min(self.vr, self.maxspeed), -self.maxspeed)

        v = (self.vl + self.vr) / 2
        omega = (self.vr - self.vl) / self.w

        self.x += v * math.cos(self.theta) * dt
        self.y -= v * math.sin(self.theta) * dt
        self.pos = (self.x, self.y)
        self.theta += omega * dt
        self.rect.center = (int(self.x), int(self.y))

    def apply_action(self, action):
        self.vl = np.clip(action[0], -1, 1) * self.maxspeed
        self.vr = np.clip(action[1], -1, 1) * self.maxspeed

    def cast_ray(self, origin, angle, max_range, walls):
        direction = pygame.Vector2(math.cos(angle), -math.sin(angle))
        end = origin + direction * max_range

        closest_dist = max_range
        for wall in walls:
            clipped = wall.clipline(origin, end)
            if clipped:
                p1, p2 = clipped
                d = min(origin.distance_to(p1), origin.distance_to(p2))
                if d < closest_dist:
                    closest_dist = d

        return closest_dist

    def reset(self, startpos):
        self.x = startpos[0]
        self.y = startpos[1]
        self.pos = (self.x, self.y)
        self.theta = 0
        self.vl = 0.01 * self.m2p
        self.vr = 0.01 * self.m2p
        self.rect = pygame.Rect(int(self.x - self.w / 2), int(self.y - self.w / 2), self.w, self.w)

