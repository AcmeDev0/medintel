"""
MedIntel AI — Compliance Checklists API Routes.
Provides step-by-step regulatory compliance workflows.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# --- Comprehensive Checklist Data ---
# This is the curated knowledge base of regulatory checklists.
# Each checklist is built from official NAFDAC guidelines and regulatory directives.

CHECKLISTS = {
    "nafdac-drug-registration": {
        "id": "nafdac-drug-registration",
        "title": "NAFDAC Drug Product Registration",
        "subtitle": "Complete guide to registering a pharmaceutical product with NAFDAC",
        "category": "Pharmaceutical",
        "jurisdiction": "Nigeria (NAFDAC)",
        "estimated_time": "6–12 months",
        "estimated_cost": "₦500,000 – ₦2,000,000",
        "icon": "💊",
        "steps": [
            {
                "step": 1,
                "title": "Pre-Registration Assessment",
                "description": "Determine if your product requires NAFDAC registration and identify the correct category.",
                "tasks": [
                    "Confirm product falls under NAFDAC-regulated categories (drug, herbal, cosmetic, etc.)",
                    "Determine if the product is a New Drug Application (NDA) or generic (ANDA equivalent)",
                    "Check if the drug is already registered in Nigeria by another company",
                    "Identify the product classification: prescription, OTC, or controlled substance",
                    "Engage a qualified regulatory affairs professional if this is your first submission"
                ],
                "documents": ["Product formulation details", "Evidence of GMP compliance"],
                "tips": "Schedule a pre-submission meeting with NAFDAC to clarify requirements before compiling your full dossier."
            },
            {
                "step": 2,
                "title": "Company Registration & Licensing",
                "description": "Ensure your company is properly registered and licensed to operate in Nigeria.",
                "tasks": [
                    "Register company with the Corporate Affairs Commission (CAC)",
                    "Obtain NAFDAC Import/Manufacture License (for importers/manufacturers)",
                    "Register premises with NAFDAC (factory/warehouse inspection required)",
                    "Obtain Pharmacist Council of Nigeria (PCN) license if applicable",
                    "Prepare company organizational chart showing qualified persons"
                ],
                "documents": ["CAC registration certificate", "NAFDAC premises license", "PCN license", "Company organogram"],
                "tips": "NAFDAC will not accept product registration applications from unlicensed companies. Complete this step first."
            },
            {
                "step": 3,
                "title": "Dossier Compilation (CTD Format)",
                "description": "Compile the product dossier in Common Technical Document (CTD) format.",
                "tasks": [
                    "Module 1: Administrative information (application form, labeling, product info)",
                    "Module 2: Quality Overall Summary, Non-clinical Summary, Clinical Summary",
                    "Module 3: Quality data (drug substance & drug product specifications, stability data)",
                    "Module 4: Non-clinical study reports (for new chemical entities)",
                    "Module 5: Clinical study reports (for new chemical entities)",
                    "For generics: Include bioequivalence study data",
                    "For established products: Literature-based evidence may be acceptable"
                ],
                "documents": [
                    "Completed CTD dossier (Modules 1-5)",
                    "Certificate of Pharmaceutical Product (CPP) from country of origin",
                    "GMP certificate from approved regulatory authority",
                    "Stability study data (ICH guidelines, Zone IVb conditions for tropical countries)",
                    "Certificate of Analysis for active ingredient and finished product",
                    "Bioequivalence study report (for generics)"
                ],
                "tips": "Incomplete dossiers are the #1 reason for rejection. Use the NAFDAC CTD checklist to verify all sections are complete before submission."
            },
            {
                "step": 4,
                "title": "Application Submission",
                "description": "Submit the complete dossier through NAFDAC's registration portal.",
                "tasks": [
                    "Create/log into NAFDAC Online Registration Portal (NAPAMS)",
                    "Upload all dossier documents in the prescribed format",
                    "Pay the applicable registration fees via the NAFDAC payment portal",
                    "Submit physical samples of the product (as required)",
                    "Obtain acknowledgment receipt and tracking number"
                ],
                "documents": ["Online application receipt", "Payment confirmation", "Physical product samples"],
                "tips": "Keep copies of everything submitted. Track your application status through NAPAMS regularly."
            },
            {
                "step": 5,
                "title": "NAFDAC Review & Evaluation",
                "description": "NAFDAC conducts scientific assessment of the submitted dossier.",
                "tasks": [
                    "Respond promptly to any NAFDAC queries or deficiency letters",
                    "Provide additional data or clarifications as requested",
                    "Facilitate GMP inspection of manufacturing site if required",
                    "Attend product presentation meetings if scheduled by NAFDAC",
                    "Laboratory analysis of submitted samples by NAFDAC labs"
                ],
                "documents": ["Response to deficiency letters", "Additional stability data if requested"],
                "tips": "Response time to deficiency letters is critical — delays can reset your review timeline. Aim to respond within 30 days."
            },
            {
                "step": 6,
                "title": "Approval & Post-Market Obligations",
                "description": "Upon successful review, receive your NAFDAC registration number and comply with ongoing obligations.",
                "tasks": [
                    "Receive NAFDAC Registration Certificate and Number",
                    "Apply NAFDAC registration number to all product packaging and labeling",
                    "Implement pharmacovigilance system for adverse event reporting",
                    "Submit annual safety/periodic reports as required",
                    "Apply for renewal before registration expiry (typically every 5 years)",
                    "Report any changes to formulation, manufacturing site, or labeling to NAFDAC"
                ],
                "documents": ["NAFDAC Registration Certificate", "Pharmacovigilance plan", "Periodic safety reports"],
                "tips": "Registration is NOT a one-time event. Post-market surveillance and renewal are mandatory obligations."
            }
        ],
        "references": [
            "NAFDAC Drug Registration Guidelines",
            "NAFDAC Regulatory Directive RD-003",
            "ICH Common Technical Document (CTD) Guidelines",
            "WHO Guidelines on Prequalification"
        ]
    },

    "nafdac-medical-device": {
        "id": "nafdac-medical-device",
        "title": "NAFDAC Medical Device Registration",
        "subtitle": "Step-by-step guide to registering medical devices under the 2025 framework",
        "category": "Medical Device",
        "jurisdiction": "Nigeria (NAFDAC)",
        "estimated_time": "3–9 months (varies by device class)",
        "estimated_cost": "₦200,000 – ₦1,500,000",
        "icon": "🏥",
        "steps": [
            {
                "step": 1,
                "title": "Device Classification",
                "description": "Determine the risk class of your medical device (Class A, B, C, or D).",
                "tasks": [
                    "Review NAFDAC Medical Devices Regulations 2025 classification rules",
                    "Assess device intended purpose, duration of contact, and invasiveness",
                    "Apply GHTF/IMDRF classification rules to determine risk class",
                    "For Software as a Medical Device (SaMD): Apply IMDRF SaMD classification framework",
                    "Document classification rationale with supporting evidence",
                    "Consider requesting NAFDAC classification confirmation for borderline devices"
                ],
                "documents": ["Device classification rationale document", "Intended purpose statement"],
                "tips": "Use the MedIntel Device Classification Helper for AI-assisted classification. When in doubt, NAFDAC applies the higher-risk classification."
            },
            {
                "step": 2,
                "title": "Establish Quality Management System",
                "description": "Implement a QMS compliant with ISO 13485 or equivalent.",
                "tasks": [
                    "Implement ISO 13485:2016 Quality Management System",
                    "Conduct risk management per ISO 14971",
                    "Establish design and development procedures",
                    "Implement document control and record-keeping systems",
                    "Set up post-market surveillance procedures",
                    "Obtain ISO 13485 certification from an accredited certification body"
                ],
                "documents": ["ISO 13485 certificate", "QMS manual", "Risk management file (ISO 14971)"],
                "tips": "ISO 13485 certification is expected for Class B and above. Class A devices may need only a declaration of conformity."
            },
            {
                "step": 3,
                "title": "Technical Documentation",
                "description": "Compile comprehensive technical file for the device.",
                "tasks": [
                    "Prepare device description and specifications",
                    "Compile design and manufacturing information",
                    "Document verification and validation test results",
                    "Prepare labeling and Instructions for Use (IFU)",
                    "Compile clinical evidence (clinical evaluation or clinical investigation data)",
                    "Prepare biocompatibility assessment (ISO 10993) if applicable",
                    "Document software lifecycle (IEC 62304) for software-containing devices",
                    "Electromagnetic compatibility testing (IEC 60601-1-2) for electrical devices"
                ],
                "documents": [
                    "Technical documentation/file",
                    "Performance test reports",
                    "Clinical evaluation report",
                    "Biocompatibility test reports",
                    "Electrical safety test reports",
                    "Software documentation (IEC 62304)"
                ],
                "tips": "Technical file requirements increase with device class. Class D devices require the most comprehensive documentation including clinical investigation data."
            },
            {
                "step": 4,
                "title": "Application Submission to NAFDAC",
                "description": "Submit registration application with all supporting documents.",
                "tasks": [
                    "Complete NAFDAC medical device registration application form",
                    "Prepare Manufacturer's Declaration of Conformity",
                    "Obtain Free Sale Certificate from country of origin (for imported devices)",
                    "Submit through NAFDAC online portal (NAPAMS)",
                    "Pay applicable registration fees",
                    "Submit physical device samples if requested"
                ],
                "documents": [
                    "NAFDAC application form",
                    "Declaration of Conformity",
                    "Free Sale Certificate / Certificate of Foreign Government",
                    "ISO 13485 certificate",
                    "Technical documentation summary",
                    "Labeling and IFU samples"
                ],
                "tips": "Ensure all documents are notarized/apostilled as required. For imported devices, the Free Sale Certificate must be from a recognized regulatory authority."
            },
            {
                "step": 5,
                "title": "NAFDAC Review & Approval",
                "description": "NAFDAC evaluates the application based on device class.",
                "tasks": [
                    "Class A: Declaration-based pathway (faster review)",
                    "Class B: Standard technical review",
                    "Class C-D: Full technical assessment and possible expert panel review",
                    "Respond to any NAFDAC queries within specified timeframes",
                    "Facilitate site inspection if required (for local manufacturers)",
                    "Provide additional testing data if requested"
                ],
                "documents": ["Responses to NAFDAC queries", "Additional test data as requested"],
                "tips": "NAFDAC's Reliance Guidelines (2025) may allow expedited review if the device is already approved by WHO PQ, US FDA, EU Notified Body, or other trusted authorities."
            },
            {
                "step": 6,
                "title": "Post-Market Requirements",
                "description": "Ongoing obligations after device registration.",
                "tasks": [
                    "Implement post-market surveillance plan",
                    "Report adverse events and device malfunctions to NAFDAC",
                    "Maintain traceability system for distributed devices",
                    "Submit periodic safety update reports",
                    "Notify NAFDAC of any significant changes to the device",
                    "Renew registration before expiry"
                ],
                "documents": ["Post-market surveillance plan", "Adverse event reports", "Periodic safety reports"],
                "tips": "Under the 2025 regulations, post-market surveillance is mandatory for all device classes. Failure to report adverse events can result in registration suspension."
            }
        ],
        "references": [
            "NAFDAC Medical Devices, Including In Vitro Diagnostics and Related Products Regulations, 2025",
            "GHTF Study Group 1: Classification of Medical Devices",
            "ISO 13485:2016",
            "ISO 14971:2019"
        ]
    },

    "nafdac-ivd-registration": {
        "id": "nafdac-ivd-registration",
        "title": "NAFDAC IVD (In-Vitro Diagnostic) Registration",
        "subtitle": "Guide for registering diagnostic test kits, reagents, and lab equipment",
        "category": "In-Vitro Diagnostics",
        "jurisdiction": "Nigeria (NAFDAC)",
        "estimated_time": "4–8 months",
        "estimated_cost": "₦300,000 – ₦1,200,000",
        "icon": "🔬",
        "steps": [
            {
                "step": 1,
                "title": "IVD Classification",
                "description": "Classify the IVD according to NAFDAC risk-based rules.",
                "tasks": [
                    "Determine if the product is an IVD under NAFDAC definitions",
                    "Apply IVD-specific classification rules (Class A-D for IVDs)",
                    "High-risk IVDs: Blood screening for HIV, Hepatitis, blood grouping → Class D",
                    "Self-testing IVDs: Pregnancy tests, glucose monitors → Typically Class C",
                    "General laboratory IVDs: Clinical chemistry, hematology → Typically Class A-B",
                    "Document classification rationale"
                ],
                "documents": ["IVD classification rationale", "Intended use statement"],
                "tips": "IVDs used for blood screening (transfusion safety) are automatically Class D regardless of complexity."
            },
            {
                "step": 2,
                "title": "Performance Evaluation",
                "description": "Generate clinical performance and analytical performance data.",
                "tasks": [
                    "Conduct analytical performance studies (sensitivity, specificity, precision)",
                    "Conduct clinical performance studies with Nigerian patient samples where required",
                    "Generate stability data (real-time and accelerated, tropical conditions)",
                    "Validate with WHO International Standards/Reference Materials where available",
                    "For rapid diagnostic tests: Include field evaluation data",
                    "Compare performance against predicate/established devices"
                ],
                "documents": ["Analytical performance report", "Clinical performance report", "Stability study report"],
                "tips": "NAFDAC may require performance evaluation using samples from the Nigerian population, especially for infectious disease diagnostics."
            },
            {
                "step": 3,
                "title": "Compile Technical Documentation & Submit",
                "description": "Prepare and submit the complete IVD registration dossier.",
                "tasks": [
                    "Prepare IVD technical file per NAFDAC requirements",
                    "Include performance evaluation data",
                    "Prepare labeling compliant with NAFDAC labeling requirements",
                    "Submit through NAFDAC portal with applicable fees",
                    "Provide reference samples/panels for NAFDAC laboratory evaluation",
                    "Respond to any review queries promptly"
                ],
                "documents": [
                    "IVD technical documentation",
                    "Performance evaluation reports",
                    "QMS certificate (ISO 13485)",
                    "Free Sale Certificate",
                    "Labeling samples"
                ],
                "tips": "WHO Prequalified IVDs benefit from NAFDAC's reliance pathway — highlight WHO PQ status in your submission if applicable."
            }
        ],
        "references": [
            "NAFDAC Medical Devices, Including In Vitro Diagnostics and Related Products Regulations, 2025",
            "WHO Prequalification of IVDs",
            "ISO 13485:2016",
            "ISO 20916 (Clinical Performance Studies for IVDs)"
        ]
    },

    "who-gmp-compliance": {
        "id": "who-gmp-compliance",
        "title": "WHO GMP Compliance for Pharmaceutical Manufacturing",
        "subtitle": "Achieve Good Manufacturing Practice compliance for drug production facilities",
        "category": "Manufacturing",
        "jurisdiction": "International (WHO)",
        "estimated_time": "12–24 months",
        "estimated_cost": "Varies significantly by facility size",
        "icon": "🏭",
        "steps": [
            {
                "step": 1,
                "title": "Gap Analysis & Planning",
                "description": "Assess current status against WHO GMP requirements.",
                "tasks": [
                    "Conduct comprehensive gap analysis against WHO Technical Report Series (TRS) requirements",
                    "Assess facility design, HVAC, water systems, and utilities",
                    "Review existing quality management systems",
                    "Evaluate personnel qualifications and training programs",
                    "Develop remediation plan with timelines and budget",
                    "Engage GMP consultants if needed"
                ],
                "documents": ["Gap analysis report", "Remediation plan", "Budget allocation"],
                "tips": "Consider engaging a WHO prequalification-experienced consultant for the gap analysis. The investment upfront saves months of rework later."
            },
            {
                "step": 2,
                "title": "Facility & Equipment Qualification",
                "description": "Ensure manufacturing facility meets GMP requirements.",
                "tasks": [
                    "Qualify facility design (DQ) — layout, material/personnel flow, contamination control",
                    "Qualify HVAC systems (IQ/OQ/PQ) — air handling, pressure differentials, HEPA filtration",
                    "Qualify water systems (Purified Water, Water for Injection)",
                    "Qualify manufacturing equipment (IQ/OQ/PQ)",
                    "Validate cleaning procedures",
                    "Establish environmental monitoring program"
                ],
                "documents": ["Qualification protocols and reports (DQ/IQ/OQ/PQ)", "Environmental monitoring data"],
                "tips": "Qualification must be completed and documented BEFORE starting process validation."
            },
            {
                "step": 3,
                "title": "Quality System Implementation",
                "description": "Implement comprehensive pharmaceutical quality system.",
                "tasks": [
                    "Establish Quality Management System with Quality Policy and Manual",
                    "Implement document control and SOP management",
                    "Set up change control, deviation, and CAPA systems",
                    "Implement batch record and production documentation systems",
                    "Establish quality control laboratory procedures",
                    "Implement supplier qualification and material management",
                    "Set up complaints handling and product recall procedures",
                    "Train all personnel on GMP principles and their specific roles"
                ],
                "documents": ["Quality Manual", "SOPs for all processes", "Training records"],
                "tips": "Documentation is the backbone of GMP. If it's not documented, it didn't happen."
            },
            {
                "step": 4,
                "title": "Process Validation & Ongoing Compliance",
                "description": "Validate manufacturing processes and maintain GMP compliance.",
                "tasks": [
                    "Conduct process validation (minimum 3 consecutive successful batches)",
                    "Validate analytical methods",
                    "Conduct stability studies under appropriate climatic conditions",
                    "Implement annual product quality reviews",
                    "Conduct regular internal audits",
                    "Prepare for regulatory inspections (NAFDAC, WHO)",
                    "Maintain continuous improvement programs"
                ],
                "documents": ["Process validation protocols and reports", "Analytical method validation", "Stability protocols"],
                "tips": "GMP is not a destination — it's a journey. Continuous monitoring and improvement are essential for maintaining compliance."
            }
        ],
        "references": [
            "WHO Technical Report Series No. 986, Annex 2 (GMP for Pharmaceutical Products)",
            "WHO Technical Report Series No. 961, Annex 6 (HVAC)",
            "WHO Technical Report Series No. 970, Annex 2 (Water for Pharmaceutical Use)",
            "PIC/S Guide to GMP for Medicinal Products"
        ]
    }
}


class ChecklistSummary(BaseModel):
    """Summary of a checklist for listing."""
    id: str
    title: str
    subtitle: str
    category: str
    jurisdiction: str
    estimated_time: str
    estimated_cost: str
    icon: str
    total_steps: int


@router.get("/checklists")
async def list_checklists():
    """Get all available compliance checklists."""
    summaries = []
    for key, checklist in CHECKLISTS.items():
        summaries.append(ChecklistSummary(
            id=checklist["id"],
            title=checklist["title"],
            subtitle=checklist["subtitle"],
            category=checklist["category"],
            jurisdiction=checklist["jurisdiction"],
            estimated_time=checklist["estimated_time"],
            estimated_cost=checklist["estimated_cost"],
            icon=checklist["icon"],
            total_steps=len(checklist["steps"]),
        ))
    return {"checklists": [s.model_dump() for s in summaries]}


@router.get("/checklists/{checklist_id}")
async def get_checklist(checklist_id: str):
    """Get a specific compliance checklist with all steps and details."""
    if checklist_id not in CHECKLISTS:
        raise HTTPException(status_code=404, detail="Checklist not found")
    return CHECKLISTS[checklist_id]
