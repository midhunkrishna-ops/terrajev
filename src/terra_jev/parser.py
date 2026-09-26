import json
import os
import subprocess
import re

SENSITIVE_KEY_PATTERN = re.compile(
    r"(^|_|-)(password|passwd|secret|token|access_key|secret_key|client_secret|api_key|credential|credentials|private_key|certificate|cert|connection_string|authorization|bearer)($|_|-)",
    re.IGNORECASE
)


# Common patterns for raw secrets in string values
VALUE_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}", re.IGNORECASE), # AWS Access Key
    re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", re.IGNORECASE), # JWT
    re.compile(r"-----BEGIN (RSA |DSA |EC |OPENSSH |)PRIVATE KEY-----", re.IGNORECASE), # Private Keys
    re.compile(r"Bearer [A-Za-z0-9\-\._~+/]+", re.IGNORECASE), # Bearer token
]

def sanitize_value(val):
    if isinstance(val, str):
        for pattern in VALUE_PATTERNS:
            if pattern.search(val):
                return "*** MASKED ***"
    return val

def _sanitize_recursive(data, sensitive_schema=None):
    if isinstance(data, dict):
        sanitized = {}
        
        # If this dict represents a change block, we might have an after_sensitive / before_sensitive schema
        after_sens = data.get("after_sensitive", {}) if isinstance(data.get("after_sensitive"), dict) else {}
        before_sens = data.get("before_sensitive", {}) if isinstance(data.get("before_sensitive"), dict) else {}
        
        for k, v in data.items():
            # Check if this key is flagged as sensitive in the schema (from parent traversal)
            is_sensitive_flagged = False
            if isinstance(sensitive_schema, dict) and sensitive_schema.get(k) is True:
                is_sensitive_flagged = True
                
            # Check for terraform native explicit "sensitive: true" in variable definitions
            if k == "value" and data.get("sensitive") is True:
                is_sensitive_flagged = True

            # Also check if it's explicitly matched by our heuristic regex
            is_heuristic_match = isinstance(k, str) and SENSITIVE_KEY_PATTERN.search(k)
            
            if is_sensitive_flagged or is_heuristic_match:
                sanitized[k] = "*** MASKED ***"
            else:
                # If we are traversing "after" or "before", pass down the sensitive schema
                child_schema = None
                if k == "after":
                    child_schema = after_sens
                elif k == "before":
                    child_schema = before_sens
                elif isinstance(sensitive_schema, dict) and isinstance(sensitive_schema.get(k), dict):
                    child_schema = sensitive_schema.get(k)
                
                sanitized[k] = _sanitize_recursive(v, child_schema)
                
        return sanitized
    elif isinstance(data, list):
        # Arrays might have an array of sensitive schemas, but for simplicity we rely on heuristics and value matches in arrays unless perfectly aligned.
        # If sensitive_schema is a list of the same length, zip them. Otherwise pass None.
        sanitized_list = []
        for i, item in enumerate(data):
            child_schema = None
            if isinstance(sensitive_schema, list) and i < len(sensitive_schema):
                child_schema = sensitive_schema[i]
            
            if child_schema is True:
                sanitized_list.append("*** MASKED ***")
            else:
                sanitized_list.append(_sanitize_recursive(item, child_schema))
        return sanitized_list
    else:
        # Check against value patterns if it's a string
        return sanitize_value(data)

def sanitize_plan(data):
    """
    Takes a parsed Terraform JSON plan and returns a sanitized dictionary
    where sensitive values are replaced with "*** MASKED ***".
    """
    return _sanitize_recursive(data)

def load_plan(plan_path):
    plan_path = os.path.abspath(plan_path)
    terraform_dir = os.path.dirname(plan_path)

    result = subprocess.run(
        ["terraform", "show", "-json", plan_path],
        cwd=terraform_dir,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Failed to read Terraform plan:\n{result.stderr.strip()}"
        )

    raw_plan = json.loads(result.stdout)
    return sanitize_plan(raw_plan)
