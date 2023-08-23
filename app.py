from flask import Flask, render_template, request
from PIL import Image
import pytesseract
from rapidfuzz import fuzz, utils
import pandas as pd
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
upload_folder = os.path.join('static', 'uploads')

app.config['UPLOAD'] = upload_folder

def calculate_text_similarity(text1, text2):
    try:
        similarity = fuzz.WRatio(text1, text2, processor=utils.default_process)
    except:
        return 0

    return similarity

pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/score', methods=['POST'])
def score():
    image = request.files['image']
    cat_id = request.form['category_id']
    widget_type = request.form['widget_type']

    try:
        cat_id = int(cat_id)
    except:
        pass

    filename = secure_filename(image.filename)
    image.save(os.path.join(app.config['UPLOAD'], filename))
    img = os.path.join(app.config['UPLOAD'], filename)

    image_path = 'temp_image.jpg'
    image.save(image_path)

    # Process the image using OCR (pytesseract)
    extracted_text_new_image = pytesseract.image_to_string(Image.open(img))
   

    extracted_image_dataframe = pd.read_csv('/Users/akshaykumar/Desktop/banner_dedup/notebooks/banner_images_final_filter.csv')
    if cat_id:
        extracted_image_dataframe = extracted_image_dataframe[extracted_image_dataframe['category_id']==cat_id]
    if widget_type:
        extracted_image_dataframe = extracted_image_dataframe[extracted_image_dataframe['widget_type_name']==widget_type]

    extracted_image_dataframe['similarity_score'] = extracted_image_dataframe['extracted_texts']\
    .apply(lambda x : calculate_text_similarity(x,extracted_text_new_image))

    count_images = extracted_image_dataframe[extracted_image_dataframe['similarity_score']>88]['image_paths_list'].count()
    if count_images !=0:
        msg = "An Image with similar text already exist, Please upload a new image with different text." + "\n" + "Below are the top three sample of the duplicate image"
        path  = list(extracted_image_dataframe[extracted_image_dataframe['similarity_score']>88].sort_values(by='similarity_score', ascending=False)['image_paths_list'])
    else:
        msg = "There are no duplicate banners corresponding to this one! Please go ahead and upload the same."
        path = None
    
    print(path)
    return render_template('score.html', text = msg, image_path = path, uploaded_image = img)

if __name__ == '__main__':
    app.run(debug=True)
