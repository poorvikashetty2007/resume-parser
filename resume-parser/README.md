# Resume Parser

A small Flask web app that extracts structured information from resumes
(PDF, DOCX, or TXT): name, email, phone, LinkedIn/GitHub links, skills,
education, experience, projects, and certifications.

No paid APIs or ML models required — extraction is done with regex and
section-heading detection, so it runs entirely offline.

## Project structure

```
resume-parser/
├── app.py               # Flask routes (upload form + parse endpoint)
├── resume_parser.py      # Core parsing logic (can also run standalone)
├── requirements.txt
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── uploads/              # Temporary storage; files are deleted after parsing
└── .gitignore
```

## Run it locally

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open **http://127.0.0.1:5000** in your browser and upload a resume.

You can also run the parser directly from the command line, without the
web UI:

```bash
python resume_parser.py path/to/resume.pdf
```

## Customizing what it detects

- **Skills list**: edit `SKILL_KEYWORDS` in `resume_parser.py` — it's a
  plain Python list, so add or remove terms freely.
- **Section headings**: edit `SECTION_HEADERS` in the same file if your
  resumes use different headings (e.g. "Work History" instead of
  "Experience").

## Deploying this to GitHub via VS Code

1. **Open the folder in VS Code**: `File → Open Folder…` and select this
   `resume-parser` folder.
2. **Initialize git** (skip if already a repo): open the built-in
   terminal (`` Ctrl+` ``) and run:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: resume parser"
   ```
3. **Create the GitHub repo**: click the **Source Control** icon in the
   left sidebar, then **Publish Branch** (or **Publish to GitHub**) —
   VS Code will prompt you to sign in to GitHub and create the repo
   for you, public or private, in one click.
   - Alternatively, create the repo manually on github.com first, then run:
     ```bash
     git remote add origin https://github.com/<your-username>/resume-parser.git
     git branch -M main
     git push -u origin main
     ```
4. **Done.** Your code is now on GitHub. Anyone cloning it can get
   running with the "Run it locally" steps above.

### Notes on hosting it live (optional)

This is a Flask app with file uploads, so it needs a real Python server —
it can't run as a static GitHub Pages site. If you want it live on the
web (not just in your GitHub repo), free options that work well with a
small Flask app like this include **Render**, **Railway**, or
**PythonAnywhere** — all support deploying straight from a GitHub repo.

## Privacy note

Uploaded files are saved briefly to the `uploads/` folder purely so the
parser can read them, then deleted immediately after parsing — nothing
is stored permanently.
