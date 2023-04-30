
aws s3api get-object --bucket $aws_bucket_name --key py_spark_test_tasks/cloud/aws/$env_params_file $tmp_dir

source $env_params_file_path

mkdir -p $SPARK_APPS_TEST \
         $SPARK_APPS_LOG
