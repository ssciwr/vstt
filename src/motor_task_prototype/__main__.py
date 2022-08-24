import logging
from typing import cast

import motor_task_prototype as mtp
from motor_task_prototype.trial import MotorTaskTrial
from psychopy import core


def main() -> None:
    logging.basicConfig(
        format="%(levelname)s %(module)s.%(funcName)s.%(lineno)d :: %(message)s"
    )
    user_choices = mtp.setup()
    if user_choices is not None:
        if user_choices.run_task:
            motor_task = mtp.MotorTask(cast(MotorTaskTrial, user_choices.conditions))
            results = motor_task.run()
            mtp.save_trial_to_psydat(results)
            mtp.display_results(results)
        elif user_choices.trials is not None:
            mtp.display_results(user_choices.trials)
        core.quit()


if __name__ == "__main__":
    main()
