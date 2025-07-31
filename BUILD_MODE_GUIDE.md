# Build Mode Guide - Create Full Presentations from Structured Text

## How to Use Build Mode

1. **Upload a Presentation**
   - Click "Upload Presentation" and select your template .pptx file
   - This can be an empty presentation or one with existing design

2. **Enter Build Mode**
   - Click the "Build Presentation" button
   - The interface will change:
     - Input area expands automatically
     - Placeholder text changes to "Paste your structured presentation content here..."
     - Execute button changes to "Build Presentation"

3. **Paste Your Structured Content**
   - Copy your entire presentation structure (like the TNF Snow Report example)
   - Paste it into the expanded text area
   - The tool accepts markdown-style formatting with:
     - `## Slide X` for slide markers
     - `**Title**` for slide titles
     - `**Content Box:** for content sections
     - Bullet points with `-` or `*`
     - Regular paragraphs

4. **Build the Presentation**
   - Click "Build Presentation"
   - The AI will:
     - Parse your structured text
     - Extract all slides and content
     - Create a properly formatted presentation
     - Replace any existing slides with the new content

5. **Review and Edit**
   - The Structure Explorer updates with all new slides
   - Preview each slide using the navigation buttons
   - Exit build mode to make individual edits to shapes

## Example Structure

```markdown
## Slide 1
**Welcome to My Presentation**
- First point
- Second point
- Third point

## Slide 2
**Key Features**

**Feature Box 1: Performance**
- Fast processing
- Low latency
- High throughput

**Feature Box 2: Usability**
- Simple interface
- Easy to learn
- Comprehensive docs
```

## Tips

- Use clear hierarchy with `##` for slides
- Bold text with `**` for titles and emphasis
- Use descriptive content box titles
- Keep bullet points concise
- The AI preserves your exact wording

## Exiting Build Mode

Click "Cancel Build Mode" or complete a build to return to normal editing mode.