from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import csv
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from mysql.connector import connect, Error
import json
import os
import io
from PIL import Image
from image_compare_crop import sift_image_comparison, crop_boxes_from_image, process_cropped_image_box, \
    convert_to_option

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'csv'}
# result_dict = {}
app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def connect_to_mysql():
    try:
        # Replace these values with your MySQL connection details
        connection = connect(
            host='127.0.0.1',
            user='root',
            password='root',
            database='omrchecker'
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


@app.route('/getUniqueIds', methods=['GET'])
def get_unique_ids():
    try:
        connection = connect_to_mysql()
        if connection:
            query = "SELECT unique_id FROM omr_template"
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(query)
                unique_ids = [row['unique_id'] for row in cursor.fetchall()]
            return jsonify({'uniqueIds': unique_ids}), 200
    except Exception as e:
        print(f"Error fetching unique IDs: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        if connection:
            connection.close()


def insert_data_into_table(connection, form_data, boxes_data, omr_template_path):
    try:
        cursor = connection.cursor()

        with open(omr_template_path, 'rb') as omr_template_file:
            omr_template_blob = omr_template_file.read()

        # Convert JSON strings to Python dictionaries
        form_data_dict = json.loads(form_data)
        boxes_data_dict = json.loads(boxes_data)

        # Insert data into the omr_template table
        insert_query = """
            INSERT INTO omr_template (image_blob, num_questions, questions_per_box, num_boxes, boxes_data)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            omr_template_blob,
            form_data_dict.get('numQuestions'),
            form_data_dict.get('questionsPerBox'),
            form_data_dict.get('numBoxes'),
            json.dumps(boxes_data_dict)
        ))

        connection.commit()
        print("Data inserted successfully.")

    except Error as e:
        print(f"Error inserting data into table: {e}")

    finally:
        if cursor:
            cursor.close()


@app.route('/submitFormData', methods=['POST'])
def submit_form_data():
    try:
        # Access the form data and boxes data
        form_data = request.form.get('formData')
        boxes_data = request.form.get('boxesData')

        # Process the data as needed
        print('Form Data:', form_data)
        print('Boxes Data:', boxes_data)

        # Access the OMR template image
        omr_template = request.files['omrTemplate']
        omr_template_path = os.path.join(app.config['UPLOAD_FOLDER'], 'omr_template.png')
        omr_template.save(omr_template_path)
        print('OMR Template image saved')

        # Connect to MySQL
        connection = connect_to_mysql()

        if connection:
            # Insert data into the table
            insert_data_into_table(connection, form_data, boxes_data, omr_template_path)
            connection.close()

        return jsonify({'message': 'Data received and inserted successfully'}), 200

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# @app.route('/submitFormData', methods=['POST'])
# def submit_form_data():
#     try:
#         # Access the form data and boxes data
#         form_data = request.form.get('formData')
#         boxes_data = request.form.get('boxesData')
#
#         # Process the data as needed
#         print('Form Data:', form_data)
#         print('Boxes Data:', boxes_data)
#
#         # Access the OMR template image
#         omr_template = request.files['omrTemplate']
#         omr_template.save(os.path.join(app.config['UPLOAD_FOLDER'], 'omr_template.png'))
#         print('OMR Template image saved')
#
#         # Add your logic here to process the data
#
#         return jsonify({'message': 'Data received successfully'}), 200
#
#     except Exception as e:
#         print(f"Error processing request: {str(e)}")
#         return jsonify({'error': 'Internal server error'}), 500

def compare_images_with_database(connection, image_files, selected_unique_id, ans_dict):
    try:
        cursor = connection.cursor(dictionary=True)

        # Retrieve the entire row from the database for the selected unique_id
        query = "SELECT * FROM omr_template WHERE unique_id = %s"
        cursor.execute(query, (selected_unique_id,))
        result = cursor.fetchone()
        # print(result)

        if not result:
            return jsonify({'error': 'Selected unique_id not found'}), 400

        # Process the entire row as needed
        stored_image_blob = result['image_blob']
        num_questions = result['num_questions']
        questions_per_box = result['questions_per_box']
        num_boxes = result['num_boxes']
        boxes_data = json.loads(result['boxes_data'])
        # print("Yo->", num_questions, questions_per_box, num_boxes, boxes_data)
        # Convert stored_image_blob to an image
        stored_image = Image.open(io.BytesIO(stored_image_blob))
        # print(stored_image)

        for file in image_files:
            if file and allowed_file(file.filename):
                # Read the uploaded image
                uploaded_image = Image.open(io.BytesIO(file.read()))
                # print(uploaded_image)
                cropped_uploaded_image = sift_image_comparison(stored_image, uploaded_image)
                # print(cropped_uploaded_image)
                # print(cropped_uploaded_image)
                cropped_box_images = crop_boxes_from_image(boxes_data, cropped_uploaded_image)
                result_dict = {key: {"Correct_ans": convert_to_option(value), "Written_ans": None} for key, value in
                               ans_dict.items()}
                for i, cropped_box_image in enumerate(cropped_box_images, start=1):
                    # print(i)
                    # print(cropped_box_images[cropped_box_image])

                    process_cropped_image_box(cropped_box_images[cropped_box_image], num_questions, questions_per_box,
                                              num_boxes, i,
                                              ans_dict, result_dict)
                # print(result_dict)
                # if cropped_box_images:
                # Process the dictionary of cropped box images as needed
                # print("Cropped Box Images:", cropped_box_images)
                # Perform image comparison logic here
                # Example: You might want to use image processing libraries like OpenCV

                # For demonstration purposes, print a message

                print(f"Image comparison result for unique_id {selected_unique_id}: Your logic here")

        return result_dict, 200

    except Exception as e:
        print(f"Error comparing images with database: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

    finally:
        if cursor:
            cursor.close()


# Add this route to call the image comparison function
# @app.route('/compareImages', methods=['POST'])
# def compare_images():
#     try:
#         # Check if the POST request has files and uniqueId
#         if 'image' not in request.files or 'uniqueId' not in request.form:
#             return jsonify({'error': 'Images or uniqueId not provided'}), 400
#
#         image_files = request.files.getlist('image')
#         selected_unique_id = request.form['uniqueId']
#
#         connection = connect_to_mysql()
#         if connection:
#             response, status_code = compare_images_with_database(connection, image_files, selected_unique_id)
#             connection.close()
#             return response, status_code
#
#     except Exception as e:
#         print(f"Error processing image comparison request: {str(e)}")
#         return jsonify({'error': 'Internal server error'}), 500


@app.route('/', methods=['POST'])
def upload_files():
    try:
        # Check if the POST request has files
        if 'csvFile' not in request.files:
            return jsonify({'error': 'CSV file not provided'}), 400

        csv_file = request.files['csvFile']
        image_files = request.files.getlist('image')
        selected_unique_id = request.form['uniqueId']

        print(image_files)
        # Ensure that the UPLOAD_FOLDER directory exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        if csv_file and allowed_file(csv_file.filename):
            csv_filename = secure_filename(csv_file.filename)
            csv_file_path = os.path.join(app.config['UPLOAD_FOLDER'], csv_filename)
            csv_file.save(csv_file_path)

            # Read CSV file into a DataFrame
            ans_df = pd.read_csv(csv_file_path)

            # Convert DataFrame to a dictionary with question number as key and answer as value
            ans_dict = ans_df.set_index('Question No.').to_dict()['Ans']

            # Print the DataFrame
            print(ans_df)
            print("Answer Dictionary:", ans_dict)

            # Close the CSV file
            csv_file.close()

        connection = connect_to_mysql()
        if connection:
            response, status_code = compare_images_with_database(connection, image_files, selected_unique_id, ans_dict)
            connection.close()
            return jsonify(response), status_code
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(port=5000)  # Run the Flask app on port 5000 (or your desired port)
