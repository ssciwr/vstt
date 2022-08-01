import cProfile

from motor_task_prototype import MotorTask
from motor_task_prototype.trial import default_trial
from psychopy import core
from psychopy.visual.window import Window


window = Window(fullscr=True, units="height")
trial = default_trial()
trial["weight"] = 1
trial["inter_target_duration"] = 0
motor_task = MotorTask(trial)
with cProfile.Profile() as pr:
    results = motor_task.run(window)
pr.dump_stats("profile_task.prof")
window.close()
core.quit()
