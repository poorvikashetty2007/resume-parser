"""
resume_parser.py

Core logic for extracting structured information out of a resume file
(PDF, DOCX, or plain text). No external NLP models required — uses
targeted regex and section-heading heuristics, which keeps the project
light to install and easy to extend.
"""

import re
import os
import docx
import pdfplumber

# ---------------------------------------------------------------------
# A reasonably broad, editable skills vocabulary. Add/remove freely —
# this is a plain Python list, not a trained model, so changes take
# effect immediately with no retraining.
# ---------------------------------------------------------------------
SKILL_KEYWORDS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "sql", "nosql", "mysql", "postgresql", "mongodb", "redis",
    "html", "css", "react", "angular", "vue", "node.js", "next.js",
    "django", "flask", "fastapi", "spring", "express",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd",
    "git", "github", "gitlab", "jira",
    "machine learning", "deep learning", "nlp", "computer vision",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "excel", "power bi", "tableau", "data analysis", "data visualization",
    "agile", "scrum", "project management", "communication", "leadership",
    "rest api", "graphql", "microservices", "linux", "bash",
]

SECTION_HEADERS = {
    "education": ["education", "academic background", "academics"],
    "experience": ["experience", "work experience", "professional experience",
                   "employment history"],
    "skills": ["skills", "technical skills", "core competencies"],
    "projects": ["projects", "personal projects", "academic projects"],
    "certifications": ["certifications", "certificates", "licenses"],
}

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(
    r"(\+?\d{1,3}[\s\-.]?)?(\(?\d{2,4}\)?[\s\-.]?)?\d{3,4}[\s\-.]?\d{3,4}"
)
LINKEDIN_RE = re.compile(r"(https?://)?(www\.)?linkedin\.com/in/[A-Za-z0-9\-_/]+")
GITHUB_RE = re.compile(r"(https?://)?(www\.)?github\.com/[A-Za-z0-9\-_/]+")


def extract_text(file_path: str) -> str:
    """Return raw text from a .pdf, .docx, or .txt file."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        text = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        return "\n".join(text)

    if ext == ".docx":
        doc = docx.Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs]
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    paragraphs.append(cell.text)
        return "\n".join(paragraphs)

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    raise ValueError(f"Unsupported file type: {ext}")


def extract_email(text: str):
    match = EMAIL_RE.search(text)
    return match.group(0) if match else None


def extract_phone(text: str):
    for match in PHONE_RE.finditer(text):
        candidate = match.group(0)
        digits = re.sub(r"\D", "", candidate)
        if 7 <= len(digits) <= 13:
            return candidate.strip()
    return None


def extract_links(text: str):
    linkedin = LINKEDIN_RE.search(text)
    github = GITHUB_RE.search(text)
    return {
        "linkedin": linkedin.group(0) if linkedin else None,
        "github": github.group(0) if github else None,
    }


def extract_name(text: str):
    """
    Heuristic: the candidate's name is usually the first non-empty line
    that isn't an email/phone/URL and doesn't look like a section header.
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for line in lines[:6]:
        low = line.lower()
        if EMAIL_RE.search(line) or PHONE_RE.search(line):
            continue
        if any(h in low for headers in SECTION_HEADERS.values() for h in headers):
            continue
        if len(line.split()) <= 5 and len(line) < 60:
            return line
    return None


def extract_skills(text: str):
    found = []
    low = text.lower()
    for skill in SKILL_KEYWORDS:
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, low):
            found.append(skill)
    return sorted(set(found))


def _find_section_bounds(lines, header_variants):
    """Find the start/end line index of a section given its header keywords."""
    start = None
    for i, line in enumerate(lines):
        clean = line.strip().lower().strip(":")
        if clean in header_variants or any(
            clean == h or clean.startswith(h) for h in header_variants
        ):
            start = i
            break
    if start is None:
        return None, None

    all_headers = [h for headers in SECTION_HEADERS.values() for h in headers]
    end = len(lines)
    for j in range(start + 1, len(lines)):
        clean = lines[j].strip().lower().strip(":")
        if clean in all_headers and clean not in header_variants:
            end = j
            break
    return start, end


def extract_section(text: str, section_key: str):
    lines = text.splitlines()
    headers = SECTION_HEADERS[section_key]
    start, end = _find_section_bounds(lines, headers)
    if start is None:
        return None
    body = [l.strip() for l in lines[start + 1:end] if l.strip()]
    return "\n".join(body) if body else None


def parse_resume(file_path: str) -> dict:
    """Main entry point: returns a dict of structured resume fields."""
    text = extract_text(file_path)
    links = extract_links(text)

    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "linkedin": links["linkedin"],
        "github": links["github"],
        "skills": extract_skills(text),
        "education": extract_section(text, "education"),
        "experience": extract_section(text, "experience"),
        "projects": extract_section(text, "projects"),
        "certifications": extract_section(text, "certifications"),
        "raw_text_preview": text[:1000],
    }


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) != 2:
        print("Usage: python resume_parser.py <path-to-resume>")
        sys.exit(1)

    result = parse_resume(sys.argv[1])
    print(json.dumps(result, indent=2))
