from flask import (
    Flask,
    request,
    render_template,
    flash,
    jsonify,
    send_file,
    redirect,
    url_for,
)
import boto3
import os
import time
from io import BytesIO
import base64
from ClearImageData import clear_s3_bucket, clear_dynamodb_table
from UploadToS3 import upload_to_s3
from faceRecognition import facial_recognition

CAM_IMAGE_PATH = "./camera_image.png"
S3_BUCKET_NAME = "cs147-project"
S3_BUCKET_PREFIX = "index"
DYNAMODB_TABLE_NAME = "images"
app = Flask(__name__)
app.secret_key = "cs147".encode("utf8")

recent_image_data = None
button_pressed = False
operation_finished = False
image_recognition = None

def decode_base64_image(image_data):
    # Decode the Base64-encoded image data
    image = base64.b64decode(image_data)

    # Write the binary data to an image file
    with open(CAM_IMAGE_PATH, "wb") as image_file:
        image_file.write(image)
    return image


@app.route("/")
def index():
    # List objects in your S3 bucket
    s3 = boto3.client("s3")
    objects = s3.list_objects_v2(Bucket=S3_BUCKET_NAME)
    image_urls = []
    for obj in objects.get("Contents", []):
        # Get the object key
        key = obj["Key"]
        # Generate the URL to access the object
        url = s3.generate_presigned_url(
            "get_object", Params={"Bucket": S3_BUCKET_NAME, "Key": key}
        )
        image_urls.append(url)
    return render_template("index.html", image_urls=image_urls)


@app.route("/manual_upload", methods=["POST"])
def upload_image():
    password = request.form.get("password")
    name_of_person = request.form.get("name_of_person")
    if password != "cs147":
        flash("Invalid password")
        return redirect(url_for("index"))

    file = request.files["file"]
    if file.filename == "" or name_of_person == "":
        flash("No selected file or no name given")
        return redirect(url_for("index"))
    if file and name_of_person:
        filename = file.filename
        file_data = file.read()
        # Upload image to S3 Bucket here
        try:
            ret = upload_to_s3(S3_BUCKET_NAME, filename, file_data, name_of_person)
            flash(f"File successfully uploaded: {ret}")
        except Exception as e:
            flash(f"File upload failed with error {e}")
        return redirect(url_for("index"))


@app.route("/delete_all_images", methods=["POST"])
def delete_all_images():
    clear_s3_bucket(S3_BUCKET_NAME, S3_BUCKET_PREFIX)
    clear_dynamodb_table(DYNAMODB_TABLE_NAME)
    flash("All images have been deleted.")
    return redirect(url_for("index"))


@app.route("/api/upload", methods=["POST"])
def esp32_cam_upload_image():
    jsonData = request.get_json()
    image = jsonData["image"]
    if not image:
        return jsonify({"error": "No image received"}), 400
    else:
        print("Adding image from cam")
        global recent_image_data
        recent_image_data = decode_base64_image(image)
        recognitionStatus = facial_recognition(CAM_IMAGE_PATH)
        print(recognitionStatus)
        global image_recognition, operation_finished, button_pressed
        image_recognition = recognitionStatus
        operation_finished = True
        button_pressed = False
        if recognitionStatus:
            return jsonify(recognitionStatus), 201
        else:
            return jsonify({"error": "Failed to do facial recognition"}), 400


@app.route("/recent_image")
def get_recent_image():
    global recent_image_data
    if recent_image_data:
        return send_file(BytesIO(recent_image_data), mimetype="image/png")
    return "No image uploaded", 404


@app.route("/check_button_pressed")
def check_button_pressed():
    global button_pressed
    return str(button_pressed), 200


@app.route("/api/button", methods=["POST"])
def api_button_pressed():
    global button_pressed, operation_finished, image_recognition
    button_pressed = True
    operation_finished = False
    image_recognition = None
    while not operation_finished:
        time.sleep(2)
    return jsonify(image_recognition), 200
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
