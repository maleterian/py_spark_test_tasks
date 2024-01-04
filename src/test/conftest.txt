import pytest
from pyspark_task import LIST_ALL_TASKS
from pyspark_task_validator import TASK_TYPES_LIST

MARKER_TECHNICAL = "technical"


def pytest_addoption(parser):
    """Add possibility to pass arguments while executing pytest
    pytest /opt/spark-apps/test/test_app.py --task_type sql --task_group_id 2 --task_id 1 --skip-technical
    """
    parser.addoption("--task_type", action="append", default=[], type=str, choices=TASK_TYPES_LIST)
    parser.addoption("--task_group_id", action="append", default=[], type=int)
    parser.addoption("--task_id", action="append", default=[], type=int)
    parser.addoption("--skip-xfail", action="store_true", help="Skip all tests marked as xfail")
    parser.addoption("--skip-technical", action="store_true", help="skip technical tests")
    parser.addoption("--deselect-technical", action="store_true", help="deselect technical tests")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--skip-technical"):
        skip_technical = pytest.mark.skip(reason="skipping technical tests")
        for item in items:
            if MARKER_TECHNICAL in item.keywords:
                item.add_marker(skip_technical)

    if config.getoption("--task_group_id") or config.getoption("--task_id"):
        skip_marker = pytest.mark.skip(reason="Skipped due to --task_group_id or --task_id flag")
        for item in items:
            if "xfail" in item.keywords:
                item.add_marker(skip_marker)

    if config.getoption("--skip-xfail"):
        skip_marker = pytest.mark.skip(reason="Skipped due to --skip-xfail flag")
        for item in items:
            if "xfail" in item.keywords:
                item.add_marker(skip_marker)

    deselected = []
    remaining = []

    if config.getoption("--deselect-technical"):
        for item in items:
            if MARKER_TECHNICAL in item.keywords:
                deselected.append(item)
            else:
                remaining.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = remaining


def pytest_generate_tests(metafunc):
    """Populate 'task_type', 'task_group_id', 'task_id' fixtures if they are mentioned in pytest"""

    if "task_type" in metafunc.fixturenames:
        types = metafunc.config.getoption("task_type") or TASK_TYPES_LIST
        metafunc.parametrize("task_type", types)

    if "task_group_id" in metafunc.fixturenames:
        task_id = metafunc.config.getoption("task_id") or None
        group_id = metafunc.config.getoption("task_group_id") or None

        tasks_to_execute = [
            task
            for task in LIST_ALL_TASKS
            if (group_id is None or task.group_id in group_id) and
               (task_id is None or task.task_id in task_id)
        ]

        metafunc.parametrize("task_group_id, task_id", tasks_to_execute)
