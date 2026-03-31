"""
conversation.py - The Conversation Flow Manager
=================================================
This module controls the step-by-step question flow of the chatbot.
Think of it as a state machine: the chatbot is always at a specific "step",
and each step knows what question to ask and how to validate the answer.

WHY a separate file?
Keeping conversation logic separate from the Flask app (app.py) makes the
code cleaner, easier to test, and easier to extend later.
"""


# --- Conversation Steps ---
# Each step is a dictionary that defines:
#   "field"    : The key to store the answer under in our data dict
#   "question" : What the bot asks the user
#   "validate" : A lambda function that checks if the answer is acceptable
#   "error"    : What to say if validation fails

STEPS = [
    {
        "field": "name",
        "question": "👋 Welcome! I'm your AI Resume Builder.\n\nLet's build your professional resume step by step.\n\n**What's your full name?**",
        "validate": lambda v: len(v.strip()) >= 2,
        "error": "Please enter your full name (at least 2 characters)."
    },
    {
        "field": "contact",
        "question": "Great! 📧 What's your **email address and phone number**?\n\n*(e.g., john@email.com | +1-555-0123)*",
        "validate": lambda v: "@" in v or len(v) >= 7,
        "error": "Please provide at least an email address or phone number."
    },
    {
        "field": "location",
        "question": "📍 What's your **city and country**?\n\n*(e.g., New York, USA)*",
        "validate": lambda v: len(v.strip()) >= 3,
        "error": "Please enter a valid location."
    },
    {
        "field": "summary",
        "question": "✍️ Write a short **professional summary** about yourself (2-3 sentences).\n\n*This appears at the top of your resume and is your elevator pitch to employers.*",
        "validate": lambda v: len(v.strip()) >= 20,
        "error": "Please write at least a sentence or two about yourself."
    },
    {
        "field": "education",
        "question": "🎓 Tell me about your **education**.\n\nInclude: Degree, Institution, Year\n*(e.g., B.Tech Computer Science, MIT, 2020-2024)*",
        "validate": lambda v: len(v.strip()) >= 10,
        "error": "Please provide your education details."
    },
    {
        "field": "skills",
        "question": "💻 List your **technical and soft skills** (comma-separated).\n\n*(e.g., Python, React, SQL, Leadership, Problem Solving)*",
        "validate": lambda v: len(v.strip()) >= 3,
        "error": "Please list at least one skill."
    },
    {
        "field": "experience",
        "question": "💼 Describe your **work experience**.\n\nInclude: Job Title, Company, Duration, Key Responsibilities\n*(Type 'None' or 'Fresher' if you have no experience yet)*",
        "validate": lambda v: len(v.strip()) >= 3,
        "error": "Please provide your work experience (or type 'Fresher' if none)."
    },
    {
        "field": "projects",
        "question": "🚀 Describe your **projects**.\n\nInclude: Project Name, Tech Used, What it does\n*(e.g., Portfolio Website - HTML/CSS/JS - A responsive personal portfolio)*",
        "validate": lambda v: len(v.strip()) >= 5,
        "error": "Please describe at least one project."
    },
    {
        "field": "achievements",
        "question": "🏆 Any **achievements, certifications, or awards**?\n\n*(e.g., AWS Certified, Hackathon Winner 2023 — or type 'None')*",
        "validate": lambda v: len(v.strip()) >= 2,
        "error": "Please enter your achievements or type 'None'."
    },
    {
        "field": "linkedin",
        "question": "🔗 Your **LinkedIn / GitHub / Portfolio URL**?\n\n*(e.g., linkedin.com/in/yourname — or type 'None')*",
        "validate": lambda v: len(v.strip()) >= 2,
        "error": "Please enter a URL or type 'None'."
    }
]

# Total number of steps (used to know when we're done)
TOTAL_STEPS = len(STEPS)


class ConversationManager:
    """
    ConversationManager handles the chatbot's question-answer loop.

    How it works:
    - Step 0: Bot sends welcome + first question
    - Steps 1..N: Bot validates the previous answer, stores it, asks next question
    - After all steps: Bot signals that data collection is complete

    Args:
        current_step (int): Which step we're currently on
        data (dict): Data collected so far
    """

    def __init__(self, current_step: int, data: dict):
        self.step = current_step
        self.data = data.copy()  # Copy to avoid mutating the original

    def process(self, user_message: str) -> tuple:
        """
        Process a user message and return the bot's response.

        Returns a tuple of:
            (reply_text, next_step, updated_data, is_done)
        """

        # --- Step 0: First message — just greet and ask first question ---
        if self.step == 0:
            first_question = STEPS[0]["question"]
            return (first_question, 1, self.data, False)

        # --- Steps 1 to N: Validate previous answer, then ask next question ---
        # The step index tells us which question we JUST asked (step - 1)
        previous_step_index = self.step - 1

        if previous_step_index < TOTAL_STEPS:
            current_step_def = STEPS[previous_step_index]
            field = current_step_def["field"]

            # Validate the user's answer
            if not current_step_def["validate"](user_message):
                # Validation failed — re-ask the same question with an error
                error_msg = f"⚠️ {current_step_def['error']}\n\n{current_step_def['question']}"
                return (error_msg, self.step, self.data, False)

            # Validation passed — store the answer
            self.data[field] = user_message.strip()

            # Are we done collecting all data?
            if self.step >= TOTAL_STEPS:
                # All data collected! Signal completion.
                done_msg = (
                    f"✅ Perfect, **{self.data.get('name', 'there')}**! "
                    "I have everything I need.\n\n"
                    "⚙️ **Generating your professional resume...** This may take a few seconds."
                )
                return (done_msg, self.step + 1, self.data, True)

            # Ask the next question
            next_question = STEPS[self.step]["question"]
            progress = f"*({self.step}/{TOTAL_STEPS - 1} complete)*\n\n"
            return (progress + next_question, self.step + 1, self.data, False)

        # Fallback: shouldn't normally reach here
        return ("Something went wrong. Type anything to restart.", 0, {}, False)
