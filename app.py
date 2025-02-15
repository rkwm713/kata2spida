from flask import Flask, request, render_template, send_file
import json
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"

# Ensure the upload and processed folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Function to replace owner values in JSON data
def replace_owner_in_json(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "owner" and isinstance(value, dict):
                if value.get("id") == "Unset Com Owner" and value.get("industry") == "COMMUNICATION":
                    data[key]["id"] = "PNM"
                    data[key]["industry"] = "UTILITY"
            else:
                replace_owner_in_json(value)
    elif isinstance(data, list):
        for item in data:
            replace_owner_in_json(item)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename.endswith('.json'):
        input_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
        processed_path = os.path.join(PROCESSED_FOLDER, f"processed_{uploaded_file.filename}")
        
        # Save the uploaded file
        uploaded_file.save(input_path)

        # Load and process the JSON file
        with open(input_path, "r") as file:
            data = json.load(file)
        replace_owner_in_json(data)

        # Save the processed JSON
        with open(processed_path, "w") as file:
            json.dump(data, file, indent=4)
        
        return send_file(processed_path, as_attachment=True)
    else:
        return "Invalid file format. Please upload a .json file."

if __name__ == "__main__":
    app.run(debug=True)
