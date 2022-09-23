import motor_task_prototype.display as mtpdisplay
import motor_task_prototype.experiment as mtpexp
import motor_task_prototype.meta as mtpmeta


def test_new_default_experiment() -> None:
    exp = mtpexp.new_default_experiment()
    assert len(exp.trialList) == 1
    assert exp.extraInfo["metadata"] == mtpmeta.default_metadata()
    assert exp.extraInfo["display_options"] == mtpdisplay.default_display_options()
