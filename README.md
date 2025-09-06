# ffxiv-char-spider
Gather data of FFXIV Characters created

> [!CAUTION]
> This is a web scraping tool!
> 
> Use it with caution! Do not disturb others and cause harm!

## Requirements
* An AWS account

## Database setup
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
