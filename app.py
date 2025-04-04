from flask import Flask, render_template, request, send_file
import os
import pandas as pd
import re

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
BASE_URL = "https://assets.central.co.th/{}?$JPG$"
pattern_remove_cds = r"^CDS"  # Pattern to remove 'CDS' from filenames

# Create upload folder if not exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Home route ("/") to render index.html
@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])  # Add route for /index
def upload_file():
    if request.method == "POST":
        excel_file = request.files["excel_file"]
        files = request.files.getlist("files")

        if not excel_file or not files:
            return "Please upload both an Excel file and images."

        # Save Excel file
        excel_path = os.path.join(UPLOAD_FOLDER, "rename_reference.xlsx")
        excel_file.save(excel_path)

        # Read Excel file
        df = pd.read_excel(excel_path)
        old_names = df.iloc[:, 0].tolist()  # First column (old names)
        new_names = df.iloc[:, 1].tolist()  # Second column (new names)

        rename_map = dict(zip(old_names, new_names))  # Create mapping

        image_urls = []
        for file in files:
            filename = file.filename

            if filename in rename_map:  # Check if filename exists in reference
                new_filename = rename_map[filename]
                new_filename = re.sub(pattern_remove_cds, "", new_filename)  # Remove 'CDS'
                file_name_without_ext, _ = os.path.splitext(new_filename)

                new_file_path = os.path.join(UPLOAD_FOLDER, new_filename)
                file.save(new_file_path)  # Save with new name

                # Generate image URL
                image_url = BASE_URL.format(new_filename)
                image_urls.append([file_name_without_ext, image_url])
            else:
                file.save(os.path.join(UPLOAD_FOLDER, filename))  # Save unchanged
                image_urls.append([filename, "No new name found"])

        # Save output Excel file
        output_file = os.path.join(UPLOAD_FOLDER, "output_urls_Rename_DAM.xlsx")
        df_output = pd.DataFrame(image_urls, columns=["Filename", "Image URL"])
        df_output.to_excel(output_file, index=False)

        return send_file(output_file, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
