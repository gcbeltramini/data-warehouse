# Run the ETL

1. [Create an AWS Redshift cluster](docs/aws_redshift.md)
1. Run the Python scripts:

   ```bash
   conda create -yn etl-env python=3.7 --file requirements/requirements.txt
   conda activate etl-env
   python create_tables.py
   python etl.py
   conda deactivate
   ```

1. [Run Python unit tests, queries, debug problems](docs/tests_debug.md)
