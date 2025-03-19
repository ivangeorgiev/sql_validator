from enum import Enum

from transitions import Machine, State
from transitions.extensions import HierarchicalMachine
from transitions.extensions.nesting import NestedState


class StageEnum(Enum):
    NEW = "new"
    VALIDATING = "validating"
    REVIEWING = "reviewing"
    PROVISIONING = "provisioning"
    COMPLETED = "completed"

    def __str__(self):
        return self.value


class StageResultEnum(Enum):
    NONE = ""
    APPROVING = "approving"
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"

    def __str__(self):
        return self.value


states = [
    f"{StageEnum.NEW}",
    State(f"{StageEnum.NEW}__{StageResultEnum.CANCELLED}", on_enter="on_cancelled"),
    f"{StageEnum.VALIDATING}",
    State(f"{StageEnum.VALIDATING}_{StageResultEnum.CANCELLED}", on_enter="on_cancelled"),
    State(f"{StageEnum.VALIDATING}_{StageResultEnum.FAILURE}", on_enter="on_failed"),
    State(f"{StageEnum.VALIDATING}_{StageResultEnum.SUCCESS}", on_enter="on_validated"),
    State(f"{StageEnum.COMPLETED}_{StageResultEnum.FAILURE}"),
    State(f"{StageEnum.COMPLETED}_{StageResultEnum.SUCCESS}"),
    State(f"{StageEnum.COMPLETED}_{StageResultEnum.CANCELLED}"),
    f"{StageEnum.REVIEWING}",
]

transitions = [
    ["start", f"{StageEnum.NEW}", f"{StageEnum.VALIDATING}"],
    ["cancel", f"{StageEnum.NEW}", f"{StageEnum.NEW}_{StageResultEnum.CANCELLED}"],
    ["cancel", f"{StageEnum.VALIDATING}", f"{StageEnum.VALIDATING}_{StageResultEnum.CANCELLED}"],
    ["succeed", f"{StageEnum.VALIDATING}", f"{StageEnum.VALIDATING}_{StageResultEnum.SUCCESS}"],
    ["fail", f"{StageEnum.VALIDATING}", f"{StageEnum.VALIDATING}_{StageResultEnum.FAILURE}"],
    ["finish", f"{StageEnum.VALIDATING}_{StageResultEnum.FAILURE}", f"{StageEnum.COMPLETED}_{StageResultEnum.FAILURE}"],
    ["finish", f"{StageEnum.VALIDATING}_{StageResultEnum.CANCELLED}", f"{StageEnum.COMPLETED}_{StageResultEnum.CANCELLED}"],
    ["review", f"{StageEnum.VALIDATING}_{StageResultEnum.SUCCESS}", f"{StageEnum.REVIEWING}"],
    ["finish", "*_cancelled", "completed_cancelled"],
    ["finish", "*_failure", "completed_failure"],
]


class CompoundMachineModel:
    stage: str = StageEnum.NEW
    stage_result: str = StageResultEnum.NONE

    def save(self):
        """Persist the machine instance."""
        print(f"Saving ... {self}")

    def __str__(self):
        return f"{type(self).__name__} (id: {id(self)}, stage: {self.stage}, result: {self.stage_result})"


class ViewsetProvisionStateMachine:
    def __init__(self, model_instance=None):
        self._model = model_instance or CompoundMachineModel()
        self.machine = Machine(
            model=self,
            states=states,
            transitions=transitions,
            initial=self.state,
            model_attribute="state",
        )

    @property
    def model(self) -> CompoundMachineModel:
        return self._model

    @property
    def state(self):
        model = self.model
        state = model.stage.value
        if model.stage_result and model.stage_result != StageResultEnum.NONE:
            state += f"_{model.stage_result.value}"
        return state

    @state.setter
    def state(self, value: str):
        model = self.model
        stage, _, stage_result = value.partition("_")
        model.stage = StageEnum(stage)
        if stage_result:
            model.stage_result = StageResultEnum(stage_result)
        else:
            model.stage_result = StageResultEnum.NONE

    def on_cancelled(self):
        print("I was cancelled...")
        self.trigger("finish")

    def on_failed(self):
        print("I was failed...")
        self.trigger("finish")

    def on_validated(self):
        print("Validation was successful...")
        self.trigger("review")


class ViewsetStateMachine:
    def __init__(self, model_instance=None):
        self.model = model_instance or CompoundMachineModel()

        # Define compound states
        self.states = [
            "initialize_new",
            "initialize_progress",
            "initialize_success",
            "initialize_failure",
            "initialize_cancelled",
            "validate_new",
            # 'validate_new', 'validate_success', 'validate_failure', 'validate_cancelled',
            # 'review_new', 'review_success', 'review_failure', 'review_cancelled',
            # 'provision_new', 'provision_success', 'provision_failure', 'provision_cancelled',
            # 'completed_new', 'completed_success', 'completed_failure', 'completed_cancelled',
        ]

        # Define transitions
        self.transitions = [
            {
                "trigger": "initialize",
                "source": "initialize_new",
                "dest": "initialize_progress",
            },
            # Transitions for stage_result changes
            {
                "trigger": "start",
                "source": f"*_{StageResultEnum.NEW}",
                "dest": f"{{}}_{StageResultEnum.PROGRESS}",
            },
            {
                "trigger": "succeed",
                "source": f"*_{StageResultEnum.PROGRESS}",
                "dest": f"{{}}_{StageResultEnum.SUCCESS}",
            },
            {"trigger": "fail", "source": "*_new", "dest": "{}_failure"},
            {"trigger": "cancel", "source": "*", "dest": "{}_cancelled"},
            {"trigger": "complete", "source": "*", "dest": "{}_cancelled"},
        ]

        # Initialize the state machine
        self.machine = Machine(
            model=self.model,
            states=self.states,
            transitions=self.transitions,
            initial=self.model.compound_state,
            model_attribute="compound_state",
        )

    def get_compound_state(self):
        """Get the current compound state from the model fields."""
        return f"{self.model.stage}_{self.model.stage_result}"

    def update_compound_state(self, stage, stage_result):
        """Update the model fields to reflect the new compound state."""
        self.model.stage = stage
        self.model.stage_result = stage_result
        self.model.save()

    def start(self):
        print(f"Starting ... {self.model.compound_state}")

    def initialize(self):
        print(f"Initializing ... {self.model.compound_state}")

    def can_validate(self):
        """Guard condition for the validate transition."""
        return True  # Example condition

    def succeed(self):
        print(f"Succeeding ... {self.model.compound_state}")

    def fail(self):
        """Transition to the failure state for the current stage."""
        new_state = f"{self.model.stage}_failure"
        self.update_compound_state(self.model.stage, StageResultEnum.FAILURE)

    def cancel(self):
        """Transition to the cancelled state for the current stage."""
        new_state = f"{self.model.stage}_cancelled"
        self.update_compound_state(self.model.stage, StageResultEnum.CANCELLED)
