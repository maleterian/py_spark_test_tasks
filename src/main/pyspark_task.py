"""
Package that defines realization of test tasks and executes them
"""

from typing import Dict, List
from pyspark.sql import functions as f, DataFrame

import pyspark_task_validator as tv
from pyspark_task_validator import TaskDef, Task

_l_dict_test_sql = {
    Task(1, 1): "account_types_count",
    Task(1, 2): "account_balance",
    Task(2, 1): "accounts_btw_18_30",
    Task(2, 2): "accounts_non_pro",
    Task(2, 3): "accounts_top_5",
    Task(2, 4): "total_per_year",
    Task(2, 5): "total_earnings_pivot",
    Task(3, 1): "first_last_concatenated",
    Task(3, 2): "avg_transaction_amount_2021_per_client",
    Task(3, 3): "account_types_count",
    Task(3, 4): "top_10_positive",
    Task(3, 5): "clients_sorted_by_first_name_descending",
    Task(4, 1): "person_with_biggest_balance_in_country",
    Task(4, 2): "invalid_accounts",
    Task(4, 3): "single_dataset",
    Task(5, 1): "account_types_count",
}

DICT_TEST_TASKS_SQL = {k: f"{k.group_id}.{k.task_id}_{v}" for k, v in _l_dict_test_sql.items()}
LIST_ALL_TASKS = [k for k, v in _l_dict_test_sql.items()]
SET_ALL_TASK_GROUPS = set([g.group_id for g in LIST_ALL_TASKS if g.group_id <= 4])


def fn_get_dict_with_all_tasks() -> Dict[int, List[TaskDef]]:
    """
    Returns Dictionary with all task groups inside
    """

    def fn_get_task_def_list1() -> List[TaskDef]:
        """
        Task 1 Data Frames List
        """
        # ORDER MATTERS !!!
        return [
            TaskDef(l_df_account_types_count),
            TaskDef(l_df_account_balance),
        ]

    def fn_get_task_def_list2() -> List[TaskDef]:
        """
        Task 2 Data Frames List
        """

        # ORDER MATTERS !!!
        return [
            TaskDef(l_df_accounts_btw_18_30),
            TaskDef(l_l_df_accounts_non_pro_with_user_info),
            TaskDef(l_df_accounts_top5),
            TaskDef(l_df_total_expenses_with_user_info),
            TaskDef(l_df_total_expenses_pivot),
        ]

    def fn_get_task_def_list3() -> List[TaskDef]:
        """
        Task 3 Data Frames List
        """

        # ORDER MATTERS !!!
        return [
            TaskDef(l_df_first_last_concatenated),
            TaskDef(l_df_avg_transaction_amount_2021_per_client),
            TaskDef(l_df_account_types_count),
            TaskDef(l_df_top_10_positive),
            TaskDef(l_df_clients_sorted_by_first_name_descending),
        ]



    def fn_get_task_def_list4() -> List[TaskDef]:
        """
        Task 4 Data Frames List
        """
        # ORDER MATTERS !!!
        return [
            TaskDef(l_df_richest_person_in_country_broadcast),
            TaskDef(l_df_invalid_accounts),
            TaskDef(l_df_all_info_broadcast)
        ]

    # Do not modify this one. It is for internal tests
    def fn_get_task_def_list5() -> List[TaskDef]:
        """
        Task 5 Data Frames List
        """

        l_df_account_types_count = df_transactions \
            .groupBy("account_type") \
            .agg(f.count("id").alias("cnt"))

        return [
            TaskDef(l_df_account_types_count),
        ]

    tv.fn_get_or_create_spark_session()

    l_all_df_dict = tv.DICT_OF_INIT_DATAFRAMES

    df_accounts: DataFrame = l_all_df_dict[tv.ACCOUNTS]
    df_transactions: DataFrame = l_all_df_dict[tv.TRANSACTIONS]
    df_country_abbr: DataFrame = l_all_df_dict[tv.COUNTRY_ABBREVIATION]

    l_result = {}

    for l_one_task_group_id in {k.group_id for k, v in DICT_TEST_TASKS_SQL.items()}:

        fn_get_task_def_list = locals()[f'fn_get_task_def_list{l_one_task_group_id}']

        l_task_df_list: List[TaskDef] = fn_get_task_def_list()

        for l_task_ind, l_task_df in enumerate(l_task_df_list):
            l_task_df.test_task = Task(l_one_task_group_id, l_task_ind + 1)

            l_sql_folder = tv.fn_get_sql_task_folder_path(in_task_group_id=l_one_task_group_id)
            l_sql_name = DICT_TEST_TASKS_SQL[l_task_df.test_task]

            l_task_df.sql_path = f"{l_sql_folder}/{l_sql_name}"

        l_result.setdefault(l_one_task_group_id, l_task_df_list)

    return l_result


if __name__ == "__main__":

    l_args = tv.fn_init_argparse(tv.TASK_TYPE_DF)
    l_args = l_args.parse_args()
    l_group_id = l_args.group_id
    l_task_id = l_args.task_id
    l_task_type = l_args.task_type

    try:
        tv.fn_run_task_type(in_task_group_id=l_group_id,
                            in_task_id=l_task_id,
                            in_task_type=l_task_type,
                            in_dict_all_group_tasks=fn_get_dict_with_all_tasks())
    finally:
        tv.fn_close_session()
