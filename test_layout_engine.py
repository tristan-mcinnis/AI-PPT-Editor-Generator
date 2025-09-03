import json
import logging
from layout_engine import LayoutEngine
from presentation_engine import PresentationEngine
from llm_provider import AnthropicProvider
from pptx import Presentation
import os
import pytest

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_content():
    """Create test content based on the user's provided slides."""
    return [
        {
            "slide_number": 1,
            "title": "US Snow Team Performance Update",
            "subtitle": "Q4 2024 Results & 2025 Outlook",
            "content_blocks": []
        },
        {
            "slide_number": 2,
            "title": "Performance Highlights",
            "content_blocks": [
                {
                    "type": "content_box",
                    "title": "Q4 2024 Achievements",
                    "items": [
                        "Exceeded revenue target by 15%",
                        "Onboarded 8 new enterprise clients",
                        "Reduced churn rate to 2.3%"
                    ]
                },
                {
                    "type": "content_box", 
                    "title": "Key Challenges",
                    "items": [
                        "Integration delays with 2 clients",
                        "Resource constraints in support team",
                        "Competitive pressure in mid-market"
                    ]
                }
            ]
        },
        {
            "slide_number": 3,
            "title": "125% Revenue Growth",
            "content_blocks": [
                {
                    "type": "text",
                    "text": "Year-over-year revenue increase driven by enterprise expansion"
                }
            ]
        },
        {
            "slide_number": 4,
            "title": "Regional Performance Breakdown",
            "content_blocks": [
                {
                    "type": "table",
                    "data": [
                        ["Region", "Q4 Revenue", "YoY Growth", "Pipeline"],
                        ["Northeast", "$4.2M", "+35%", "$8.1M"],
                        ["West Coast", "$3.8M", "+28%", "$7.5M"],
                        ["Southeast", "$2.1M", "+42%", "$4.3M"],
                        ["Midwest", "$1.9M", "+18%", "$3.2M"]
                    ]
                }
            ]
        },
        {
            "slide_number": 5,
            "title": "Customer Success Timeline",
            "content_blocks": [
                {
                    "type": "bullets",
                    "items": [
                        "Q1 2024: Launched Customer Success 2.0 program",
                        "Q2 2024: Achieved 95% satisfaction score",
                        "Q3 2024: Implemented automated onboarding",
                        "Q4 2024: Reduced time-to-value by 40%",
                        "Q1 2025: Rolling out premium support tier"
                    ]
                }
            ]
        },
        {
            "slide_number": 6,
            "title": "Sales Process Optimization",
            "content_blocks": [
                {
                    "type": "process",
                    "steps": [
                        "Lead Qualification",
                        "Discovery Call",
                        "Solution Design",
                        "Proposal & Negotiation",
                        "Contract & Close"
                    ]
                }
            ]
        },
        {
            "slide_number": 7,
            "title": "\"Our partnership with Snow has transformed how we approach data analytics\"",
            "content_blocks": [
                {
                    "type": "attribution",
                    "text": "- Sarah Chen, CTO at TechCorp"
                }
            ]
        },
        {
            "slide_number": 8,
            "title": "Team Expansion Plans",
            "content_blocks": [
                {
                    "type": "column",
                    "title": "Engineering",
                    "items": [
                        "15 new hires",
                        "Focus on ML/AI",
                        "Q1-Q2 2025"
                    ]
                },
                {
                    "type": "column",
                    "title": "Sales",
                    "items": [
                        "10 new AEs", 
                        "Enterprise focus",
                        "Q1 2025"
                    ]
                },
                {
                    "type": "column",
                    "title": "Customer Success",
                    "items": [
                        "8 new CSMs",
                        "Technical expertise",
                        "Q1-Q3 2025"
                    ]
                }
            ]
        },
        {
            "slide_number": 9,
            "title": "Product Feature Roadmap",
            "content_blocks": [
                {
                    "type": "bullets",
                    "items": [
                        "Advanced Analytics Dashboard",
                        "Real-time Collaboration Tools",
                        "AI-Powered Insights Engine",
                        "Mobile Application Launch",
                        "Enterprise Security Features"
                    ]
                }
            ]
        },
        {
            "slide_number": 10,
            "title": "Market Position Analysis",
            "content_blocks": [
                {
                    "type": "text",
                    "text": "Competitive landscape overview with market share data"
                }
            ]
        },
        {
            "slide_number": 11,
            "title": "Key Success Metrics",
            "content_blocks": [
                {
                    "type": "bullets",
                    "items": [
                        "Customer Acquisition Cost: $12,500",
                        "Customer Lifetime Value: $125,000", 
                        "Net Promoter Score: 72",
                        "Monthly Recurring Revenue: $12M",
                        "Annual Contract Value: $156,000"
                    ]
                }
            ]
        },
        {
            "slide_number": 12,
            "title": "Strategic Initiatives 2025",
            "content_blocks": []
        },
        {
            "slide_number": 13,
            "title": "Q1 2025 Priorities",
            "content_blocks": [
                {
                    "type": "bullets",
                    "items": [
                        "Launch Enterprise 3.0 platform",
                        "Expand into European markets",
                        "Achieve SOC 2 Type II certification",
                        "Implement partner channel program",
                        "Scale customer success operations"
                    ]
                }
            ]
        },
        {
            "slide_number": 14,
            "title": "Next Steps & Action Items",
            "content_blocks": [
                {
                    "type": "text",
                    "text": "Schedule follow-up meetings with key stakeholders"
                },
                {
                    "type": "text", 
                    "text": "Review detailed financial projections"
                },
                {
                    "type": "text",
                    "text": "Finalize Q1 hiring plans"
                }
            ]
        },
        # Additional test slides for new layouts
        {
            "slide_number": 15,
            "title": "Sales Performance Dashboard",
            "content_blocks": [
                {
                    "type": "kpi",
                    "value": "$12.5M",
                    "label": "Total Revenue"
                },
                {
                    "type": "kpi",
                    "value": "156",
                    "label": "New Customers"
                },
                {
                    "type": "kpi",
                    "value": "98.5%",
                    "label": "Retention Rate"
                }
            ]
        },
        {
            "slide_number": 16,
            "title": "Product vs Competition",
            "content_blocks": [
                {
                    "type": "comparison",
                    "data": {
                        "left": {"title": "Our Product", "items": ["Cloud-native", "Real-time sync", "Enterprise security"]},
                        "right": {"title": "Competition", "items": ["Legacy architecture", "Batch processing", "Basic security"]}
                    }
                }
            ]
        },
        {
            "slide_number": 17,
            "title": "Company Hierarchy",
            "content_blocks": [
                {
                    "type": "pyramid",
                    "levels": ["Executive Team", "Department Heads", "Team Leaders & Staff"]
                }
            ]
        },
        {
            "slide_number": 18,
            "title": "Product Ecosystem",
            "content_blocks": [
                {
                    "type": "bullets",
                    "items": ["Data Integration", "Analytics Engine", "Visualization Tools", "API Gateway"]
                }
            ]
        },
        {
            "slide_number": 19,
            "title": "Before vs After Implementation",
            "content_blocks": [
                {
                    "type": "text",
                    "text": "Manual processes, 48-hour turnaround"
                },
                {
                    "type": "text",
                    "text": "Automated workflows, real-time processing"
                }
            ]
        },
        {
            "slide_number": 20,
            "title": "Q1 Goals with Key Metrics",
            "content_blocks": [
                {
                    "type": "bullets",
                    "items": ["Launch new product line", "Expand to 3 new markets", "Achieve $15M in revenue"]
                },
                {
                    "type": "highlight",
                    "title": "Critical KPI",
                    "text": "15% QoQ Growth"
                }
            ]
        }
    ]

def test_layout_selection():
    """Test the layout selection with different slide types."""
    
    # Initialize components
    layout_engine = LayoutEngine()
    
    # Get test content
    test_slides = create_test_content()
    
    print("\n=== Layout Selection Test Results ===\n")
    
    # Test layout selection for each slide
    for slide_data in test_slides:
        # Use fallback selection for testing (to avoid LLM costs)
        layout_id = layout_engine._fallback_layout_selection(slide_data)
        
        print(f"Slide {slide_data['slide_number']}: {slide_data['title']}")
        print(f"  Selected Layout: {layout_id}")
        print(f"  Reasoning: {get_layout_reasoning(slide_data, layout_id)}")
        print()

def get_layout_reasoning(slide_data, layout_id):
    """Explain why a particular layout was selected."""
    reasoning_map = {
        'title_slide': "First slide with subtitle - perfect for opening",
        'two_content_boxes': "Contains two content boxes for comparison",
        'big_number': "Features a prominent statistic/percentage",
        'table': "Contains tabular data",
        'timeline': "Shows chronological events/milestones",
        'process_flow': "Displays a step-by-step process",
        'quote': "Features a testimonial or quote",
        'three_columns': "Has three distinct column sections",
        'icon_list': "List of features/services with icons",
        'picture_right': "Content with image placeholder",
        'section_divider': "Section break or chapter divider",
        'call_to_action': "Final slide with next steps",
        'content_with_title': "Standard content slide with bullets/text"
    }
    
    return reasoning_map.get(layout_id, "Default layout selected")

def test_full_presentation_generation():
    """Test generating a full presentation with layouts."""
    print("\n=== Full Presentation Generation Test ===\n")
    
    # Skip test if Anthropic API key is not available
    if not os.getenv('ANTHROPIC_API_KEY'):
        pytest.skip('Skipping full presentation generation test: ANTHROPIC_API_KEY not set')
    
    # Initialize components
    presentation_engine = PresentationEngine()
    llm_provider = AnthropicProvider()
    
    # Create a test presentation
    test_file = "test_layout_presentation.pptx"
    
    # Create a blank presentation first
    prs = Presentation()
    prs.save(test_file)
    
    # Convert test content to structured text format
    structured_text = convert_to_structured_text(create_test_content())
    
    # Build presentation with layouts
    success = presentation_engine.build_from_structured_text(
        test_file, 
        structured_text, 
        llm_provider
    )
    
    if success:
        print(f"✅ Successfully created presentation: {test_file}")
        print(f"   File size: {os.path.getsize(test_file)} bytes")
    else:
        print("❌ Failed to create presentation")

def convert_to_structured_text(slides):
    """Convert slide data to structured text format."""
    lines = []
    
    for slide in slides:
        lines.append(f"Slide {slide['slide_number']}: {slide['title']}")
        
        if 'subtitle' in slide:
            lines.append(f"Subtitle: {slide['subtitle']}")
        
        for block in slide.get('content_blocks', []):
            if block['type'] == 'bullets' and 'items' in block:
                for item in block['items']:
                    lines.append(f"• {item}")
            elif block['type'] == 'text':
                lines.append(block['text'])
            elif block['type'] == 'content_box':
                lines.append(f"{block['title']}:")
                for item in block.get('items', []):
                    lines.append(f"  • {item}")
            elif block['type'] == 'table':
                lines.append("Table:")
                for row in block['data']:
                    lines.append(" | ".join(row))
            elif block['type'] == 'process':
                lines.append("Process Steps:")
                for step in block['steps']:
                    lines.append(f"→ {step}")
            elif block['type'] == 'column':
                lines.append(f"{block['title']}:")
                for item in block.get('items', []):
                    lines.append(f"  - {item}")
            elif block['type'] == 'attribution':
                lines.append(block['text'])
        
        lines.append("")  # Empty line between slides
    
    return "\n".join(lines)

def demonstrate_layout_capabilities():
    """Demonstrate all 35 layout types with examples."""
    print("\n=== Layout Capabilities Demonstration ===\n")
    
    with open('slide_layouts.json', 'r') as f:
        layouts = json.load(f)
    
    print(f"Total layouts available: {len(layouts['layouts'])}\n")
    
    # Group layouts by category
    categories = {
        "Basic": ["title_slide", "section_divider", "content_with_title", "blank_content"],
        "Multi-Column": ["two_column_text", "two_content_boxes", "three_columns", "five_columns", "vertical_split"],
        "Grid Layouts": ["four_content_grid", "six_box_grid", "picture_grid_2x2"],
        "Image Layouts": ["picture_right", "picture_left", "left_content_right_image", "three_column_images"],
        "Data Visualization": ["table", "timeline", "process_flow", "kpi_dashboard", "comparison_table"],
        "Special Effects": ["quote", "big_number", "full_image_overlay", "pyramid_hierarchy", "circular_diagram"],
        "Mixed Content": ["content_with_sidebar", "split_header", "top_bottom_split", "alternating_content", "content_with_highlights"],
        "Action": ["call_to_action", "icon_list", "centered_content"]
    }
    
    for category, layout_ids in categories.items():
        print(f"\n{category}:")
        print("-" * 40)
        for layout_id in layout_ids:
            layout = next((l for l in layouts['layouts'] if l['id'] == layout_id), None)
            if layout:
                print(f"• {layout['name']} ({layout['id']})")
                print(f"  {layout['description']}")
                print(f"  Triggers: {', '.join(layout['contentTriggers'][:3])}...")
        print()

if __name__ == "__main__":
    print("🎯 PowerPoint Layout Engine Test Suite")
    print("=" * 50)
    
    # Run tests
    demonstrate_layout_capabilities()
    test_layout_selection()
    
    # Uncomment to test full presentation generation
    # test_full_presentation_generation()
    
    print("\n✅ Test suite completed!")