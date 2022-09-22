import logging

import motor_task_prototype as mtp
from psychopy import core


def main() -> None:
    logging.basicConfig(
        format="%(levelname)s %(module)s.%(funcName)s.%(lineno)d :: %(message)s"
    )
    user_choices = mtp.setup()
    if user_choices is not None:
        if user_choices.run_task:
            motor_task = mtp.MotorTask(user_choices.experiment)
            results = motor_task.run()
            mtp.save_experiment(results)
        elif user_choices.display_trial_indices is not None:
            mtp.display_results(
                user_choices.experiment, user_choices.display_trial_indices
            )
        core.quit()


if __name__ == "__main__":
    main()
