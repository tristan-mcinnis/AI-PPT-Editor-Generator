Of course. This is excellent feedback. Integrating these ideas will result in a much more robust, flexible, and powerful product.

Here is the fully revised Product Requirements Document, incorporating your feedback and using the provided image as a core example for our most innovative feature.

---

# PRD: SlideSpark AI - The Intelligent Presentation Co-pilot

**Version:** 2.0  
**Status:** Proposed  
**Author:** Raycast AI

## 1. Vision & Opportunity

The creation of professional presentations is a high-value, time-intensive task. It involves two distinct phases: **structuring** raw information into a coherent narrative, and **formatting** that narrative into a visually appealing deck. Current tools are manual, while existing AI solutions often lack the precision for granular edits or the intelligence to structure content from scratch.

**SlideSpark AI** is a novel, cross-platform application that acts as an intelligent co-pilot for the entire presentation lifecycle. It transforms raw text documents into well-structured presentations and provides a powerful, chat-based interface for making precise edits. By combining a human-in-the-loop design with a flexible, multi-provider LLM backend, SlideSpark dramatically accelerates workflow and enhances creativity.

## 2. Goals & Objectives

*   **From Draft to Deck:** Provide a "one-click" workflow to ingest raw text documents (e.g., `.docx`, `.txt`) and generate a structured, professional presentation.
*   **Empower Conversational Editing:** Enable users to perform complex, targeted edits on presentation elements using natural language, with both local and global context awareness.
*   **Deliver an Intuitive IDE for Slides:** Offer a visual, three-panel interface that provides a structural overview, a command console, and an immediate visual preview, ensuring user confidence and control.
*   **Build a Modular & Future-Proof Core:** Utilize an abstracted architecture that is cross-platform by design and allows for easy integration of various LLM providers (Cloud APIs or local models).

## 3. User Personas & Stories

*   **Persona 1: Raj, the Market Analyst**
    *   **Story:** "I have a 4-page Word document filled with research notes and data points for my 'China Snow Market' report. I need to transform this into a 10-slide professional presentation, with each key finding on its own slide and data visualized in tables. I want the AI to propose a structure and generate the initial deck for me to refine."

*   **Persona 2: Dana, the Marketing Manager**
    *   **Story:** "Our primary brand color just changed. I need to update all 30 slides in our quarterly report. I want to tell the app, 'Using the entire presentation as context, change every instance of our old blue (#007bff) to the new blue (#0056b3) in shape fills and text.'"

*   **Persona 3: Alex, the Consultant**
    *   **Story:** "I've selected a single chart on slide 15. The title is too long. I want to tell the AI, 'Using only the context of this shape, shorten the title to be more concise,' without it affecting any other part of the presentation."

## 4. Core Features: The Three-Panel Interface

SlideSpark AI's workflow is centered around an intuitive, three-panel Integrated Development Environment (IDE) for presentations.

### 4.1. Panel 1: The Structure Explorer

A hierarchical tree view of the presentation, providing a clear map of the document's contents.

*   **Functionality:**
    *   Users upload a `.pptx` file to begin an editing session.
    *   The backend uses `python-pptx` to parse the file into a JSON structure, which is rendered as an interactive tree.
    *   Users can expand/collapse slides and shapes.
    *   Clicking an element selects it as the **local context** for the AI Command Console.

### 4.2. Panel 2: The AI Command Console

The intelligent, context-aware chat interface for all editing and generation tasks.

*   **Functionality:**
    *   **Context Mode Toggle:** A crucial UI switch allows the user to select the context for their command:
        *   **Local Context:** (Default) The AI's context is limited to the XML of the shape selected in Panel 1. Ideal for precise, isolated edits.
        *   **Global Context:** The AI's context includes the selected shape's XML *plus* a structured summary of the entire presentation's text content. Ideal for consistency-based edits (e.g., "make this title match the style of the others").
    *   **AI-Powered Editing:** Users type commands to edit the selected element. The backend manages the LLM call and applies the returned XML.
    *   **Content Ingestion:** An "Ingest from Document" button allows users to upload a `.docx` or `.txt` file, kicking off the "Draft-to-Deck" workflow.

### 4.3. Panel 3: The Live Visual Preview

A high-fidelity, non-interactive "hot reload" preview of the current slide.

*   **Functionality:**
    *   After every successful edit, the backend saves the modified presentation to a temporary file.
    *   A conversion engine (Headless LibreOffice) renders the edited slide as a PNG image.
    *   The frontend is notified to reload the image, providing immediate visual feedback. This ensures the user sees the result of their command without needing to open PowerPoint.

## 5. Feature Deep Dive: Content Ingestion ("Draft-to-Deck")

This is SlideSpark's flagship feature, addressing the "blank page" problem and turning raw notes into structured presentations.

**User Workflow:**
1.  User clicks "Ingest from Document" in Panel 2 and selects the `Snow report updates 07.30.25.docx` file.
2.  The backend extracts the raw text from the document.
3.  The text is sent to the LLM with a specialized prompt to analyze the content and propose a slide structure.

    **Example "Planning" Prompt:**
    ```
    You are a presentation structuring expert. Analyze the following text from a document and propose a slide-by-slide plan in JSON format. Identify titles, bullet points, and data.

    DOCUMENT TEXT:
    "2. Snow consumers in China
    Still an entry level market:~75% of participants were 'experience-focused'...
    滑雪主力人群为25-44岁 (占比约80%)...
    3. Nuances for China market: snow is highly social...
    Leverage Findings from KOL..."

    RESPONSE (should be):
    [
      { "slide": 1, "title": "Snow Consumers in China", "content": ["~75% of participants are 'experience-focused'...", "Rental is still mainstream..."] },
      { "slide": 2, "title": "Key Demographics", "content_type": "table", "data": [["Age Group", "Percentage"], ["25-44", "80%"], ["25-34 (core)", "50%"]] },
      { "slide": 3, "title": "Social Commerce & Market Nuances", "content": ["Platforms like Xiaohongshu and Douyin are key.", "Style rivals functionality in importance.", "Leverage findings from KOLs."] }
    ]
    ```
4.  The AI's proposed plan is shown to the user in Panel 2 for confirmation or editing.
5.  Once confirmed, the backend executes this plan, using `python-pptx` to generate a new presentation from scratch. Each slide and its content are created programmatically.
6.  The newly generated presentation is loaded into the application, with the Structure Explorer (Panel 1) and Visual Preview (Panel 3) populating automatically, ready for further refinement.

## 6. Technical Architecture

### 6.1. Frontend
*   **Framework:** **Flask with Jinja2 Templating.** This provides a simple, highly functional, server-rendered frontend.
*   **Interactivity:** **htmx and minimal vanilla JavaScript.** We will use htmx to handle dynamic updates for the preview panel and structure explorer without the complexity of a full SPA framework. This keeps the frontend light and tightly integrated with the Python backend.

### 6.2. Backend
*   **Framework:** **Flask.** It will serve the frontend, handle API requests, and manage the core application logic.
*   **Presentation Engine:** `python-pptx` for all OOXML manipulation. `python-docx` for ingesting `.docx` files.
*   **Conversion Engine:** **Headless LibreOffice.** Called via a `subprocess` to render slide previews. This is a robust, free, and cross-platform solution.

### 6.3. LLM Service Abstraction
To ensure flexibility, the LLM service will be abstracted behind a common interface. This allows for easy switching between providers.

**Core Design (`llm_provider.py`):**
```python
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """Generates a response from the LLM."""
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4-turbo"):
        # Initialization logic for OpenAI client
        self.client = ...
        self.model = model

    def generate_response(self, prompt: str) -> str:
        # Logic to call OpenAI API
        response = self.client.chat.completions.create(...)
        return response.choices[0].message.content

class OllamaProvider(LLMProvider):
    def __init__(self, host: str, model: str = "llama3"):
        # Initialization logic for a local Ollama client
        self.host = host
        self.model = model

    def generate_response(self, prompt: str) -> str:
        # Logic to call a local Ollama instance
        import requests
        response = requests.post(f"{self.host}/api/generate", json={...})
        return response.json()['response']
```
This allows the main application logic to be decoupled from the specific LLM provider, simply calling `llm_service.generate_response(prompt)`.

## 7. API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/upload/presentation` | Uploads a `.pptx` file to start an editing session. |
| `POST` | `/api/upload/document` | Uploads a `.docx`/`.txt` file to start the "Draft-to-Deck" planning phase. |
| `GET` | `/api/presentation/{session_id}/structure` | Returns the JSON structure for Panel 1. |
| `GET` | `/api/presentation/{session_id}/slide/{slide_index}/preview.png` | Returns the specified slide as a PNG image for Panel 3. |
| `POST`| `/api/presentation/{session_id}/plan`| Accepts the AI-generated plan and creates the new presentation. |
| `POST` | `/api/presentation/{session_id}/edit` | Core editing endpoint. **Body:** `{ "shape_id": "...", "command": "...", "context_mode": "local" | "global" }`. |

