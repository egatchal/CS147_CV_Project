import boto3


# Put the image into the S3 bucket, which then triggers a lambda function
# to put the image along with the name of the person into the DynamoDB
def upload_to_s3(bucket_name, filename, file_bytes, name_of_person):
    s3 = boto3.resource("s3")
    ret = None
    try:
        object = s3.Object(bucket_name, "index/" + filename)
        ret = object.put(Body=file_bytes, Metadata={"FullName": name_of_person})
    except Exception as e:
        raise e
    return ret
