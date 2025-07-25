# AI Document Management System

This project is an AI-powered document management system designed to streamline the processing, analysis, and retrieval of financial documents. It leverages a suite of powerful technologies to offer features like automated data extraction, intelligent tagging, semantic search, and fraud detection.

## How it Works: A Step-by-Step Guide

This system is built as a web service that you can interact with through API calls. Here’s a breakdown of the key processes:

### 1. Document Upload and Initial Processing

When you upload a document (e.g., an invoice, receipt, or financial statement), the system kicks off a multi-step process:

- **Optical Character Recognition (OCR)**: The system first extracts all the text from the document. This works even for scanned images or PDFs that aren't text-based.
- **Intelligent Tagging**: Using Natural Language Processing (NLP), the system identifies and extracts key pieces of information from the text, such as:
    - **Document Type**: It classifies the document (e.g., "Invoice," "Receipt").
    - **Key-Value Pairs**: It extracts specific data points like invoice numbers, dates, vendor names, and total amounts.
    - **Named Entities**: It recognizes and tags entities like people, organizations, and locations mentioned in the document.

### 2. Fraud Detection

For each uploaded document, a sophisticated fraud detection module runs a series of checks:

- **Duplicate Detection**: It verifies if an identical document has been uploaded before, preventing duplicate payments.
- **Data Integrity**: It cross-references figures within the document (e.g., ensuring that the subtotal and tax add up to the total amount).
- **High-Risk Keywords**: It scans the document for keywords and phrases that are commonly associated with fraudulent activities.

### 3. Semantic Search

The true power of this system lies in its search capabilities. Instead of just searching for keywords, it understands the *meaning* behind your queries.

- **Embeddings Generation**: Every document's text is converted into a numerical representation called an "embedding." These embeddings capture the semantic meaning of the text.
- **Semantic Search in Action**: When you type a search query (e.g., "all invoices from last month from 'Tech Solutions Inc.'"), the system converts your query into an embedding as well. It then compares your query's embedding with the embeddings of all the stored documents to find the most relevant matches.

## Getting Started: A Local Setup Tutorial

Here’s how you can get the project running on your local machine.

### Prerequisites

- Python 3.9 or higher
- `pip` for package management

### 1. Clone the Repository

```bash
git clone <repository-url>
cd findocs-ai-server
```

### 2. Install Dependencies

This project uses a number of Python libraries. You can install them all with a single command:

```bash
pip install -r requirements.txt
```

### 3. Set Up Google Cloud Credentials

This project uses Google Cloud services (like Vertex AI and Firestore). You'll need to set up authentication.

1.  **Create a Service Account**: In the Google Cloud Console, create a service account and download the JSON key file.
2.  **Set Environment Variable**: For the application to find your credentials, you need to set an environment variable that points to your service account key file.

    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service_account.json"
    ```

    Alternatively, you can place the `service_account.json` file in the root of the project directory.

### 4. Run the Application

Once the dependencies are installed and your credentials are set up, you can start the web server:

```bash
uvicorn main:app --reload
```

The `--reload` flag makes the server automatically restart when you make changes to the code.

### 5. Access the API

The API will be running at `http://127.0.0.1:8000`. You can access the interactive API documentation (provided by Swagger UI) at `http://127.0.0.1:8000/docs`.

From there, you can test the `/api/upload` and `/api/search` endpoints.

## Project Structure

Here's a brief overview of the project's directory structure:

```
/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── search.py       # Handles the search API endpoint
│   │   └── upload.py       # Handles the document upload API endpoint
│   └── services/
│       ├── __init__.py
│       ├── firestore_service.py # Interacts with Google Firestore
│       ├── ocr_service.py       # Handles OCR
│       ├── tagging_service.py   # Handles intelligent tagging
│       └── vertex_ai.py         # Interacts with Google Vertex AI for embeddings
├── main.py                 # Main application file (FastAPI setup)
├── requirements.txt        # Project dependencies
└── README.md               # This file
```
