Commands are classes that take data in their constructor along with an AgentManager instance. They have an async `run` method that then runs the command a returns the pydantic model result.

Commands also define `getAgentRequirements`, `getFuelRequirement`, and `getTimeRequirement` methods.