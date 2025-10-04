# ffxiv-char-spider
Gather data of FFXIV Characters created

> [!CAUTION]
> This is a web scraping tool!
> 
> Use it with caution! Do not disturb others and cause harm!

## Requirements
* An AWS account
* AWS CLI
* AWS SAM
* Python3.13
* Pip
* Make

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

### Deployment
1. Package dependencies by running `make build-layer`
2. Build template with `sam build`
3. (Optional) Validate using `sam validate`
4. Deploy using `sam deploy --guided` and follow the instructions 
5. Wait patiently :) Do not forget to delete the CloudFormation Stack if you don't want to run this anymore. It won't auto delete.
   1. You can delete the resources with `sam delete --stack-name FFXIV`, where stack-name is what you provided during the deployment