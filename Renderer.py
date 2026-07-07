import pygame
import math


class Renderer:
    def __init__(self, env):
        pygame.init()
        pygame.display.set_caption("Robotic Simulation")
        self.screen = pygame.display.set_mode((env.width, env.height))
        self.clock = pygame.time.Clock()
        self.colors = {
            "background": (200, 200, 200),
            "wall": (40, 40, 40),
            "robot": (0, 0, 255),
            "goal": (0, 255, 0),
            "ray": (255, 0, 0),
            "trajectory": (0, 0, 0)
        }

    def draw(self, env):
        self.screen.fill(self.colors["background"])
        self._draw_walls(env)
        self._draw_goal(env)
        self._draw_rays(env)
        self._draw_robot(env)
        self._draw_trajectory(env)
        pygame.display.flip()

    def _draw_walls(self, env):
        for wall in env.walls:
            pygame.draw.rect(self.screen, self.colors["wall"], wall)

    def _draw_goal(self, env):
        pygame.draw.circle(self.screen, self.colors["goal"],
    (int(env.goal.x), int(env.goal.y)),
           int(env.goal_radius))

    def _draw_robot(self, env):
        pygame.draw.rect(self.screen, self.colors["robot"], env.robot.rect)

    def _draw_rays(self, env):
        state = env.robot.get_state()
        origin = pygame.Vector2(state["x"], state["y"])
        for offset in env.robot.ray_offsets:
            angle = state["theta"] + offset
            direction = pygame.Vector2(math.cos(angle), -math.sin(angle))
            dist = env.robot.cast_ray(origin, angle, env.max_range, env.walls)
            end = origin + direction * dist
            pygame.draw.line(self.screen, self.colors["ray"],
                             (int(origin.x), int(origin.y)),
                             (int(end.x), int(end.y)), 1)

    def _draw_trajectory(self, env):
        tip = env.robot.trajectory()
        pygame.draw.line(self.screen, self.colors["trajectory"],
                         (int(env.robot.x), int(env.robot.y)),
                         (int(tip.x), int(tip.y)), 2)