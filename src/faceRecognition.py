import boto3
import io
from PIL import Image

rekognition = boto3.client("rekognition", region_name="us-east-1")
dynamodb = boto3.client("dynamodb", region_name="us-east-1")


def facial_recognition(image_path):
    image = Image.open(image_path)
    stream = io.BytesIO()
    image.save(stream,format="JPEG")
    image_binary = stream.getvalue()
    
    try:
        response = rekognition.search_faces_by_image(
            CollectionId="image_db", Image={"Bytes": image_binary}
        )
    except Exception as e:
        response = None
        print("FACIAL RECOGNITION FAILED GOT ERROR", e)
        return None

    found = False
    names = []
    for match in response["FaceMatches"]:
        print("Face ID:", match["Face"]["FaceId"])
        print("Confidence", match["Face"]["Confidence"])
        # The .get_item() method gets the document/row from Dynamodb via the FaceId
        # SELECT * FROM images WHERE RekognitionId = match['Face']['FaceId']
        face = dynamodb.get_item(
            TableName="images", Key={"RekognitionId": {"S": match["Face"]["FaceId"]}}
        )
        # Returns a dictionary of the form:
        # {'Item': {'RekognitionId': {'S': 'FACEID_HERE'}, 'FullName': {'S': 'Firstname Lastname'}, ...}

        if "Item" in face:
            print("Found Person:", face["Item"]["FullName"]["S"])
            found = True
            names.append(face["Item"]["FullName"]["S"])
    return {"found": found, "names_of_person": names}
