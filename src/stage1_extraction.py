import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import spacy

# Load spaCy model (NER)
# If this fails, run: python -m spacy download en_core_web_sm
NLP = spacy.load("en_core_web_sm")

# -----------------------------
# Regex patterns (logs + chat)
# -----------------------------
TS_RE = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")
LEVEL_RE = re.compile(r"\b(INFO|WARN|ERROR)\b")
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
HOST_RE = re.compile(r"\b(node-\d+|vm-\d+|db-server-\d+)\b", re.IGNORECASE)

# Simple service pattern to match your synthetic services
SERVICE_RE = re.compile(r"\b([A-Za-z]+Service|APIService|Gateway)\b")

# Command “looks like” patterns (very lightweight)
CMD_HINT_RE = re.compile(r"\b(kubectl|systemctl|iptables|ufw|fail2ban-client|netsh|rm|find|journalctl|curl|ping|traceroute)\b")


@dataclass
class ExtractedEvent:
    time: str
    level: Optional[str]
    event: str


def normalize_text(s: Any) -> str:
    """Basic normalization for logs/chat fields."""
    if pd.isna(s):
        return ""
    s = str(s)
    # Keep newlines (useful for log lines), just normalize whitespace a bit
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    return s.strip()


def parse_log_events(logs: str) -> Tuple[List[ExtractedEvent], List[str]]:
    """
    Log Parsing & Normalization:
    - Extract timestamps
    - Extract level
    - Create structured event objects
    Returns (events, validation_errors)
    """
    errors: List[str] = []
    events: List[ExtractedEvent] = []

    lines = [ln.strip() for ln in logs.split("\n") if ln.strip()]
    for ln in lines:
        ts_m = TS_RE.search(ln)
        lvl_m = LEVEL_RE.search(ln)

        if not ts_m:
            errors.append(f"Missing timestamp in log line: {ln[:80]}")
            continue

        time_str = ts_m.group(1)
        level_str = lvl_m.group(1) if lvl_m else None

        # remove timestamp from event text
        event_txt = ln.replace(time_str, "").strip()
        events.append(ExtractedEvent(time=time_str, level=level_str, event=event_txt))

    # Temporal parsing (sequence): sort by timestamp string (works because format is YYYY-MM-DD HH:MM:SS)
    events.sort(key=lambda e: e.time)

    return events, errors


def extract_entities_from_text(text: str) -> Dict[str, List[str]]:
    """
    Information Extraction:
    - NER via spaCy for general entities
    - Regex for domain entities (service, host, IP)
    """
    entities = {
        "services": set(),
        "hosts": set(),
        "ips": set(),
        "orgs": set(),
        "people": set(),
        "dates": set(),
    }

    # Regex entities (reliable for our synthetic patterns)
    for m in SERVICE_RE.findall(text):
        entities["services"].add(m)

    for m in HOST_RE.findall(text):
        entities["hosts"].add(m.lower())

    for m in IP_RE.findall(text):
        entities["ips"].add(m)

    # spaCy NER (best-effort) 
    doc = NLP(text)
    for ent in doc.ents:
        if ent.label_ == "ORG":
            entities["orgs"].add(ent.text)
        elif ent.label_ == "PERSON":
            entities["people"].add(ent.text)
        elif ent.label_ in ("DATE", "TIME"):
            entities["dates"].add(ent.text)

    # Convert to sorted lists
    return {k: sorted(list(v)) for k, v in entities.items()}


def extract_commands(commands_executed: str) -> Dict[str, Any]:
    """
    Extract command-related info.
    We keep the raw command, and also mark if it looks like a command.
    """
    cmd = commands_executed.strip()
    return {
        "raw": cmd,
        "has_command": bool(CMD_HINT_RE.search(cmd)) if cmd else False,
        "command_hint": CMD_HINT_RE.search(cmd).group(1) if cmd and CMD_HINT_RE.search(cmd) else None
    }


def context_fusion(
    log_events: List[ExtractedEvent],
    log_entities: Dict[str, List[str]],
    chat_entities: Dict[str, List[str]],
    cmd_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Context Fusion:
    Merge events + entities from logs and chat + commands into one incident representation.
    """
    services = sorted(set(log_entities["services"]) | set(chat_entities["services"]))
    hosts = sorted(set(log_entities["hosts"]) | set(chat_entities["hosts"]))
    ips = sorted(set(log_entities["ips"]) | set(chat_entities["ips"]))

    timeline = [
        {"time": e.time, "level": e.level, "event": e.event}
        for e in log_events
    ]

    return {
        "services_affected": services,
        "hosts": hosts,
        "ips": ips,
        "timeline": timeline,
        "commands": cmd_info,
    }


# def validate_extraction(incident_json: Dict[str, Any], raw_logs: str) -> List[str]:
#     """
#     Output Evaluation / Fact Validation:
#     Check that extracted services/hosts/IPs appear in the raw logs.
#     (Simple consistency checks to reduce hallucination-like issues.)
#     """
#     issues: List[str] = []

#     def _must_appear(items: List[str], label: str):
#         for it in items:
#             if it and it not in raw_logs and it.lower() not in raw_logs.lower():
#                 issues.append(f"{label} '{it}' not found in logs")

#     _must_appear(incident_json.get("services_affected", []), "Service")
#     _must_appear(incident_json.get("hosts", []), "Host")
#     _must_appear(incident_json.get("ips", []), "IP")

#     # Validate timeline timestamps are sorted
#     times = [ev["time"] for ev in incident_json.get("timeline", [])]
#     if times != sorted(times):
#         issues.append("Timeline timestamps are not sorted (temporal parsing failed)")

#     return issues
def validate_extraction(incident_json: Dict[str, Any], raw_logs: str, raw_chat: str) -> List[str]:
    issues: List[str] = []

    combined = (raw_logs or "") + "\n" + (raw_chat or "")

    def _must_appear(items: List[str], label: str):
        for it in items:
            if it and it not in combined and it.lower() not in combined.lower():
                issues.append(f"{label} '{it}' not found in logs/chat")

    _must_appear(incident_json.get("services_affected", []), "Service")
    _must_appear(incident_json.get("hosts", []), "Host")
    _must_appear(incident_json.get("ips", []), "IP")

    times = [ev["time"] for ev in incident_json.get("timeline", [])]
    if times != sorted(times):
        issues.append("Timeline timestamps are not sorted (temporal parsing failed)")

    return issues


def stage1_extract_row(logs: Any, chat: Any, commands: Any) -> Dict[str, Any]:
    """
    Full Stage 1:
    1) Parse logs -> events
    2) Extract entities from logs + chat
    3) Extract commands
    4) Fuse into JSON
    5) Validate / add issues
    """
    logs_n = normalize_text(logs)
    chat_n = normalize_text(chat)
    cmd_n = normalize_text(commands)

    log_events, parse_errors = parse_log_events(logs_n)

    log_entities = extract_entities_from_text(logs_n)
    chat_entities = extract_entities_from_text(chat_n)
    cmd_info = extract_commands(cmd_n)

    incident_json = context_fusion(log_events, log_entities, chat_entities, cmd_info)

    # validation_issues = validate_extraction(incident_json, logs_n)
    validation_issues = validate_extraction(incident_json, logs_n, chat_n)
    incident_json["stage1_parse_errors"] = parse_errors
    incident_json["stage1_validation_issues"] = validation_issues

    return incident_json