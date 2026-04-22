
"""Top level agent for the Smart Vendor Compliance Officer."""

import logging
import os
from typing import Any

import google.cloud.logging
from google.adk.agents import LlmAgent
from google.genai import types

from .pipeline import process_proposal_text
from .prompts import return_instructions_root

IS_RUNNING_IN_GCP = os.getenv("K_SERVICE") is not None

if IS_RUNNING_IN_GCP:
    try:
        cloud_logging_client = google.cloud.logging.Client()
        cloud_logging_client.setup_logging()
        logging.basicConfig(level=logging.INFO)
    except Exception:
        logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
logger.info("agent.py loaded successfully.")


def analyze_vendor_proposal(proposal_text: str) -> dict[str, Any]:
    logger.info("analyze_vendor_proposal called.")

    if proposal_text is None:
        proposal_text = ""

    proposal_text = str(proposal_text).strip()

    if not proposal_text:
        return {
            "reference_id": "",
            "company_name": "N/A",
            "contact_person": "N/A",
            "crn": "N/A",
            "total_bid_value_text": "N/A",
            "annual_revenue_text": "N/A",
            "project_timeline_text": "N/A",
            "executive_summary": "No proposal text was available for analysis.",
            "innovation_score": 0,
            "risk_level": "High",
            "risk_reasoning": "Readable proposal content is required.",
            "rules": [
                {"rule_id": "R-01", "status": "FAIL", "observation": "No readable proposal text was available."},
                {"rule_id": "R-02", "status": "FAIL", "observation": "No readable proposal text was available."},
                {"rule_id": "R-03", "status": "FAIL", "observation": "No readable proposal text was available."},
                {"rule_id": "R-04", "status": "FAIL", "observation": "No readable proposal text was available."},
            ],
            "final_decision": "REJECT FOR INCOMPLETENESS. To be considered for approval, please provide a readable proposal and resubmit.",
            "routing_decision": "Rejected",
            "certificate_file": "",
            "certificate_gcs_uri": "",
            "certificate_browser_url": "",
        }

    try:
        logger.info("Processing proposal text. Length=%s chars", len(proposal_text))
        result = process_proposal_text(proposal_text)
        logger.info(
            "Proposal processed successfully. reference_id=%s company=%s",
            result.get("reference_id", ""),
            result.get("company_name", ""),
        )
        return result
    except Exception as exc:
        logger.exception("Unhandled error in analyze_vendor_proposal: %s", exc)
        return {
            "reference_id": "",
            "company_name": "N/A",
            "contact_person": "N/A",
            "crn": "N/A",
            "total_bid_value_text": "N/A",
            "annual_revenue_text": "N/A",
            "project_timeline_text": "N/A",
            "executive_summary": "The proposal could not be processed automatically due to an internal error.",
            "innovation_score": 0,
            "risk_level": "High",
            "risk_reasoning": f"Internal processing error: {exc}",
            "rules": [
                {"rule_id": "R-01", "status": "FAIL", "observation": "Processing failed before the rule could be evaluated."},
                {"rule_id": "R-02", "status": "FAIL", "observation": "Processing failed before the rule could be evaluated."},
                {"rule_id": "R-03", "status": "FAIL", "observation": "Processing failed before the rule could be evaluated."},
                {"rule_id": "R-04", "status": "FAIL", "observation": "Processing failed before the rule could be evaluated."},
            ],
            "final_decision": "REJECT FOR INCOMPLETENESS. To be considered for approval, please retry submission or contact the system administrator.",
            "routing_decision": "Rejected",
            "certificate_file": "",
            "certificate_gcs_uri": "",
            "certificate_browser_url": "",
        }


def get_root_agent() -> LlmAgent:
    return LlmAgent(
        model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.5-pro"),
        name=os.getenv("ROOT_AGENT_NAME", "smart_vendor_compliance_officer"),
        instruction=return_instructions_root(),
        tools=[analyze_vendor_proposal],
        generate_content_config=types.GenerateContentConfig(temperature=0.01),
    )


root_agent = get_root_agent()
