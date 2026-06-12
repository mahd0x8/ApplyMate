import anthropic
from django.conf import settings


def get_client():
    return anthropic.Anthropic(api_key=settings.CLAUDE_API_KEY)


def _profile_context(profile):
    if not profile:
        return "No profile available."
    parts = [f"Name: {profile.full_name}", f"Location: {profile.location}"]
    if profile.professional_summary:
        parts.append(f"Summary: {profile.professional_summary}")
    if hasattr(profile, 'work_experiences'):
        for exp in profile.work_experiences.all()[:5]:
            end = "Present" if exp.is_current else str(exp.end_date or "")
            parts.append(f"Experience: {exp.title} at {exp.company} ({exp.start_date} - {end})\n{exp.description}")
    if hasattr(profile, 'educations'):
        for edu in profile.educations.all()[:3]:
            parts.append(f"Education: {edu.degree} in {edu.field_of_study} from {edu.institution}")
    if hasattr(profile, 'skills'):
        skill_names = ", ".join(s.name for s in profile.skills.all())
        parts.append(f"Skills: {skill_names}")
    if hasattr(profile, 'projects'):
        for proj in profile.projects.all()[:3]:
            parts.append(f"Project: {proj.name} - {proj.description[:200]}")
    if hasattr(profile, 'certifications'):
        for cert in profile.certifications.all()[:3]:
            parts.append(f"Certification: {cert.name} from {cert.issuer}")
    return "\n".join(parts)


def generate_cv(profile, job_application):
    client = get_client()
    profile_text = _profile_context(profile)
    prompt = f"""You are an expert ATS-optimized resume writer.

Candidate Profile:
{profile_text}

Job Description:
Company: {job_application.company}
Role: {job_application.role}
Location: {job_application.location}
Description:
{job_application.job_description}

Create a tailored, ATS-optimized CV/resume for this specific role. Include:
1. Professional Summary (3-4 sentences tailored to the role)
2. Key Skills (highlight skills matching the JD)
3. Work Experience (quantified achievements, relevant to the role)
4. Education
5. Projects (if relevant)
6. Certifications (if any)

Format it cleanly in plain text with clear section headers. Optimize for ATS keywords from the job description."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


def generate_cover_letter(profile, job_application, tone='formal'):
    client = get_client()
    profile_text = _profile_context(profile)
    tone_instruction = {
        'formal': 'Use a professional, formal tone.',
        'conversational': 'Use a friendly, conversational tone while remaining professional.',
        'enthusiastic': 'Use an enthusiastic, energetic tone that conveys genuine excitement for the role.',
    }.get(tone, 'Use a professional tone.')

    prompt = f"""You are an expert cover letter writer.

Candidate Profile:
{profile_text}

Job Details:
Company: {job_application.company}
Role: {job_application.role}
Hiring Manager: {job_application.hiring_manager or 'Hiring Manager'}
Job Description:
{job_application.job_description}

Write a compelling cover letter. {tone_instruction}

The letter should:
- Open with a strong hook
- Connect the candidate's experience directly to the role requirements
- Show genuine interest in the company
- Include a clear call to action
- Be 3-4 paragraphs
- Not repeat the resume verbatim

Format as a proper business letter."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


def analyze_job_description(job_description, profile=None):
    client = get_client()
    profile_text = _profile_context(profile) if profile else "No profile provided."

    prompt = f"""Analyze this job description and provide structured insights.

Job Description:
{job_description}

Candidate Profile (for match scoring):
{profile_text}

Provide a JSON response with this exact structure:
{{
  "key_skills": ["skill1", "skill2", ...],
  "requirements": ["req1", "req2", ...],
  "keywords": ["keyword1", "keyword2", ...],
  "match_score": 85,
  "missing_skills": ["skill1", "skill2", ...],
  "red_flags": ["flag1", "flag2", ...],
  "summary": "Brief 2-sentence summary of the role"
}}

match_score should be 0-100 based on how well the profile matches.
red_flags are unrealistic requirements, vague descriptions, or concerning patterns."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    import json, re
    text = message.content[0].text
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {"error": "Could not parse response", "raw": text}


def answer_form_question(question, profile, length_mode='medium', tone='balanced'):
    client = get_client()
    profile_text = _profile_context(profile)
    length_guide = {
        'short': '1-2 sentences (50-80 words)',
        'medium': '1 paragraph (100-150 words)',
        'detailed': '2-3 paragraphs (200-300 words)',
    }.get(length_mode, '1 paragraph')
    tone_guide = {
        'confident': 'assertive and self-assured',
        'humble': 'modest and collaborative',
        'balanced': 'professional and genuine',
    }.get(tone, 'professional and genuine')

    prompt = f"""You are helping a job applicant answer application form questions.
Answer should be {length_guide} and {tone_guide} in tone.

Candidate Profile:
{profile_text}

Application Question:
{question}

Write a humanized, authentic answer grounded in the candidate's real experience.
Do not use generic phrases. Be specific and concrete."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


def generate_interview_questions(job_application):
    client = get_client()
    prompt = f"""Generate likely interview questions for this role.

Company: {job_application.company}
Role: {job_application.role}
Job Description:
{job_application.job_description or 'No description provided.'}

Generate 10 interview questions grouped by category:
1. Behavioral (3 questions using STAR method)
2. Technical/Role-specific (4 questions)
3. Company/Culture fit (2 questions)
4. Situational (1 question)

For each behavioral question, also provide a STAR-method answer framework hint."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


def generate_follow_up_email(job_application, email_type='follow_up'):
    client = get_client()
    email_templates = {
        'follow_up': 'a post-application follow-up email (sent 1 week after applying)',
        'thank_you': 'a thank-you email after an interview',
        'negotiation': 'a salary negotiation email',
    }
    email_desc = email_templates.get(email_type, 'a professional email')

    prompt = f"""Write {email_desc}.

Company: {job_application.company}
Role: {job_application.role}
Hiring Manager: {job_application.hiring_manager or 'Hiring Manager'}

Keep it concise, professional, and personalized. Include a subject line."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


def chat_with_application(application, message_history, user_message, profile=None):
    """Contextual chat for a specific job application."""
    client = get_client()
    profile_text = _profile_context(profile) if profile else ""

    system_prompt = f"""You are ApplyMate AI, a helpful job application assistant.
You are helping the user with their application to {application.company} for the role of {application.role}.

Application context:
- Company: {application.company}
- Role: {application.role}
- Status: {application.get_status_display()}
- Location: {application.location}
- Job Description: {application.job_description[:1000] if application.job_description else 'Not provided'}

Candidate Profile:
{profile_text}

You can help with: refining their CV, improving cover letters, answering form questions,
interview prep, follow-up emails, and general job application advice.
Be concise, practical, and specific to this application."""

    messages = [{"role": msg.role, "content": msg.content} for msg in message_history]
    messages.append({"role": "user", "content": user_message})

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=system_prompt,
        messages=messages,
    )
    return response.content[0].text
