from motor_task_prototype.setup import setup
from motor_task_prototype.task import MotorTask
from motor_task_prototype.trial import get_trial_from_user
from motor_task_prototype.trial import save_trial_to_psydat
from motor_task_prototype.vis import display_results

__all__ = [
    "__version__",
    "setup",
    "MotorTask",
    "get_trial_from_user",
    "save_trial_to_psydat",
    "display_results",
]

__version__ = "0.0.7"
