import pygame
from SceneRandomization import Environment
from Renderer import Renderer

env = Environment(rows=40, cols=40, start=(5, 1), end=(35, 25), cell_size=25)
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