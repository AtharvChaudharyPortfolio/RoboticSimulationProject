import pygame
from SceneRandomization import Environment
from Renderer import Renderer

env = Environment(rows=30, cols=30, start=(5,1), end=(12,25), cell_size=35)
renderer = Renderer(env)
obs = env.reset()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    action = [0, 0]  # placeholder until your policy is wired up
    obs, reward, done, _ = env.step(action)
    renderer.draw(env)
    renderer.clock.tick(60)

    if done:
        obs = env.reset()

pygame.quit()