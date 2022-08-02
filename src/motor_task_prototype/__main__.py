from typing import cast

import motor_task_prototype as mtp
from motor_task_prototype.trial import MotorTaskTrial
from psychopy import core
from psychopy.visual.window import Window


def main() -> None:
    user_choices = mtp.setup()
    if user_choices is not None:
        window = Window(fullscr=True, units="height")
        if user_choices.run_task:
            motor_task = mtp.MotorTask(cast(MotorTaskTrial, user_choices.conditions))
            results = motor_task.run(window)
            mtp.save_trial_to_psydat(results)
            mtp.display_results(window, results)
        elif user_choices.trials is not None:
            mtp.display_results(window, user_choices.trials)
        window.close()
        core.quit()


if __name__ == "__main__":
    main()
