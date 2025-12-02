"""
Explanation Tools - Functions for generating explanations in different styles.
"""
from google.adk.tools import FunctionTool
from typing import Dict, Any, Optional
import json


def generate_explanation(
    rag_results: Dict[str, Any],
    explanation_style: str = "with example",
    question: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generates an explanation based on RAG results in the specified style.
    
    Args:
        rag_results: Dictionary containing RAG search results from the corpus
        explanation_style: Style of explanation. Options:
            - "with example" or "example": Explain with practical examples
            - "with memory technique" or "memory technique": Use mnemonic devices
            - "using story" or "story": Explain through narrative
            - "in [language]" or specific language name: Explain in native/user language
        question: The original question (optional, for context)
    
    Returns:
        A dictionary containing the explanation in the requested style
    """
    try:
        # Extract relevant information from RAG results
        results = rag_results.get("results", [])
        if not results:
            return {
                "status": "error",
                "message": "No RAG results available to generate explanation",
                "error": "Empty results"
            }
        
        # Combine all result texts
        context_text = "\n\n".join([
            result.get("text", "") for result in results
        ])
        
        # Determine explanation style
        style_lower = explanation_style.lower().strip()
        
        if "example" in style_lower:
            style_instruction = "Explain with clear, practical examples. Use real-world scenarios and step-by-step examples."
        elif "memory" in style_lower or "mnemonic" in style_lower:
            style_instruction = "Explain using memory techniques, mnemonic devices, acronyms, or memory aids. Create memorable associations."
        elif "story" in style_lower or "narrative" in style_lower:
            style_instruction = "Explain using an engaging story or narrative. Use characters and scenarios to illustrate the concept."
        elif "language" in style_lower or any(word in style_lower for word in ["hindi", "tamil", "telugu", "bengali", "marathi", "gujarati", "kannada", "malayalam", "odia", "punjabi", "urdu"]):
            # Extract language if specified
            language = explanation_style
            if "in " in style_lower:
                language = style_lower.split("in ")[-1].strip()
            style_instruction = f"Explain in {language} language. Use culturally appropriate examples and natural language flow."
        else:
            # Default to example
            style_instruction = "Explain with clear, practical examples. Use real-world scenarios and step-by-step examples."
        
        # Format the explanation request
        explanation_prompt = f"""
        Based on the following educational content, provide an explanation {style_instruction}
        
        Question: {question or "General explanation"}
        
        Content from textbook:
        {context_text}
        
        Please provide a comprehensive explanation that:
        1. Is accurate and based on the provided content
        2. Follows the requested explanation style
        3. Is appropriate for the student's grade level
        4. Is clear, engaging, and educational
        """
        
        return {
            "status": "success",
            "explanation_style": explanation_style,
            "explanation_prompt": explanation_prompt,
            "rag_context": context_text,
            "results_count": len(results),
            "message": f"Explanation ready to be generated in '{explanation_style}' style"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
            "message": f"Failed to generate explanation: {str(e)}"
        }


# Create FunctionTool from the function
generate_explanation_tool = FunctionTool(generate_explanation)

