# ApplyMate

> AI-powered job application assistant — craft tailored resumes, generate cover letters, and track your entire job search from one dashboard.

Built with Django + HTMX + Claude API. No JavaScript build step required.

---

## Features

### Application Tracking
- **Kanban board** — drag-and-drop cards across Wishlist → Applied → Interview → Offer → Rejected
- **List view** — sortable, filterable table of all applications
- Per-application detail page storing company, role, job description, salary, location, work mode, notes, deadline, and follow-up date

### AI Document Generation (Claude-powered)
- **CV / Resume** — ATS-optimized, tailored to the specific job description
- **Cover letter** — three tone modes: Formal, Conversational, Enthusiastic
- **Export** — download any generated document as PDF, DOCX, or plain TXT
- **Version history** — every generated document is saved per application

### Per-Job Chat
- Isolated chat thread per application with full persistent message history
- Ask Claude to refine output, explain decisions, or generate new variations
- Real-time HTMX streaming with auto-scroll

### AI Tools
| Tool | What it does |
|---|---|
| **Form Assistant** | Paste any application question → get a profile-grounded answer with length and tone controls |
| **JD Analyzer** | Extract key skills, requirements, match score, and red flags from any job description |
| **Interview Prep** | Auto-generate likely interview questions; STAR-method answer guidance |
| **Follow-up Email** | Post-application, post-interview, and salary negotiation email templates |

### Profile / CV Builder
Structured master profile with sections for:
- Personal info and job preferences (titles, industries, salary, work mode)
- Work experience
- Education
- Skills
- Projects
- Certifications

All profile data feeds every AI prompt automatically.

### UI
- Dark / light theme toggle (persists across sessions)
- Collapsible sidebar (state persists)
- Modal-driven forms throughout — no full-page reloads
- Toast notifications for all actions
- Responsive two-column layouts

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 6.0 |
| Frontend | HTMX 2.0 + vanilla JS (no build step) |
| AI | Anthropic Claude (`claude-sonnet-4-6`) |
| Auth | django-allauth (email-based, no username) |
| PDF export | WeasyPrint |
| DOCX export | python-docx |
| Database | SQLite (dev) — PostgreSQL-ready |
| Fonts | Hanken Grotesk + JetBrains Mono (Google Fonts) |

---

## Project Structure

```
ApplyMate/
├── applymate/              # Django project — settings, URLs, WSGI
├── core/                   # Landing page, dashboard, templatetags
├── applications/           # JobApplication, GeneratedDocument, ChatMessage
├── profiles/               # UserProfile, WorkExperience, Education, Skill, Project, Certification
├── ai_tools/               # Claude API client, Form Assistant, JD Analyzer, Interview Prep, Email Generator
├── templates/
│   ├── base.html           # App shell — sidebar, topbar, toast container
│   ├── components/         # HTMX partial templates (kanban card, chat, document preview, etc.)
│   ├── core/               # landing.html, dashboard.html
│   ├── applications/       # list.html, detail.html
│   ├── profiles/           # profile.html
│   ├── ai_tools/           # home.html
│   └── allauth/            # Auth form overrides (field, button, alert, form elements)
├── static/
│   ├── css/main.css        # Full design system with CSS variables (dark/light themes)
│   └── js/main.js          # Theme toggle, sidebar, modals, drag-drop kanban, HTMX config
├── secrets.json            # API keys — never committed (in .gitignore)
└── requirements.txt
```

---

## Setup

### Prerequisites
- Python 3.12
- A Claude API key from [console.anthropic.com](https://console.anthropic.com)

### 1. Clone and create the virtual environment

```bash
git clone <repo-url>
cd ApplyMate
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Add your API key

Create `secrets.json` in the project root (next to `manage.py`):

```json
{
  "claude_API_key": "sk-ant-api03-..."
}
```

This file is in `.gitignore` and must never be committed.

### 3. Run migrations and create a superuser

```bash
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser
```

### 4. Start the development server

```bash
.venv/bin/python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) — you'll land on the sign-in page.

---

## URL Map

| URL | Page |
|---|---|
| `/` | Landing / redirect to dashboard if authenticated |
| `/accounts/signup/` | Sign up |
| `/accounts/login/` | Sign in |
| `/dashboard/` | Kanban board + stats |
| `/applications/` | Application list view |
| `/applications/<id>/` | Application detail + Claude chat |
| `/profile/` | Master profile / CV builder |
| `/ai/` | AI tools hub |
| `/ai/form-assistant/` | Form question assistant |
| `/ai/analyze-jd/` | Job description analyzer |
| `/ai/interview-prep/` | Interview question generator |
| `/ai/follow-up-email/` | Follow-up email generator |
| `/admin/` | Django admin |

---

## Configuration

All settings live in `applymate/settings.py`. The key ones:

```python
CLAUDE_API_KEY          # loaded from secrets.json
ACCOUNT_LOGIN_METHODS   # {'email'} — no username required
ACCOUNT_EMAIL_VERIFICATION = 'none'   # no email confirmation in dev
LOGIN_REDIRECT_URL = '/'
DEBUG = True            # set False and configure ALLOWED_HOSTS for production
```

For production, also set:
- A strong `SECRET_KEY`
- `DATABASES` pointing to PostgreSQL
- `STATIC_ROOT` + run `collectstatic`
- `ALLOWED_HOSTS`

---

## How AI Generation Works

All AI calls go through `ai_tools/claude_client.py`. Each function:

1. Builds a structured prompt that includes the user's full profile (work experience, education, skills, projects, certifications)
2. Appends the job-specific context (company, role, job description)
3. Calls `claude-sonnet-4-6` via the `anthropic` SDK
4. Returns the response text, which is saved to the database and rendered via HTMX

The chat feature (`chat_with_application`) maintains full conversation history by loading all `ChatMessage` rows for the application and passing them as the `messages` array.

---

## Development Notes

- **HTMX targets** — partial responses use `hx-target` / `hx-swap` to update fragments without full-page reloads. CSRF tokens are injected globally in `main.js` via `htmx:configRequest`.
- **Kanban drag-and-drop** — uses native HTML5 drag events (`ondragstart`, `ondrop`). Dropping a card fires a POST to `/applications/<id>/move/` which updates `status` in the database.
- **Theme system** — CSS variables defined on `:root` and `[data-theme="light"]`. JS toggles the `data-theme` attribute on `<html>` and persists the choice to `localStorage`.
- **Allauth forms** — auth pages use custom element overrides in `templates/allauth/elements/` to apply the app's CSS classes to allauth-rendered inputs.

---

## Roadmap

- [ ] Browser extension for auto-filling job application forms
- [ ] LinkedIn import
- [ ] Analytics dashboard (funnel visualization, response rate trends)
- [ ] CSV / Excel export of all applications
- [ ] Follow-up reminders (email / in-app)
- [ ] Weekly digest email
- [ ] Mobile PWA
- [ ] Multi-profile support ("Software Engineer" vs "Product Manager" variants)

---

## License

MIT
