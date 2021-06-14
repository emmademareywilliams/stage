import numpy as np
import gym
import random
import math
import tensorflow as tf
import matplotlib.pylab as plt

# size of the training batch
BATCH_SIZE=50

MAX_EPS = 1
MIN_EPS = 0.01
LAMBDA = 0.0001
GAMMA = 0.99

class Memory:
    """
    The memory class
    stores samples (state,action,reward,nextState) as tuples into _samples

    Attributes
    ----------
    _samples : list of tuples
        list containing max_memory elements
    _max_memory : int
        maximum number of tuples that can be injected into _samples
    """

    def __init__(self, max_memory):
        """ initialize the memory list """
        self._max_memory = max_memory
        self._memory = []

    def addSample(self, sample):
        """ add a sample to the memory list """
        self._memory.append(sample)
        if len(self._memory) > self._max_memory:
            self._memory.pop(0)

    def samples(self, nb_samples):
        """ return a random sample with nb_samples elements """
        if nb_samples > len(self._memory):
            nb_samples = len(self._memory)
        return random.sample(self._memory,nb_samples)

    def size(self):
        return len(self._memory)

# initialize the Memory
mem = Memory(50000)
eps = MAX_EPS

# initialize the game
env_name = 'MountainCar-v0'
env = gym.make(env_name)
numStates = env.env.observation_space.shape[0]
numActions = env.env.action_space.n
print("This game is a {} actions game".format(numActions))
print("Environment is described by a {} elements vector".format(numStates))
input("Press Enter to continue...")

# initialize the model
# input is a 2 dim vector or tensor  (x position, velocity)
tf.keras.backend.set_floatx('float64')
inputs=tf.keras.Input(shape=(numStates,), name='states')
x=tf.keras.layers.Dense((50), activation='relu')(inputs)
x=tf.keras.layers.Dense((50), activation='relu')(x)
outputs=tf.keras.layers.Dense(numActions,activation='linear')(x)
model=tf.keras.Model(inputs=inputs,outputs=outputs,name='myLittleCar')
model.compile(loss="mse",optimizer="adam",metrics=['mae'])
print("model created")
model.summary()
input("Press Enter to continue...")
print("model starting to play the game")
num_episodes = 300

steps=0
reward_store = []
max_x_store = []

for episode in range(num_episodes):
    state = env.reset()
    if episode % 10 == 0:
        print('Episode {} of {}'.format(episode+1, num_episodes))
        print("memory length is {}".format(mem.size()))
    tot_reward = 0
    max_x = -100
    while True:
        env.render()

        if random.random() < eps:
            action = random.randint(0, numActions - 1)
        else:
            rspd=state.reshape(1,numStates)
            # do not use high level function such as predict or predict_classes (in case you dont have to use argmax)
            predictionBrute = model(rspd)
            action = np.argmax(predictionBrute)

        # we realize the action
        nextState, reward, done, info = env.step(action)

        if nextState[0] >= 0.5:
            reward += 100
            print("Top of the hill reached after {} timesteps".format(steps))
        elif nextState[0] >= 0.25:
            reward += 20
        elif nextState[0] >= 0.1:
            reward += 10
        if nextState[0] > max_x:
            max_x = nextState[0]
        if done:
            nextState = None

        # feed the memory
        mem.addSample((state,action,reward,nextState))

        # train the model - only if we have something representative in the memory
        if mem.size() > BATCH_SIZE * 3:
            train_samples=mem.samples(BATCH_SIZE)
            nb=len(train_samples)
            #print("we are going to train on a batch with {} elements".format(nb))
            state_samples= np.array([val[0] for val in train_samples])
            nextState_samples= np.array([(np.zeros(numStates) if val[3] is None else val[3]) for val in train_samples])
            qsa=model(state_samples)
            qsad=model(nextState_samples)
            x=np.zeros((nb,numStates))
            y=np.zeros((nb,numActions))

            # according to the structure adopted for the memory
            # b[0] is state, b[1] is action, b[2] is reward and b[3] is the nextState
            for i, b in enumerate(train_samples):
                current_q = tf.unstack(qsa[i])
                if b[3] is None:
                    current_q[b[1]]=b[2]
                else:
                    current_q[b[1]]=b[2]+GAMMA*np.amax(qsad[i])
                x[i] = b[0]
                y[i] = tf.stack(current_q)

            # do not use model.fit(x, y, epochs=1, verbose=0)
            model.train_on_batch(x, y)

        # prepare next iteration
        # increase the step counter
        steps+=1
        # evaluate the new value for eps
        eps = MIN_EPS + (MAX_EPS - MIN_EPS) * math.exp(-LAMBDA * steps)
        # update state
        state = nextState

        tot_reward += reward

        if done:
            reward_store.append(tot_reward)
            max_x_store.append(max_x)
            break

    print("step {} Total reward {} Eps {}".format(steps,tot_reward,eps))

env.close()
plt.plot(reward_store)
plt.show()
plt.close("all")
plt.plot(max_x_store)
plt.show()
model.save('moutainCar.h5')
