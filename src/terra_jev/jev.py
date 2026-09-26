import os
import requests


JEV_URL = "https://api.typesafe.ai/v1/systemone"


def build_small_state(plan):
    resources = []

    for resource in plan.get("resource_changes", []):
        change = resource.get("change", {})
        actions = change.get("actions", [])

        if actions == ["no-op"]:
            continue

        resources.append({
            "address": resource.get("address"),
            "type": resource.get("type"),
            "actions": actions,
        })

    return {
        "terraform_version": plan.get("terraform_version"),
        "format_version": plan.get("format_version"),
        "resource_changes": resources,
    }


def build_full_state(plan):
    return plan


def analyze_with_jev(plan, full=False):
    api_key = os.environ.get("TYPESAFE_API_KEY")

    if not api_key:
        raise RuntimeError(
            "TYPESAFE_API_KEY environment variable is not set."
        )

    state = build_full_state(plan) if full else build_small_state(plan)

    payload = {
        "model": "jev-latest",
        "state": state,

        "questions": {

            # ---------------------------------------------------------
            # 1. Overall Risk
            # ---------------------------------------------------------
            "risk": {
                "type": "choice",
                "instructions": (
                    "Assess the overall risk of applying this Terraform "
                    "plan. Consider security, destructive changes, "
                    "availability, networking, identity, data exposure, "
                    "and infrastructure impact."
                ),
                "criteria": {
                    "low": (
                        "The changes have limited scope and introduce "
                        "no significant security, availability, "
                        "destructive, or operational concerns."
                    ),
                    "medium": (
                        "The changes affect infrastructure or security "
                        "and require review, but there is no clearly "
                        "critical or highly destructive change."
                    ),
                    "high": (
                        "The changes contain significant security risks, "
                        "destructive operations, major infrastructure "
                        "changes, public exposure, privilege changes, "
                        "or potential service disruption."
                    ),
                },
            },

            # ---------------------------------------------------------
            # 2. Security
            # ---------------------------------------------------------
            "security": {
                "type": "choice",
                "instructions": (
                    "Determine whether this Terraform plan introduces "
                    "a security concern. Check for public exposure, "
                    "network access, insecure configuration, identity "
                    "and access changes, secrets, authentication, "
                    "encryption, security groups, firewall rules, "
                    "storage access, and sensitive infrastructure."
                ),
                "criteria": {
                    "yes": (
                        "One or more identifiable security concerns "
                        "are introduced or weakened by the changes."
                    ),
                    "no": (
                        "No identifiable security concern is introduced "
                        "by the provided Terraform changes."
                    ),
                },
            },

            # ---------------------------------------------------------
            # 3. Destructive Changes
            # ---------------------------------------------------------
            "destructive": {
                "type": "choice",
                "instructions": (
                    "Determine whether the Terraform plan contains "
                    "destructive or potentially data-impacting changes. "
                    "Consider destroy actions, replacements, recreation "
                    "of resources, and changes that may cause data loss."
                ),
                "criteria": {
                    "yes": (
                        "The plan contains resource destruction, "
                        "replacement, recreation, or another potentially "
                        "data-impacting operation."
                    ),
                    "no": (
                        "The plan does not contain destructive or "
                        "potentially data-loss-causing changes."
                    ),
                },
            },

            # ---------------------------------------------------------
            # 4. Availability
            # ---------------------------------------------------------
            "availability": {
                "type": "choice",
                "instructions": (
                    "Determine whether applying this Terraform plan "
                    "could cause service downtime, availability impact, "
                    "restart, replacement, networking disruption, "
                    "or loss of service."
                ),
                "criteria": {
                    "yes": (
                        "The changes could cause service disruption, "
                        "downtime, restart, replacement, or availability "
                        "impact."
                    ),
                    "no": (
                        "No significant availability impact is apparent "
                        "from the Terraform changes."
                    ),
                },
            },

            # ---------------------------------------------------------
            # 5. Network Exposure
            # ---------------------------------------------------------
            "network_exposure": {
                "type": "choice",
                "instructions": (
                    "Determine whether the Terraform changes introduce "
                    "or increase network exposure. Check for public IPs, "
                    "public endpoints, open firewall or security-group "
                    "rules, unrestricted inbound access, exposed ports, "
                    "internet-facing services, and changes from private "
                    "to public connectivity."
                ),
                "criteria": {
                    "yes": (
                        "The plan introduces or increases potentially "
                        "unnecessary network exposure."
                    ),
                    "no": (
                        "The plan does not introduce a significant "
                        "increase in network exposure."
                    ),
                },
            },

            # ---------------------------------------------------------
            # 6. Identity / Permissions
            # ---------------------------------------------------------
            "identity_risk": {
                "type": "choice",
                "instructions": (
                    "Determine whether the Terraform plan changes "
                    "identity, authentication, authorization, IAM, "
                    "RBAC, service principals, managed identities, "
                    "roles, policies, or permissions in a potentially "
                    "risky way."
                ),
                "criteria": {
                    "yes": (
                        "The plan introduces or expands potentially "
                        "risky permissions, roles, identities, or "
                        "authentication configuration."
                    ),
                    "no": (
                        "No significant identity or permission risk "
                        "is apparent."
                    ),
                },
            },

            # ---------------------------------------------------------
            # 7. Secrets
            # ---------------------------------------------------------
            "secrets_risk": {
                "type": "choice",
                "instructions": (
                    "Determine whether sensitive information such as "
                    "passwords, API keys, tokens, private keys, "
                    "connection strings, certificates, or credentials "
                    "may be exposed, stored, or configured insecurely "
                    "by the Terraform changes."
                ),
                "criteria": {
                    "yes": (
                        "Sensitive information appears to be exposed "
                        "or handled in a potentially insecure manner."
                    ),
                    "no": (
                        "No identifiable secret-handling concern "
                        "is present in the provided plan."
                    ),
                },
            },

            # ---------------------------------------------------------
            # 8. Encryption
            # ---------------------------------------------------------
            "encryption": {
                "type": "choice",
                "instructions": (
                    "Determine whether the Terraform changes introduce "
                    "or weaken encryption or data-protection controls. "
                    "Consider encryption at rest, encryption in transit, "
                    "TLS, HTTPS, database encryption, storage encryption, "
                    "and insecure protocol configuration."
                ),
                "criteria": {
                    "yes": (
                        "The changes weaken, disable, or omit an "
                        "important encryption or data-protection control."
                    ),
                    "no": (
                        "No significant encryption or data-protection "
                        "concern is apparent."
                    ),
                },
            },

            # ---------------------------------------------------------
            # 9. Data Protection
            # ---------------------------------------------------------
            "data_protection": {
                "type": "choice",
                "instructions": (
                    "Determine whether the Terraform changes could "
                    "affect data integrity, persistence, backup, "
                    "retention, recovery, or accidental data loss."
                ),
                "criteria": {
                    "yes": (
                        "The plan could negatively affect data "
                        "persistence, backup, retention, recovery, "
                        "integrity, or availability."
                    ),
                    "no": (
                        "No significant data-protection concern "
                        "is apparent."
                    ),
                },
            },

            # ---------------------------------------------------------
            # 10. Configuration Risk
            # ---------------------------------------------------------
            "configuration_risk": {
                "type": "choice",
                "instructions": (
                    "Determine whether the Terraform plan introduces "
                    "a potentially unsafe infrastructure configuration, "
                    "including overly permissive settings, disabled "
                    "security controls, incorrect networking, missing "
                    "dependencies, or configuration that could cause "
                    "unexpected behavior."
                ),
                "criteria": {
                    "yes": (
                        "The plan contains one or more potentially "
                        "unsafe or misconfigured infrastructure settings."
                    ),
                    "no": (
                        "No significant configuration concern is apparent."
                    ),
                },
            },

            # ---------------------------------------------------------
            # 11. Operational Risk
            # ---------------------------------------------------------
            "operational_risk": {
                "type": "choice",
                "instructions": (
                    "Assess the operational risk of applying the plan. "
                    "Consider infrastructure replacement, dependency "
                    "changes, networking changes, scaling changes, "
                    "service restarts, and changes that could affect "
                    "production workloads."
                ),
                "criteria": {
                    "low": (
                        "The changes have limited operational impact."
                    ),
                    "medium": (
                        "The changes could affect infrastructure or "
                        "services and should be reviewed."
                    ),
                    "high": (
                        "The changes could cause significant service "
                        "disruption or operational impact."
                    ),
                },
            },

            # ---------------------------------------------------------
            # 12. Review Required
            # ---------------------------------------------------------
            "review_required": {
                "type": "choice",
                "instructions": (
                    "Determine whether this Terraform plan requires "
                    "human review before it should be applied."
                ),
                "criteria": {
                    "yes": (
                        "The plan contains meaningful security, "
                        "destructive, operational, networking, identity, "
                        "data, or configuration risks that should be "
                        "reviewed by an engineer."
                    ),
                    "no": (
                        "No significant issue requiring additional "
                        "human review is apparent."
                    ),
                },
            },

            # ---------------------------------------------------------
            # 13. Final Action
            # ---------------------------------------------------------
            "action": {
                "type": "choice",
                "instructions": (
                    "Based on the Terraform plan and identified risks, "
                    "determine the appropriate action before applying it."
                ),
                "criteria": {
                    "approve": (
                        "No significant issue requiring additional "
                        "review is identified."
                    ),
                    "review": (
                        "The plan should be reviewed before applying "
                        "because meaningful risks or uncertainties "
                        "were identified."
                    ),
                    "reject": (
                        "The plan contains a significant security, "
                        "destructive, data, or operational concern "
                        "that should be addressed before applying."
                    ),
                },
            },
        },
    }

    response = requests.post(
        JEV_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"JEV API returned HTTP {response.status_code}\n"
            f"{response.text}"
        )

    return response.json()