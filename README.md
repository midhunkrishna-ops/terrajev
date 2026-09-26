# 🛡️ terrajev

> **AI-assisted Terraform plan risk and security analyzer**

`terrajev` is a powerful command-line tool that leverages AI to review your Terraform plans, providing insightful analysis on risk, security, and suggested actions.

## 🚀 Features

- **Automated Risk Assessment**: Quickly gauge the risk level of your infrastructure changes before applying them.
- **Security Analysis**: Identify potential security vulnerabilities and misconfigurations in your plan.
- **Actionable Insights**: Get clear recommendations on whether to proceed, review, or halt the changes.
- **Two Analysis Modes**: Choose between a compact analysis for speed or a full analysis for deep insights.

## 📦 Installation

To install `terrajev` directly from source, clone the repository and run:

```bash
pip install .
```

Alternatively, if you're developing locally:

```bash
pip install -e .
```

## 🛠️ Usage

Analyze a Terraform plan with the `review` command:

```bash
terrajev review <path/to/terraform/plan.json>
```

### Options

- `--full`: Send the entire Terraform plan for a more detailed and comprehensive JEV analysis.

### Example Output

```text
Loading Terraform plan: my_plan.json
Terraform plan loaded successfully

JEV analysis mode: COMPACT
Sending Terraform plan to JEV...

==================================================
TERRAFORM JEV REVIEW
==================================================

Risk      : LOW
Confidence: 95%

Security  : PASS
Confidence: 90%

Action    : APPROVE
Confidence: 92%

--------------------------------------------------
Mode      : COMPACT
JEV Model : jev-model-v1
Tokens    : 1500 in / 120 out
==================================================
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue if you have any ideas, bug reports, or feature requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Security Limitations

While `terrajev` attempts to aggressively sanitize Terraform plans before passing data to the AI model, please be aware of the following:

- **No Guarantees**: No regex or heuristic-based sanitizer can guarantee detection of every possible secret, token, or password.
- **Provider Differences**: Different Terraform providers may expose or flag sensitive properties differently, which could lead to missed detections.
- **Always Review**: Users are strongly encouraged to review the sanitized output behavior on their typical plans before blindly relying on it, especially in highly restrictive environments. Do not assume perfectly zero risk.
