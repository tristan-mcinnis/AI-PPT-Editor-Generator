"""
Example demonstrating the new layout system integration
"""
from presentation_engine import PresentationEngine
from llm_provider import AnthropicProvider
from pptx import Presentation
import os

def create_example_presentation():
    """Create an example presentation showcasing different layouts."""
    
    # Sample structured text that will trigger different layouts
    structured_text = """
Slide 1: Advanced Analytics Platform
Subtitle: Transforming Data into Insights

Slide 2: Platform Overview vs Competition
Our Platform:
• Real-time processing
• AI-powered insights  
• Enterprise security
• 99.9% uptime

Competition:
• Batch processing only
• Basic analytics
• Limited security
• 95% uptime

Slide 3: 87% Customer Satisfaction
Industry-leading satisfaction scores across all segments

Slide 4: Implementation Timeline
Q1 2024: Requirements gathering and design phase
Q2 2024: Development and initial testing
Q3 2024: Beta launch with select customers
Q4 2024: Full platform rollout
Q1 2025: Advanced features release

Slide 5: Customer Success Process
Lead Qualification → Discovery → Proof of Concept → Implementation → Success

Slide 6: "This platform revolutionized our data strategy and delivered ROI within 3 months"
- Michael Chang, VP of Analytics at DataCorp

Slide 7: Performance Metrics
Region | Users | Revenue | Growth
North America | 15,000 | $4.5M | +45%
Europe | 8,500 | $2.8M | +38%
Asia Pacific | 6,200 | $2.1M | +52%

Slide 8: Key Features
• Advanced Machine Learning Models
• Real-time Data Processing  
• Custom Dashboard Builder
• API Integration Suite
• Enterprise Security

Slide 9: Three Pillars of Success
Technology:
- Cloud-native
- Scalable
- Secure

People:
- Expert team
- 24/7 support
- Training

Process:
- Agile delivery
- Best practices
- Continuous improvement

Slide 10: Next Steps
Ready to transform your data strategy?
Contact us at sales@example.com or call 1-800-ANALYTICS
"""
    
    # Initialize the presentation engine
    engine = PresentationEngine()
    
    # Create a blank presentation to start with
    prs = Presentation()
    output_file = "example_with_layouts.pptx"
    prs.save(output_file)
    
    # For this example, we'll use a mock LLM response
    # In production, this would use the actual LLM provider
    class MockLLM:
        def generate_response(self, prompt):
            # Return a mock structured response
            return """[
                {
                    "slide_number": 1,
                    "title": "Advanced Analytics Platform",
                    "subtitle": "Transforming Data into Insights",
                    "content_blocks": []
                },
                {
                    "slide_number": 2,
                    "title": "Platform Overview vs Competition",
                    "content_blocks": [
                        {
                            "type": "content_box",
                            "title": "Our Platform",
                            "items": ["Real-time processing", "AI-powered insights", "Enterprise security", "99.9% uptime"]
                        },
                        {
                            "type": "content_box",
                            "title": "Competition",
                            "items": ["Batch processing only", "Basic analytics", "Limited security", "95% uptime"]
                        }
                    ]
                },
                {
                    "slide_number": 3,
                    "title": "87% Customer Satisfaction",
                    "content_blocks": [
                        {
                            "type": "text",
                            "text": "Industry-leading satisfaction scores across all segments"
                        }
                    ]
                },
                {
                    "slide_number": 4,
                    "title": "Implementation Timeline",
                    "content_blocks": [
                        {
                            "type": "bullets",
                            "items": [
                                "Q1 2024: Requirements gathering and design phase",
                                "Q2 2024: Development and initial testing",
                                "Q3 2024: Beta launch with select customers",
                                "Q4 2024: Full platform rollout",
                                "Q1 2025: Advanced features release"
                            ]
                        }
                    ]
                },
                {
                    "slide_number": 5,
                    "title": "Customer Success Process",
                    "content_blocks": [
                        {
                            "type": "process",
                            "steps": ["Lead Qualification", "Discovery", "Proof of Concept", "Implementation", "Success"]
                        }
                    ]
                },
                {
                    "slide_number": 6,
                    "title": "\\"This platform revolutionized our data strategy and delivered ROI within 3 months\\"",
                    "content_blocks": [
                        {
                            "type": "attribution",
                            "text": "- Michael Chang, VP of Analytics at DataCorp"
                        }
                    ]
                }
            ]"""
    
    # Build the presentation
    mock_llm = MockLLM()
    success = engine.build_from_structured_text(output_file, structured_text, mock_llm)
    
    if success:
        print(f"✅ Successfully created presentation with layouts: {output_file}")
        print(f"   File size: {os.path.getsize(output_file)} bytes")
        print("\nLayouts used:")
        print("- Slide 1: Title Slide (with subtitle)")
        print("- Slide 2: Two Content Boxes (comparison)")
        print("- Slide 3: Big Number (87% statistic)")
        print("- Slide 4: Timeline (implementation phases)")
        print("- Slide 5: Process Flow (customer journey)")
        print("- Slide 6: Quote (testimonial)")
    else:
        print("❌ Failed to create presentation")

if __name__ == "__main__":
    create_example_presentation()