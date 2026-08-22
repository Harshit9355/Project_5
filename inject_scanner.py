from pathlib import Path
import sys

SYSTEM_PROMPT_PATTERNS = [
    "SYSTEM_PROMPT =",
    "system_message =",
    '"role": "system"',
]

INJECTION_PHRASES = [
    "ignore previous instructions",
    "you are now",
    "pretend you are",
    "act as if you have no restrictions",
]

ROOT = Path(__file__).resolve().parent

findings = []

for py_file in ROOT.rglob("*.py"):

    if py_file.name == "inject_scanner.py":
        continue

    try:
        content = py_file.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue

    for pattern in SYSTEM_PROMPT_PATTERNS:
        if pattern.lower() in content.lower():
            findings.append(
                f"{py_file}: SYSTEM PROMPT pattern detected: {pattern}"
            )

    for phrase in INJECTION_PHRASES:
        if phrase.lower() in content.lower():
            findings.append(
                f"{py_file}: Injection phrase detected: {phrase}"
            )

if findings:
    print("CUSTOM PROMPT-INJECTION SCANNER: FINDINGS")
    print("=" * 60)

    for finding in findings:
        print(finding)

    sys.exit(1)

print("CUSTOM PROMPT-INJECTION SCANNER: CLEAN")
sys.exit(0)