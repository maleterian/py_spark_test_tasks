import pytest
from pyspark_task import SET_ALL_TASK_GROUPS, LIST_ALL_TASKS
from pyspark_task_validator import TASK_TYPES_LIST


def pytest_addoption(parser):
    """Add possibility to pass arguments while executing pytest
    pytest /opt/spark-apps/test/test_app.py --task_type sql --task_group_id 2 --task_id 1 --skip-xfail
    """
    parser.addoption("--task_type", dest="task_type",
                     action="append", default=[], type=str, choices=TASK_TYPES_LIST)
    parser.addoption("--task_group_id", dest="task_group_id",
                     action="append", default=[], type=int)
    parser.addoption("--task_id", dest="task_id",
                     action="append", default=[], type=int)


def pytest_generate_tests(metafunc):
    """Populate 'task_type', 'task_group_id', 'task_id' fixtures if they are mentioned in pytest"""

    if "task_type" in metafunc.fixturenames:
        types = metafunc.config.getoption("task_type") or TASK_TYPES_LIST
        metafunc.parametrize("task_type", types)

    if "task_group_id" in metafunc.fixturenames:
        task_id = metafunc.config.getoption("task_id") or None
        group_id = metafunc.config.getoption("task_group_id") or SET_ALL_TASK_GROUPS

        tasks_to_execute = [
            task
            for task in LIST_ALL_TASKS
            if task.group_id in group_id and (task.task_id == task_id or task_id is None)
        ]

        metafunc.parametrize("task_group_id, task_id", tasks_to_execute)
