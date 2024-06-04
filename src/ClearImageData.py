import boto3

# Initialize a session using Amazon DynamoDB
session = boto3.Session(
    aws_access_key_id="ACCESS KEY HERE",
    aws_secret_access_key="SECRET KEY HERE",
    region_name="us-east-1",
)

# Initialize DynamoDB resource
dynamodb = session.resource("dynamodb")


# Scan the table to get all the items
def scan_table(table):
    response = table.scan()
    data = response["Items"]
    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        data.extend(response["Items"])
    return data


# Delete items from the table
def delete_items(table, items):
    with table.batch_writer() as batch:
        for item in items:
            batch.delete_item(
                Key={
                    "RekognitionId": item["RekognitionId"]
                    # Add other key attributes if your table has a composite primary key
                }
            )


# Main function to scan and delete all items
def clear_dynamodb_table(table_name):
    table = dynamodb.Table(table_name)
    items = scan_table(table)
    delete_items(table, items)
    print(f"Deleted {len(items)} items from DynamoDB table {table_name}")


def clear_s3_bucket(bucket_name, prefix):
    s3 = boto3.client("s3")
    # List all objects in the specified S3 bucket with the given prefix
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    if "Contents" in response:
        # Extract the filenames from the response
        file_keys = [{"Key": file["Key"]} for file in response["Contents"]]

        # Delete the objects
        response = s3.delete_objects(Bucket=bucket_name, Delete={"Objects": file_keys})
        print(response)
        return response
    else:
        print("No objects found with the given prefix.")
        return None
