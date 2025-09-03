#!/usr/bin/env python
"""
Live Build Test for AI PPT Editor

This script performs a live test of the DeepSeek-powered presentation builder by:
1. Creating a blank PPTX file
2. Using the 'Consulting Proposal' recipe as structured text
3. Building a presentation using the PresentationEngine and DeepSeek LLM

Usage:
    python live_build_test.py
"""

import os
import sys
import logging
from pathlib import Path

# ---------------------------------------------------------------------------
# Ensure repository root is on sys.path so top-level imports resolve
# ---------------------------------------------------------------------------
from pathlib import Path as _PathForSys  # pylint: disable=wrong-import-position
sys.path.insert(0, str(_PathForSys(__file__).resolve().parents[1]))

from dotenv import load_dotenv
from pptx import Presentation
from llm_provider import get_llm_provider
from presentation_engine import PresentationEngine

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Consulting Proposal recipe text
CONSULTING_PROPOSAL = """## Slide 1
**Consulting Proposal**
- Client: ACME Corp
- Objective: Increase operational efficiency by 30%
- Timeline: 12-week engagement

## Slide 2
**Current Business Challenges**
- Manual processes causing 40% productivity loss
- Data silos preventing cross-functional insights
- Inconsistent customer experience across channels

## Slide 3
**Recommended Solution**
- Process automation & workflow redesign
- Integrated data platform implementation
- Customer journey optimization

## Slide 4
**Expected Business Outcomes**
- 30% increase in operational efficiency
- $2.4M annual cost savings
- Improved customer satisfaction metrics
- Scalable foundation for future growth"""

def main():
    """Run the live build test."""
    try:
        # Load environment variables
        logger.info("Loading environment variables from .env")
        load_dotenv()
        
        # Ensure uploads directory exists
        uploads_dir = Path("uploads")
        uploads_dir.mkdir(exist_ok=True)
        
        # Create filepath for the test presentation
        filepath = uploads_dir / "live_test.pptx"
        logger.info(f"Creating blank presentation at {filepath}")
        
        # Create a blank presentation
        prs = Presentation()
        prs.save(str(filepath))
        logger.info(f"Blank presentation created: {os.path.getsize(filepath)} bytes")
        
        # Get the LLM provider (DeepSeek)
        logger.info("Initializing DeepSeek LLM provider")
        llm = get_llm_provider()
        
        # Use the presentation engine to build from structured text
        logger.info("Building presentation from 'Consulting Proposal' template")
        engine = PresentationEngine()
        success = engine.build_from_structured_text(
            str(filepath),
            CONSULTING_PROPOSAL,
            llm
        )
        
        if success:
            file_size = os.path.getsize(filepath)
            logger.info(f"✅ Success! Presentation built at {filepath}")
            logger.info(f"   File size: {file_size} bytes")
            return 0
        else:
            logger.error("❌ Failed to build presentation")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Error during live build test: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
