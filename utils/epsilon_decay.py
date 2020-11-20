import math

class EpsilonDecay:
	def __init__(self, epsilon_start, epsilon_end, epsilon_decay = 0, total_steps = 0):
		self.eps_start = epsilon_start
		self.eps_end = epsilon_end
		self.eps_decay = epsilon_decay
		self.total_steps = total_steps

	def update_expo(self, frame_id):
		epsilon = self.eps_end + (self.eps_start - self.eps_end) * math.exp(-1 * frame_id * self.eps_decay)
		return epsilon

	def update_linear(self, current_eps):
		epsilon = current_eps - ( (self.eps_start - self.eps_end)/self.total_steps )
		return epsilon 



# Testing
DEBUG = 0

if DEBUG:
	from torch.utils.tensorboard import SummaryWriter
	writer = SummaryWriter()

	episodes = 1000
	steps = 50
	epsilon_start = 1.0
	epsilon_end = 0.1
	epsilon_decay = 5e-5
	total_steps = episodes

	epsilon_decay = EpsilonDecay(epsilon_start = epsilon_start, epsilon_end = epsilon_end, epsilon_decay = epsilon_decay, total_steps = total_steps)

	# Testing for exponential update
	# frame_counter = 0
	# for i in range(episodes):
	# 	for j in range(steps):
	# 		epsilon = epsilon_decay.update_expo(frame_id = frame_counter)
	# 		writer.add_scalar('Epsilon decay exponential', epsilon, frame_counter)
	# 		frame_counter += 1


	# Testing for simple update
	epsilon = epsilon_start
	frame_counter = 0
	for i in range(episodes):
		#for j in range(steps):
			epsilon = epsilon_decay.update_linear(current_eps = epsilon)
			writer.add_scalar('Epsilon decay simple', epsilon, i)
			frame_counter += 1
	print('done')
