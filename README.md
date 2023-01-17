### Creating a new command
1. Create the command in the static actuator commands folder
2. Add the id of the command to the command_enums in models/commands/__command_enums.py
3. Create the command request and response models in a models/commands/[command_name].py file
4. Create the command class in a agents/commands/[command_name].py file
5. Add the command to the command_map in agents/commands/__init__.py
6. Add the command to the command_res_class_map in models/commands/__init__.py