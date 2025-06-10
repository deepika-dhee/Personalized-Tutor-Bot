import json
from flask import Flask, render_template, request, jsonify, session
import openai
import datetime
import os

app = Flask(__name__)
app.secret_key = "super-secret-key"  # Replace with a robust key in production.

# --------------------------
# Persistence Files & Helper Functions
# --------------------------
USERS_FILE = "users.json"
NOTES_FILE = "notes.json"

def load_json_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {}

def save_json_file(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)

# Load persistent user data and notes.
users = load_json_file(USERS_FILE)
notes_data = load_json_file(NOTES_FILE)

# Ensure the uploads folder exists.
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# --------------------------
# Configure OpenRouter API – update with your API key.
# --------------------------
openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = "Here place your api key from ex. deepseek rover v2"  # Replace with your valid API key.

def query_model(prompt_text):
    try:
        response = openai.ChatCompletion.create(
            model="deepseek/deepseek-prover-v2:free",
            messages=[{"role": "user", "content": prompt_text}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print("Error querying model:", e)
        return ""

def get_json_output(prompt):
    output_text = query_model(prompt)
    if output_text.startswith("```"):
        lines = output_text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        output_text = "\n".join(lines)
    print("Cleaned output:", output_text)
    try:
        return json.loads(output_text)
    except Exception as e:
        print("JSON parse error:", e)
        return {"questions": []}

def clean_html(text):
    if text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines)
    return text

def current_timestamp():
    return datetime.datetime.now().isoformat(timespec='seconds')

# --------------------------
# USER AUTHENTICATION
# --------------------------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    global users
    if username in users:
        return jsonify({"success": False, "message": "Username already exists."})
    users[username] = password
    save_json_file(USERS_FILE, users)
    # Initialize the profile; extra fields for graduates:
    session["profile"] = {"type": "", "level": "", "grade": "", "stream": "", "field": "", "other": ""}
    return jsonify({"success": True, "message": "Signup successful! Please log in."})

@app.route("/login", methods=["POST"])
def login_route():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    if users.get(username) == password:
        session["username"] = username
        session.setdefault("history", []).append(f"{current_timestamp()} - {username} logged in.")
        if "profile" not in session:
            session["profile"] = {"type": "", "level": "", "grade": "", "stream": "", "field": "", "other": ""}
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route("/logout", methods=["POST"])
def logout():
    session.setdefault("history", []).append(f"{current_timestamp()} - {session.get('username', 'Unknown')} logged out.")
    session.clear()
    return jsonify({"success": True})

# --------------------------
# LANGUAGE (English Only)
# --------------------------
@app.route("/set_language", methods=["POST"])
def set_language_route():
    data = request.get_json()
    language = data.get("language", "en").strip()
    session["language"] = language
    session.setdefault("history", []).append(f"{current_timestamp()} - Language set to {language}.")
    return jsonify({"success": True, "language": language})

# --------------------------
# PROFILE & PERSONALIZATION
# --------------------------
@app.route("/update_profile", methods=["POST"])
def update_profile_route():
    data = request.get_json()
    profile = {
        "type": data.get("type", ""),
        "level": data.get("level", ""),
        "grade": data.get("grade", ""),    # For school students.
        "stream": data.get("stream", ""),  # For college students.
        "field": data.get("field", ""),    # For professionals.
        "other": data.get("other", "")
    }
    session["profile"] = profile
    session.setdefault("history", []).append(f"{current_timestamp()} - Profile updated: {profile}")
    return jsonify({"success": True, "message": "Profile updated successfully!"})

@app.route("/get_profile", methods=["GET"])
def get_profile_route():
    profile = session.get("profile", {"type": "Not Set", "level": "Not Set", "grade": "Not Set", "stream": "Not Set", "field": "Not Set", "other": ""})
    # Build HTML showing the stored profile info.
    html = (
        f"<h3>Profile Details</h3>"
        f"<p><strong>Type:</strong> {profile['type']}</p>"
        f"<p><strong>Level:</strong> {profile['level']}</p>"
        f"<p><strong>Grade (if school):</strong> {profile['grade'] or 'N/A'}</p>"
        f"<p><strong>Stream (if college):</strong> {profile['stream'] or 'N/A'}</p>"
        f"<p><strong>Field (if professional):</strong> {profile['field'] or 'N/A'}</p>"
        f"<p><strong>Other:</strong> {profile.get('other', '') or 'N/A'}</p>"
    )
    return jsonify({"profile": html})

# --------------------------
# GOAL SELECTION & LEARNING PATH
# --------------------------
@app.route("/select_goal", methods=["POST"])
def select_goal_route():
    data = request.get_json()
    goal = data.get("goal", "").strip()
    if goal:
        session["goal"] = goal
        session.setdefault("history", []).append(f"{current_timestamp()} - Goal Selected: {goal}")
        return jsonify({"success": True, "message": f"Your goal '{goal}' has been selected."})
    return jsonify({"error": "No goal provided"}), 400

@app.route("/get_learning_path", methods=["GET"])
def get_learning_path_route():
    goal = session.get("goal", "General")
    prompt = (
        f"Provide an extremely detailed study plan for becoming a {goal} in India tailored for a user with this profile: {session.get('profile', {})}. "
        "Break down the plan step-by-step with clear recommendations and direct links (video tutorials, study materials). "
        "Output must be plain HTML (using headings, paragraphs, lists and links that open in a new window). "
        "First output the text 'Generating personalized path…' and then the complete plan."
    )
    learning_path = query_model(prompt)
    learning_path = clean_html(learning_path)
    session.setdefault("history", []).append(f"{current_timestamp()} - Personalized learning path generated.")
    return jsonify({"learning_path": learning_path})

# --------------------------
# CAPACITY TEST ENDPOINTS
# --------------------------
@app.route("/get_capacity_test", methods=["GET"])
def get_capacity_test_endpoint():
    prompt = (
        "Generate a JSON object with key 'questions' that is an array of 15 mixed-format IQ/GK questions tailored to the user's profile. "
        "If the user is a student: If level is 'school', include grade-appropriate IQ questions (including one about age or grade), "
        "if 'college', include advanced questions concerning their stream, and if 'graduated', include questions about their degree. "
        "For working professionals, include questions relating to their field; for Other, generate detailed free-form questions. "
        "Ensure that ~75% of questions are multiple choice with exactly 3 options and ~25% are fill-in-the-blanks. "
        "Each question must include a key 'answer' with the correct answer in lowercase. Output valid JSON."
    )
    result = get_json_output(prompt)
    session["capacity_test_answers"] = {
        f"q{idx+1}": q.get("answer", "").strip().lower() 
        for idx, q in enumerate(result.get("questions", []))
    }
    session.setdefault("history", []).append(f"{current_timestamp()} - Capacity Test questions fetched.")
    return jsonify(result)

@app.route("/submit_capacity_test", methods=["POST"])
def submit_capacity_test_route():
    responses = request.get_json()
    stored = session.get("capacity_test_answers", {})
    score, details = 0, []
    for key, correct in stored.items():
        user_ans = responses.get(key, "").strip().lower()
        is_correct = (user_ans == correct) and user_ans != ""
        result_str = "✅ Correct" if is_correct else "❌ Wrong"
        if is_correct: score += 1
        details.append({
            "question": f"Question {key[1:]}",
            "user_answer": user_ans if user_ans else "(not answered)",
            "correct_answer": correct if correct else "(not provided)",
            "result": result_str
        })
    percent = (score / len(stored)) * 100 if stored else 0
    category = "Fast Learner" if percent >= 70 else "Average Learner" if percent >= 40 else "Slow Learner"
    session["capacity_test_score"] = score
    session["learner_category"] = category
    session.setdefault("history", []).append(f"{current_timestamp()} - Capacity Test: {score}/{len(stored)} - {category}")
    return jsonify({"score": score, "category": category, "details": details})

# --------------------------
# FINAL EXAM ENDPOINTS
# --------------------------
@app.route("/get_final_exam", methods=["GET"])
def get_final_exam():
    goal = session.get("goal", "General")
    prompt = (
        f"Generate a JSON object with key 'questions' that is an array of 25 deep, conceptual final exam questions for a career in {goal}. "
        "Exactly 7 must be multiple choice with 3 options each; the remaining 18 should be fill-in-the-blanks. "
        "Each question must include a key 'answer' with the correct answer in lowercase. "
        "Output valid JSON including keys 'id', 'question', 'type', and (for MCQs) an 'options' array."
    )
    result = get_json_output(prompt)
    session["final_exam_answers"] = {
        f"q{idx+1}": q.get("answer", "").strip().lower() 
        for idx, q in enumerate(result.get("questions", []))
    }
    session.setdefault("history", []).append(f"{current_timestamp()} - Final Exam questions fetched.")
    return jsonify(result)

@app.route("/submit_final_exam", methods=["POST"])
def submit_final_exam():
    responses = request.get_json()
    correct_answers = session.get("final_exam_answers", {})
    score, details = 0, []
    for key, correct in correct_answers.items():
        user_ans = responses.get(key, "").strip().lower()
        is_correct = (user_ans == correct) and user_ans != ""
        result_str = "✅ Correct" if is_correct else "❌ Wrong"
        if is_correct: score += 1
        details.append({
            "question": f"Question {key[1:]}",
            "user_answer": user_ans if user_ans else "(not answered)",
            "correct_answer": correct if correct else "(not provided)",
            "result": result_str
        })
    total = len(correct_answers)
    prompt = (
        f"Act as an enthusiastic mentor and provide detailed, step-by-step feedback for a final exam in the field '{session.get('goal', 'General')}'. "
        f"The student scored {score} out of {total}. Include elaborate study recommendations, clear explanations, and direct links to video tutorials and study materials. "
        "Output as pure HTML with clear headings, paragraphs, lists, and clickable links (with target='_blank')."
    )
    feedback = query_model(prompt)
    feedback = clean_html(feedback)
    if not feedback:
        feedback = "Your final exam has been graded. Please review your weak areas and study diligently!"
    session.setdefault("history", []).append(f"{current_timestamp()} - Final Exam: {score}/{total}")
    return jsonify({"score": score, "total": total, "details": details, "feedback": feedback})

# --------------------------
# AI CHAT BOT ENDPOINT
# --------------------------
@app.route("/ask", methods=["POST"])
def ask_endpoint():
    data = request.get_json()
    message = data.get("message", "").strip()
    greetings = ["hi", "hey", "hello", "howdy"]
    if message.lower() in greetings:
        response = "Hey there! How can I help you today?"
    else:
        prompt = f"Respond as a friendly mentor with detailed answers to: {message}"
        response = query_model(prompt)
        if not response:
            response = "I'm sorry, I could not process your request. Please try again later! 🤖"
        response = response.replace("#", "<br>")
    session.setdefault("history", []).append(f"{current_timestamp()} - Chat: {message} | Bot: {response}")
    return jsonify({"reply": response})

# --------------------------
# HISTORY RETRIEVAL (Per-User)
# --------------------------
@app.route("/get_history", methods=["GET"])
def get_history_route():
    user_history = session.get("history", [])
    history_html = "<ul>"
    for item in user_history:
        history_html += f"<li>{item}</li>"
    history_html += "</ul>"
    return jsonify({"history": history_html})

# --------------------------
# LEADERBOARD (Per-User)
# --------------------------
@app.route("/get_leaderboard", methods=["GET"])
def get_leaderboard():
    user = session.get("username", "Anonymous")
    score = session.get("capacity_test_score", 0)
    html = f"<h3>Live Leaderboard</h3><p>User: {user}</p><p>Your Score: {score}</p>"
    return jsonify({"leaderboard": html})

# --------------------------
# DASHBOARD (Progress Tracking – Placeholder)
# --------------------------
@app.route("/get_dashboard", methods=["GET"])
def get_dashboard():
    progress = {
        "quizzesTaken": 5,
        "averageScore": 65,
        "lastQuiz": "Capacity Test - 70%"
    }
    html = (
        "<h3>Progress Dashboard</h3>"
        "<ul>"
        f"<li>Quizzes Taken: {progress['quizzesTaken']}</li>"
        f"<li>Average Score: {progress['averageScore']}%</li>"
        f"<li>Last Quiz: {progress['lastQuiz']}</li>"
        "</ul>"
    )
    return jsonify({"dashboard": html})

# --------------------------
# COMMUNITY Q&A (Placeholder)
# --------------------------
@app.route("/get_community", methods=["GET"])
def get_community():
    html = (
        "<h3>Community Q&amp;A</h3>"
        "<p>Welcome to the community forum! Ask questions and share your insights.</p>"
    )
    return jsonify({"community": html})

# --------------------------
# PERSONAL NOTES (File Uploads Supported)
# --------------------------
@app.route("/save_note", methods=["POST"])
def save_note():
    note_text = request.form.get("note", "").strip()
    file = request.files.get("file")
    filename = ""
    if file:
        filename = file.filename
        file_path = os.path.join("uploads", filename)
        file.save(file_path)
    if not note_text and not filename:
        return jsonify({"success": False, "message": "Empty note."})
    notes = session.get("notes", [])
    note_entry = f"{current_timestamp()} - {note_text}"
    if filename:
        note_entry += f" [File: {filename}]"
    notes.append(note_entry)
    session["notes"] = notes
    save_json_file(NOTES_FILE, notes)
    return jsonify({"success": True, "message": "Note saved!"})

@app.route("/get_notes", methods=["GET"])
def get_notes():
    notes = session.get("notes", [])
    html = "<h3>Your Notes</h3><ul>"
    for note in notes:
        html += f"<li>{note}</li>"
    html += "</ul>"
    return jsonify({"notes": html})

# --------------------------
# HOME ROUTE – Permanent Dashboard
# --------------------------
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
