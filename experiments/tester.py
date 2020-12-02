import time


DEBUG = 0

class Tester:
    def __init__(self, env, agent, spawner, params):
        self.env = env
        self.agent = agent
        self.spawner = spawner
        self.params = params


    def test(self):

        for ep in range(self.params.testing_episodes):
            for step in range(self.params.testing_steps_per_episode): 
                # Select action
                if DEBUG:
                    action = input('Enter action: ')
                    action = int(action)
                else:
                    action = self.agent.pick_action(state, self.epsilon)

                # Execute action for n times
                #self.spawner.run_step(step) # running spawner step

                for i in range(0, self.params.action_repeat):
                    next_state, reward, done = self.env.step(action)

        try:
            for ep in range(self.params.testing_episodes):
                state = self.env.reset()
                self.spawner.reset(config = self.env.config, spawn_points = self.env.walker_spawn_points, ev_id = self.env.get_ego_vehicle_id())

                average_speed = 0.0
                average_speed_steps = 0

                for step in range(10000):
                    action = input('Enter action: ')
                    action = int(action)
                    print("action:", action)
                    self.env.step(action = action)
                    # current_speed = self.env.get_ego_vehicle_speed(kmph = True)
                    # if current_speed > 0:
                    #     average_speed += current_speed
                    #     average_speed_steps += 1
                    if step%10 == 0 or step > 2:
                        self.spawner.run_step()
                    #time.sleep(1.0)
                    # #print('average_speed: ', average_speed/average_speed_steps, average_speed, average_speed_steps)

                self.spawner.close()
                self.env.close()

        except KeyboardInterrupt:
            print('Closing tester')

        finally:
            self.spawner.close()
            self.env.close()



