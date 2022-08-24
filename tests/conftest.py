import pytest
from psychopy.visual.window import Window


# fixture to create a wxPython Window for testing gui functions
@pytest.fixture(scope="session")
# session scope means this is only called once by the test suite
def window() -> Window:
    window = Window(fullscr=False, units="height", size=(800, 600))
    # yield is like return but control flow returns here afterwards
    yield window
    # clean up window once all tests are done
    window.close()
