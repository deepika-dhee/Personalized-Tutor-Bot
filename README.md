---
---
# Personalized Tutor Bot

**Personalized Tutor Bot** is an AI-powered interactive learning platform that helps users assess their learning capacity, create personalized career goals, and receive detailed performance feedback through adaptive quizzes and intelligent study plans.

**Key Modules include:**

- **Learning Capacity Analysis**  
- **Goal Selection & Recommendation**  
- **Final Assessment & Performance Feedback**  
- **Interactive Chat Bot**  
- **Personalized Notes with File Uploads**

---

## Features

- **User Authentication:**  
  Users can **sign up** and **log in** with a modern, responsive interface. Once logged in, a profile button (showing only an animated avatar with an overlaid “Profile” label) is visible at the top right.
  
- **Profile Management:**  
  After logging in, users update their profile by selecting their type:
  - **Student:** Choose between School, College, or Graduated. If "School" is selected, an input field for the grade appears; if "College" is selected, a dropdown of streams appears; if "Graduated" is selected, a free-text input asks “What is your degree in?”  
  - **Working Professional:** A text input is available to specify your field of work.  
  - **Other:** A simple free-text field is provided.
  
- **Learning Capacity Test:**  
  The system generates an adaptive quiz based on your profile. You’ll see an animated “Your personalized quizzes are generating…” message before a full-height, scrollable quiz loads. When submitted, a large, centered animated pie chart (using Chart.js) and a detailed results table are shown.
  
- **Goal Selection & Learning Path:**  
  Enter your career goal, and the system will show a “Generating personalized path…” message before displaying a detailed study plan with resource links and video tutorials.
  
- **Final Exam & Feedback:**  
  Take a final exam that presents tailored questions in a scrollable container with a running elapsed timer (starting at 00:00:00). Detailed feedback and study recommendations are then provided.
  
- **Chat Bot:**  
  The interactive chat bot uses a wider, auto-expanding text area with square send and microphone buttons (with larger icons) for efficient communication.
  
- **Progress Tracking:**  
  A progress bar is fixed at the left center of the Dashboard to give you a visual indicator of overall progress.

- **Responsive Design & Animations:**  
  The website features subtle animations, moving images, and a standard (normal) font size (around 16–18px) to ensure a modern look similar to most websites.

---

## Installation

1. **Clone the Repository**

   Open your terminal and run:
   ```bash
   git clone https://github.com/YourUsername/PersonalizedTutorBot.git
   cd PersonalizedTutorBot
   ```

2. **Create a Virtual Environment**

   For example, run:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   Install the required packages with:
   ```bash
   pip install -r requirements.txt
   ```
   If you don’t have a `requirements.txt`, install these manually:
   - Flask (see [Flask Documentation](https://flask.palletsprojects.com/))
   - openai (see [OpenAI API Documentation](https://platform.openai.com/docs/))

4. **Project Structure**

   Ensure your project resembles:
   ```
   PersonalizedTutorBot/
   ├── app.py
   ├── users.json          # Initialized with {}
   ├── notes.json          # Initialized with {}
   ├── uploads/            # Folder for file uploads
   ├── templates/
   │     └── index.html
   └── static/
         ├── styles.css
         ├── home_icon.png    (for the home icon)
         ├── avatar.png       (for the profile avatar)
         ├── robot.gif        (for the loading screen)
         └── tutor_bot.png    (for the floating bot image)
   ```

5. **API Key Configuration**

   In **app.py**, replace the placeholder:
   ```python
   openai.api_key = "use your personla api key(such as from deepseek v2 rover)"
   ```
   with your valid API key.

6. **Run the Application**

   Execute:
   ```bash
   python app.py
   ```
   Then open [http://localhost:5000](http://localhost:5000) in your browser.

---

## Usage

- **Sign Up / Log In:**  
  Use the provided forms to create a new account or sign in. After logging in, you gain access to all features.

- **Profile Management:**  
  Update your profile by choosing your type. For students, specify your school, college, or degree if graduated; professionals and others can fill in their details.

- **Learning Capacity Test:**  
  Take the adaptive quiz to assess your skill level. Detailed results appear as an animated pie chart and a result table.

- **Goal Selection & Final Exam:**  
  Enter your career goal to generate a personalized study plan before taking the final exam. The final exam displays an elapsed timer and provides detailed feedback upon submission.

- **Chat Bot & Notes:**  
  Chat with the bot using the interactive messaging area with square send/mic buttons. Save personal notes and upload files as needed.

- **Progress Tracking:**  
  Monitor your progress with the left-center progress bar on the Dashboard.

---

## Contributing

Contributions are welcome! Please fork the repository, make your updates or bug fixes, and submit pull requests. For more information, see our [CONTRIBUTING.md](https://github.com/YourUsername/PersonalizedTutorBot/blob/main/CONTRIBUTING.md).

---

## Resources & Acknowledgements

- **Flask Documentation:** https://flask.palletsprojects.com/  
- **OpenAI API Documentation:** https://platform.openai.com/docs/  
- **Chart.js:** https://www.chartjs.org/  
- **Tippy.js:** https://atomiks.github.io/tippyjs/  

Special thanks to the open source community for their support and inspiration.

---
---
