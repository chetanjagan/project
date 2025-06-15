from flask import Flask,request,render_template
from PyPDF2 import PdfReader
import docx

app=Flask(__name__)
def hash_shingle(shingle):
    p=31
    hash_value=31
    for char in shingle:
        hash_value=hash_value*p+ord(char)
    return hash_value
def get_shingle_hashes(text,shingle_size):
    shingle_hashes=set()
    for i in range(len(text)-shingle_size+1):
        shingle=text[i:i+shingle_size]
        hashed=hash_shingle(shingle)
        shingle_hashes.add(hashed)
    return shingle_hashes
def jaccard_similarity(set1,set2):
    if not set1 and not set2:
        return 0.0
    intersection=len(set1 & set2)
    union=len(set1 | set2)
    return intersection/union
# to read the pdf and other files
def extract_text(file_storage):
    filename = file_storage.filename.lower()
    if filename.endswith(".txt"):
        return file_storage.read().decode("utf-8")
    elif filename.endswith(".pdf"):
        reader=PdfReader(file_storage)
        text=""
        for page in reader.pages:
            page_text=page.extract_text()
            if page_text:
                text+=page_text
        return text
    elif filename.endswith(".docx"):
        doc=docx.Document(file_storage)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        raise ValueError("Unsupported file format")
@app.route("/", methods=["GET", "POST"])
def index():
    similarity = None
    error = None

    if request.method == "POST":
        file1 = request.files.get("file1")
        file2 = request.files.get("file2")
        shingle_size = int(request.form.get("shingle_size", 3))

        try:
            if not file1 or not file2:
                raise ValueError("Both files must be uploaded.")

            text1 = extract_text(file1)
            text2 = extract_text(file2)

            hashes1 = get_shingle_hashes(text1, shingle_size)
            hashes2 = get_shingle_hashes(text2, shingle_size)

            similarity = jaccard_similarity(hashes1, hashes2)

        except Exception as e:
            error = str(e)

    return render_template("index.html", similarity=similarity, error=error)
if __name__=="__main__":
    app.run(debug=True)