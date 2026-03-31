"""
resume_generator.py - The AI Resume Generation Engine
======================================================
This is where the magic happens. Once we've collected all the user's data,
we send it to OpenAI's API with a carefully crafted "system prompt" that
instructs the AI to format a professional, ATS-friendly resume.

KEY CONCEPTS:
- System Prompt: Instructions we give the AI about its role and output format
- User Prompt: The actual data (name, skills, etc.) we want the AI to use
- ATS-Friendly: Applicant Tracking Systems scan resumes for keywords; proper
  formatting ensures the resume passes automated screening

If no OpenAI API key is set, we fall back to a built-in template generator
so the app still works without any API key (great for development/demo).
"""

import os
import re


def generate_resume(data: dict) -> str:
    """
    Generate a professional resume from collected user data.

    Tries OpenAI first. Falls back to a structured template if no API key.

    Args:
        data: Dictionary with keys: name, contact, location, summary,
              education, skills, experience, projects, achievements, linkedin

    Returns:
        A formatted resume as a string
    """
    api_key = os.environ.get("OPENAI_API_KEY", "")

    if api_key and api_key.startswith("sk-"):
        try:
            return _generate_with_openai(data, api_key)
        except Exception as e:
            print(f"OpenAI error: {e}. Falling back to template.")
            return _generate_with_template(data)
    else:
        # No API key — use the built-in template (still looks great!)
        return _generate_with_template(data)


def _generate_with_openai(data: dict, api_key: str) -> str:
    """
    Use OpenAI's GPT model to generate the resume.

    PROMPT ENGINEERING EXPLAINED:
    --------------------------------
    A good AI resume prompt has three parts:
    1. ROLE: Tell the AI who it is ("You are an expert resume writer...")
    2. INSTRUCTIONS: Exactly what format and style to use
    3. DATA: The user's actual information to fill in

    ATS-FRIENDLY tips baked into the prompt:
    - Use standard section headings (EXPERIENCE, EDUCATION, SKILLS)
    - No tables or columns (ATS can't parse them)
    - Use bullet points with action verbs
    - Include keywords naturally
    """
    # We import openai here so the app doesn't crash if it's not installed
    try:
        from openai import OpenAI
    except ImportError:
        raise Exception("openai package not installed. Run: pip install openai")

    client = OpenAI(api_key=api_key)

    # --- System Prompt: Defines the AI's role and output rules ---
    system_prompt = """You are an expert resume writer with 15+ years of experience helping 
candidates land jobs at top companies. You specialize in writing ATS-friendly resumes 
that are clear, professional, and impactful.

RESUME FORMATTING RULES:
1. Use ALL CAPS for section headers (e.g., PROFESSIONAL SUMMARY, SKILLS, EDUCATION)
2. Use bullet points (•) for experience and project descriptions
3. Start every bullet with a strong action verb (Developed, Built, Led, Designed, etc.)
4. Keep it concise but impactful — quantify achievements where possible
5. No tables, no columns — plain text only (ATS requirement)
6. Section order: Header → Summary → Skills → Experience → Projects → Education → Achievements
7. Add a horizontal divider (═══) under the person's name
8. Format contact info on one line separated by | symbols
9. If experience is "Fresher" or "None", skip the experience section gracefully

OUTPUT: Return ONLY the resume text. No explanations, no markdown code blocks. 
Just clean, formatted text ready to copy-paste."""

    # --- User Prompt: The actual data to turn into a resume ---
    user_prompt = f"""Please create a professional, ATS-friendly resume using this information:

FULL NAME: {data.get('name', 'N/A')}
CONTACT: {data.get('contact', 'N/A')}
LOCATION: {data.get('location', 'N/A')}
PROFESSIONAL SUMMARY: {data.get('summary', 'N/A')}
EDUCATION: {data.get('education', 'N/A')}
SKILLS: {data.get('skills', 'N/A')}
WORK EXPERIENCE: {data.get('experience', 'N/A')}
PROJECTS: {data.get('projects', 'N/A')}
ACHIEVEMENTS & CERTIFICATIONS: {data.get('achievements', 'N/A')}
LINKS (LinkedIn/GitHub/Portfolio): {data.get('linkedin', 'N/A')}

Generate a complete, polished resume. Make it compelling and professional."""

    # --- API Call ---
    # model: gpt-3.5-turbo is fast and cheap; use gpt-4 for higher quality
    # temperature: 0.7 gives slightly creative but professional output
    # max_tokens: 1500 is plenty for a one-page resume
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=1500
    )

    return response.choices[0].message.content.strip()


def _generate_with_template(data: dict) -> str:
    """
    Built-in template resume generator — no API key needed!

    This produces a clean, professional resume by simply formatting
    the collected data into a well-structured template.

    WHY have this fallback?
    - Lets you demo the app without spending API credits
    - Works offline
    - Zero latency (instant generation)
    - Still produces a genuinely useful resume
    """
    name = data.get("name", "Your Name").upper()
    contact = data.get("contact", "")
    location = data.get("location", "")
    summary = data.get("summary", "")
    education = data.get("education", "")
    skills_raw = data.get("skills", "")
    experience = data.get("experience", "")
    projects = data.get("projects", "")
    achievements = data.get("achievements", "")
    linkedin = data.get("linkedin", "")

    # --- Format Skills into bullet groups ---
    skills_list = [s.strip() for s in skills_raw.split(",") if s.strip()]
    skills_formatted = " • ".join(skills_list)

    # --- Format Experience ---
    exp_section = ""
    if experience and experience.lower() not in ["none", "fresher", "n/a", "na"]:
        exp_lines = experience.strip().split("\n")
        exp_section = f"""
WORK EXPERIENCE
{"─" * 60}
"""
        for line in exp_lines:
            if line.strip():
                exp_section += f"  • {line.strip()}\n"

    # --- Format Projects ---
    project_lines = projects.strip().split("\n")
    projects_formatted = ""
    for line in project_lines:
        if line.strip():
            projects_formatted += f"  • {line.strip()}\n"

    # --- Format Achievements ---
    ach_section = ""
    if achievements and achievements.lower() not in ["none", "n/a", "na"]:
        ach_lines = achievements.strip().split("\n")
        ach_section = f"""
ACHIEVEMENTS & CERTIFICATIONS
{"─" * 60}
"""
        for line in ach_lines:
            if line.strip():
                ach_section += f"  • {line.strip()}\n"

    # --- Format Links ---
    links_section = ""
    if linkedin and linkedin.lower() not in ["none", "n/a"]:
        links_section = f"  {linkedin}"

    # --- Assemble the Full Resume ---
    resume = f"""
{"═" * 70}
{name:^70}
{"═" * 70}
  {contact}  |  {location}
{links_section}
{"─" * 70}

PROFESSIONAL SUMMARY
{"─" * 60}
  {summary}

TECHNICAL SKILLS
{"─" * 60}
  {skills_formatted}

{exp_section}
PROJECTS
{"─" * 60}
{projects_formatted}
EDUCATION
{"─" * 60}
  {education}
{ach_section}
{"═" * 70}
    """.strip()

    return resume
