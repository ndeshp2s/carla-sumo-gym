from gym.envs.registration import register

register(
    id='Urban-v0',
    entry_point='environments.urban_env_0.env:UrbanEnv',
)

register(
    id='Urban-v1',
    entry_point='environments.urban_env_1.env:UrbanEnv1',
)
