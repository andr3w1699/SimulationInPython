"""
Customer service counter 
- how to model processes that interact directly rather than sharing resources 
- customers arrive with exponentially distributed delays and queuing into a line
- the operator takes next customer from the line and serve him in SERVICE_DELAY time units
- a customer is served successfully with a probability of 0.9 
- no customers in the line --> the operator becomes idle and is reactived at by the next customer arrival

Simpy provides two direct interaction mechanism: process interruption and event-based synchronization
- to interact Simpy processes must have references to simpy.events.Process or to simpy.events.Event
- SimPy uses Python exceptions to manage process interruptions 
- class CustomerFailedException is created to distinguish SimPy process-related exceptions from proper Python exceptions

"""
import random 
from collections import deque
import simpy 

# Shared global variables and "constants"
SERVICE_DELAY = 10
service_line = deque()
counter_idle = False # The state of the operator at the service counter 
env = simpy.Environment()

class CustomerFailedException(Exception):
    pass

# function that model the process that spawn customer  
def customer_generator():
    for _ in range(10):
        env.process(customer())
        yield env.timeout(random.expovariate(1 / SERVICE_DELAY))

customer_generator_p = env.process(customer_generator())

# customers in the model are stateless creature 
# they born, they obtain a service ticket (simpy.events.Event) so they enter the service line
# if service counter operator is idle the customer interrupts the target process and awakens him
# as the operator is working the customer yields the ticket, the events gets triggered
# the customer is blocked until some other process processes the event
# as the event is processed succesfully the execution of the customer resumes

def customer():
    print("Customer arrived @{0:.1f}".format(env.now))
    ticket = env.event()
    service_line.append(ticket)

    if counter_idle:
        # START_HIGHLIGHT
        counter_p.interrupt()
        # END_HIGHLIGHT
    
    try:
        yield ticket
        print("Customer left @{0:.1f}".format(env.now))
    except CustomerFailedException:
        print("Customer failed (and left) @{0:.1f}".format(env.now))

def counter():
    global counter_idle
    while True:
        if service_line:
            ticket = service_line.popleft()
            yield env.timeout(SERVICE_DELAY)
            if random.randint(0,9) == 9:
                ticket.fail(CustomerFailedException())
            else:
                ticket.succeed()
        else:
            counter_idle = True
            print("The operator fell asleep @{0:.1f}".format(env.now))
            try: 
                yield env.event()
            # START_HIGHLIGHT 
            except simpy.Interrupt:
                 # END_HIGHLIGHT
                 counter_idle = False
                 print("The operator woke up @{0:.1f}".format(env.now))

counter_p = env.process(counter())

env.run()