# Create an AWS Redshift cluster

Reference: [Getting started with Amazon Redshift](<https://docs.aws.amazon.com/redshift/latest/gsg/getting-started.html>)

## Create an AWS account

1. <https://aws.amazon.com/console/> --> "Create a Free Account"
1. After the account is created, sign in at <https://aws.amazon.com/console/> using "Root user"

## Create an IAM role

Redshift has to act as a user who has read access to S3.

1. IAM: <https://console.aws.amazon.com/iam/>
1. Left navigation pane: [Roles](https://console.aws.amazon.com/iam/home#/roles)
1. [Create role](https://console.aws.amazon.com/iam/home#/roles$new?step=type)
   1. `Select type of trusted entity`: AWS service
   1. `Choose a use case`: Redshift
   1. `Select your use case`: Redshift - Customizable
   1. `Attach permissions policies`: check `AmazonS3ReadOnlyAccess`
   1. `Add tags`: skip
   1. `Review` - `Role name`: "myRedshiftRole" (it cannot be changed later)
1. In the list of roles, click on the role created now and copy the role ARN.
1. Insert the value in file `dwh.cfg` (`[IAM_ROLE]` --> `ARN`)

## Create a security group

The BI tools (e.g., jupyter) have to be able to connect to Redshift, otherwise it is accessible only
from the VPC (virtual private cloud).

1. EC2: <https://console.aws.amazon.com/ec2>
1. Since we are going to create the Redshift cluster in region `us-west-2`, make sure this is the
region in the top right corner.
1. Left navigation pane: `Network & Security` --> `Security Groups` --> `Create Security Group`
1. `Basic details`:
   - `Security group name`: "RedshiftSecurityGroup"
   - `Description`: "Authorize Redshift cluster access"
   - `VPC`: leave the default
1. `Inbound rules` --> `Add Rule`:
   - `Type`: Custom TCP
   - `Protocol`: TCP
   - `Port range`: 5439 (default port for Amazon Redshift)
   - `Source`: "Custom", 0.0.0.0/0; or "My IP", and let AWS find your IP (check [here](https://www.whatsmyip.org))
     - **Important**: Using 0.0.0.0/0 is not recommended for anything other than demonstration
     purposes because it allows access from any computer on the internet. In a real environment, you
     would create inbound rules based on your own network settings.
1. `Create security group`

## Launch a Redshift cluster

**Important**: The standard Amazon Redshift usage fees will apply for the cluster that is about to
be created until it is deleted.

1. Redshift: <https://console.aws.amazon.com/redshift/>. The following instructions refer to the old
UI.
1. At the top right corner, choose the AWS region `us-west-2` to create the cluster.
1. On the navigation menu, choose `Clusters` --> `Launch cluster`.
1. `Cluster details`:
   - `Cluster identifier`: "redshift-cluster"
   - `Database name`: "dev"
   - `Database port`: 5439
   - `Master user name`: "awsuser"
   - `Master user password`: enter a password (keep closely guarded, e.g., don't share on GitHub)
1. `Node configuration`:
   - `Node type`: dc2.large
   - `Cluster type`: "Multi Node"
   - `Number of compute nodes`: 4
1. `Additional configuration` (leave the default for the rest):
   - `Publicly accessible`: Yes
   - `VPC security groups`: choose the security group previously created (e.g.,
   "RedshiftSecurityGroup") - click to select; Command + click or Shift + click to select multiple
   groups.
   - `Available IAM roles`: choose the IAM role previously created (e.g., "myRedshiftRole")
1. `Launch cluster`. (it takes about 5-10 minutes)
1. In the list of clusters, click on the cluster created now --> tab `Properties` and copy the
endpoint
1. Insert the value in file `dwh.cfg` (`[CLUSTER]` --> `HOST`)

## Cleanup

Perform these steps after running the ETL.

1. Delete the cluster:
   - Redshift: <https://console.aws.amazon.com/redshift/>. Select the cluster and delete it. It is
   not necessary to create a snapshot.
1. Revoke access to the port and CIDR/IP address in the security group:
   - EC2: <https://console.aws.amazon.com/ec2> --> region `us-west-2`
   - `Network & Security` --> `Security Groups` --> select the security group that was created
   (e.g., "RedshiftSecurityGroup")
   - `Inbound rules` --> `Edit inbound rules` --> delete the rule related to Redshift

# Run the ETL

```bash
conda create -yn etl-env python=3.7 --file requirements/requirements.txt
conda activate etl-env
python create_tables.py
python etl.py
conda deactivate
```

# Debugging

## Run the unit tests

```bash
conda install -yn etl-env --file requirements/requirements_test.txt
conda activate etl-env
python -m pytest
conda deactivate
```

## Run the jupyter notebooks

```bash
conda install -yn base nb_conda_kernels
conda install -yn etl-env --file requirements/requirements_dev.txt
conda activate base
jupyter notebook
```

## Check the content of the files in S3

To check the file content (useful for the `CREATE TABLE` command):

1. Navigate in the terminal until you find a file:

   ```shell
   aws s3 ls s3://udacity-dend/song_data/A/A/A/TRAAAAV128F421A322.json
   aws s3 ls s3://udacity-dend/log_data/2018/11/2018-11-01-events.json
   ```

   But if you try to copy it to the local machine, it will fail:

   ```shell
   $ aws s3 cp s3://udacity-dend/song_data/A/A/A/TRAAAAV128F421A322.json .
   fatal error: An error occurred (403) when calling the HeadObject operation: Forbidden
   
   $ aws s3 cp s3://udacity-dend/log_data/2018/11/2018-11-01-events.json .
   fatal error: An error occurred (403) when calling the HeadObject operation: Forbidden
   ```

1. Open it in the web browser. The path in S3 becomes `http://[bucket-name].s3.amazonaws.com/[prefix]/[file]`,
e.g., <http://udacity-dend.s3.amazonaws.com/song_data/A/A/A/TRAAAAV128F421A322.json> or
<http://udacity-dend.s3.amazonaws.com/log_data/2018/11/2018-11-01-events.json>.

## Run the queries in the AWS query editor

1. Redshift: <https://console.aws.amazon.com/redshift/> --> Query editor
1. Choose the cluster, and enter the database name, user name and password.
