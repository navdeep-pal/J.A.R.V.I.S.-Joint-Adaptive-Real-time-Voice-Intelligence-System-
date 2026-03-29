Place your personal/project documents in this folder so J.A.R.V.I.S. can read and search them.

Supported file types:
- `.txt`
- `.md`
- `.json`
- `.csv`
- `.docx`
- `.pdf` (requires `pypdf` to be installed in the backend environment)

How it works:
- The backend scans this folder at session startup.
- The assistant gets local document tools:
  - `list_local_documents`
  - `search_local_documents`
- When you ask about a file, report, PDF, or notes, the assistant can search these files and answer from matched passages.

Recommended usage:
- Keep file names descriptive, such as `project_report.pdf` or `meeting_notes.docx`.
- Avoid adding extremely large or irrelevant files.
- If you update a file, start a new session so the latest contents are reloaded.
