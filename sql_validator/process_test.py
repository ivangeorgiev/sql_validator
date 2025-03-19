from sql_validator.process import ViewsetProvisionStateMachine, CompoundMachineModel, StageEnum, StageResultEnum

machine = ViewsetProvisionStateMachine()
machine.start()
machine.cancel()
str(machine.model)

machine = ViewsetProvisionStateMachine()
machine.start()
str(machine.model)
machine.succeed()
str(machine.model)

# model = MachineModel()
# machine = ViewsetStateMachine(model)
# print(f"Result: {machine.model}")
# print("machine.initialize()...")
# machine.initialize()
# print(f"Result: {machine.model}")
