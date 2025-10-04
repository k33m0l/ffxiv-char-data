# ffxiv-char-spider
Gather data of FFXIV Characters created

> [!CAUTION]
> This is a web scraping tool!
> 
> Use it with caution! Do not disturb others and cause harm!

## Requirements
* An AWS account
* Python3
* AWS CLI
* AWS SAM

## Architecture
![Architecture diagram for the app](https://github.com/k33m0l/ffxiv-char-spider/blob/main/FFXIV-crawler.drawio.png)

## Configure
* With the default configuration, it ends up with roughly 3 requests/second. I recommend this or lower to avoid harm on the target website.
* Update [FETCH_LIMIT](https://github.com/k33m0l/ffxiv-char-spider/blob/07d3f5eb96ad078d52ace86407008e6bd96be0dd/loader/loader.py#L12) to configure the number of IDs that go into SQS every 15 minutes
* Update [LoaderEventRule](https://github.com/k33m0l/ffxiv-char-spider/blob/07d3f5eb96ad078d52ace86407008e6bd96be0dd/cloudformation.yaml#L85) timing to change how often the loader lambda gets triggered
* Update [ScraperEventRule](https://github.com/k33m0l/ffxiv-char-spider/blob/07d3f5eb96ad078d52ace86407008e6bd96be0dd/cloudformation.yaml#L161) timing to change how often the scraper lambda gets triggered

## Deployment

### Prerequisites
#### Database base CSV
* Generate the base CSV using the [base_csv_generator.py](util/base_csv_generator.py)
* Create an S3 bucket or use an existing one
* Upload the [base_ids.csv](util/base_ids.csv) to S3

### Creating a Lambda Layer
* `python -m venv .venv`
* `source .venv/Scripts/activate`
* `cd scraper`
* `pip install -r requirements.txt`
* `cd .venv/Lib/site-packages`
* Copy all files into a directory called `python`
* Zip the newly created directory (The first file within the zip must be the directory)
* Upload to S3

### Deployment to AWS
1. Package SAM
   1. Replace `{add-s3-bucket-here}` in the command with your S3 bucket name
```shell
sam package --template-file .\cloudformation-template.yaml --output-template-file packaged.yaml --s3-bucket {add-s3-bucket-here} --s3-prefix templates
```
2. Deploy SAM 
   1. Replace `{add-s3-bucket-here}` in the command with your S3 bucket name
   2. Repalce `{add-csv-filename-here}` in the command with you CSV file name
```shell
sam deploy --template-file .\packaged.yaml --stack-name FFXIV --capabilities CAPABILITY_IAM --parameter-overrides ParameterKey=DataBucket,ParameterValue={add-s3-bucket-here} ParameterKey=DataS3Key,ParameterValue={add-csv-filename-here}
```
3. Wait patiently :) Do not forget to delete the CloudFormation Stack if you don't want to run this anymore. It won't auto delete.
```shell
sam delete --stack-name FFXIV
```
