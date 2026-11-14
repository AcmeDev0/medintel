"""
MedIntel AI — Document Ingestion Pipeline.
Processes regulatory documents (PDFs, text) into the ChromaDB vector store.
Run this module to ingest documents: python -m app.ingest
"""

import os
import sys
from pathlib import Path
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from pypdf import PdfReader

# Ensure utf-8 encoding on Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.config import settings


def load_pdf(file_path: str) -> List[Document]:
    """Load a PDF file and return LangChain Documents with metadata."""
    documents = []
    filename = Path(file_path).name

    try:
        reader = PdfReader(file_path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                documents.append(Document(
                    page_content=text,
                    metadata={
                        "source": filename,
                        "page": i + 1,
                        "total_pages": len(reader.pages),
                        "file_path": str(file_path),
                    }
                ))
    except Exception as e:
        print(f"  ⚠️  Error reading {filename}: {e}")

    return documents


def load_text(file_path: str) -> List[Document]:
    """Load a text/markdown file and return LangChain Documents."""
    filename = Path(file_path).name

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        if content.strip():
            return [Document(
                page_content=content,
                metadata={
                    "source": filename,
                    "page": 1,
                    "file_path": str(file_path),
                }
            )]
    except Exception as e:
        print(f"  ⚠️  Error reading {filename}: {e}")

    return []


def load_all_documents(docs_dir: str) -> List[Document]:
    """Load all supported documents from the documents directory."""
    docs_path = Path(docs_dir)

    if not docs_path.exists():
        print(f"📁 Creating documents directory: {docs_path}")
        docs_path.mkdir(parents=True, exist_ok=True)
        return []

    documents = []
    supported_extensions = {".pdf", ".txt", ".md"}

    for file_path in sorted(docs_path.rglob("*")):
        if file_path.suffix.lower() in supported_extensions:
            print(f"  📄 Loading: {file_path.name}")

            if file_path.suffix.lower() == ".pdf":
                docs = load_pdf(str(file_path))
            else:
                docs = load_text(str(file_path))

            documents.extend(docs)
            print(f"     → {len(docs)} page(s) extracted")

    return documents


def chunk_documents(documents: List[Document]) -> List[Document]:
    """Split documents into chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_documents(documents)
    return chunks


def ingest_to_vectorstore(chunks: List[Document]):
    """Embed chunks and store in ChromaDB."""
    persist_dir = Path(settings.CHROMA_PERSIST_DIR)
    persist_dir.mkdir(parents=True, exist_ok=True)

    embeddings = GoogleGenerativeAIEmbeddings(
        model=f"models/{settings.GEMINI_EMBEDDING_MODEL}",
        google_api_key=settings.GEMINI_API_KEY,
        transport="rest",
    )

    # Create the vector store
    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory=str(persist_dir),
        collection_name=settings.CHROMA_COLLECTION_NAME,
    )
    
    # Add documents in small batches to prevent 504 Deadline Exceeded timeouts
    batch_size = 5
    total_batches = (len(chunks) + batch_size - 1) // batch_size
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        print(f"      - Batch {i//batch_size + 1}/{total_batches}...")
        vectorstore.add_documents(batch)

    return vectorstore


def run_ingestion() -> dict:
    """Run the complete ingestion pipeline and return statistics."""
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_gemini_api_key_here":
        raise ValueError("GEMINI_API_KEY is not configured.")

    docs_path = Path(settings.DOCS_DIR)
    docs_path.mkdir(parents=True, exist_ok=True)

    # Load custom documents from data/documents
    custom_docs = load_all_documents(settings.DOCS_DIR)
    builtin_docs = create_builtin_knowledge_base()
    
    # Combine custom documents with baseline regulatory knowledge base
    all_documents = custom_docs + builtin_docs

    # Chunk all documents
    chunks = chunk_documents(all_documents)

    # Ingest into vector store
    vectorstore = ingest_to_vectorstore(chunks)
    collection = vectorstore._collection
    count = collection.count()

    return {
        "status": "success",
        "custom_documents_found": len(custom_docs),
        "builtin_documents": len(builtin_docs),
        "total_documents": len(all_documents),
        "total_chunks": len(chunks),
        "collection_count": count,
    }


def main():
    """Main ingestion pipeline CLI entrypoint."""
    print("=" * 60)
    print("🧠 MedIntel AI — Document Ingestion Pipeline")
    print("=" * 60)

    # Check API key
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_gemini_api_key_here":
        print("\n❌ ERROR: GEMINI_API_KEY not set!")
        print("   Please set your API key in .env file")
        print("   Get a key at: https://aistudio.google.com/apikey")
        sys.exit(1)

    print(f"\n📂 Loading documents from: {settings.DOCS_DIR}")
    stats = run_ingestion()

    print(f"\n✅ Ingestion complete!")
    print(f"   Custom documents loaded: {stats['custom_documents_found']}")
    print(f"   Built-in knowledge docs: {stats['builtin_documents']}")
    print(f"   Total chunks in vector store: {stats['collection_count']}")
    print(f"   Collection: {settings.CHROMA_COLLECTION_NAME}")
    print("=" * 60)


def create_builtin_knowledge_base() -> List[Document]:
    """
    Create a built-in knowledge base from curated regulatory content.
    This provides baseline knowledge even without external PDF documents.
    """
    documents = []

    # --- NAFDAC Overview ---
    documents.append(Document(
        page_content="""
NAFDAC (National Agency for Food and Drug Administration and Control) is the Nigerian federal agency responsible for regulating and controlling the manufacture, importation, exportation, advertisement, distribution, sale and use of food, drugs, cosmetics, medical devices, chemicals, and packaged water.

NAFDAC was established by Decree 15 of 1993 (now NAFDAC Act Cap N1 Laws of the Federation of Nigeria 2004). The agency operates under the Federal Ministry of Health.

Key regulatory functions of NAFDAC include:
1. Registration of food, drugs, medical devices, cosmetics, and chemicals
2. Regulation of the manufacture and importation of regulated products
3. Establishment and enforcement of quality standards
4. Post-market surveillance and pharmacovigilance
5. Laboratory analysis and testing of products
6. Consumer education and awareness

NAFDAC registration is MANDATORY for all regulated products before they can be manufactured, imported, exported, advertised, sold or distributed in Nigeria. Operating without NAFDAC registration is a criminal offense under Nigerian law.

NAFDAC's regulatory framework is increasingly aligned with international standards and WHO guidelines. In 2025, Nigeria achieved WHO benchmarking for medical device regulation, marking a significant milestone in regulatory maturity.
        """,
        metadata={"source": "MedIntel Built-in Knowledge Base", "page": 1, "section": "NAFDAC Overview"}
    ))

    # --- NAFDAC Drug Registration ---
    documents.append(Document(
        page_content="""
NAFDAC Drug Registration Process - Comprehensive Guide

All pharmaceutical products (prescription drugs, OTC medicines, herbal medicines, biologics) must be registered with NAFDAC before marketing in Nigeria.

TYPES OF DRUG APPLICATIONS:
1. New Drug Application: For novel chemical entities or new formulations not previously registered in Nigeria
2. Generic Drug Application: For products bioequivalent to already-approved reference products
3. Variation Application: For changes to already-registered products (formulation, manufacturer, labeling changes)

DOSSIER FORMAT:
All drug registration dossiers must be submitted in Common Technical Document (CTD) format:
- Module 1: Administrative Information and Prescribing Information
- Module 2: Common Technical Document Summaries
- Module 3: Quality (Chemistry, Manufacturing, and Controls)
- Module 4: Nonclinical Study Reports
- Module 5: Clinical Study Reports

KEY REQUIREMENTS:
1. Certificate of Pharmaceutical Product (CPP) from country of origin
2. GMP Certificate from a recognized regulatory authority
3. Stability data under ICH Zone IVb conditions (30°C/75% RH for long-term studies)
4. Certificate of Analysis from an independent laboratory
5. Bioequivalence study data (for generic products)
6. Drug master file for active pharmaceutical ingredients

REGISTRATION FEES:
Fees vary by product type and application category. Current fee schedules are published in NAFDAC Regulatory Directives. Fees are payable through the NAFDAC payment portal.

REVIEW TIMELINES:
- Standard review: 6-12 months
- Priority review (for essential medicines): 3-6 months
- NAFDAC Reliance pathway (for products approved by trusted authorities): Potentially shortened timelines

COMMON REASONS FOR REJECTION:
1. Incomplete dossier (most common — accounts for majority of initial rejections)
2. Insufficient stability data
3. GMP non-compliance
4. Labeling deficiencies
5. Missing or expired CPP
6. Inadequate bioequivalence data for generics
        """,
        metadata={"source": "MedIntel Built-in Knowledge Base", "page": 2, "section": "Drug Registration"}
    ))

    # --- NAFDAC Medical Device Regulations 2025 ---
    documents.append(Document(
        page_content="""
NAFDAC Medical Devices Regulations 2025 - Key Provisions

The Medical Devices, Including In Vitro Diagnostics and Related Products Regulations, 2025 establishes Nigeria's first comprehensive, dedicated regulatory framework for medical devices. This replaces the previous fragmented approach under general NAFDAC Act mandates.

SCOPE:
The regulations cover:
- Medical devices (all classes)
- In vitro diagnostic medical devices (IVDs)
- Active implantable medical devices
- Software as a Medical Device (SaMD)
- Accessories to medical devices

CLASSIFICATION SYSTEM (Risk-Based, aligned with GHTF/IMDRF):

Class A (Low Risk):
- Non-invasive devices not in contact with injured skin
- Examples: bandages, stethoscopes, hospital beds, wheelchairs, examination gloves
- Regulatory pathway: Declaration of conformity (self-certification)

Class B (Low-Moderate Risk):
- Short-term invasive devices, devices for channeling/storing body fluids
- Examples: hypodermic needles, surgical sutures, hearing aids, dental fillings
- Regulatory pathway: Technical documentation review

Class C (Moderate-High Risk):
- Long-term invasive devices, active therapeutic devices, devices incorporating medicinal substances
- Examples: ventilators, orthopedic pins/plates, dialysis equipment, insulin pumps
- Regulatory pathway: Full technical assessment, may require clinical data

Class D (High Risk):
- Life-sustaining/supporting devices, devices in contact with central nervous system or cardiovascular system
- Examples: heart valves, pacemakers, spinal implants, coronary stents, defibrillators
- Regulatory pathway: Full conformity assessment including clinical investigation data

ESSENTIAL PRINCIPLES:
All medical devices must meet Essential Principles of Safety and Performance (aligned with IMDRF Essential Principles), including:
1. Design for safety and intended performance
2. Chemical, physical, and biological properties acceptable for intended use
3. Infection and microbial contamination prevention
4. Construction and environmental properties
5. Devices with measuring function must be accurate
6. Protection against radiation
7. Software-containing devices must meet IEC 62304

QUALITY MANAGEMENT SYSTEM:
- ISO 13485:2016 certification required for Class B and above manufacturers
- Class A manufacturers must maintain documented quality management procedures

POST-MARKET SURVEILLANCE:
Mandatory for all device classes. Includes:
- Adverse event reporting (within specified timeframes)
- Periodic safety update reports
- Trend reporting
- Field safety corrective actions
        """,
        metadata={"source": "MedIntel Built-in Knowledge Base", "page": 3, "section": "Medical Device Regulations 2025"}
    ))

    # --- NAFDAC SaMD and AI Regulation ---
    documents.append(Document(
        page_content="""
Software as a Medical Device (SaMD) and Artificial Intelligence in Nigerian Regulation

CURRENT STATUS (2025):
Nigeria does not yet have specific, standalone regulations for AI-powered medical devices or Software as a Medical Device (SaMD). However, the Medical Devices Regulations 2025 includes SaMD within its scope, and the following principles apply:

DEFINITION:
Software as a Medical Device is software intended to be used for one or more medical purposes that perform these purposes without being part of a hardware medical device. This includes:
- Diagnostic algorithms
- Clinical decision support systems
- AI-powered imaging analysis
- Patient monitoring software
- Health management applications

SaMD CLASSIFICATION:
SaMD classification should consider:
1. The significance of the information provided by the SaMD to the healthcare decision
2. The state of the healthcare situation or condition
3. IMDRF SaMD Risk Categorization Framework applies

REGULATORY REQUIREMENTS:
1. Software lifecycle management per IEC 62304
2. Risk management per ISO 14971 (with software-specific considerations)
3. Usability engineering per IEC 62366-1
4. Cybersecurity risk assessment
5. Clinical evidence for intended diagnostic/therapeutic claims
6. Documentation of algorithm validation and performance testing
7. For AI/ML: Documentation of training data, algorithm transparency, and performance metrics

GAPS AND CHALLENGES:
- No specific mandatory pre-market AI validation requirements in Nigeria
- No established framework for continuous learning algorithms (locked vs. adaptive AI)
- Post-market surveillance for algorithmic drift not yet standardized
- Limited NAFDAC expertise in AI/ML device evaluation

RECOMMENDATIONS FOR SaMD MANUFACTURERS:
1. Follow IMDRF SaMD guidance documents as a baseline
2. Apply FDA's AI/ML-based SaMD guidance principles
3. Engage NAFDAC in pre-submission consultations
4. Document comprehensive clinical validation
5. Implement robust cybersecurity measures
6. Prepare for evolving regulatory requirements
        """,
        metadata={"source": "MedIntel Built-in Knowledge Base", "page": 4, "section": "SaMD and AI Regulation"}
    ))

    # --- NAFDAC Reliance Guidelines ---
    documents.append(Document(
        page_content="""
NAFDAC Reliance Guidelines 2025

The NAFDAC Reliance Guidelines allow the agency to leverage scientific assessments and regulatory decisions from recognized reference regulatory authorities to streamline the registration process for eligible products.

PURPOSE:
To reduce redundant reviews, accelerate access to quality-assured products, and optimize NAFDAC's regulatory resources.

RECOGNIZED REFERENCE AUTHORITIES:
- US Food and Drug Administration (FDA)
- European Medicines Agency (EMA) / EU Notified Bodies
- WHO Prequalification Programme
- Health Canada
- Therapeutic Goods Administration (TGA), Australia
- Pharmaceuticals and Medical Devices Agency (PMDA), Japan
- Swissmedic
- Other NRAs achieving WHO Global Benchmarking Tool (GBT) maturity level 3 or 4

ELIGIBILITY:
Products eligible for reliance pathway include:
1. Pharmaceutical products approved by a recognized reference authority
2. Medical devices certified by recognized conformity assessment bodies
3. IVDs prequalified by WHO or approved by reference authorities
4. Vaccines prequalified by WHO

PROCESS:
1. Submit standard NAFDAC application
2. Include approval documentation from the reference authority
3. NAFDAC conducts abbreviated review focusing on Nigeria-specific requirements
4. Local labeling, storage conditions for tropical climate, and pricing may still require full review
5. Potentially reduced review timelines compared to full de novo review

LIMITATIONS:
- Reliance is not automatic approval — NAFDAC retains sovereign decision-making authority
- Products must still meet Nigerian-specific labeling requirements
- Local clinical data may still be required for certain product types
- Post-market surveillance obligations remain fully in effect
        """,
        metadata={"source": "MedIntel Built-in Knowledge Base", "page": 5, "section": "Reliance Guidelines"}
    ))

    # --- Pharmaceutical Traceability ---
    documents.append(Document(
        page_content="""
NAFDAC Pharmaceutical Products Traceability Regulations 2024

The Pharmaceutical Products Traceability Regulations mandate the implementation of a comprehensive track-and-trace system for pharmaceutical products in Nigeria to combat substandard and falsified medicines.

KEY REQUIREMENTS:
1. SERIALIZATION: All pharmaceutical products must carry a unique serial number encoded in a GS1-compliant 2D DataMatrix barcode
2. AGGREGATION: Packaging hierarchy must be maintained (unit → bundle → case → pallet)
3. TRANSACTION RECORDS: All supply chain participants must maintain electronic transaction records
4. VERIFICATION: Products must be verifiable at any point in the supply chain

TECHNOLOGY REQUIREMENTS:
- GS1-compliant 2D DataMatrix codes on all product packaging
- Integration with NAFDAC Traceability Information System (TIS)
- Electronic data interchange capabilities
- Compatible serialization software and hardware

NAFDAC DIGITAL TOOLS:
- NAFDAC Traceability Information System (TIS): Central database for product tracking
- Scan2Verify mobile app: Consumer-facing verification tool
- Med Safety app: Adverse event reporting by healthcare workers and patients

COMPLIANCE TIMELINE:
- Phased implementation based on product category and company size
- Check current NAFDAC Regulatory Directives for specific deadlines

PENALTIES FOR NON-COMPLIANCE:
- Product seizure and destruction
- Suspension or revocation of registration
- Criminal prosecution under NAFDAC Act
- Financial penalties
        """,
        metadata={"source": "MedIntel Built-in Knowledge Base", "page": 6, "section": "Traceability Regulations"}
    ))

    # --- ISO Standards Overview ---
    documents.append(Document(
        page_content="""
Key ISO Standards for Medical Device and Pharmaceutical Compliance

ISO 13485:2016 — Quality Management Systems for Medical Devices
- Specifies QMS requirements for organizations involved in medical device lifecycle
- Required by NAFDAC for Class B and above medical device manufacturers
- Covers design control, purchasing, production, service, monitoring
- Must be certified by an accredited certification body
- Renewal audit every 3 years with annual surveillance audits

ISO 14971:2019 — Application of Risk Management to Medical Devices
- Mandatory risk management framework for all medical devices
- Covers: risk analysis, risk evaluation, risk control, residual risk evaluation
- Must be applied throughout the entire product lifecycle
- Risk management file must be maintained and updated
- Key tool for demonstrating safety to regulatory authorities

IEC 62304:2006+A1:2015 — Medical Device Software Lifecycle Processes
- Required for all software-containing medical devices and SaMD
- Defines software development lifecycle activities
- Three safety classes: A (no injury), B (non-serious injury), C (death/serious injury)
- Higher safety class = more rigorous development requirements
- Covers development planning, requirements, design, implementation, testing, maintenance

IEC 62366-1:2015 — Usability Engineering for Medical Devices
- Ensures medical devices are safe and effective when used by intended users
- Requires usability engineering process throughout device development
- Formative evaluations during design, summative evaluation before release
- Critical for devices used by laypersons (home-use devices)

ISO 10993 series — Biological Evaluation of Medical Devices
- Framework for evaluating biocompatibility of medical devices
- ISO 10993-1: Evaluation and testing within a risk management process
- Required for all devices with direct or indirect body contact
- Tests may include cytotoxicity, sensitization, irritation, systemic toxicity
- Extent of testing depends on nature and duration of body contact

IEC 60601-1 — Medical Electrical Equipment Safety
- General requirements for basic safety and essential performance
- Required for all electrically powered medical devices
- Collateral standards cover electromagnetic compatibility (60601-1-2), alarms, usability
- Particular standards exist for specific device types (ventilators, infusion pumps, etc.)
        """,
        metadata={"source": "MedIntel Built-in Knowledge Base", "page": 7, "section": "ISO Standards for Medical Devices"}
    ))

    # --- Clinical Trials in Nigeria ---
    documents.append(Document(
        page_content="""
Clinical Trials and Clinical Investigation in Nigeria

REGULATORY OVERSIGHT:
Clinical trials and clinical investigations in Nigeria are regulated by:
1. NAFDAC — Approval of clinical trial applications
2. National Health Research Ethics Committee (NHREC) — Ethical oversight
3. Institutional Review Boards/Ethics Committees — Site-level ethical review

NAFDAC CLINICAL TRIAL APPROVAL:
1. Submit Clinical Trial Application (CTA) to NAFDAC
2. Provide Investigator's Brochure, protocol, informed consent forms
3. NAFDAC reviews for safety, scientific validity, and regulatory compliance
4. Approval required BEFORE trial can commence
5. NAFDAC may conduct site inspections during and after trials

ETHICS COMMITTEE APPROVAL:
1. All clinical research involving human subjects requires ethics committee approval
2. Protocol must be reviewed by the relevant Institutional Health Research Ethics Committee (IHREC)
3. Informed consent must be obtained from all participants
4. Special protections for vulnerable populations (children, pregnant women, prisoners)
5. Ethics approval must be renewed annually

GOOD CLINICAL PRACTICE (GCP):
All clinical trials must comply with ICH E6(R2) Good Clinical Practice guidelines:
- Ethical conduct and regulatory compliance
- Qualified investigators and adequate resources
- Scientifically sound protocols
- Informed consent and participant protection
- Data integrity and accurate reporting
- Adverse event monitoring and reporting

CLINICAL INVESTIGATION FOR MEDICAL DEVICES:
Under the 2025 Medical Device Regulations, clinical investigation may be required for:
- Class C and D devices without sufficient predicate device data
- Devices with novel technologies or intended purposes
- When clinical performance data from existing literature is insufficient
- Must follow ISO 14155 (Clinical Investigation of Medical Devices)
        """,
        metadata={"source": "MedIntel Built-in Knowledge Base", "page": 8, "section": "Clinical Trials in Nigeria"}
    ))

    # --- WHO Prequalification ---
    documents.append(Document(
        page_content="""
WHO Prequalification Programme

The WHO Prequalification Programme evaluates and lists medicines, vaccines, in vitro diagnostics, and medical devices that meet global standards of quality, safety, and efficacy.

BENEFITS OF WHO PREQUALIFICATION:
1. Access to UN procurement agencies (UNICEF, UNDP, Global Fund)
2. Eligibility for NAFDAC reliance pathway (faster registration in Nigeria)
3. International recognition of product quality
4. Market access across multiple African and developing countries

WHO PREQUALIFICATION FOR MEDICINES:
- Open to generic manufacturers worldwide
- Products must demonstrate bioequivalence to innovator product
- Manufacturing facility must comply with WHO GMP
- Dossier must be in CTD format
- WHO conducts comprehensive quality assessment and site inspection
- Timeline: 12-18 months typically

WHO PREQUALIFICATION FOR IVDs:
- Focus on diagnostics for priority diseases (HIV, TB, malaria, hepatitis)
- Products assessed against WHO Technical Specifications
- Performance evaluation may be required
- Post-qualification surveillance and monitoring

WHO PREQUALIFICATION FOR MEDICAL DEVICES:
- Currently limited to specific device categories (e.g., male circumcision devices, immunization devices)
- Expanding scope based on public health needs
- Assessment includes technical documentation review and quality systems evaluation

NIGERIAN MANUFACTURERS AND WHO PREQUALIFICATION:
- Several Nigerian pharmaceutical manufacturers have achieved WHO prequalification
- NAFDAC actively supports Nigerian manufacturers seeking WHO PQ
- WHO PQ status facilitates exports to other African countries
- Government incentives may be available for companies pursuing WHO PQ
        """,
        metadata={"source": "MedIntel Built-in Knowledge Base", "page": 9, "section": "WHO Prequalification"}
    ))

    # --- FDA Overview for Nigerian Exporters ---
    documents.append(Document(
        page_content="""
US FDA Regulatory Pathways — Guide for Nigerian Manufacturers

For Nigerian medical device and drug manufacturers seeking to export to the United States, understanding FDA requirements is essential.

FDA DRUG APPROVAL PATHWAYS:
1. New Drug Application (NDA) — For novel drugs. Requires full clinical trial data.
2. Abbreviated New Drug Application (ANDA) — For generic drugs. Requires bioequivalence data.
3. 505(b)(2) — For drugs with modifications to approved drugs. May use existing data.

FDA MEDICAL DEVICE PATHWAYS:
1. 510(k) Premarket Notification — For devices substantially equivalent to legally marketed predicates
   - Most common pathway for Class II devices
   - Requires demonstration of substantial equivalence
   - Average review time: 3-6 months
   - Does NOT require clinical trials in most cases

2. Premarket Approval (PMA) — For Class III high-risk devices
   - Most stringent pathway
   - Requires clinical investigation data
   - Scientific review by FDA
   - Average review time: 12-18 months

3. De Novo Classification — For novel low-to-moderate risk devices without a predicate
   - Creates a new regulatory classification
   - Requires demonstration of safety and effectiveness
   - Average review time: 6-12 months

4. Exempt Devices — Low-risk Class I devices exempt from premarket review
   - Still must comply with general controls
   - Must register establishment and list device with FDA

FDA FACILITY REQUIREMENTS:
- All facilities manufacturing for US market must register with FDA
- Subject to FDA inspection (including international sites)
- Must comply with FDA Quality System Regulation (21 CFR 820) — being updated to align with ISO 13485
- Device listing required for all marketed products

KEY DIFFERENCES FROM NAFDAC:
- FDA uses a predicate-based system (510k) vs NAFDAC's classification-based system
- FDA requires establishment registration regardless of device class
- FDA's Unique Device Identification (UDI) system is mandatory
- Post-market reporting requirements differ in scope and timeline
        """,
        metadata={"source": "MedIntel Built-in Knowledge Base", "page": 10, "section": "FDA Pathways for Nigerian Exporters"}
    ))

    print(f"   📝 Created {len(documents)} built-in knowledge documents")
    return documents


if __name__ == "__main__":
    main()
