# PowerPoint Layout System Guide

## Overview

The enhanced PowerPoint generation tool now includes a sophisticated layout system that automatically selects and applies appropriate slide layouts based on content analysis. The system includes 35 different professional layouts and uses LLM intelligence to choose the best layout for each slide.

## Features

### 35 Professional Slide Layouts

#### Basic Layouts
1. **Title Slide** - Opening slides with title and subtitle
2. **Section Divider** - Bold section breaks with large centered text
3. **Content with Title** - Standard slides with title and bullet points
4. **Blank Content** - Flexible layout for custom content

#### Multi-Column Layouts
5. **Two Column Text** - Two equal columns of text content
6. **Two Content Boxes** - Side-by-side comparison layouts
7. **Three Columns** - Parallel content in three columns
8. **Five Columns** - Five equal columns for parallel content
9. **Vertical Split** - Content split vertically with separate titles

#### Grid Layouts
10. **Four Content Grid** - 2x2 grid of content boxes
11. **Six Box Grid** - 3x2 grid of content boxes
12. **Picture Grid 2x2** - Four images in a 2x2 grid with captions

#### Image Layouts
13. **Picture Right** - Content on left, large image on right
14. **Picture Left** - Large image on left, content on right
15. **Left Content Right Image** - Content (60%) with image (40%)
16. **Three Column Images** - Three columns with images and captions

#### Data Visualization
17. **Table** - Data tables with headers
18. **Timeline** - Horizontal timeline with milestones
19. **Process Flow** - Step-by-step workflows with arrows
20. **KPI Dashboard** - Multiple KPI boxes with metrics
21. **Comparison Table** - Side-by-side comparison in table format

#### Special Effects
22. **Quote** - Large centered quote with attribution
23. **Big Number** - Prominent statistics with supporting text
24. **Full Image Overlay** - Full slide image with text overlay
25. **Pyramid Hierarchy** - Hierarchical pyramid structure
26. **Circular Diagram** - Central concept with surrounding elements

#### Mixed Content
27. **Content with Sidebar** - Main content with narrow sidebar
28. **Split Header** - Split header with two sections
29. **Top Bottom Split** - Content split horizontally
30. **Alternating Content** - Alternating left-right content blocks
31. **Content with Highlights** - Main content with highlight boxes

#### Action & Focus
32. **Call to Action** - Bold CTA with centered content
33. **Icon List** - List items with icon placeholders
34. **Centered Content** - Centered content box with margins

### Intelligent Layout Selection

The system uses two approaches for layout selection:

1. **LLM-Based Selection** - Uses AI to analyze content and select the most appropriate layout
2. **Rule-Based Fallback** - Smart fallback rules based on content patterns and keywords

## How It Works

### Content Analysis

The layout engine examines:
- Slide titles for keywords and patterns
- Content block types (bullets, tables, quotes, etc.)
- Slide position (first slide, section breaks, conclusions)
- Data patterns (percentages, timelines, comparisons)

### Layout Application

Once a layout is selected, the engine:
- Creates properly positioned text boxes and shapes
- Applies consistent formatting and styling
- Handles special elements (tables, timelines, process flows)
- Maintains visual hierarchy and professional appearance

## Integration with Existing Tool

The layout system is fully integrated into the presentation engine. When building a presentation from structured text:

1. The LLM parses the content into structured slide data
2. For each slide, the layout engine selects the best layout
3. The selected layout is applied with proper formatting
4. Special elements are rendered (tables, timelines, etc.)

## Usage Examples

### Example 1: Comparison Slide
```
Title: Performance Highlights
Content:
- Q4 Achievements: [list items]
- Key Challenges: [list items]
```
**Result**: Automatically uses "Two Content Boxes" layout

### Example 2: Statistics Slide
```
Title: 125% Revenue Growth
Content: Year-over-year increase
```
**Result**: Uses "Big Number" layout with prominent statistic

### Example 3: Timeline Slide
```
Title: Customer Success Timeline
Content:
- Q1 2024: Launch program
- Q2 2024: Achieve milestone
- Q3 2024: Expand services
```
**Result**: Creates horizontal timeline with milestones

### Example 4: Dashboard Slide
```
Title: Sales Performance Dashboard
Content:
- Total Revenue: $12.5M
- New Customers: 156
- Retention Rate: 98.5%
```
**Result**: Uses "KPI Dashboard" layout with metric boxes

### Example 5: Pyramid Hierarchy
```
Title: Company Hierarchy
Content:
- Executive Team
- Department Heads
- Team Leaders & Staff
```
**Result**: Creates pyramid structure with three levels

### Example 6: Vertical Split
```
Title: Product vs Competition
Content: Two separate content areas with individual titles
```
**Result**: Uses "Vertical Split" layout with side-by-side comparison

### Example 7: Grid Layout
```
Title: Four Key Initiatives
Content: Four equal content blocks
```
**Result**: Creates "Four Content Grid" with 2x2 layout

### Example 8: Full Image Impact
```
Title: Transform Your Business Today
Content: Dramatic message with background
```
**Result**: Uses "Full Image Overlay" with text on image background

## Configuration

### Customizing Layouts

Layouts are defined in `slide_layouts.json`:
- Modify element positions and sizes
- Adjust styling (fonts, colors, alignment)
- Add new content triggers for selection
- Create custom layouts

### Layout Selection Rules

Priority and fallback rules can be customized:
- Adjust keyword triggers
- Modify selection priority
- Add domain-specific rules

## Best Practices

1. **Content Structure** - Use clear, structured content for best results
2. **Keywords** - Include relevant keywords in titles for accurate layout selection
3. **Content Types** - Use appropriate content blocks (tables, bullets, quotes, KPIs)
4. **Balance** - Avoid overcrowding slides; the system handles spacing automatically
5. **Multi-Column Content** - For 2-6 column layouts, provide the appropriate number of content blocks
6. **Special Layouts** - Use specific keywords to trigger special layouts:
   - "dashboard", "metrics", "KPI" → KPI Dashboard
   - "hierarchy", "pyramid", "levels" → Pyramid Hierarchy
   - "ecosystem", "hub", "central" → Circular Diagram
   - "vs", "versus", "comparison" → Comparison layouts
   - "split", "dual view" → Vertical Split
   - Numbers with % → Big Number layout

## Testing

Run the test suite to see layout selection in action:
```bash
python test_layout_engine.py
```

## Layout Categories Summary

The 35 layouts are organized into 7 categories:

1. **Basic (4)** - Essential layouts for any presentation
2. **Multi-Column (5)** - Various column arrangements for parallel content
3. **Grid Layouts (3)** - Grid-based layouts for multiple items
4. **Image Layouts (4)** - Layouts incorporating image placeholders
5. **Data Visualization (5)** - Specialized layouts for data presentation
6. **Special Effects (5)** - Eye-catching layouts for impact
7. **Mixed Content (5)** - Flexible layouts combining different elements
8. **Action & Focus (3)** - Layouts for CTAs and key messages

## Future Enhancements

- Image integration from content
- Chart and graph generation
- Custom color themes
- Animation presets
- Template importing
- Smart image placement based on content
- Dynamic layout suggestions based on presentation flow