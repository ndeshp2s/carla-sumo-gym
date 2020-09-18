from gym.envs.registration import register

register(
    id='Urban-v0',
    entry_point='environments.urban_environment.urban_env:UrbanEnv',
)