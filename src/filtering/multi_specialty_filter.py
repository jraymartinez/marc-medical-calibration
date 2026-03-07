"""
Multi-Specialty Filtering Pipeline
Filters medical question datasets for Respiratory, Cardiology, Neurology, and Gastroenterology questions
using keyword-based matching.

Specialties:
- Respiratory (lung, pulmonary, breathing, etc.)
- Cardiology (cardiac, heart, myocardial, etc.)
- Neurology (neurological, brain, stroke, etc.)
- Gastroenterology (GI, digestive, liver, etc.)

Methodology:
  Keyword-based filtering across all four specialties
  - Diseases, symptoms, diagnostic procedures, anatomical terms
  - Questions matching ANY of the four specialties are included
"""

import json
import re
from typing import Dict, List, Set, Tuple
from pathlib import Path


class MultiSpecialtyFilter:
    """
    Filters medical datasets for Respiratory, Cardiology, Neurology, or Gastroenterology questions.
    """
    
    # Respiratory keywords
    RESPIRATORY_KEYWORDS = {
        # Diseases
        'pneumonia', 'asthma', 'copd', 'bronchitis', 'tuberculosis',
        'emphysema', 'bronchiectasis', 'respiratory failure', 'ards',
        'acute respiratory distress syndrome', 'pulmonary embolism',
        'pulmonary edema', 'pulmonary fibrosis', 'interstitial lung disease',
        'chronic obstructive pulmonary disease', 'cystic fibrosis',
        'bronchiolitis', 'mesothelioma', 'sarcoidosis',
        'respiratory syncytial virus', 'rsv', 'pertussis', 'whooping cough',
        'bacterial pneumonia', 'viral pneumonia',
        
        # Symptoms
        'dyspnea', 'wheeze', 'wheezing', 'hemoptysis', 'stridor', 'tachypnea',
        'hypoxia', 'hypoxemia', 'shortness of breath', 'difficulty breathing',
        'respiratory distress', 'productive cough', 'nonproductive cough',
        'chronic cough', 'persistent cough', 'labored breathing', 'rapid breathing',
        
        # Diagnostic
        'spirometry', 'pulmonary function test', 'pft', 'peak flow', 'fev1', 'fvc',
        'fev1/fvc', 'chest x-ray', 'chest xray', 'chest radiograph',
        'arterial blood gas', 'abg', 'pulse oximetry', 'oxygen saturation', 'spo2',
        'bronchoscopy', 'lung biopsy', 'sputum culture', 'sputum analysis',
        'thoracentesis', 'chest tube', 'ventilation perfusion scan', 'v/q scan',
        'diffusing capacity', 'dlco',
        
        # Anatomical
        'bronchi', 'bronchus', 'bronchial', 'alveoli', 'alveolar',
        'pleura', 'pleural', 'pleural effusion', 'trachea', 'tracheal',
        'bronchioles', 'bronchiolar', 'respiratory tract',
        'upper respiratory tract', 'lower respiratory tract', 'lung', 'pulmonary'
    }
    
    # Cardiology keywords
    CARDIOLOGY_KEYWORDS = {
        # Diseases
        'myocardial infarction', 'MI', 'heart attack', 'angina', 'coronary artery disease',
        'CAD', 'arrhythmia', 'atrial fibrillation', 'AFib', 'atrial flutter',
        'ventricular fibrillation', 'VF', 'ventricular tachycardia', 'VT',
        'bradycardia', 'tachycardia', 'heart failure', 'CHF', 'congestive heart failure',
        'cardiomyopathy', 'dilated cardiomyopathy', 'hypertrophic cardiomyopathy',
        'pericarditis', 'pericardial effusion', 'cardiac tamponade',
        'endocarditis', 'valvular heart disease', 'aortic stenosis', 'mitral regurgitation',
        'tricuspid regurgitation', 'pulmonic stenosis', 'aortic regurgitation',
        'mitral stenosis', 'hypertension', 'HTN', 'hypotension',
        
        # Symptoms
        'chest pain', 'angina', 'palpitations', 'dyspnea on exertion',
        'orthopnea', 'paroxysmal nocturnal dyspnea', 'PND',
        'syncope', 'dizziness', 'fatigue',
        
        # Diagnostic
        'ECG', 'EKG', 'electrocardiogram', 'echocardiogram', 'echo',
        'stress test', 'cardiac catheterization', 'coronary angiography',
        'cardiac MRI', 'cardiac CT', 'Holter monitor', 'event monitor',
        'troponin', 'BNP', 'brain natriuretic peptide', 'CK-MB',
        'cardiac enzymes', 'electrocardiography',
        
        # Procedures
        'CABG', 'coronary artery bypass graft', 'PCI', 'percutaneous coronary intervention',
        'stent', 'angioplasty', 'pacemaker', 'ICD', 'implantable cardioverter defibrillator',
        'cardiac ablation', 'cardioversion',
        
        # Anatomical
        'heart', 'cardiac', 'myocardial', 'coronary', 'atrial', 'ventricular',
        'aortic', 'mitral', 'tricuspid', 'pulmonic', 'pericardium', 'endocardium',
        'myocardium', 'cardiac output', 'ejection fraction', 'stroke volume',
        'blood pressure', 'BP', 'pulse', 'heart rate', 'HR'
    }
    
    # Neurology keywords
    NEUROLOGY_KEYWORDS = {
        # Diseases
        'stroke', 'CVA', 'cerebrovascular accident', 'TIA', 'transient ischemic attack',
        'seizure', 'epilepsy', 'status epilepticus', 'headache', 'migraine',
        'cluster headache', 'tension headache', 'meningitis', 'bacterial meningitis',
        'viral meningitis', 'encephalitis', 'dementia', 'Alzheimer', "Alzheimer's disease",
        'Parkinson', "Parkinson's disease", 'multiple sclerosis', 'MS',
        'amyotrophic lateral sclerosis', 'ALS', 'Guillain-Barré syndrome', 'GBS',
        'myasthenia gravis', 'neuropathy', 'peripheral neuropathy', 'diabetic neuropathy',
        'neuralgia', 'trigeminal neuralgia', 'Bell palsy', 'Bell\'s palsy',
        'facial palsy', 'cerebral palsy',
        
        # Symptoms
        'aphasia', 'dysarthria', 'ataxia', 'tremor', 'rigidity', 'bradykinesia',
        'hemiparesis', 'hemiplegia', 'paraplegia', 'quadriplegia', 'tetraplegia',
        'dysphagia', 'dysphonia', 'diplopia', 'nystagmus', 'vertigo',
        'syncope', 'loss of consciousness', 'LOC', 'altered mental status', 'AMS',
        'confusion', 'delirium', 'coma',
        
        # Diagnostic
        'CT head', 'CT brain', 'MRI brain', 'MRI head', 'EEG', 'electroencephalography',
        'EMG', 'electromyography', 'nerve conduction study', 'NCS',
        'lumbar puncture', 'LP', 'spinal tap', 'CSF', 'cerebrospinal fluid',
        'cerebral angiography', 'carotid ultrasound', 'Doppler',
        
        # Anatomical
        'brain', 'cerebral', 'cerebellar', 'brainstem', 'cerebrum', 'cerebellum',
        'brain stem', 'cranial nerve', 'CN', 'spinal cord', 'myelopathy',
        'radiculopathy', 'meninges', 'dura mater', 'arachnoid', 'pia mater',
        'cortex', 'cortical', 'subcortical', 'white matter', 'gray matter',
        'basal ganglia', 'thalamus', 'hypothalamus', 'brainstem'
    }
    
    # Gastroenterology keywords
    GASTROENTEROLOGY_KEYWORDS = {
        # Diseases
        'gastroesophageal reflux disease', 'GERD', 'peptic ulcer', 'gastric ulcer',
        'duodenal ulcer', 'gastritis', 'inflammatory bowel disease', 'IBD',
        'Crohn disease', "Crohn's disease", 'ulcerative colitis', 'UC',
        'irritable bowel syndrome', 'IBS', 'celiac disease', 'celiac sprue',
        'hepatitis', 'hepatitis A', 'hepatitis B', 'hepatitis C',
        'cirrhosis', 'liver cirrhosis', 'portal hypertension',
        'pancreatitis', 'acute pancreatitis', 'chronic pancreatitis',
        'cholecystitis', 'cholelithiasis', 'gallstones', 'cholangitis',
        'diverticulitis', 'diverticulosis', 'appendicitis',
        'bowel obstruction', 'intestinal obstruction', 'ileus',
        'gastrointestinal bleeding', 'GI bleed', 'upper GI bleed', 'lower GI bleed',
        'esophageal varices', 'Mallory-Weiss tear',
        'colorectal cancer', 'colon cancer', 'gastric cancer', 'esophageal cancer',
        'hepatocellular carcinoma', 'HCC', 'pancreatic cancer',
        'achalasia', 'esophageal dysmotility', 'gastroparesis',
        'lactose intolerance', 'malabsorption', 'short bowel syndrome',
        'hepatic encephalopathy', 'ascites', 'spontaneous bacterial peritonitis', 'SBP',
        
        # Symptoms
        'abdominal pain', 'epigastric pain', 'right upper quadrant pain', 'RUQ pain',
        'left lower quadrant pain', 'LLQ pain', 'right lower quadrant pain', 'RLQ pain',
        'nausea', 'vomiting', 'hematemesis', 'coffee ground emesis',
        'diarrhea', 'constipation', 'hematochezia', 'melena', 'bloody stool',
        'jaundice', 'icterus', 'dyspepsia', 'heartburn', 'regurgitation',
        'dysphagia', 'odynophagia', 'bloating', 'distension', 'abdominal distension',
        'weight loss', 'anorexia', 'early satiety',
        
        # Diagnostic
        'endoscopy', 'upper endoscopy', 'EGD', 'esophagogastroduodenoscopy',
        'colonoscopy', 'sigmoidoscopy', 'ERCP', 'endoscopic retrograde cholangiopancreatography',
        'abdominal ultrasound', 'abdominal CT', 'CT abdomen', 'abdominal MRI',
        'HIDA scan', 'hepatobiliary scan', 'liver function test', 'LFT',
        'AST', 'ALT', 'alkaline phosphatase', 'ALP', 'bilirubin',
        'amylase', 'lipase', 'stool culture', 'fecal occult blood', 'FOBT',
        'H. pylori test', 'Helicobacter pylori', 'liver biopsy',
        
        # Anatomical
        'esophagus', 'esophageal', 'stomach', 'gastric', 'duodenum', 'duodenal',
        'small intestine', 'small bowel', 'jejunum', 'ileum',
        'large intestine', 'colon', 'cecum', 'ascending colon', 'transverse colon',
        'descending colon', 'sigmoid colon', 'rectum', 'anus',
        'liver', 'hepatic', 'gallbladder', 'bile duct', 'biliary',
        'pancreas', 'pancreatic', 'spleen', 'splenic',
        'peritoneum', 'peritoneal', 'mesentery', 'omentum',
        'gastrointestinal', 'GI tract', 'digestive system', 'alimentary canal'
    }
    
    def __init__(self):
        """Initialize the filter with combined keyword sets."""
        self.all_keywords = (
            self.RESPIRATORY_KEYWORDS |
            self.CARDIOLOGY_KEYWORDS |
            self.NEUROLOGY_KEYWORDS |
            self.GASTROENTEROLOGY_KEYWORDS
        )
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for keyword matching."""
        if not text:
            return ""
        return text.lower().strip()
    
    def matches_specialty(self, question_data: Dict) -> Tuple[bool, Set[str], str]:
        """
        Check if question matches any of the four specialties.
        
        Args:
            question_data: Question dictionary
            
        Returns:
            Tuple of (matches, matched_keywords, specialty)
        """
        # Extract question text
        question_text = question_data.get('question', '') or question_data.get('Question', '')
        
        # Extract options
        options = question_data.get('options', {}) or question_data.get('Options', {})
        if not options:
            # MedMCQA format: opa, opb, opc, opd
            options = {}
            for key in ['opa', 'opb', 'opc', 'opd']:
                if key in question_data:
                    options[key.upper().replace('OP', '')] = question_data[key]
        
        # Combine text
        text_lower = self._normalize_text(question_text)
        options_text = ' '.join(str(v).lower() for v in options.values()) if options else ''
        combined_text = text_lower + ' ' + options_text
        
        # Check for keywords
        matched_keywords = set()
        matched_specialties = set()
        
        # Check respiratory
        for keyword in self.RESPIRATORY_KEYWORDS:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, combined_text, re.IGNORECASE):
                matched_keywords.add(keyword)
                matched_specialties.add('respiratory')
        
        # Check cardiology
        for keyword in self.CARDIOLOGY_KEYWORDS:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, combined_text, re.IGNORECASE):
                matched_keywords.add(keyword)
                matched_specialties.add('cardiology')
        
        # Check neurology
        for keyword in self.NEUROLOGY_KEYWORDS:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, combined_text, re.IGNORECASE):
                matched_keywords.add(keyword)
                matched_specialties.add('neurology')
        
        # Check gastroenterology
        for keyword in self.GASTROENTEROLOGY_KEYWORDS:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, combined_text, re.IGNORECASE):
                matched_keywords.add(keyword)
                matched_specialties.add('gastroenterology')
        
        matches = len(matched_specialties) > 0
        specialty = ', '.join(sorted(matched_specialties)) if matched_specialties else 'none'
        
        return matches, matched_keywords, specialty
    
    def filter_question(self, question_data: Dict) -> Tuple[bool, Dict]:
        """
        Filter a single question.
        
        Args:
            question_data: Question dictionary
            
        Returns:
            Tuple of (matches, metadata)
        """
        matches, matched_keywords, specialty = self.matches_specialty(question_data)
        
        metadata = {
            'matched_keywords': list(matched_keywords),
            'specialty': specialty,
            'match_type': 'keywords'
        }
        
        return matches, metadata
    
    def filter_dataset(self, dataset: List[Dict], dataset_name: str = "unknown") -> Tuple[List[Dict], Dict]:
        """
        Filter an entire dataset.
        
        Args:
            dataset: List of question dictionaries
            dataset_name: Name of the dataset
            
        Returns:
            Tuple of (filtered_questions, stats)
        """
        filtered = []
        stats = {
            'total': len(dataset),
            'filtered': 0,
            'by_specialty': {
                'respiratory': 0,
                'cardiology': 0,
                'neurology': 0,
                'gastroenterology': 0,
                'multiple': 0
            }
        }
        
        for q in dataset:
            matches, metadata = self.filter_question(q)
            if matches:
                # Add metadata to question
                q['multi_specialty_metadata'] = metadata
                filtered.append(q)
                stats['filtered'] += 1
                
                # Count by specialty
                specialty = metadata['specialty']
                specialty_count = specialty.count(',') + 1 if specialty != 'none' else 0
                
                if specialty_count > 1:
                    stats['by_specialty']['multiple'] += 1
                elif 'respiratory' in specialty:
                    stats['by_specialty']['respiratory'] += 1
                elif 'cardiology' in specialty:
                    stats['by_specialty']['cardiology'] += 1
                elif 'neurology' in specialty:
                    stats['by_specialty']['neurology'] += 1
                elif 'gastroenterology' in specialty:
                    stats['by_specialty']['gastroenterology'] += 1
        
        return filtered, stats


def load_medqa_jsonl(file_path: Path) -> List[Dict]:
    """Load MedQA JSONL file."""
    questions = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    q = json.loads(line)
                    questions.append(q)
                except json.JSONDecodeError:
                    continue
    return questions


def load_medmcqa_dataset(file_path: Path) -> List[Dict]:
    """Load MedMCQA dataset."""
    from src.filtering.respiratory_filter import load_medmcqa_dataset as load_medmcqa
    return load_medmcqa(str(file_path))


def main():
    """Filter raw datasets for multi-specialty questions."""
    import sys
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    raw_dir = project_root / "data" / "raw"
    output_dir = project_root / "data" / "filtered"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*70)
    print("MULTI-SPECIALTY FILTERING (Respiratory, Cardiology, Neurology, Gastroenterology)")
    print("="*70)
    
    filter_obj = MultiSpecialtyFilter()
    
    all_filtered = []
    all_stats = {}
    
    # Load and filter MedQA datasets
    medqa_dir = raw_dir / "MedQA"
    if medqa_dir.exists():
        print("\nProcessing MedQA datasets...")
        
        # MedQA-US
        us_dir = medqa_dir / "US"
        if us_dir.exists():
            for file_name in ['phrases_no_exclude_dev.jsonl', 'phrases_no_exclude_test.jsonl', 'phrases_no_exclude_train.jsonl']:
                file_path = us_dir / file_name
                if file_path.exists():
                    print(f"  Loading {file_name}...")
                    questions = load_medqa_jsonl(file_path)
                    filtered, stats = filter_obj.filter_dataset(questions, f"MedQA-US-{file_name}")
                    all_filtered.extend(filtered)
                    all_stats[f"MedQA-US-{file_name}"] = stats
                    print(f"    Filtered: {stats['filtered']}/{stats['total']} ({stats['filtered']/stats['total']*100:.1f}%)")
        
        # MedQA-Mainland (EXCLUDED - Chinese language, Llama has difficulty)
        # Skipping Mainland dataset as it contains Chinese questions
        # Llama 3.1 8B struggles with Chinese medical terminology
        print("  Skipping MedQA-Mainland (Chinese - excluded)")
        
        # MedQA-Taiwan (INCLUDED - English language, verified)
        taiwan_dir = medqa_dir / "Taiwan"
        if taiwan_dir.exists():
            for file_name in ['tw_dev.jsonl', 'tw_test.jsonl', 'tw_train.jsonl']:
                file_path = taiwan_dir / file_name
                if file_path.exists():
                    print(f"  Loading {file_name}...")
                    questions = load_medqa_jsonl(file_path)
                    # Filter out any Chinese questions (Taiwan is mixed but mostly English)
                    english_questions = []
                    for q in questions:
                        question_text = q.get('question', '') or q.get('Question', '')
                        # Check if contains Chinese characters
                        has_chinese = any('\u4e00' <= c <= '\u9fff' for c in question_text)
                        if not has_chinese:
                            english_questions.append(q)
                    
                    if len(english_questions) < len(questions):
                        print(f"    Filtered out {len(questions) - len(english_questions)} Chinese questions")
                    
                    filtered, stats = filter_obj.filter_dataset(english_questions, f"MedQA-Taiwan-{file_name}")
                    all_filtered.extend(filtered)
                    all_stats[f"MedQA-Taiwan-{file_name}"] = stats
                    print(f"    Filtered: {stats['filtered']}/{stats['total']} ({stats['filtered']/stats['total']*100:.1f}%)")
    
    # Load and filter MedMCQA
    medmcqa_dir = raw_dir / "MedMCQA"
    if medmcqa_dir.exists():
        print("\nProcessing MedMCQA dataset...")
        for file_name in ['dev.json', 'test.json', 'train.json']:
            file_path = medmcqa_dir / file_name
            if file_path.exists():
                print(f"  Loading {file_name}...")
                questions = load_medmcqa_dataset(file_path)
                filtered, stats = filter_obj.filter_dataset(questions, f"MedMCQA-{file_name}")
                all_filtered.extend(filtered)
                all_stats[f"MedMCQA-{file_name}"] = stats
                print(f"    Filtered: {stats['filtered']}/{stats['total']} ({stats['filtered']/stats['total']*100:.1f}%)")
    
    # Save filtered dataset
    output_file = output_dir / "multi_specialty_cases_all.json"
    
    output_data = {
        'filtered_questions': all_filtered,
        'num_questions': len(all_filtered),
        'filter_stats': all_stats,
        'specialties': ['respiratory', 'cardiology', 'neurology', 'gastroenterology']
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*70)
    print("FILTERING COMPLETE")
    print("="*70)
    print(f"Total filtered: {len(all_filtered)} questions")
    print(f"Saved to: {output_file}")
    
    # Print summary by specialty
    total_by_specialty = {'respiratory': 0, 'cardiology': 0, 'neurology': 0, 'gastroenterology': 0, 'multiple': 0}
    for stats in all_stats.values():
        for specialty, count in stats['by_specialty'].items():
            total_by_specialty[specialty] += count
    
    print("\nBy Specialty:")
    for specialty, count in total_by_specialty.items():
        print(f"  {specialty.capitalize()}: {count}")


if __name__ == '__main__':
    main()
