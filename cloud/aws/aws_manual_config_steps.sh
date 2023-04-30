# install awscli
sudo apt-get update
sudo apt-get install awscli

# config for keys
mkdir -p ~/.aws
aws configure

# aws set up
export aws_cli_user=ubart-cli
export aws_bucket_region=eu-central-1
export aws_bucket_name=eu-python-retraining-airflow-emr
export aws_account_id=XXXXX
export project_name=$(basename `pwd`)
export aws_s3_project_location="s3://$aws_bucket_name/$project_name"

# create aws cli user
aws iam create-user        --user-name $aws_cli_user

# create attach policy
aws iam attach-user-policy --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess --user-name $aws_cli_user
aws iam attach-user-policy --policy-arn arn:aws:iam::aws:policy/AmazonEMRFullAccessPolicy_v2 --user-name $aws_cli_user
aws iam attach-user-policy --policy-arn arn:aws:iam::aws:policy/AmazonEMRFullAccess --user-name $aws_cli_user

# create key
aws iam create-access-key  --user-name $aws_cli_user

# ~/.aws/config should look like
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

#Copy whole project to bucket
aws s3 ls "s3://$aws_bucket_name" --profile $aws_cli_user
aws s3 rm "$aws_s3_project_location" --recursive --profile $aws_cli_user
aws s3 cp ./  "$aws_s3_project_location" --recursive \
    --exclude "id_rsa*" \
    --exclude "*.iml"   \
    --exclude ".idea/*" \
    --exclude ".git*"   \
    --exclude ".git/*"  \
    --exclude "docker*" \
    --exclude "airflow" \
    --exclude "*.pem"   \
    --exclude "*.log"   \
    --exclude "data/df/task*" \
    --exclude "data/sql/task*"\
    --exclude "data/*.csv"    \
    --exclude ".pytest_cache" \
    --exclude ".__pycache__"  \
    --profile $aws_cli_user

#EMR
# aws ec2 create-key-pair --key-name MY-EMR-KEY-PAIR --query 'KeyMaterial' --output text > MY-EMR-KEY-PAIR.pem
# aws emr create-cluster --name MY-EMR-CLUSTER --release-label emr-6.3.0 \
# --instance-count 3 --instance-type m5.xlarge --ec2-attributes KeyName=MY-EMR-KEY-PAIR \
# --applications Name=Spark --use-default-roles --enable-debugging \
# --service-role EMR_DefaultRole --security-configuration 'Name=MyEmrSecurityConfig'


export SCRIPTS=/opt/bash
export SPARK_DATA=$aws_s3_project_location/data
export SPARK_APPS=/opt/spark-apps/main
export SPARK_APPS_LOG=/opt/spark-apps/log
export SPARK_APPS_TEST=/opt/spark-apps/test
export SPARK_SUBMIT_SCRIPT=$SCRIPTS/spark-submit.sh

# python var
export PYSPARK_PYTHON=python3
export PYTHONHASHSEED=1
export PYTHONPATH=$PYTHONPATH:$SPARK_APPS

mkdir -p $SCRIPTS    \
         $SPARK_APPS \
         $SPARK_APPS_LOG \
         $SPARK_APPS_TEST

