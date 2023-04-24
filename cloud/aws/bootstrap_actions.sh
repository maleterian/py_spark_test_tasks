set -eEu
set -o pipefail

export project_name=${1:-py_spark_test_tasks}
export aws_bucket_name=${2:-eu-python-retraining-airflow-emr}

export project_path=~/$project_name
export aws_bash_scripts_path=$project_path/cloud/aws
export aws_bashrc=$aws_bash_scripts_path/.bashrc
export aws_spark_submit=$aws_bash_scripts_path/spark-submit.sh
export aws_pyspark_task_file_path=$project_path/

export aws_s3_project_location="s3://$aws_bucket_name/$project_name"

if [[ -s $aws_bashrc ]]; then
    source $aws_bashrc
else
    for l_folder in src \
                    cloud/aws  ; do

        l_from="$aws_s3_project_location/$l_folder"
        l_to="$project_path/$l_folder"

        echo "Copy from $l_from to $l_to"
        if ! aws s3 cp  "$l_from" "$l_to" --recursive ; then
            echo "cannot copy $l_folder from $l_from to $l_to"
            exit 1
        fi
    done

    source $aws_bashrc
fi

for l_script in $aws_bashrc $aws_spark_submit; do
    echo "Copy from $l_script to ~"
    cp $l_script ~
done

