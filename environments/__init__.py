from gym.envs.registration import register

register(
    id='Urban-v0',
    entry_point='environments.urban_env.urban_env_0:UrbanEnv0',
)