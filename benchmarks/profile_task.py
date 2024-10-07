import cProfile
import ctypes

from psychopy import core

from vstt.experiment import Experiment
from vstt.task import MotorTask

xlib = ctypes.cdll.LoadLibrary("libX11.so")
xlib.XInitThreads()

experiment = Experiment()
experiment.trial_list[0]["weight"] = 3
experiment.trial_list[0]["pre_target_delay"] = 0.0
experiment.trial_list[0]["pre_central_target_delay"] = 0.0
experiment.trial_list[0]["post_block_display_results"] = False
task = MotorTask(experiment)
with cProfile.Profile() as pr:
    task.run()
pr.dump_stats("profile_task.prof")
core.quit()
