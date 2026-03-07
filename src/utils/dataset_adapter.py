"""
Dataset adapter for normalizing different medical QA datasets to a common format.

Supports:
- MedQA-USMLE
- MedMCQA
"""

from typing import Dict, Any, List


def normalize_medqa_question(question: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize MedQA question to standard format.
    
    MedQA format:
    {
        "question": str,
        "answer": str,  # Full text answer
        "options": {"A": str, "B": str, "C": str, "D": str},
        "answer_idx": str,  # "A", "B", "C", or "D"
        "meta_info": str,  # "step1" or "step2&3"
        ...
    }
    
    Returns normalized format with all required fields.
    """
    # MedQA is already in standard format, just ensure all fields exist
    normalized = {
        'question': question.get('question', ''),
        'answer': question.get('answer', ''),
        'options': question.get('options', {}),
        'answer_idx': question.get('answer_idx', ''),
        'meta_info': question.get('meta_info', ''),
        'source': 'medqa'
    }
    
    # Preserve other fields
    for key, value in question.items():
        if key not in normalized:
            normalized[key] = value
    
    return normalized


def normalize_medmcqa_question(question: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize MedMCQA question to standard format.
    
    MedMCQA format:
    {
        "question": str,
        "opa": str,  # Option A
        "opb": str,  # Option B
        "opc": str,  # Option C
        "opd": str,  # Option D
        "ope": str,  # Option E (optional, rare)
        "cop": int,  # Correct option: 1=A, 2=B, 3=C, 4=D, 5=E
        "exp": str,  # Explanation
        "subject_name": str,
        "topic_name": str,
        "id": str,
        "choice_type": str  # "single" or "multiple"
    }
    
    Returns normalized format matching MedQA structure.
    """
    # Build options dict
    options = {}
    option_map = {
        'opa': 'A',
        'opb': 'B',
        'opc': 'C',
        'opd': 'D',
        'ope': 'E'  # Rare, but handle if present
    }
    
    for op_key, letter in option_map.items():
        if op_key in question and question[op_key]:
            options[letter] = question[op_key]
    
    # Convert cop (1/2/3/4/5) to answer_idx (A/B/C/D/E)
    cop = question.get('cop', 1)
    cop_to_letter = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
    answer_idx = cop_to_letter.get(cop, 'A')
    
    # Get answer text from options
    answer = options.get(answer_idx, '')
    
    # Create normalized format
    normalized = {
        'question': question.get('question', ''),
        'answer': answer,
        'options': options,
        'answer_idx': answer_idx,
        'meta_info': question.get('subject_name', ''),  # Use subject_name as meta_info
        'source': 'medmcqa',
        # Preserve MedMCQA-specific fields
        'subject_name': question.get('subject_name', ''),
        'topic_name': question.get('topic_name', ''),
        'explanation': question.get('exp', ''),
        'choice_type': question.get('choice_type', 'single'),
        'id': question.get('id', '')
    }
    
    # Preserve any other fields
    for key, value in question.items():
        if key not in normalized and key not in ['opa', 'opb', 'opc', 'opd', 'ope', 'cop', 'exp']:
            normalized[key] = value
    
    return normalized


def normalize_question(question: Dict[str, Any], dataset_type: str = 'auto') -> Dict[str, Any]:
    """
    Normalize a question from any supported dataset to standard format.
    
    Args:
        question: Raw question dict
        dataset_type: 'medqa', 'medmcqa', or 'auto' (auto-detect)
    
    Returns:
        Normalized question dict with standard fields
    """
    # Auto-detect dataset type if not specified
    if dataset_type == 'auto':
        if 'opa' in question and 'cop' in question:
            dataset_type = 'medmcqa'
        elif 'options' in question and 'answer' in question:
            dataset_type = 'medqa'
        else:
            # Default to medqa format
            dataset_type = 'medqa'
    
    # Normalize based on dataset type
    if dataset_type == 'medmcqa':
        return normalize_medmcqa_question(question)
    else:
        return normalize_medqa_question(question)


def load_and_normalize_dataset(file_path: str, dataset_type: str = 'auto') -> List[Dict[str, Any]]:
    """
    Load and normalize a dataset file.
    
    Args:
        file_path: Path to dataset file (JSON or JSONL)
        dataset_type: 'medqa', 'medmcqa', or 'auto'
    
    Returns:
        List of normalized questions
    """
    import json
    from pathlib import Path
    
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {file_path}")
    
    questions = []
    
    # Try to load as JSON first
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                questions = data
            elif isinstance(data, dict):
                # Try common keys
                for key in ['filtered_questions', 'questions', 'data']:
                    if key in data:
                        questions = data[key]
                        break
                if not questions:
                    # Single question wrapped in dict
                    questions = [data]
    except json.JSONDecodeError:
        # Try JSONL format (one JSON per line)
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        questions.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    
    # Normalize all questions
    normalized = [normalize_question(q, dataset_type) for q in questions]
    
    return normalized


# Example usage and testing
if __name__ == '__main__':
    # Test MedQA normalization
    medqa_sample = {
        'question': 'What is the diagnosis?',
        'answer': 'Pneumonia',
        'options': {'A': 'Pneumonia', 'B': 'Asthma', 'C': 'COPD', 'D': 'Bronchitis'},
        'answer_idx': 'A',
        'meta_info': 'step1'
    }
    
    print("MedQA normalization:")
    print(normalize_medqa_question(medqa_sample))
    
    # Test MedMCQA normalization
    medmcqa_sample = {
        'question': 'What is the diagnosis?',
        'opa': 'Pneumonia',
        'opb': 'Asthma',
        'opc': 'COPD',
        'opd': 'Bronchitis',
        'cop': 1,
        'exp': 'Explanation here',
        'subject_name': 'Respiratory',
        'topic_name': 'Infections',
        'id': '12345',
        'choice_type': 'single'
    }
    
    print("\nMedMCQA normalization:")
    print(normalize_medmcqa_question(medmcqa_sample))
    
    # Test auto-detection
    print("\nAuto-detection:")
    print("MedQA:", normalize_question(medqa_sample, 'auto')['source'])
    print("MedMCQA:", normalize_question(medmcqa_sample, 'auto')['source'])
