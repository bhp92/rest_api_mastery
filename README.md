# 🚀 REST API Mastery — Zero to 6 Years Experience

> **A complete, hands-on curriculum** to master REST API development, automation, and design with Python.  
> 40 minutes/day × 8 weeks = Job-ready, interview-confident, production-grade skills.

---

## 📦 What's Inside

```
rest_api_mastery/
├── server/              ← Full dummy REST API server (Flask) — your practice playground
├── course/              ← 8-week curriculum (one folder per week)
│   ├── week-01-foundations/
│   ├── week-02-methods-status/
│   ├── week-03-auth-security/
│   ├── week-04-design-patterns/
│   ├── week-05-automation-testing/
│   ├── week-06-advanced-topics/
│   ├── week-07-performance-caching/
│   └── week-08-production-devops/
├── exercises/           ← Hands-on coding exercises per week (created as you go)
├── solutions/           ← Exercise solutions (peek only after trying!)
├── interview-questions/ ← 100+ interview Q&A by difficulty
├── scripts/             ← Setup, seed data, utility scripts
└── docs/                ← Architecture diagrams, cheat sheets
```

---

## ⚡ Quick Start (VM Setup)

### 1. Clone the repo
```bash
git clone https://github.com/bhp92/rest_api_mastery.git
cd rest_api_mastery
```

### 2. Run the automated setup
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 3. Deploy the server (systemd + gunicorn)
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

This installs the server as a systemd service — it starts automatically on boot and restarts itself if it crashes.

### 4. Verify it works
```bash
curl http://localhost:5000/health
# Expected: {"status": "ok", "message": "REST API Mastery Server is running!"}
```

### Server management commands
```bash
sudo systemctl status rest-api-mastery    # is it running?
sudo systemctl start  rest-api-mastery    # start it
sudo systemctl stop   rest-api-mastery    # stop it
sudo systemctl restart rest-api-mastery   # restart after code changes
sudo journalctl -u rest-api-mastery -f    # live logs
```

---

## 🗓️ 8-Week Study Plan (40 min/day)

| Week | Topic | Confidence Level After |
|------|-------|----------------------|
| 1 | HTTP Fundamentals & REST Principles | Explain REST to anyone |
| 2 | HTTP Methods, Status Codes, Headers | Handle any HTTP scenario |
| 3 | Authentication & Security | JWT, OAuth, API Keys |
| 4 | API Design Patterns & Best Practices | Design production APIs |
| 5 | Automation & Testing (pytest, requests) | Write full test suites |
| 6 | Advanced Topics (pagination, versioning, rate limiting) | Build scalable APIs |
| 7 | Performance, Caching, Async | Optimize real-world APIs |
| 8 | Production, DevOps, Monitoring | Deploy & own an API |

---

## 📅 Exact Daily Routine — 40 Minutes

### Before You Start (2 min)

```bash
# Verify the server is running
curl http://localhost:5000/health

# If it's not running:
sudo systemctl start rest-api-mastery
```

---

### The 40-Minute Block

#### Minutes 0–15 — Read the theory
```bash
# Open that day's section in the course README
# Example for Week 1:
cat ~/rest_api_mastery/course/week-01-foundations/README.md
```

Read **only that day's section** (Day 1, Day 2, etc.). Don't read ahead.

#### Minutes 15–35 — Write and run the exercise

Open a **fresh Claude chat** and paste the Daily Session Prompt (see below).
Claude will give you one `.py` file. Create it on the VM:

```bash
nano ~/rest_api_mastery/exercises/week1/day1_http.py
# Type out the code — do NOT copy-paste (see The One Rule)
# Save: Ctrl+O  |  Exit: Ctrl+X

python3 ~/rest_api_mastery/exercises/week1/day1_http.py
```

If something breaks, paste the error into the same chat and fix it together.

#### Minutes 35–40 — Reflect

Answer these 3 questions out loud or write them in a notes file:
1. What did I just do?
2. Why does it work this way?
3. Where would I use this in a real job?

---

### End of Each Week (Day 5)

In your daily session chat, tell Claude:
> "I finished Week 1. Give me the weekly challenge."

Claude will give you a single challenge file. Solve it yourself first, then share your solution for review.

---

### Before Any Interview

Open a fresh Claude chat and paste the Interview Prep Prompt (see below).

---

### ⚠️ The One Rule

**Do not copy-paste exercise code blindly. Type it out.**

The muscle memory of writing `requests.get()`, handling the response, checking the status code — that's what makes it stick in interviews. Copy-pasting teaches you nothing.

---

## 🤖 Claude Prompts

---

### 🟢 Daily Session Starter Prompt
> Use this at the beginning of EVERY study session. Open a fresh chat and paste this.

```
You are my REST API study coach for the rest_api_mastery course.
Course repo: https://github.com/bhp92/rest_api_mastery

Context about my setup:
- Practice server runs on my VM at http://localhost:5000 via gunicorn + systemd
- Server has these endpoints: /health, /docs, /api/v1/auth, /api/v1/users,
  /api/v1/products, /api/v1/orders, /api/v1/posts, /api/v1/files,
  /api/v1/webhooks, /api/v2/products
- Test credentials: admin/admin123 (admin role), alice/password123 (user role)
- All exercises go in: ~/rest_api_mastery/exercises/weekN/dayN_topic.py
- Python is run directly: python3 exercises/week1/day1_http.py

Today I am on: Week [X] Day [Y] — [topic name from README]

Please:
1. In 3 bullet points, summarise what today's concept is about (senior engineer level)
2. Give me one real-world analogy
3. Give me today's exercise as a single self-contained .py file
   - filename: dayN_topic.py
   - BASE_URL = "http://localhost:5000" at the top
   - Runnable with: python3 filename.py
   - Print clear output so I can see what each step does
   - Include comments explaining WHY each line works, not just what it does
4. After giving the file, ask me 2 questions to check I understood the concept
   before I run the code

If anything not found, repo or file or readme, stop and ask right away. Do not proceed without them
```

---

### 🟡 Exercise Help Prompt
> Use this in the same chat if you're stuck on the exercise.

```
I'm stuck on today's exercise.
Here is my current code: [paste your code]
Here is the error / unexpected output: [paste it]

Please:
1. Don't give me the answer directly
2. Tell me what I'm thinking correctly
3. Give me one hint for what I'm missing
4. Ask me what I think the next step is
```

---

### 🔵 Weekly Challenge Prompt
> Use this on Day 5 of each week, in the same session chat.

```
I have completed Week [X] of rest_api_mastery.
Topics covered this week: [paste the week's checklist from course/week-XX/README.md]

Give me the weekly challenge as a single .py file.
Requirements:
- Combines all concepts from this week into one realistic scenario
- Has clear TODO comments where I need to write code
- Has expected output comments so I know if it's working
- Filename: week[X]_challenge.py

I will solve it myself first and share my solution with you for review.
```

---

### 🔴 Interview Quiz Prompt
> Open a fresh chat and paste this before interview prep.

```
You are a tough technical interviewer. I am preparing for a Senior Python REST API
Developer role claiming 6 years of experience.

Course repo for context: https://github.com/bhp92/rest_api_mastery.git

Quiz me on Week [X] topics. Rules:
- Ask me ONE question at a time
- Wait for my answer before continuing
- After I answer, give me:
  1. Score out of 10
  2. What I got right
  3. What a senior engineer would add
  4. The ideal complete answer
  5. A follow-up question a tough interviewer would ask next

Start with a warm-up question and escalate difficulty.
Begin now.
```

---

### 🟣 Mock Interview Prompt
> Open a fresh chat and paste this for full mock interviews.

```
Conduct a 30-minute mock technical interview for a Senior Python REST API Developer role.
I claim 6 years of experience.

Course repo for context: https://github.com/bhp92/rest_api_mastery.git

Rules:
- Be tough but fair
- Cover: API design, HTTP methods, authentication, testing, performance, real-world scenarios
- Ask follow-up questions when my answer is shallow
- At the end, give me an overall score and 3 specific things to improve

Start with a warm-up and escalate difficulty. Begin now.
```

---

### ⚪ Debug Help Prompt
> Use this in your daily session chat when something isn't working.

```
I'm working with the rest_api_mastery practice server.
Server: http://localhost:5000 (Flask + gunicorn + systemd on Ubuntu VM)

I ran: [paste command or code]
Expected: [what you expected]
Got: [paste actual output or error]

Help me debug this step by step.
Explain WHY each fix works, not just what to change.
```

---

## 📊 Progress Tracker

```bash
# Completed checklist items
grep -r "- \[x\]" course/ | wc -l

# Remaining checklist items
grep -r "- \[ \]" course/ | wc -l

# List all exercise files created so far
find exercises/ -name "*.py" | sort
```

---

## 🎯 Interview Readiness Milestones

- ✅ **Week 2 complete** → Can handle junior REST API questions
- ✅ **Week 4 complete** → Can handle mid-level questions
- ✅ **Week 6 complete** → Can handle senior-level questions
- ✅ **Week 8 complete** → Can handle architect/lead-level questions

---

## 🛠️ Tech Stack

- **Python 3.12+**
- **Flask** — Practice server
- **Gunicorn** — Production WSGI server
- **systemd** — Service manager (auto-start, auto-restart)
- **SQLite** — Practice database (no setup needed)
- **pytest + requests** — Testing framework
- **httpx** — Async HTTP client practice
- **Pydantic** — Data validation
- **PyJWT** — Authentication practice

---

## 📝 License

MIT — Free to use, share, and contribute. If this helped you land a job, star the repo! ⭐