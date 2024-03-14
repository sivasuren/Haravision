from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import tensorflow as tf
import os
from collections import Counter

app = Flask(__name__)
model = tf.keras.models.load_model('C:/Users/Surend/OneDrive/Desktop/Projects/Haravision/Model/plant_disease.h5')

class_names = [
    "Apple___Apple_scab", "Apple___Black_rot", "Apple___Cedar_apple_rust", "Apple___healthy", "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew", "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot", "Corn_(maize)__Common_rust",
    "Corn_(maize)___Northern_Leaf_Blight", "Corn_(maize)__healthy", "Grape__Black_rot",
    "Grape__Esca_(Black_Measels)", "Grape__Leaf_blight(Isariopsis_Leaf_Spot)", "Grape___healthy",
    "Orange__Haunglongbing(Citrus_greening)", "Peach___Bacterial_spot", "Peach___healthy",
    "Pepper,bell__Bacterial_spot", "Pepper,bell__healthy", "Potato___Early_blight", "Potato___Late_blight",
    "Potato___healthy", "Raspberry___healthy", "Soybean___healthy", "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch", "Strawberry___healthy", "Tomato___Bacterial_spot", "Tomato__Early_blight",
    "Tomato___Late_blight", "Tomato___Leaf_Mold", "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite", "Tomato___Target_Spot", "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus", "Tomato___healthy"
]

solutions = {
    "Apple___Apple_scab": "Mancozeb",
    "Apple___Black_rot": "Captan",
    "Apple___Cedar_apple_rust": "Myclobutanil",
    "Cherry_(including_sour)___Powdery_mildew": "Sulfur",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "Chlorothalonil",
    "Corn_(maize)__Common_rust": "Triazoles (Propiconazole)",
    "Corn_(maize)___Northern_Leaf_Blight": "Pyraclostrobin",
    "Grape__Black_rot": "Mancozeb",
    "Grape__Leaf_blight(Isariopsis_Leaf_Spot)": "Mancozeb",
    "Orange__Haunglongbing(Citrus_greening)": "No disease",
    "Peach___Bacterial_spot": "Copper-based fungicides",
    "Potato___Early_blight": "Chlorothalonil",
    "Potato___Late_blight": "Mancozeb",
    "Pepper,bell__Bacterial_spot": "Copper-based fungicide",
    "Squash___Powdery_mildew": "Potassium Bicarbonate",
    "Strawberry___Leaf_scorch": "Azoxystrobin",
    "Tomato___Bacterial_spot": "Copper-based fungicide",
    "Tomato__Early_blight": "Chlorothalonil",
    "Tomato___Late_blight": "Chlorothalonil",
    "Tomato___Leaf_Mold": "Chlorothalonil",
    "Tomato___Septoria_leaf_spot": "Chlorothalonil",
    "Tomato___Spider_mites Two-spotted_spider_mite": "Insecticidal Soap",
    "Tomato___Target_Spot": "Chlorothalonil",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "No solution",
    "Tomato___Tomato_mosaic_virus": "No solution"
}

# Configure the upload folder
app.config['UPLOAD_FOLDER'] = 'C:/Users/Surend/OneDrive/Desktop/Tomato app/Saved Images'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def calculate_severity(predictions):
    top_probability = np.max(predictions)
    severity = top_probability * 100
    return severity

def calculate_ratings(severity):
    if severity < 1:
        return 0
    elif severity < 11:
        return 1
    elif severity < 26:
        return 3
    elif severity < 51:
        return 5
    else:
        return 7

def calculate_lifespan(pi, pdi):
    # Calculate lifespan based on PI and PDI
    if pi == 0:
        return 0
    lifespan = (100 / pi) * pdi
    return int(round(lifespan))

@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(request.url)
    files = request.files.getlist('file')
    results = []
    total_count = len(files)
    infected_count = 0
    sum_ratings = 0
    disease_predictions = []
    for file in files:
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            img = cv2.imread(file_path)
            img = cv2.resize(img, (224, 224))
            b, g, r = cv2.split(img)
            b = cv2.medianBlur(b, 5)
            g = cv2.medianBlur(g, 5)
            r = cv2.medianBlur(r, 5)
            denoised_img = cv2.merge((b, g, r))
            img = img / 255.0
            img = np.expand_dims(img, axis=0)
            prediction = model.predict(img)
            predicted_class = class_names[np.argmax(prediction)]
            # Calculate severity based on the probability
            severity = round(calculate_severity(prediction), 2) if predicted_class != "Tomato___healthy" else 0
            # Fetch the respective solution for the predicted disease
            solution = solutions.get(predicted_class, "Solution not available")
            image_path = "/static/Saved Images/{filename}"
            infected_count += 1 if predicted_class != "Tomato___healthy" else 0
            sum_ratings += calculate_ratings(severity)
            results.append({
                'filename': filename,
                'disease_prediction': predicted_class,
                'severity': severity,
                'solution': solution,
                'image_path': image_path,
                'infected_count': infected_count,
                'total_count': total_count,
                'sum_ratings': sum_ratings
            })
            disease_predictions.append(predicted_class)

    # Calculate overall PI and PDI
    if infected_count > 0:
        overall_pi = (infected_count / total_count) * 100
        overall_pdi = (sum_ratings / (infected_count * 9)) * 100
    else:
        overall_pi = 0
        overall_pdi = 0
    # Calculate lifespan
    lifespan = calculate_lifespan(overall_pi, overall_pdi)
    # Calculate the most common disease prediction
    most_common_disease = Counter(disease_predictions).most_common(1)[0][0]
    # Fetch the respective solution for the most common disease
    overall_solution = solutions.get(most_common_disease, "Solution not available")

    overall_results = {
        'overall_pi': round(overall_pi, 2),
        'overall_pdi': round(overall_pdi, 2),
        'overall_solution': overall_solution,
        'lifespan': lifespan
    }

    return render_template('result.html', results=results, overall_results=overall_results)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='::', port=5001)
