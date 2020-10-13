import time

class Tester:
    def __init__(self, env, agent, spawner, params):
        self.env = env
        self.agent = agent
        self.spawner = spawner
        self.params = params


    def test(self):

        try:
            for ep in range(self.params.testing_episodes):
                state = self.env.reset()
                self.spawner.reset(config = self.env.config, spawn_points = self.env.walker_spawn_points, ev_id = self.env.get_ego_vehicle_id())

                average_speed = 0.0
                average_speed_steps = 0

                for step in range(self.params.testing_steps_per_episode):
                    action = input('Enter action: ')
                    action = int(action)
                    self.env.step(action = action)
                    current_speed = self.env.get_ego_vehicle_speed(kmph = True)
                    if current_speed > 0:
                        average_speed += current_speed
                        average_speed_steps += 1
                    self.spawner.run_step()
                    #time.sleep(1.0)
                    print('average_speed: ', average_speed/average_speed_steps, average_speed, average_speed_steps)

                self.spawner.close()
                self.env.close()

        except KeyboardInterrupt:
            print('Closing tester')

        finally:
            self.spawner.close()
            self.env.close()



