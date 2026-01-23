"""
Knowledge bases for different medical specialties.
Contains domain-specific information for specialist agents.
"""
from typing import Dict, List


class KnowledgeBase:
    """Base class for specialist knowledge bases."""
    
    def __init__(self, specialty: str):
        self.specialty = specialty
        self.key_concepts = []
        self.diagnostic_criteria = {}
        self.treatment_guidelines = {}
    
    def get_context(self) -> str:
        """Get knowledge base context as string."""
        return f"Specialty: {self.specialty}"


class RespiratoryKnowledgeBase(KnowledgeBase):
    """Knowledge base for respiratory medicine."""
    
    def __init__(self):
        super().__init__("Respiratory Medicine")
        self.key_concepts = [
            "Asthma", "COPD", "Pneumonia", "Tuberculosis",
            "Pulmonary Embolism", "Lung Cancer", "Bronchitis",
            "Interstitial Lung Disease", "Sleep Apnea"
        ]
        self.diagnostic_criteria = {
            "asthma": "Reversible airway obstruction, bronchial hyperresponsiveness",
            "copd": "Post-bronchodilator FEV1/FVC < 0.70, persistent symptoms",
            "pneumonia": "Infiltrate on chest X-ray with clinical symptoms"
        }
    
    def get_context(self) -> str:
        """Get respiratory medicine context."""
        context = f"Specialty: {self.specialty}\n"
        context += f"Key Areas: {', '.join(self.key_concepts)}\n"
        context += "Focus: Respiratory system disorders, pulmonary function, lung pathology\n"
        context += "Diagnostic Approach:\n"
        context += "- Evaluate respiratory symptoms: dyspnea, cough, chest pain, hemoptysis\n"
        context += "- Assess pulmonary function: FEV1, FVC, DLCO, arterial blood gases\n"
        context += "- Consider imaging: chest X-ray, CT scan, ventilation-perfusion scan\n"
        context += "- Review diagnostic criteria for asthma, COPD, pneumonia, PE, ILD\n"
        context += "- Consider differential diagnoses: cardiac causes, neurological causes, systemic diseases\n"
        return context


class CardiologyKnowledgeBase(KnowledgeBase):
    """Knowledge base for cardiology."""
    
    def __init__(self):
        super().__init__("Cardiology")
        self.key_concepts = [
            "Myocardial Infarction", "Heart Failure", "Arrhythmias",
            "Hypertension", "Valvular Disease", "Coronary Artery Disease",
            "Pericarditis", "Cardiomyopathy"
        ]
    
    def get_context(self) -> str:
        """Get cardiology context."""
        context = f"Specialty: {self.specialty}\n"
        context += f"Key Areas: {', '.join(self.key_concepts)}\n"
        context += "Focus: Cardiovascular system, cardiac function, heart pathology\n"
        context += "Diagnostic Approach:\n"
        context += "- Evaluate cardiac symptoms: chest pain, dyspnea, palpitations, syncope\n"
        context += "- Assess cardiac function: ECG, echocardiography, cardiac enzymes, BNP\n"
        context += "- Consider imaging: chest X-ray, cardiac MRI, coronary angiography\n"
        context += "- Review diagnostic criteria for MI, heart failure, arrhythmias, valvular disease\n"
        context += "- Consider differential diagnoses: respiratory causes, GI causes, musculoskeletal causes\n"
        return context


class NeurologyKnowledgeBase(KnowledgeBase):
    """Knowledge base for neurology."""
    
    def __init__(self):
        super().__init__("Neurology")
        self.key_concepts = [
            "Stroke", "Epilepsy", "Multiple Sclerosis", "Parkinson's Disease",
            "Alzheimer's Disease", "Migraine", "Neuropathy", "Meningitis"
        ]
    
    def get_context(self) -> str:
        """Get neurology context."""
        context = f"Specialty: {self.specialty}\n"
        context += f"Key Areas: {', '.join(self.key_concepts)}\n"
        context += "Focus: Nervous system disorders, neurological function, CNS/PNS pathology\n"
        context += "Diagnostic Approach:\n"
        context += "- Evaluate neurological symptoms: headache, weakness, numbness, seizures, altered mental status\n"
        context += "- Assess neurological function: mental status exam, cranial nerves, motor, sensory, reflexes\n"
        context += "- Consider imaging: CT head, MRI brain/spine, EEG, EMG\n"
        context += "- Review diagnostic criteria for stroke, epilepsy, MS, Parkinson's, neuropathy\n"
        context += "- Consider differential diagnoses: metabolic causes, infectious causes, systemic diseases\n"
        return context


class GastroenterologyKnowledgeBase(KnowledgeBase):
    """Knowledge base for gastroenterology."""
    
    def __init__(self):
        super().__init__("Gastroenterology")
        self.key_concepts = [
            "IBD", "GERD", "Peptic Ulcer", "Hepatitis", "Cirrhosis",
            "Pancreatitis", "Colorectal Cancer", "IBS"
        ]
    
    def get_context(self) -> str:
        """Get gastroenterology context."""
        context = f"Specialty: {self.specialty}\n"
        context += f"Key Areas: {', '.join(self.key_concepts)}\n"
        context += "Focus: GI tract disorders, digestive system, hepatobiliary pathology\n"
        context += "Diagnostic Approach:\n"
        context += "- Evaluate GI symptoms: abdominal pain, nausea, vomiting, diarrhea, constipation, GI bleeding\n"
        context += "- Assess GI function: liver function tests, pancreatic enzymes, inflammatory markers\n"
        context += "- Consider imaging: abdominal CT, endoscopy, colonoscopy, ERCP\n"
        context += "- Review diagnostic criteria for IBD, GERD, peptic ulcer, hepatitis, cirrhosis, pancreatitis\n"
        context += "- Consider differential diagnoses: cardiac causes, infectious causes, systemic diseases\n"
        return context


class GeneralPractitionerKnowledgeBase(KnowledgeBase):
    """Knowledge base for General Practitioner (GP)."""
    
    def __init__(self):
        super().__init__("General Practice")
        self.key_concepts = [
            "Primary Care", "Differential Diagnosis", "Multi-system Assessment",
            "Common Conditions", "Preventive Medicine", "Chronic Disease Management",
            "Acute Care", "Referral Criteria", "Evidence-Based Medicine"
        ]
        self.diagnostic_criteria = {
            "differential_diagnosis": "Consider multiple systems and causes",
            "red_flags": "Identify serious conditions requiring urgent referral",
            "common_first": "Consider common conditions before rare ones"
        }
    
    def get_context(self) -> str:
        """Get General Practitioner context."""
        context = f"Specialty: {self.specialty}\n"
        context += "Role: Primary care physician with broad medical knowledge across all specialties\n"
        context += "Approach: Consider differential diagnoses across multiple systems\n"
        context += "Focus: Comprehensive assessment, considering respiratory, cardiac, neurological, GI, and other causes\n"
        context += "Key Principle: Think broadly, consider common conditions first, identify red flags for specialist referral"
        return context


KNOWLEDGE_BASES = {
    "respiratory": RespiratoryKnowledgeBase(),
    "cardiology": CardiologyKnowledgeBase(),
    "neurology": NeurologyKnowledgeBase(),
    "gastroenterology": GastroenterologyKnowledgeBase(),
    "general practitioner": GeneralPractitionerKnowledgeBase(),
    "general practice": GeneralPractitionerKnowledgeBase(),
    "gp": GeneralPractitionerKnowledgeBase()
}


def get_knowledge_base(specialty: str) -> KnowledgeBase:
    """Get knowledge base for a specific specialty."""
    specialty_lower = specialty.lower()
    if specialty_lower in KNOWLEDGE_BASES:
        return KNOWLEDGE_BASES[specialty_lower]
    else:
        raise ValueError(f"Unknown specialty: {specialty}")
