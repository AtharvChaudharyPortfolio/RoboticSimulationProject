import pygame
pygame.init()

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from stable_baselines3.common.monitor import Monitor
from gym_wrapper import RobotEnv
from Renderer import Renderer
from SceneRandomization import Environment


env_inner = Environment(rows=15, cols=15, start=(2,1), end=(12,12), cell_size=40)
renderer = Renderer(env_inner)


def make_eval_env():
    e = RobotEnv()
    e.env = env_inner
    return Monitor(e)


env = DummyVecEnv([make_eval_env])
env = VecNormalize.load("vec_normalize.pkl", env)
env.training = False
env.norm_reward = False

model = PPO.load("robot_ppo_final", env=env)

obs = env.reset()
clock = pygame.time.Clock()
running = True
total_reward = 0
episode = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    action, _ = model.predict(obs, deterministic=True)
    obs, reward, done, info = env.step(action)
    total_reward += float(reward[0])

    renderer.draw(env_inner)
    clock.tick(60)

    if done[0]:
        print(f"Episode {episode} | reward: {total_reward:.2f}")
        total_reward = 0
        episode += 1
        obs = env.reset()

pygame.quit()