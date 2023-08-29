import pyspark_task as t


def pytest_addoption(parser):
    """Add possibility to pass arguments while executing pytest
    >>> pytest test --type sql --group 2 --task 1
    """
    parser.addoption("--type", action="append", default=[], type=str, choices=['sql', 'df'])
    parser.addoption("--group", action="append", default=[], type=int)
    parser.addoption("--task", action="append", default=[], type=int)


def pytest_generate_tests(metafunc):
    """Populate 'task_type', 'task_group_id', 'task_id' fixtures if they are mentioned in pytest"""
    all_task_groups = list(set([task.group_id for task, sql in t.DICT_TEST_TASKS_SQL.items()]))

    if "task_type" in metafunc.fixturenames:
        types = metafunc.config.getoption("type") or ["sql", "df"]
        metafunc.parametrize("task_type", types)
    if "task_group_id" in metafunc.fixturenames:
        group_id = metafunc.config.getoption("group") or all_task_groups
        tasks_to_execute = [
            (task.group_id, task.task_id) for task, sql in t.DICT_TEST_TASKS_SQL.items() if task.group_id in group_id]

        task_id = metafunc.config.getoption("task")
        if task_id:
            tasks_to_execute = [task for task in tasks_to_execute if task[1] in task_id]

        metafunc.parametrize("task_group_id, task_id", tasks_to_execute)
