import subprocess
import re

VERSION_PATTERN = r'\b(v?\d+(?:\.\d+){1,})\b'
VSC_EXTENSION_PATTERN = r'\b([a-z0-9]+(?:\.[a-z0-9]+){1,})\b'

def extract_words_by_pattern(string: str, pattern: str) -> str:
    """Extract a word that matches a given pattern from the PowerShell output."""
    matches = re.findall(pattern, string)
    if not matches:
        raise ValueError("No matches found")
    return matches

