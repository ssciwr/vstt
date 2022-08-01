import motor_task_prototype as mtp
from psychopy import core
from psychopy.visual.window import Window


def main() -> None:
    trial = mtp.get_trial_from_user()
    window = Window(fullscr=True, units="height")
    motor_task = mtp.MotorTask(trial)
    results = motor_task.run(window)
    mtp.display_results(window, results)
    window.close()
    core.quit()


if __name__ == "__main__":
    main()
