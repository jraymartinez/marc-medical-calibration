"""
Local LLM Client for Medical Diagnosis
Uses HuggingFace Transformers for local inference
No LangChain - direct and transparent implementation
"""

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig
)
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class LocalLLMClient:
    """
    Local Large Language Model Client
    
    Supports local inference with HuggingFace models
    Optimized for medical diagnosis tasks with 4-bit quantization
    
    Example:
        >>> llm = LocalLLMClient("meta-llama/Llama-3.1-8B-Instruct", use_4bit=True)
        >>> response = llm.generate("You are a doctor", "Diagnose pneumonia")
        >>> probs = llm.get_token_probabilities("System prompt", "Question?", ["A", "B", "C"])
    """
    
    def __init__(
        self,
        model_name: str = "meta-llama/Llama-3.1-8B-Instruct",
        use_4bit: bool = True,
        device: str = "cuda",
        max_memory: Optional[Dict[int, str]] = None,
        hf_token: Optional[str] = None
    ):
        """
        Initialize Local LLM Client
        
        Args:
            model_name: HuggingFace model identifier
                Options: "meta-llama/Llama-3.1-8B-Instruct",
                        "meta-llama/Llama-3.1-70B-Instruct",
                        "mistralai/Mistral-7B-Instruct-v0.3"
            use_4bit: Enable 4-bit quantization (saves VRAM)
            device: 'cuda' or 'cpu'
            max_memory: Custom memory allocation per GPU
            hf_token: HuggingFace access token (required for gated models like Llama)
        """
        self.model_name = model_name
        self.device = device
        self.use_4bit = use_4bit
        
        # Get HuggingFace token from parameter or environment
        import os
        self.hf_token = hf_token or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
        
        if not self.hf_token and "llama" in model_name.lower():
            logger.warning(
                "⚠️  Llama models require HuggingFace authentication!\n"
                "Please set HF_TOKEN environment variable or pass hf_token parameter.\n"
                "See: https://huggingface.co/docs/hub/security-tokens"
            )
        
        logger.info(f"Loading {model_name}...")
        
        # Configure quantization for memory efficiency
        # Only use quantization if CUDA is available and 4bit is requested
        if use_4bit and device == "cuda" and torch.cuda.is_available():
            try:
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True,
                )
            except Exception as e:
                logger.warning(f"4-bit quantization not available: {e}. Using full precision.")
                quantization_config = None
                use_4bit = False
        else:
            quantization_config = None
            if use_4bit and device == "cpu":
                logger.warning("4-bit quantization not supported on CPU. Using full precision.")
                use_4bit = False
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
            padding_side='left',  # Important for batch generation
            token=self.hf_token  # Add authentication token
        )
        
        # Set pad token if not exists
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model
        try:
            # Set device_map based on device selection
            if device == "cpu":
                device_map = None
                torch_dtype = torch.float32
                logger.info("Loading model on CPU (this may take a few minutes)...")
            elif torch.cuda.is_available():
                device_map = "auto"
                torch_dtype = torch.float16
            else:
                device_map = None
                torch_dtype = torch.float32
                logger.warning("CUDA not available, falling back to CPU")
            
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                quantization_config=quantization_config,
                device_map=device_map,
                torch_dtype=torch_dtype,
                trust_remote_code=True,
                max_memory=max_memory,
                token=self.hf_token,  # Add authentication token
                low_cpu_mem_usage=True  # Optimize CPU memory usage
            )
            
            # Move to CPU explicitly if needed
            if device == "cpu" and device_map is None:
                self.model = self.model.to("cpu")
            
            print("Setting model to evaluation mode...")
            logger.info("Setting model to evaluation mode...")
            try:
                self.model.eval()  # Set to evaluation mode
                print("OK Model set to eval mode")
                logger.info("✓ Model set to eval mode")
            except Exception as e:
                print(f"ERROR setting eval mode: {e}")
                logger.error(f"Failed to set eval mode: {e}")
                raise
            
            # Log GPU memory usage
            print("Checking GPU memory...")
            if torch.cuda.is_available():
                memory_allocated = torch.cuda.memory_allocated() / 1024**3
                print(f"OK Model loaded on {device} - VRAM: {memory_allocated:.2f} GB")
                logger.info(f"✓ Model loaded on {device}")
                logger.info(f"✓ VRAM usage: {memory_allocated:.2f} GB")
            else:
                print("OK Model loaded on CPU")
                logger.info(f"✓ Model loaded on CPU")
                
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        do_sample: bool = True,
        return_full_text: bool = False
    ) -> str:
        """
        Generate text response from LLM
        
        Args:
            system_prompt: System instruction (e.g., specialist role)
            user_prompt: User query (e.g., patient case)
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = random)
            top_p: Nucleus sampling parameter
            do_sample: Use sampling (True) or greedy decoding (False)
            return_full_text: Return full text including prompt
        
        Returns:
            Generated text response
            
        Example:
            >>> response = llm.generate(
            ...     "You are a pulmonologist",
            ...     "Patient has fever and cough. Diagnose."
            ... )
        """
        # Format conversation using chat template
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Apply chat template
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        # Tokenize
        inputs = self.tokenizer(
            formatted_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=4096,
            padding=True
        )
        
        # Move to device
        if torch.cuda.is_available():
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generate
        try:
            with torch.no_grad():
                # Only pass sampling parameters if do_sample=True
                generate_kwargs = {
                    **inputs,
                    'max_new_tokens': max_new_tokens,
                    'do_sample': do_sample,
                    'pad_token_id': self.tokenizer.pad_token_id,
                    'eos_token_id': self.tokenizer.eos_token_id
                }
                
                # Only add sampling parameters if using sampling
                if do_sample:
                    generate_kwargs['temperature'] = temperature
                    generate_kwargs['top_p'] = top_p
                
                outputs = self.model.generate(**generate_kwargs)
            
            # Decode
            if return_full_text:
                generated_text = self.tokenizer.decode(
                    outputs[0],
                    skip_special_tokens=True
                )
            else:
                # Decode only the new tokens (exclude input)
                generated_text = self.tokenizer.decode(
                    outputs[0][inputs['input_ids'].shape[1]:],
                    skip_special_tokens=True
                )
            
            return generated_text.strip()
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
    
    def get_token_probabilities(
        self,
        system_prompt: str,
        user_prompt: str,
        candidate_tokens: List[str]
    ) -> Dict[str, float]:
        """
        Get probability distribution over candidate tokens
        
        Used for Multiple Choice Question Answering (MCQA)
        Following Wang et al. 2024 approach
        
        Args:
            system_prompt: System instruction
            user_prompt: User query with multiple choice options
            candidate_tokens: List of option tokens (e.g., ["A", "B", "C", "D"])
        
        Returns:
            Dictionary mapping tokens to probabilities (normalized to sum to 1.0)
            
        Example:
            >>> probs = llm.get_token_probabilities(
            ...     "You are a doctor",
            ...     "Patient has fever. Diagnosis?\nA. Flu\nB. COVID\nC. Cold",
            ...     ["A", "B", "C"]
            ... )
            >>> # Returns: {"A": 0.6, "B": 0.3, "C": 0.1}
        """
        # Format conversation
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        # Tokenize
        inputs = self.tokenizer(
            formatted_prompt,
            return_tensors="pt"
        )
        
        if torch.cuda.is_available():
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Get logits for next token
        try:
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits[0, -1, :]  # Logits for last token position
            
            # Get token IDs for candidates
            candidate_token_ids = []
            for token in candidate_tokens:
                # Encode token (handle multi-token cases)
                encoded = self.tokenizer.encode(token, add_special_tokens=False)
                if len(encoded) > 0:
                    candidate_token_ids.append(encoded[0])
                else:
                    logger.warning(f"Token '{token}' could not be encoded")
                    candidate_token_ids.append(0)  # Fallback
            
            # Extract logits for candidate tokens
            candidate_logits = logits[candidate_token_ids]
            
            # Convert to probabilities (softmax)
            probs_tensor = torch.softmax(candidate_logits, dim=0)
            
            # Create probability dictionary
            probs = {
                token: prob.item()
                for token, prob in zip(candidate_tokens, probs_tensor)
            }
            
            # Normalize (should already sum to 1, but ensure it)
            total = sum(probs.values())
            if total > 0:
                probs = {k: v/total for k, v in probs.items()}
            
            return probs
            
        except Exception as e:
            logger.error(f"Probability extraction failed: {e}")
            # Return uniform distribution as fallback
            n = len(candidate_tokens)
            return {token: 1.0/n for token in candidate_tokens}
    
    def get_model_info(self) -> Dict[str, any]:
        """
        Get information about loaded model
        
        Returns:
            Dictionary with model information
        """
        info = {
            'model_name': self.model_name,
            'device': self.device,
            'quantization': '4-bit' if self.use_4bit else 'full-precision',
            'vocab_size': len(self.tokenizer),
            'max_length': self.tokenizer.model_max_length
        }
        
        if torch.cuda.is_available():
            info['gpu_memory_allocated'] = f"{torch.cuda.memory_allocated() / 1024**3:.2f} GB"
            info['gpu_memory_reserved'] = f"{torch.cuda.memory_reserved() / 1024**3:.2f} GB"
        
        return info
    
    def __repr__(self) -> str:
        return f"LocalLLMClient(model='{self.model_name}', device='{self.device}')"


# Convenience function for backward compatibility
def get_llm_client(
    model_name: str = "meta-llama/Llama-3.1-8B-Instruct",
    use_4bit: bool = True,
    device: str = "cuda",
    hf_token: Optional[str] = None
) -> LocalLLMClient:
    """
    Factory function to create LLM client.
    
    Args:
        model_name: HuggingFace model identifier
        use_4bit: Enable 4-bit quantization
        device: Device to load model on
        hf_token: HuggingFace access token (required for gated models)
        
    Returns:
        LocalLLMClient instance
    """
    return LocalLLMClient(model_name=model_name, use_4bit=use_4bit, device=device, hf_token=hf_token)
