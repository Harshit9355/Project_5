import base64
import re

MAX_LENGTH = 500

INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.I),
    re.compile(r"you\s+are\s+now", re.I),
    re.compile(r"pretend\s+you\s+are", re.I),
    re.compile(r"act\s+as\s+if\s+you\s+have\s+no", re.I),
]

CREDENTIAL_PATTERNS = [
    re.compile(r"password\s*=", re.I),
    re.compile(r"api[_-]?key\s*=", re.I),
    re.compile(r"token\s*=", re.I),
]

URL_PATTERN = re.compile(r"https?://\S+", re.I)

SYSTEM_PROMPT_MARKERS = (
    "system prompt",
    "system instructions",
    "internal configuration",
)


def validate_input(value):
    # Layer 1: input length limit
    if len(value) > MAX_LENGTH:
        return False, f"Input exceeds the {MAX_LENGTH}-character limit."

    # Layer 2: direct prompt-injection detection
    for pattern in INJECTION_PATTERNS:
        if pattern.search(value):
            return False, "Prompt-injection phrase detected."

    # Layer 3: encoded/Base64 payload detection
    base64_candidates = re.findall(
        r"(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{20,}={0,2}(?![A-Za-z0-9+/])",
        value,
    )

    for candidate in base64_candidates:
        if len(candidate) % 4 != 0:
            continue

        try:
            decoded = base64.b64decode(
                candidate,
                validate=True
            ).decode("utf-8", errors="ignore")
        except (ValueError, UnicodeDecodeError):
            decoded = ""

        if decoded:
            return False, "Encoded payload detected."

    return True, "Input accepted."


def scan_output(value):
    lowered = value.lower()

    # Block system-prompt disclosure
    if any(marker in lowered for marker in SYSTEM_PROMPT_MARKERS):
        return False, "System-prompt content detected."

    # Block credential-like output
    for pattern in CREDENTIAL_PATTERNS:
        if pattern.search(value):
            return False, "Credential-pattern content detected."

    # Block unsolicited external URLs
    if URL_PATTERN.search(value):
        return False, "Unsolicited external URL detected."

    return True, "Output accepted."
