from flask import Flask, request, render_template, flash, jsonify, send_file, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
from io import BytesIO
import base64
import threading
import time
import cv2
import numpy as np
from deepface import DeepFace

def decode_base64_image(image_data):
    # Decode the Base64-encoded image data
    image = base64.b64decode(image_data)

    # Write the binary data to an image file
    with open(CAM_IMAGE_PATH, "wb") as image_file:
        image_file.write(image)
    return image

CAM_IMAGE_PATH = "./camera_image.png"
app = Flask(__name__)
app.secret_key = 'cs147'.encode('utf8')

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'ubuntu'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'image_db'

mysql = MySQL(app)

recent_image_data = None
recognized_faces = []  # To store recognized faces information

@app.route('/')
def index():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id, filename FROM images")
    images = cursor.fetchall()
    cursor.close()
    return render_template('index.html', images=images)

@app.route('/upload', methods=['POST'])
def upload_image():
    password = request.form.get('password')
    if not password:
        flash('Password is required')
        return redirect(url_for('index'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM passwords WHERE password = %s", [password])
    password_record = cursor.fetchone()
    if not password_record:
        flash('Invalid password')
        return redirect(url_for('index'))
    
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
    if file:
        filename = file.filename
        file_data = file.read()
        cursor.execute("INSERT INTO images (filename, data) VALUES (%s, %s)", (filename, file_data))
        mysql.connection.commit()
        cursor.close()
        flash('File successfully uploaded')
        return redirect(url_for('index'))

@app.route('/image/<int:image_id>')
def image(image_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT data FROM images WHERE id = %s", [image_id])
    image = cursor.fetchone()
    cursor.close()
    if image:
        return send_file(BytesIO(image['data']), mimetype='image/jpeg')
    return 'Image not found', 404

@app.route('/delete_all_images', methods=["POST"])
def delete_all_images():
    cursor = mysql.connection.cursor()
    cursor.execute("TRUNCATE TABLE images")
    mysql.connection.commit()
    cursor.close()
    flash('All images have been deleted.')
    return redirect(url_for('index'))

@app.route('/recent_image')
def get_recent_image():
    global recent_image_data
    if recent_image_data:
        return send_file(BytesIO(recent_image_data), mimetype='image/png')
    return 'No image uploaded', 404

@app.route('/api/upload', methods=['POST'])
def api_upload_image():
    jsonData = request.get_json()
    image = jsonData["image"]
    if not image:
        return jsonify({'error': 'No image received'}), 400
    else:
        print("Adding image from cam")
        global recent_image_data
        recent_image_data = decode_base64_image(image)
        facial_recognition()
        return jsonify({'success': 'Image received'}), 201
    
@app.route('/recognized_faces')
def get_recognized_faces():
    return jsonify(recognized_faces)

def facial_recognition():
    global recognized_faces
    if os.path.exists(CAM_IMAGE_PATH):
        try:
            # Read the current image
            img1 = cv2.imread(CAM_IMAGE_PATH)
            recognized_faces = []
            
            # Fetch all images from the database
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT id, filename, data FROM images")
            images = cursor.fetchall()
            cursor.close()
            if len(images) == 0:
                print("There are no images in the DB!")
            for image in images:
                print("Comparing image here")
                # Convert binary data to numpy array
                img_data = image['data']
                print("1")
                img2 = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
                print("2")
                # Perform face recognition
                try:
                    print("3")
                    result = DeepFace.verify(img1, img2, enforce_detection=False)
                    print("4")
                    if result["verified"]:
                        print("5")
                        recognized_faces.append({
                            "image_id": image["id"],
                            "filename": image["filename"],
                            "match": result["verified"]
                        })
                        print("6")
                except Exception as e:
                    print(f"Error in face recognition: {e}")

            print("Faces recognized:", recognized_faces)
        except Exception as e:
            print(f"Error in face recognition: {e}")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
