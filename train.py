import pygame
pygame.init()

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import VecNormalize

from gym_wrapper import RobotEnv


env = DummyVecEnv([lambda: Monitor(RobotEnv())])
env = VecNormalize(env, norm_obs=True, norm_reward=True, clip_obs=10.0)

checkpoint_cb = CheckpointCallback(
    save_freq=50_000,
    save_path="./checkpoints/",
    name_prefix="robot_ppo"
)

model = PPO(
    "MlpPolicy",
    env,
    learning_rate=1e-4,
    n_steps=2048,
    batch_size=64,
    n_epochs=5,
    gamma=0.99,
    max_grad_norm=0.5,
    vf_coef=0.25,
    gae_lambda=0.95,
    clip_range=0.2,
    ent_coef=0.05,
    policy_kwargs=dict(net_arch=[64, 64], log_std_init=0.0),
    verbose=1,
    tensorboard_log="./logs/"
)

model.learn(
    total_timesteps=2_000_000,
    callback=checkpoint_cb
)
model.save("robot_ppo_final")
env.save("vec_normalize.pkl")
print("Training Complete")
