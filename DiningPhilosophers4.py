import simpy 
import random 

class Chef():
    T2 = 150
    def __init__(self, env, bowl):
        self.env = env
        self.bowl = bowl
        env.process(self.replenish())

    def replenish(self):
        while True:
            yield self.env.timeout(self.T2)
            if self.bowl.level < self.bowl.capacity:
                yield self.bowl.put(self.bowl.capacity - self.bowl.level)

class Philosopher():
    T0 = 10 # Mean thinking time 
    T1 = 10 # Mean eating time 
    DT = 1 # Time to pick the other chopstick 
    PORTION = 20 # Single meal size 
    # START_HIGHLIGHT 
    MAX_WAIT = Chef.T2 / 4
    # END_HIGHLIGHT 

    
    def __init__(self, env, chopsticks, my_id, bowl = None, DIAG = False):    
        self.env = env
        self.chopsticks = sorted(chopsticks, key=id)
        self.id = my_id
        self.waiting = 0
        # START_HIGHLIGHT 
        self.bowl = bowl
        # END_HIGHLIGHT 
        self.DIAG = DIAG
        # Register the process with the environment 
        env.process(self.run_the_party())

    def get_hungry(self, meal_size):
        start_waiting = self.env.now
        self.diag("requested chopstick")
        rq1 = self.chopsticks[0].request()
        yield rq1

        self.diag("obtained chopstick")
        yield self.env.timeout(self.DT)

        self.diag("requested another chopstick")
        rq2 = self.chopsticks[1].request()
        yield rq2

        self.diag("obtained another chopstick")        
        if self.bowl is not None:
            # START_HIGHLIGHT
            request = self.bowl.get(meal_size)
            yield request | self.env.timeout(self.MAX_WAIT)
            if request.processed:
                self.diag("reserved food")
            else: # Timeout
                self.diag("gave up")       
                self.waiting += self.env.now - start_waiting
                yield simpy.Event(self.env).fail(ValueError(rq1, rq2))
            # END_HIGHLIGHT      
        
        # Either no bowl or no timeout!
        self.waiting += self.env.now - start_waiting
        return rq1, rq2
    
    def run_the_party(self): # Do everything ...
        # START_HIGHLIGHT
        meal_size = self.PORTION
        # END_HIGHLIGHT      
        while True:
            #Thinking 
            thinking_delay = random.expovariate(1 / self.T0)
            yield self.env.timeout(thinking_delay)

            # Getting hungry 
            get_hungry_p = self.env.process(self.get_hungry(meal_size))
            # START_HIGHLIGHT 
            try:
                rq1, rq2 = yield get_hungry_p
                yield self.env.timeout(random.expovariate(1 / self.T1))
                meal_size = self.PORTION
            except ValueError as values: # Timeout chef waiting expired
                rq1, rq2 = values.args
                meal_size += self.PORTION
            # END_HIGHLIGHT

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
    # START_HIGHLIGHT 
    rice_bowl = simpy.Container(env, init=1000, capacity=1000)
    chef = Chef(env, rice_bowl)
    # END_HIGHLIGHT
    chopsticks = [simpy.Resource(env, capacity=1) for i in range(n)]
    philosophers = [Philosopher(env, (chopsticks[i],chopsticks[(i+1)%n]), i, 
                                # START_HIGHLIGHT 
                                rice_bowl)
                                # END_HIGHLIGHT
                                for i in range(n)]
    env.run(until=t)
    return sum(ph.waiting for ph in philosophers) / n

# Set up the plotting system 
import matplotlib.pyplot as plt 
import matplotlib
matplotlib.style.use("ggplot")

# Simulate 
N = 100
X = range(2,N)
Y = [simulate(n, 50000) for n in X]

# Plot 
plt.plot(X, Y, "-o")
plt.ylabel("Waiting time")
plt.xlabel("Number of philosophers")
plt.show()
