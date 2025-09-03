# AI PPT Editor - Intelligent Presentation Co-pilot

AI PPT Editor is a powerful cross-platform application that acts as an intelligent co-pilot for creating and editing presentations. It transforms raw text documents into well-structured presentations and provides a chat-based interface for making precise edits.

## Features

- **Draft-to-Deck**: Convert text documents (.docx, .txt) into structured presentations
- **AI-Powered Editing**: Use natural language commands to edit presentations
- **Three-Panel Interface**: Structure explorer, AI command console, and live visual preview
- **DeepSeek-Powered**: Optimized prompts and flows for DeepSeek
- **Context-Aware Editing**: Choose between local (single shape) or global (entire presentation) context

## Installation

1. Clone the repository:
```bash
git clone https://github.com/tristan-mcinnis/AI-PPT-Editor-Generator.git
cd AI-PPT-Editor-Generator
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Configuration

### LLM Provider Setup

AI PPT Editor uses DeepSeek as its LLM provider. Configure your API key in the `.env` file:

```
DEEPSEEK_API_KEY=your-api-key-here
DEEPSEEK_MODEL=deepseek-chat
```

### Slide Preview (Optional)

For slide preview functionality, install LibreOffice:

- **macOS**: `brew install --cask libreoffice`
- **Ubuntu/Debian**: `sudo apt-get install libreoffice`
- **Windows**: Download from [libreoffice.org](https://www.libreoffice.org/)

If LibreOffice is not installed, the app will show placeholder images instead.

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your browser to `http://localhost:5030`

3. **Upload a Presentation**:
   - Click "Upload Presentation" in the Structure Explorer panel
   - Select a `.pptx` file

4. **Edit with AI**:
   - Select a shape in the Structure Explorer
   - Choose context mode (Local or Global)
   - Type your command in the AI Command Console
   - Click "Execute" to apply changes

5. **Create from Document**:
   - Click "Ingest from Document" in the AI Command Console
   - Upload a `.docx` or `.txt` file
   - Review the proposed structure
   - Confirm to generate the presentation

## Example Commands

- "Make the title larger and bold"
- "Change the color to blue"
- "Shorten this bullet point"
- "Add a new bullet point about market growth"
- "Make this consistent with other slide titles" (use Global context)

## Testing

Run the test suite:
```bash
pytest
```

## Project Structure

```
AI-PPT-Editor-Generator/
├── app.py                  # Main Flask application
├── llm_provider.py         # LLM provider abstraction
├── presentation_engine.py  # PowerPoint manipulation logic
├── document_processor.py   # Document ingestion logic
├── templates/
│   └── index.html         # Frontend interface
├── static/
│   ├── css/
│   │   └── style.css      # Styling
│   └── js/
│       └── app.js         # Frontend JavaScript
├── test_layout_engine.py  # Test suite
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload/presentation` | Upload a .pptx file |
| POST | `/api/upload/document` | Upload a document for ingestion |
| GET | `/api/presentation/{id}/structure` | Get presentation structure |
| GET | `/api/presentation/{id}/slide/{n}/preview.png` | Get slide preview |
| POST | `/api/presentation/{id}/plan` | Execute presentation plan |
| POST | `/api/presentation/{id}/edit` | Edit a shape |

## Troubleshooting

### LibreOffice not found
- Ensure LibreOffice is installed and `soffice` is in your PATH
- The app will still work but show placeholder images

### LLM API errors
- Check your DeepSeek API key in the `.env` file
- Ensure you have sufficient API credits

### File upload issues
- Maximum file size is 16MB
- Only `.pptx`, `.docx`, and `.txt` files are supported

## License

MIT License - see LICENSE file for details
