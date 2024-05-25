from flask import Flask, request, render_template, flash, jsonify, send_file, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'cs147'.encode('utf8')

# Variable to store the most recently uploaded image
recent_image = {'filename': None, 'data': None}

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'ubuntu'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'image_db'

mysql = MySQL(app)

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
    if recent_image['data'] is not None:
        return send_file(BytesIO(recent_image['data']), mimetype='image/jpeg')
    return 'No image uploaded', 404

@app.route('/api/upload', methods=['POST'])
def api_upload_image():
    print("RECEIVEING IMAGE FROM CAMERA")
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        recent_image['filename'] = file.filename
        recent_image['data'] = file.read()
        print(recent_image['data'])
        return jsonify({'success': 'File successfully uploaded'}), 201

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
