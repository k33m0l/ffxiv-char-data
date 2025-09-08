# ffxiv-char-spider
Gather data of FFXIV Characters created

> [!CAUTION]
> This is a web scraping tool!
> 
> Use it with caution! Do not disturb others and cause harm!

## Requirements
* An AWS account
* Python3

## Architecture
![Architecture diagram for the app](https://github.com/k33m0l/ffxiv-char-spider/blob/main/FFXIV-crawler.drawio.png)

## Configure
* With the default configuration, it ends up with roughly 3 requests/second. I recommend this or lower to avoid harm on the target website.
* Update [FETCH_LIMIT](https://github.com/k33m0l/ffxiv-char-spider/blob/07d3f5eb96ad078d52ace86407008e6bd96be0dd/loader/loader.py#L12) to configure the number of IDs that go into SQS every 15 minutes
* Update [LoaderEventRule](https://github.com/k33m0l/ffxiv-char-spider/blob/07d3f5eb96ad078d52ace86407008e6bd96be0dd/cloudformation.yaml#L85) timing to change how often the loader lambda gets triggered
* Update [ScraperEventRule](https://github.com/k33m0l/ffxiv-char-spider/blob/07d3f5eb96ad078d52ace86407008e6bd96be0dd/cloudformation.yaml#L161) timing to change how often the scraper lambda gets triggered

## Deployment

### Database setup
* Generate the base CSV using the [base_csv_generator.py](util/base_csv_generator.py)
* (Optional) Create an S3 bucket
* Upload the [base_ids.csv](util/base_ids.csv) to S3
* Using the [DynamoDB import from S3](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/S3DataImport.HowItWorks.html) feature, import the CSV.
  * You can use the first line for keys and `id` as the partition key.
  * Create a Global Secondary Index for the status
    * Partition Key = status
    * Index name = status-index
    * Attribute Projection = All
  * This may take a while (~10 minutes)

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
1. Publish loader
   1. Create a ZIP file of the `loader` folder (The loader folder must be within the ZIP file)
   2. Upload to S3
2. Publish scraper
   1. Create a ZIP file of the `scraper` folder (The scraper folder must be within the ZIP file)
   2. Upload to S3
3. Deploy the CloudFormation template
   1. DynamoDBTableName = `FFXIV` (or the name you provided during [Database setup](#database-setup))
   2. LambdaCodeBucket = `ffxiv-data-gdsafgdgfdg` (the name of the S3 bucket where the ZIP files are uploaded)
   3. LoaderLambdaCodeKey = `loader.zip` (the name of the zip file)
   4. ScraperLambdaCodeKey = `scraper.zip` (the name of the zip file)
   5. ScraperLayerCodeKey = `scraper-layer.zip` (the name of the zip file)
