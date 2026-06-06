from flask import Flask, render_template, request
import sqlite3
import PyPDF2

app = Flask(__name__)

def create_table():

    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS candidates (

       id INTEGER PRIMARY KEY AUTOINCREMENT,

       candidate_name TEXT,

       resume TEXT,

       job_description TEXT,

       score REAL

   )
   ''')

    conn.commit()

    conn.close()


create_table()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    
    candidate_name = request.form.get('candidate_name', '')
    resume_file = request.files['resume_file']
    pdf_path = "uploads/" + resume_file.filename

    resume_file.save(pdf_path)

    resume = ""

    pdf_reader = PyPDF2.PdfReader(pdf_path)

    for page in pdf_reader.pages:

       text = page.extract_text()

       if text:
          resume += text
          
    job = request.form['job']

    resume_skills = resume.lower().replace(",", " ").split()
    job_skills = job.lower().replace(",", " ").split()

    matched_skills = []
    missing_skills = []

    for skill in job_skills:

        if skill in resume_skills:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    score = (len(matched_skills) / len(job_skills)) * 100

    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    cursor.execute(
       '''
       INSERT INTO candidates
       (candidate_name, resume, job_description, score)

       VALUES (?, ?, ?, ?)
       ''',
       (candidate_name, resume, job, score)
    )

    conn.commit()

    conn.close()

    return render_template(
       'result.html',
       candidate_name=candidate_name,
       score=round(score, 2),
       matched_skills=matched_skills,
       missing_skills=missing_skills
    )

@app.route('/history')
def history():

    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM candidates")

    records = cursor.fetchall()

    conn.close()

    return render_template(
        'history.html',
        records=records
    )

if __name__ == '__main__':
    app.run(debug=True)
