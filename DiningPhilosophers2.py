import simpy 
import random 

class Philosopher():
    T0 = 10 # Mean thinking time 
    T1 = 10 # Mean eating time 
    DT = 1 # Time to pick the other chopstick 

    def __init__(self, env, chopsticks, my_id, DIAG = True):
        self.env = env
        # self.chopsticks = chopsticks 
        self.chopsticks = sorted(chopsticks, key=id) # uncomment to avoid deadlock
        self.id = my_id
        # START_HIGHLIGHT 
        self.waiting = 0
        # END_HIGHLIGHT 
        self.DIAG = DIAG 
        # Register the process with the environment
        env.process(self.run_the_party())

    def get_hungry(self):
        # START_HIGHLIGHT
        start_waiting = self.env.now
        # END_HIGHLIGHT 
        self.diag("requested chopstick")
        rq1 = self.chopsticks[0].request()
        yield rq1

        self.diag("obtained chopstick")
        yield self.env.timeout(self.DT)

        self.diag("requested another chopstick")
        rq2 = self.chopsticks[1].request()
        yield rq2

        self.diag("obtained another chopstick")
        # START_HIGHLIGHT 
        self.waiting += self.env.now - start_waiting
        # END_HIGHLIGHT
        return rq1, rq2



    def run_the_party(self): # Do everything ...
        while True:
            #Thinking 
            thinking_delay = random.expovariate(1 / self.T0)
            yield self.env.timeout(thinking_delay)

            # Getting hungry 
            get_hungry_p = self.env.process(self.get_hungry())
            rq1, rq2 = yield get_hungry_p

            # Eating 
            eating_delay = random.expovariate(1/self.T1)
            yield self.env.timeout(eating_delay)

            # Done eating, put down the chopsticks 
            self.chopsticks[0].release(rq1)
            self.chopsticks[1].release(rq2)
            self.diag("released the chopsticks")
    
    def diag(self, message): # Diagnostic routine 
        if self.DIAG:
            print("P{} {} @{}".format(self.id, message, self.env.now))

def simulate(n, t):
    """
    Simulate the system of n philosophers for up to t time units.
    Return the average waiting time.
    """
    env = simpy.Environment()
    chopsticks = [simpy.Resource(env, capacity=1) for i in range(n)]
    philosophers = [Philosopher(env, (chopsticks[i], chopsticks[(i+1) % n]), i) for i in range(n)]
    env.run(until=t)
    return sum(ph.waiting for ph in philosophers) / n

# Set up the plotting system 
import matplotlib.pyplot as plt 
import matplotlib
matplotlib.style.use("ggplot")

# Simulate 
N = 20
X = range(2,N)
Y = [simulate(n, 50000) for n in X]

# Plot 
plt.plot(X, Y, "-o")
plt.ylabel("Waiting time")
plt.xlabel("Number of philosophers")
plt.show()