from psychopy.visual.window import Window
from psychopy import core
from motor_task_prototype import task


def main() -> None:
    settings = task.get_settings_from_user()
    window = Window(fullscr=True, units="height")
    motor_task = task.MotorTask(settings)
    results = motor_task.run(window)
    motor_task.display_results(window, results)
    window.close()
    core.quit()


if __name__ == "__main__":
    main()
