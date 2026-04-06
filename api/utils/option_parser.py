import re

def normalize_option(message: str) -> str:
    """
    Robustly identifies if the user is selecting an option (A, B, or C).
    Standardizes the input to 'option a', 'option b', or 'option c' 
    to prevent translation logic from breaking intent detection.
    """
    if not message:
        return message
        
    msg = message.lower().strip()
    
    # Define regex patterns for A, B, and C
    patterns = {
        "option a": [r"\boption\s*a\b", r"^a$", r"^a\.$", r"\bchoose\s*a\b", r"\bselect\s*a\b"],
        "option b": [r"\boption\s*b\b", r"^b$", r"^b\.$", r"\bchoose\s*b\b", r"\bselect\s*b\b"],
        "option c": [r"\boption\s*c\b", r"^c$", r"^c\.$", r"\bchoose\s*c\b", r"\bselect\s*c\b"],
    }
    
    for canonical_option, regex_list in patterns.items():
        for pattern in regex_list:
            if re.search(pattern, msg):
                return canonical_option
                
    return message
