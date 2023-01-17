from pydantic import BaseModel
import asyncio
from typing import Any, List, Union

from server import TopicSocketManager
from models import CommandSet, SetResponse, SetStatus, CommandReq
from models.commands import InitializeResData, FieldID
from agents.commands import Command, command_class_map, InitializeCommand
from models.failures import CommandException, FailureID

from tasks import PokeHoleTask, SpeakTestTask, PokeHoleTaskV2, ScanTestTask, SolveMazeTask, PathPlanTask, ScanAndPathfindTask
from worlds import SubWorld
from models.__agent_models import StateLocation, AgentState
from models.__world_models import BlockData

class AgentManager:
    def __init__(self, socket_manager: TopicSocketManager):
        print('New agent')
        self.socket_manager = socket_manager
        self.initialized = False
        self.id = None
        self.label = None
        asyncio.ensure_future(self.initialize())

    async def initialize(self):
        """
        We send an initialize command to the agent
        """
        await asyncio.sleep(0.1)
        command = InitializeCommand(self)
        res: InitializeResData = await self.send_command(command)
        for field in res.initializedFields:
            print(field)
            if field.fieldId == FieldID.ID:
                self.id = field.value
            elif field.fieldId == FieldID.LABEL:
                self.label = field.value
        print(f'Initialized agent {self.id} with label {self.label}')
        
        # TODO: Remove this test task
        test_world = SubWorld()

        # test_task = PokeHoleTask(self, 10)
        # test_task = PokeHoleTaskV2(self, 120, notify=True)
        # test_task = SpeakTestTask(self)
        # test_task = ScanTestTask(self, 1)
        # test_task = SolveMazeTask(self, test_world, sight_radius=8, goal_block="minecraft:gold_block", scan_every=None)
        x_start = -234
        y_start = 75
        z_start = -326

        x_1, y_1, z_1 = -228, 13, -310

        def to_goal(x, y, z, inverse=False):
            return AgentState(location=StateLocation(
                forward=x - x_start * (-1 if inverse else 1),
                up=y - y_start * (-1 if inverse else 1),
                side=(z - z_start) * (1 if inverse else -1)
            ))

        test_task = ScanAndPathfindTask(self, test_world, goal=to_goal(x_1, y_1, z_1, inverse=False))

        # for x in range(0, 10):
        #     for z in range(0, 10):
        #         test_world.set_block(StateLocation(forward=z, up=0, side=x), BlockData(name='minecraft:air'))

        # for z in range(0, 8+1):
        #     test_world.set_block(StateLocation(forward=z, up=0, side=1), BlockData(name='minecraft:stone'))

        # for z in range(7, 9+1):
        #     test_world.set_block(StateLocation(forward=z, up=0, side=3), BlockData(name='minecraft:stone'))

        # test_world.set_block(StateLocation(forward=3, up=0, side=3), BlockData(name='minecraft:stone'))

        # test_world.set_block(StateLocation(forward=1, up=0, side=2), BlockData(name='minecraft:stone'))
        # goal_state = AgentState(location=StateLocation(forward=0, up=0, side=2))
        # test_task = PathPlanTask(self, test_world, goal_state)

        await test_task.run()
        test_world.show()

    def command_to_req(self, command: Command) -> CommandReq:
        data = command.format_data()
        command_class = command.__class__
        command_id = command_class_map[command_class]
        return CommandReq(command=command_id, data=data)

    async def send_command(self, command: Command, ignore_failure: Union[bool, List[FailureID]] = False) -> BaseModel:
        res = await self.send_command_set([command], ignore_failure=ignore_failure)
        return res[0]

    async def send_command_set(self, commands: List[Command], ignore_failure: Union[bool, List[FailureID]] = False) -> List[BaseModel]:
        message = CommandSet(commands=[self.command_to_req(command) for command in commands])
        res: dict = await self.socket_manager.send_and_await_response(message)
        try:
            res: SetResponse = SetResponse.parse_obj(res)
        except Exception as e:
            print("Received malformed response", res)
            raise e
        if res.setStatus == SetStatus.COMPLETED:
            return [command.data for command in res.commands]
        elif res.setStatus == SetStatus.FAILED:
            if ignore_failure:
                if isinstance(ignore_failure, bool):
                    return [command.data for command in res.commands]
                else:
                    if res.failure.failureID in ignore_failure:
                        return [command.data for command in res.commands]
            raise CommandException(res.failure)
        else:
            raise RuntimeError('Unknown status')

