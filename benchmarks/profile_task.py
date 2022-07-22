from psychopy.visual.window import Window
from psychopy import core
from motor_task_prototype import task
import cProfile


window = Window(fullscr=True, units="height")
settings = task.get_default_motor_task_trial()
settings["weight"] = 1
settings["inter_target_duration"] = 0
motor_task = task.MotorTask(settings)
with cProfile.Profile() as pr:
    results = motor_task.run(window)
pr.dump_stats("profile_task.prof")
window.close()
core.quit()
