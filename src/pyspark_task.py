"""
Package that defines realization of test tasks and executes them
"""
import sys
from typing import Dict, List
from pyspark.sql import functions as f, DataFrame

import pyspark_task_validator as tv
from pyspark_task_validator import TaskDef, TestTask

_l_dict_test_sql = {
    TestTask(1, 1): "account_types_count",
    TestTask(1, 2): "account_balance",
    TestTask(2, 1): "accounts_btw_18_30",
    TestTask(2, 2): "accounts_non_pro",
    TestTask(2, 3): "accounts_top_5",
    TestTask(2, 4): "total_per_year",
    TestTask(2, 5): "total_earnings_pivot",
    TestTask(3, 1): "first_last_concatenated",
    TestTask(3, 2): "avg_transaction_amount_2021_per_client",
    TestTask(3, 3): "account_types_count",
    TestTask(3, 4): "top_10_positive",
    TestTask(3, 5): "clients_sorted_by_first_name_descending",
    TestTask(4, 1): "person_with_biggest_balance_in_country",
    TestTask(4, 2): "invalid_accounts",
    TestTask(4, 3): "single_dataset",
}

DICT_TEST_TASKS_SQL = {k: "{}.{}_{}".format(k.group_id, k.task_id, v) for k, v in _l_dict_test_sql.items()}
TEST_TASK_FUNCTION_NAME = "fn_get_task_def_list"

def fn_get_task_def_list1() -> List[TaskDef]:
    """
    Task 1 Data Frames List
    """

    l_df_account_types_count = DF_TRANSACTIONS \
        .groupBy("account_type") \
        .agg(f.countDistinct("id").alias("cnt"))

    l_df_account_balance = DF_TRANSACTIONS \
        .groupBy(f.col("id")) \
        .agg(f.round(f.sum("amount"), tv.ROUND_DIGITS).alias("balance"),
             f.max("transaction_date").alias("latest_date"))

    return [
        TaskDef(l_df_account_types_count),
        TaskDef(l_df_account_balance),
    ]


def fn_inner_join_acc_names_to_df(in_dataframe: tv.DataFrame) -> tv.DataFrame:
    """
    Inner join of "first_name", "last_name" by id
    """

    return in_dataframe.join(
        f.broadcast(DF_ACCOUNTS.select("id", "first_name", "last_name")),
        "id",
        "inner")


def fn_get_task_def_list2() -> List[TaskDef]:
    """
    Task 2 Data Frames List
    """

    l_df_accounts_btw_18_30 = DF_ACCOUNTS.selectExpr(
        "id",
        "first_name",
        "last_name",
        "age",
        "country"
    ).where("age between 18 and 30")

    l_df_accounts_non_pro = DF_TRANSACTIONS.selectExpr(
        "id",
        "account_type"
    ).where(f.col("account_type") != 'Professional') \
        .groupBy("id") \
        .agg(f.count("id").alias("cnt"))

    l_l_df_accounts_non_pro_with_user_info = fn_inner_join_acc_names_to_df(l_df_accounts_non_pro)

    l_df_accounts_top5 = DF_ACCOUNTS \
        .groupBy("first_name") \
        .agg(f.count("first_name").alias("cnt")) \
        .orderBy(f.col("cnt").desc()) \
        .limit(5)

    l_df_total_expenses = DF_TRANSACTIONS.selectExpr(
        "id",
        " case when amount < 0 then amount else 0 end as expenses",
        " case when amount > 0 then amount else 0 end as earnings "
    ).groupBy("id") \
        .agg(f.round(f.abs(f.sum("expenses")), tv.ROUND_DIGITS).alias("expenses"),
             f.round(f.sum("earnings"), tv.ROUND_DIGITS).alias("earnings"))

    l_df_total_expenses_with_user_info = fn_inner_join_acc_names_to_df(l_df_total_expenses)

    l_df_total_expenses_pivot = DF_TRANSACTIONS.selectExpr(
        "id",
        "case when amount > 0 then amount else 0 end as earnings",
        "int(substring(transaction_date, 1, 4)) as tr_year",
    ).groupBy("id") \
        .pivot("tr_year") \
        .agg(f.round(f.sum("earnings").alias("earnings"), tv.ROUND_DIGITS)) \
        .fillna(value=0)

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

    l_df_first_last_concatenated = DF_ACCOUNTS \
        .selectExpr("concat(first_name,  ' ', last_name) as first_last_concat") \
        .where("age between 18 and 30").distinct()

    l_df_avg_transaction_amount_2021_per_client = DF_TRANSACTIONS.selectExpr(
        "id",
        "amount"
    ).where("transaction_date like '2021%'") \
        .groupBy("id") \
        .agg(f.round(f.avg("amount"), tv.ROUND_DIGITS).alias("avg_amount"))

    l_df_account_types_count = DF_TRANSACTIONS \
        .groupBy(f.col("account_type")) \
        .agg(f.countDistinct("id").alias("cnt"))

    l_df_top_10_positive = DF_TRANSACTIONS.where("amount > 0") \
        .groupBy("id") \
        .agg(f.round(f.sum("amount"), tv.ROUND_DIGITS).alias("total_amount")) \
        .orderBy(f.col("total_amount").desc()) \
        .limit(10)

    l_df_clients_sorted_by_first_name_descending = DF_ACCOUNTS \
        .select("first_name", "last_name").distinct() \
        .orderBy(f.col("first_name").desc())

    return [
        TaskDef(l_df_first_last_concatenated),
        TaskDef(l_df_avg_transaction_amount_2021_per_client),
        TaskDef(l_df_account_types_count),
        TaskDef(l_df_top_10_positive),
        TaskDef(l_df_clients_sorted_by_first_name_descending),
    ]


def fn_get_richest_person_in_country_broadcast():
    """
    DF for richest person using broadcast
    """

    l_richest_person_transactions = DF_TRANSACTIONS.selectExpr(
        "id",
        "amount"
    ).groupBy("id") \
        .agg(
        f.round(f.sum("amount"), tv.ROUND_DIGITS).alias("total_amount")
    )

    l_df_richest_person_account_info = l_richest_person_transactions.join(
        f.broadcast(DF_ACCOUNTS),
        "id",
        "inner"
    ).withColumn(colName="rn", col=f.expr("row_number() over (partition by country order by total_amount desc)")) \
        .selectExpr(
        "id",
        "first_name",
        "last_name",
        "country",
        "total_amount",
    ).where("rn  == 1 ")

    l_df_richest_person_all_info = l_df_richest_person_account_info.join(
        f.broadcast(DF_COUNTRY_ABBR),
        DF_COUNTRY_ABBR.abbreviation == l_df_richest_person_account_info.country,
        "inner"
    ).drop("abbreviation", "country", "id")

    return l_df_richest_person_all_info


def fn_get_invalid_accounts():
    """
    DF for invalid accounts using broadcast
    """

    l_df_tr_filtered = DF_TRANSACTIONS \
        .where(" account_type = 'Professional' ") \
        .drop("country")

    l_df_acc_filtered = DF_ACCOUNTS.where(" age < 26 ") \
        .withColumnRenamed("id", "account_id")

    l_df_tr_invalid_acc = l_df_tr_filtered.join(f.broadcast(l_df_acc_filtered),
                                                l_df_acc_filtered.account_id == l_df_tr_filtered.id,
                                                "inner")

    return l_df_tr_invalid_acc


def fn_get_all_info_broadcast():
    """
    DF for all data in one place using broadcast
    """

    l_df_trans_info = DF_TRANSACTIONS \
        .select("id",
                "amount",
                "account_type") \
        .groupBy("id", "account_type") \
        .agg(f.round(f.sum("amount"), tv.ROUND_DIGITS).alias("total_amount"))
    # f.concat_ws(",", f.collect_list("account_type")).alias("account_types")

    l_df_trans_and_acc_info = l_df_trans_info \
        .join(f.broadcast(DF_ACCOUNTS),
              "id",
              "inner") \
        .withColumnRenamed("country", "abbreviation")

    l_df_all_info = l_df_trans_and_acc_info \
        .join(f.broadcast(DF_COUNTRY_ABBR),
              "abbreviation",
              "inner").drop("abbreviation")

    return l_df_all_info


def fn_get_task_def_list4() -> List[TaskDef]:
    """
    Task 4 Data Frames List
    """

    return [
        TaskDef(fn_get_richest_person_in_country_broadcast()),
        TaskDef(fn_get_invalid_accounts()),
        TaskDef(fn_get_all_info_broadcast())
    ]


def fn_get_dict_with_all_tasks() -> Dict[int, List[TaskDef]]:
    """
    Returns Dictionary with all task groups inside
    """
    l_result = {}

    for l_one_task_group_id in tv.fn_get_task_group_range():
        fn_get_task_def_list = getattr(sys.modules[__name__], f'{TEST_TASK_FUNCTION_NAME}{l_one_task_group_id}')

        l_task_df_list: List[TaskDef] = fn_get_task_def_list()

        for l_task_ind, l_task_df in enumerate(l_task_df_list):
            l_task_df.test_task = TestTask(l_one_task_group_id, l_task_ind + 1)

            l_sql_folder = tv.fn_get_sql_task_folder_path(in_task_group_id=l_one_task_group_id)
            l_sql_name = DICT_TEST_TASKS_SQL[l_task_df.test_task]

            l_task_df.sql_path = f"{l_sql_folder}/{l_sql_name}"

            print(l_task_df)

        l_result.setdefault(l_one_task_group_id, l_task_df_list)

    return l_result


l_all_df_dict = tv.fn_init_tables()

DF_ACCOUNTS: DataFrame = l_all_df_dict[tv.ACCOUNTS]
DF_TRANSACTIONS: DataFrame = l_all_df_dict[tv.TRANSACTIONS]
DF_COUNTRY_ABBR: DataFrame = l_all_df_dict[tv.COUNTRY_ABBREVIATION]

DICT_ALL_GROUP_TASKS = fn_get_dict_with_all_tasks()

if __name__ == "__main__":
    l_args = tv.fn_init_argparse(tv.TASK_TYPE_DF)
    l_args = l_args.parse_args()
    l_group_id = l_args.group_id
    l_task_id = l_args.task_id
    l_task_type = l_args.task_type

    tv.fn_run_task_type(in_task_group_id=l_group_id,
                       in_task_id=l_task_id,
                       in_task_type=l_task_type,
                       in_dict_all_group_tasks=DICT_ALL_GROUP_TASKS)