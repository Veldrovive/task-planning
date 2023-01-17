### Creating a new command
1. Create the command in the static actuator commands folder
2. Add the id of the command to the command_enums in models/commands/__command_enums.py
3. Create the command request and response models in a models/commands/[command_name].py file
4. Create the command class in a agents/commands/[command_name].py file
5. Add the command to the command_map in agents/commands/__init__.py
6. Add the command to the command_res_class_map in models/commands/__init__.py

### Ideas
This time, the task should have a `run` method that can use complete logic and async calls to a function that just immediately calls the commands instead of just using a command list that cannot by dynamic. Goals should still by static graphs since they need to be parallelized. I thought it would be important for latency, but what should be done instead is that the task can send a batch of commands that will be executed and get an array of the results from each of those commands returned.

Commands should be able to return the requirements for agent capabilities, fuel, and time so that tasks can use these values to estimate their requirements by using helper functions to combine the requirements of the commands it expects to run.

Tasks should also be able to return estimated requirements for the capabilities the agent executing it must have, the fuel it may require, and the time required. Before starting a task, a command to get the capabilities and current fuel level of the agent should be sent to verify that the task can actually be executed. Now, if the agent doesn't have the required fuel, we may be able to have the task yield (or just return a value that tell the task scheduler to retry) and a new refuel task be run before resuming the original.

Originally, I had a system where a task could internally recover from issues, but this just led to opaque failures. Instead, whatever is running the task should be given information about how far the task got and what the error was and that what to do next is up to whatever is running the task.