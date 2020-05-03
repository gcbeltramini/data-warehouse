# Debugging

## Run the unit tests

```bash
conda install -yn etl-env --file requirements/requirements_test.txt
conda activate etl-env
python -m pytest
conda deactivate
```

## Run the jupyter notebooks

It's possible to run any query on Redshift.

```bash
conda install -yn base nb_conda_kernels
conda install -yn etl-env --file requirements/requirements_dev.txt
conda activate base
jupyter notebook
```

## Check the content of the files in S3

To check the file content (useful for the `CREATE TABLE` command):

1. Navigate in the terminal until a file is found:

   ```shell
   aws s3 ls s3://udacity-dend/song_data/A/A/A/TRAAAAV128F421A322.json
   aws s3 ls s3://udacity-dend/log_data/2018/11/2018-11-01-events.json
   ```

1. Copy the file to the local machine:

   ```shell
   aws s3 cp s3://udacity-dend/song_data/A/A/A/TRAAAAV128F421A322.json .
   aws s3 cp s3://udacity-dend/log_data/2018/11/2018-11-01-events.json .
   ```

   But if it fails with

   ```shell
   fatal error: An error occurred (403) when calling the HeadObject operation: Forbidden
   ```

   open it in the web browser. The path in S3 becomes `http://[bucket-name].s3.amazonaws.com/[prefix]/[file]`,
e.g., <http://udacity-dend.s3.amazonaws.com/song_data/A/A/A/TRAAAAV128F421A322.json> or
<http://udacity-dend.s3.amazonaws.com/log_data/2018/11/2018-11-01-events.json>.

## Run the queries in the AWS query editor

1. Redshift: <https://console.aws.amazon.com/redshift/> --> Query editor
   - The IAM user needs the policies `AmazonRedshiftQueryEditor` and `AmazonRedshiftReadOnlyAccess`.
1. Choose the cluster, and enter the database name, database user and password.
