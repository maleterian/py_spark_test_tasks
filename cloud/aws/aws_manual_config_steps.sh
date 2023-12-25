#https://www.youtube.com/watch?v=snfkRC78oQ8&ab_channel=StartDataEngineering

# install awscli
sudo apt-get update --fix-missing
# way 1
sudo apt-get install awscli
sudo apt-get upgrade awscli
#sudo apt remove awscli

# way 2
pip3 install --install awscli
pip3 install --upgrade awscli
python3.11 -m pip install --upgrade pip

# config for keys
mkdir -p $project_path/.aws
aws configure

# aws set up
export aws_cli_user=ubart-cli
export aws_bucket_region=eu-central-1
export aws_bucket_name=eu-python-retraining-airflow-emr
export aws_account_id=XXXXX
export project_name=py_spark_test_tasks
export aws_s3_project_location="s3://$aws_bucket_name/$project_name"

# create aws cli user
aws iam create-user        --user-name $aws_cli_user

# attach policy to cli user
aws iam attach-user-policy --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess --user-name $aws_cli_user
aws iam attach-user-policy --policy-arn arn:aws:iam::aws:policy/AmazonEMRFullAccessPolicy_v2 --user-name $aws_cli_user
aws iam attach-user-policy --policy-arn arn:aws:iam::aws:policy/AmazonEMRFullAccess --user-name $aws_cli_user

# create key
aws iam create-access-key  --user-name $aws_cli_user

# $project_path/.aws/config should look like
##################
# Install and use AWS tool kit plug in for your IDE for better work experience
##################
# [default]
# region=eu-central-1
# aws_access_key_id=KEY
# aws_secret_access_key=SECRET_KEY
#
# [profile ubart-cli]
# region=eu-central-1
# aws_access_key_id=KEY
# aws_secret_access_key=SECRET_KEY

# create bucket
aws s3api create-bucket --bucket $aws_bucket_name --region $aws_bucket_region --create-bucket-configuration LocationConstraint=$aws_bucket_region

# add permissions for cli user to access the bucket
aws s3api put-bucket-policy   \
    --bucket $aws_bucket_name \
    --policy \
        envsubst <<< '
        {
           "Version":"2012-10-17",
           "Statement":[
              {
                 "Effect":"Allow",
                 "Principal":{
                    "AWS":"arn:aws:iam::$aws_account_id:user/$aws_cli_user"
                 },
                 "Action":[
                    "s3:GetObject",
                    "s3:PutObject"
                 ],
                 "Resource":[
                    "arn:aws:s3:::$aws_bucket_name/*"
                 ]
              }
           ]
        }'

#clean up before copy
aws s3 ls "s3://$aws_bucket_name" --profile $aws_cli_user
aws s3 rm "$aws_s3_project_location" --recursive --profile $aws_cli_user

#Copy input data and project source files to the bucket

for l_folder in src \
                cloud/aws \
                data/input ; do
    aws s3 cp ./$l_folder  "$aws_s3_project_location/$l_folder" --recursive \
        --exclude "*.log"   \
        --exclude ".pytest_cache" \
        --exclude "__pycache__"  \
        --profile $aws_cli_user
done


#EMR
aws ec2 create-key-pair --key-name MY-EMR-KEY-PAIR --query 'KeyMaterial' --output text > MY-EMR-KEY-PAIR.pem

#works
aws emr create-cluster \
    --name "ubart-python-retraining" \
    --release-label "emr-6.10.0" \
    --service-role "arn:aws:iam::516763997660:role/EMR_DefaultRole" \
    --ec2-attributes '{"InstanceProfile":"EMR_EC2_DefaultRole","EmrManagedMasterSecurityGroup":"sg-04cf4867d3b16f5c6","EmrManagedSlaveSecurityGroup":"sg-092b6c6432801b42e","KeyName":"ubart-python-retraining-program","AdditionalMasterSecurityGroups":[],"AdditionalSlaveSecurityGroups":[],"SubnetId":"subnet-06ae5853fb2ddbb80"}' \
    --applications Name=Spark Name=Zeppelin --instance-groups '[
    {"InstanceCount":1,"InstanceGroupType":"CORE","Name":"Core","InstanceType":"m5.xlarge","EbsConfiguration":{"EbsBlockDeviceConfigs":[{"VolumeSpecification":{"VolumeType":"gp2","SizeInGB":32},"VolumesPerInstance":2}]}},
    {"InstanceCount":1,"InstanceGroupType":"MASTER","Name":"Primary","InstanceType":"m5.xlarge","EbsConfiguration":{"EbsBlockDeviceConfigs":[{"VolumeSpecification":{"VolumeType":"gp2","SizeInGB":32},"VolumesPerInstance":2}]}}]' \
    --scale-down-behavior "TERMINATE_AT_TASK_COMPLETION" \
    --region "eu-central-1"

ssh -i ~/.ssh/ubart-python-retraining-program.pem  hadoop@ec2-3-70-253-73.eu-central-1.compute.amazonaws.com

# change variables to run on EMR
export aws_bucket_name=eu-python-retraining-airflow-emr
export project_name=py_spark_test_tasks

export project_path=~/$project_name
export SCRIPTS=$project_path/bash
export SPARK_DATA="s3://$aws_bucket_name/$project_name/data"
export SPARK_APPS=$project_path/src/main
export SPARK_APPS_LOG=$project_path/src/log
export SPARK_APPS_TEST=$project_path/src/test
export SPARK_SUBMIT_SCRIPT=$SCRIPTS/spark-submit.sh
export SPARK_MASTER="yarn"

# python var
export PYSPARK_PYTHON=python3
export PYTHONHASHSEED=1
export PYTHONPATH=$PYTHONPATH:$SPARK_APPS

mkdir -p  $SPARK_APPS \
          $SPARK_APPS_LOG \
          $SPARK_APPS_TEST

# copy files to execute
for l_folder in src \
                cloud/aws  ; do
    aws s3 cp  "$aws_s3_project_location/$l_folder" "$project_path/$l_folder" --recursive
done

# run job
spark-submit pyspark_task_validator.py -g 1
spark-submit pyspark_task_validator.py -g 2
spark-submit pyspark_task_validator.py -g 3
spark-submit pyspark_task_validator.py -g 4

spark-submit pyspark_task.py -g 1 -t 1 -tt df &\
spark-submit pyspark_task.py -g 1 -t 2 -tt df

spark-submit pyspark_task.py -g 2 -t 1 -tt df &\
spark-submit pyspark_task.py -g 2 -t 2 -tt df &\
spark-submit pyspark_task.py -g 2 -t 3 -tt df &\
spark-submit pyspark_task.py -g 2 -t 4 -tt df &\
spark-submit pyspark_task.py -g 2 -t 5 -tt df

