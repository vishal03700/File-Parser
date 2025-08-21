
# Django File Parser CRUD API with Progress Tracking

A Django REST API to upload, parse, and manage files (CSV, Excel, PDF) with asynchronous processing and real-time progress tracking.

---

## Table of Contents

1. [Project Overview]
2. [Prerequisites]
3. [Setup Instructions]
4. [Project Structure]
5. [API Documentation]

---

## Project Overview

* Upload files and track upload/processing progress in real-time
* Asynchronous parsing of CSV, Excel, and PDF files
* CRUD operations for uploaded files
* Large file support without blocking server
* Error handling and status management

### Supported File Types

* CSV (.csv)
* Excel (.xlsx, .xls)
* PDF (text extraction only)

---

## Prerequisites

* **Python 3.8+**
* **pip**
* **Postman** (for testing)
* **Git** (optional)

Verify installation:

```bash
python --version
pip --version
```

---

## Setup Instructions

### 1. Clone Project Directory

```bash
# Clone the project from GitHub
git clone https://github.com/vishal03700/File-Parser.git
cd File-Parser
```

### 2. Create & Activate Virtual Environment

```bash
# Create
python -m venv venv

# Activate
# macOS/Linux
source venv/bin/activate


### 3. Install Dependencies

```bash
pip install Django==4.2.7
pip install djangorestframework==3.14.0
pip install pandas==2.1.3
pip install PyPDF2==3.0.1
pip install pdfplumber==0.10.3
pip install openpyxl==3.1.2
pip install python-dotenv==1.0.0
pip install django-cors-headers==4.3.1
```

Or use:

```bash
pip install -r requirements.txt
```

### 4. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```


### 5. Start Development Server

```bash
python manage.py runserver
```

Access API base: `http://127.0.0.1:8000/api/`
Admin: `http://127.0.0.1:8000/admin/`

---

## Project Structure

```
django-file-parser/
├── venv/
├── file_parser_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── file_parser_app/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── file_parser.py
│   ├── async_processor.py
│   ├── progress_tracker.py
│   └── migrations/
├── requirements.txt
├── .env
├── manage.py
└── README.md
```

---

## API Documentation

### Base URL

```
http://127.0.0.1:8000/api/
```

### Endpoints

| Endpoint                     | Method | Description                       |
| ---------------------------- | ------ | --------------------------------- |
| `/files/upload/`             | POST   | Upload a file for parsing         |
| `/files/`                    | GET    | List all uploaded files           |
| `/files/{file_id}/`          | GET    | Get parsed file content or status |
| `/files/{file_id}/progress/` | GET    | Check upload/processing progress  |
| `/files/{file_id}/`          | DELETE | Delete file and parsed content    |

---

## Sample Requests & Responses

### 1. Upload File

**Curl Command**:

```bash
curl -X POST "http://127.0.0.1:8000/api/files/upload/" \
  -H "accept: application/json" \
  -F "file=@sample.csv"
```

**Response (201 Created)**:

```json
{
    "file_id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "sample.csv",
    "status": "uploading",
    "message": "File uploaded successfully and processing started"
}
```

---

### 2. Get Upload Progress

**Request**:

```
GET /api/files/{file_id}/progress/
```

**Response**:

```json
{
    "file_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "processing",
    "progress": 50
}
```

---

### 3. Get File Content

**Request**:

```
GET /api/files/{file_id}/
```

**Response (Ready)**:

```json
{
    "file_id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "sample.csv",
    "status": "ready",
    "parsed_content": {
        "content": {
            "headers": ["Name", "Age", "City"],
            "rows": [
                {"Name": "John", "Age": 30, "City": "New York"},
                {"Name": "Jane", "Age": 25, "City": "Los Angeles"}
            ],
            "total_rows": 2,
            "columns": 3
        },
        "content_type": "csv",
        "row_count": 2,
        "created_at": "2024-12-20T10:00:00Z"
    }
}
```

**Response (Processing)**:

```json
{
    "message": "File upload or processing in progress. Please try again later.",
    "status": "processing",
    "progress": 50
}
```

---

### 4. List Files

```
GET /api/files/
```

**Response**:

```json
{
    "files": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "filename": "sample.csv",
            "original_filename": "sample.csv",
            "status": "ready",
            "created_at": "2024-12-20T10:00:00Z",
            "file_size": 1024
        }
    ],
    "total_count": 1
}
```

---

### 5. Delete File

```
DELETE /api/files/{file_id}/
```

**Response**:

```json
{
    "message": "File \"sample.csv\" deleted successfully"
}
```

---

