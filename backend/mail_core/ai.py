import json
import logging
import os
import re
import urllib.error
import urllib.request
from typing import Dict, List, Optional, Tuple


logger = logging.getLogger(__name__)

ALLOWED_TONES = {'formal', 'casual', 'friendly', 'neutral'}
ALLOWED_ACTIONS = {'send', 'remind', 'draft'}


def _extract_first_json_block(text: str) -> Optional[dict]:
    if not text:
        return None

    text = text.strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    match = re.search(r'\{.*?\}', text, flags=re.DOTALL)
    if not match:
        return None

    try:
        parsed = json.loads(match.group(0))
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        return None

    return None


def _split_possible_commands(command_text: str) -> List[str]:
    if not command_text:
        return []
    parts = re.split(r'\s*(?:\band then\b|\bthen\b|;|\.|\n)\s*', command_text, flags=re.IGNORECASE)
    commands = [p.strip() for p in parts if p and p.strip()]
    return commands[:5]


def _heuristic_language(text: str) -> str:
    lowered = (text or '').lower()
    if not lowered.strip():
        return 'unknown'

    has_devanagari = any('\u0900' <= ch <= '\u097f' for ch in lowered)
    has_english = any('a' <= ch <= 'z' for ch in lowered)
    hinglish_tokens = ['hai', 'nahi', 'kya', 'ko', 'bhejo', 'yaar', 'kal', 'aaj', 'bhai']
    token_hits = sum(1 for token in hinglish_tokens if token in lowered)

    if has_devanagari and has_english:
        return 'hinglish'
    if has_devanagari:
        return 'hindi'
    if token_hits >= 2 and has_english:
        return 'hinglish'
    return 'english'


def _heuristic_fallback(command_text: str, ai_error: str) -> Dict:
    text = (command_text or '').lower()

    if 'birthday' in text or 'wish' in text or 'bday' in text:
        intent = 'birthday_wish'
        occasion = 'birthday'
    elif 'apology' in text or 'sorry' in text:
        intent = 'apology'
        occasion = 'apology'
    elif 'remind' in text or 'meeting' in text:
        intent = 'reminder'
        occasion = 'meeting'
    else:
        intent = 'general'
        occasion = ''

    if any(token in text for token in ['formal', 'sir', 'madam', 'boss']):
        tone = 'formal'
    elif any(token in text for token in ['friend', 'bro', 'yaar', 'bhai']):
        tone = 'friendly'
    else:
        tone = 'neutral'

    recipient_match = re.search(r'(?:to|for|ko)\s+([A-Za-z\u0900-\u097f\s]{2,40})', command_text or '', flags=re.IGNORECASE)
    recipient_name = recipient_match.group(1).strip() if recipient_match else ''

    return {
        'intent': intent,
        'tone': tone,
        'occasion': occasion,
        'recipient_name': recipient_name,
        'action': 'draft',
        'schedule_time': '',
        'language': _heuristic_language(command_text),
        'commands': _split_possible_commands(command_text),
        'ai_used': False,
        'confidence': 0.45,
        'ai_raw_output': '',
        'ai_error': ai_error or 'fallback_used',
    }


def _normalize_infer_payload(parsed: dict, command_text: str, raw_text: str) -> Optional[dict]:
    if not isinstance(parsed, dict):
        return None

    intent = str(parsed.get('intent', '')).strip() or 'general'
    tone = str(parsed.get('tone', 'neutral')).strip().lower()
    if tone not in ALLOWED_TONES:
        tone = 'neutral'

    action = str(parsed.get('action', 'draft')).strip().lower()
    if action not in ALLOWED_ACTIONS:
        action = 'draft'

    commands = parsed.get('commands')
    if isinstance(commands, list):
        cleaned_commands = [str(c).strip() for c in commands if str(c).strip()]
    else:
        cleaned_commands = _split_possible_commands(command_text)

    confidence = parsed.get('confidence')
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.85
    confidence = max(0.0, min(1.0, confidence))

    return {
        'intent': intent,
        'tone': tone,
        'occasion': str(parsed.get('occasion', '')).strip(),
        'recipient_name': str(parsed.get('recipient_name', '')).strip(),
        'action': action,
        'schedule_time': str(parsed.get('schedule_time', '')).strip(),
        'language': str(parsed.get('language', '')).strip() or _heuristic_language(command_text),
        'commands': cleaned_commands,
        'ai_used': True,
        'confidence': confidence,
        'ai_raw_output': raw_text,
        'ai_error': '',
    }


def _normalize_generate_payload(parsed: dict, raw_text: str) -> Optional[dict]:
    if not isinstance(parsed, dict):
        return None
    subject = str(parsed.get('subject', '')).strip()
    body = str(parsed.get('body', '')).strip()
    if not subject or not body:
        return None
    return {
        'subject': subject,
        'body': body,
        'ai_used': True,
        'ai_raw_output': raw_text,
        'ai_error': '',
    }


def _ollama_generate(prompt: str) -> Tuple[Dict, str]:
    base_url = os.getenv('OLLAMA_BASE_URL', 'http://127.0.0.1:11434').rstrip('/')
    model = os.getenv('OLLAMA_MODEL', 'mistral')
    timeout = int(os.getenv('OLLAMA_TIMEOUT_SECONDS', '20'))

    payload = {
        'model': model,
        'prompt': prompt,
        'stream': False,
        'format': 'json',
        'options': {'temperature': 0.2},
    }

    req = urllib.request.Request(
        f'{base_url}/api/generate',
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )

    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw_body = resp.read().decode('utf-8')

    outer = json.loads(raw_body)
    response_text = outer.get('response', '')
    parsed_json = _extract_first_json_block(response_text) or {}
    return parsed_json, response_text


def infer_command(command_text: str) -> Dict:
    prompt = f"""
You are an assistant that extracts structured intent from a mail instruction.
The user may write English, Hindi, or Hinglish and may include multiple commands.
Return ONLY valid JSON with keys:
- intent (string)
- tone (formal/casual/friendly/neutral)
- occasion (string)
- recipient_name (string)
- action (send/remind/draft)
- schedule_time (string; keep empty if not present)
- language (english/hindi/hinglish/unknown)
- commands (array of command strings)
- confidence (number from 0 to 1)

Instruction: {command_text}
""".strip()

    max_retries = 3
    last_error = ''

    for attempt in range(max_retries):
        try:
            parsed, raw_text = _ollama_generate(prompt)
            normalized = _normalize_infer_payload(parsed, command_text, raw_text)
            if normalized:
                return normalized
            last_error = 'Invalid structured output from model'
            logger.warning('ai_infer_invalid_output', extra={'attempt': attempt + 1, 'error': last_error})
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            last_error = str(exc)
            logger.warning('ai_infer_failure', extra={'attempt': attempt + 1, 'error': last_error})

    fallback = _heuristic_fallback(command_text, last_error)
    logger.error('ai_infer_fallback', extra={'error': last_error, 'command': command_text[:180]})
    return fallback


def generate_email(command_text: str, intent: str, tone: str, recipient_name: str, relationship: str) -> Dict:
    prompt = f"""
You are a professional AI Email Assistant.

Your task is to generate a high-quality email draft based on the user's command.

-----------------------------------
📌 OUTPUT FORMAT (STRICT)
-----------------------------------
Return ONLY valid JSON. No extra text.

{{
  "subject": "string",
  "body": "string"
}}

-----------------------------------
📌 INPUT DETAILS
-----------------------------------
User Command: {command_text}
Intent: {intent}
Tone: {tone}
Recipient Name: {recipient_name}
Relationship: {relationship}

-----------------------------------
📌 INSTRUCTIONS
-----------------------------------

1. LANGUAGE HANDLING:
- Input may be in English, Hindi, or Hinglish
- Output MUST always be in clear, professional English

2. SUBJECT RULES:
- Short, clear, and relevant (max 8–10 words)
- Should reflect the main purpose of the email

3. BODY RULES:
- Proper email structure:
  - Greeting (based on relationship)
  - Opening line (context/purpose)
  - Main message (clear and actionable)
  - Closing line
  - Signature (use sender-neutral closing)

4. GREETING RULES (VERY IMPORTANT):
- If relationship is:
  - "formal" → "Dear {recipient_name},"
  - "manager" → "Dear {recipient_name},"
  - "client" → "Dear {recipient_name},"
  - "friend" → "Hi {recipient_name},"
  - "colleague" → "Hi {recipient_name},"
  - unknown → "Hello {recipient_name},"

5. TONE HANDLING:
- "formal" → professional, polite
- "casual" → friendly, relaxed
- "apologetic" → sincere and respectful
- "urgent" → clear and action-focused

6. INTENT HANDLING:
- Ensure the email clearly reflects the intent: {intent}
- Focus ONLY on the main actionable request
- Ignore unnecessary or multiple side requests

7. QUALITY RULES:
- Keep it concise but complete
- No grammar mistakes
- No repetition
- Make it realistic like a human wrote it

8. STRICT JSON RULE:
- DO NOT include markdown
- DO NOT include explanation
- DO NOT include extra keys
- ONLY return subject and body

-----------------------------------
📌 EXAMPLE OUTPUT
-----------------------------------
{{
  "subject": "Leave Request for Tomorrow",
  "body": "Dear John,\\n\\nI hope you are doing well. I would like to request leave for tomorrow due to personal reasons.\\n\\nPlease let me know if any arrangements are needed from my side.\\n\\nThank you for your understanding.\\n\\nBest regards,"
}}
""".strip()
    max_retries = 3
    last_error = ''

    for attempt in range(max_retries):
        try:
            parsed, raw_text = _ollama_generate(prompt)
            normalized = _normalize_generate_payload(parsed, raw_text)
            if normalized:
                return normalized
            last_error = 'Missing subject/body in model output'
            logger.warning('ai_generate_invalid_output', extra={'attempt': attempt + 1, 'error': last_error})
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            last_error = str(exc)
            logger.warning('ai_generate_failure', extra={'attempt': attempt + 1, 'error': last_error})

    logger.error('ai_generate_fallback', extra={'error': last_error, 'intent': intent, 'tone': tone})
    return {
        'subject': '',
        'body': '',
        'ai_used': False,
        'ai_raw_output': '',
        'ai_error': last_error or 'fallback_used',
    }
