# 🛡️ terrajev
 
> **AI-assisted Terraform plan risk and security analyzer**
 
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
 
`terrajev` is a command-line tool that uses **Jev by TypeSafe AI** to analyze Terraform plans and identify potential infrastructure, security, and operational risks **before changes are applied**.
 
---
 
## 📖 Table of Contents
 
- [Why terrajev?](#why-terrajev)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Analysis Modes](#analysis-modes)
- [Example Output](#example-output)
- [Security & Data Handling](#security--data-handling)
- [How It Works](#how-it-works)
- [Contributing](#contributing)
- [License](#license)
---
 
## Why terrajev?
 
Terraform plans can contain hundreds or thousands of infrastructure changes, making manual review time-consuming and error-prone. `terrajev` automates the initial risk assessment layer.
 
### What It Detects
 
- 🚨 **Overall infrastructure risk** — High-impact changes at a glance
- 🔓 **Security concerns** — Network exposure, IAM drift, credential handling
- ⚠️ **Destructive changes** — Deletions, major version upgrades, breaking modifications
- 📊 **Availability impact** — Changes affecting uptime or redundancy
- 🔐 **Secret handling risks** — Potential credential or token exposure
- 🛡️ **Encryption & data protection** — Configuration changes to sensitive protections
- 👤 **Identity & permission changes** — IAM policy modifications
- 🔍 **Operational risk** — Configuration drift and compliance concerns
### Why Jev?
 
[Jev](https://typesafe.ai) is a **System One model** from TypeSafe AI—not a general-purpose LLM, but a decision engine built for structured data.
 
**Benefits for Terraform analysis:**
 
| Feature | Benefit |
|---------|---------|
| **Structured decisions** | Returns risk classifications, not prose |
| **Speed** | 70–500ms analysis (100x faster than LLMs) |
| **Cost** | $0.042 per million input tokens, free output |
| **No text generation** | Evaluates what matters: infrastructure risk |
| **Calibrated confidence** | Trust levels for each decision |
 
Instead of building a custom inference system, `terrajev` delegates analysis to Jev while focusing on:
1. Loading and parsing Terraform plans
2. Sanitizing sensitive information
3. Structuring data for analysis
4. Presenting results in developer-friendly format
---
 
## Quick Start
 
### Prerequisites
 
- Python 3.8+
- Terraform 1.0+
- A TypeSafe AI API key for Jev
### 1. Get Your API Key
 
Obtain your API key from [TypeSafe AI](https://typesafe.ai).
 
### 2. Set Environment Variable
 
```bash
export TYPESAFE_API_KEY="your-api-key-here"
```
 
Verify it's set:
 
```bash
echo $TYPESAFE_API_KEY
```
 
### 3. Install terrajev
 
```bash
pip install terrajev
```
 
### 4. Analyze a Plan
 
```bash
terraform plan -out=tfplan
terrajev review tfplan
```
 
---
 
## Installation
 
### From PyPI (Recommended)
 
```bash
pip install terrajev
```
 
### From Source
 
```bash
git clone https://github.com/midhunkrishna-ops/terrajev.git
cd terrajev
pip install .
```
 
### For Development
 
```bash
git clone https://github.com/midhunkrishna-ops/terrajev.git
cd terrajev
pip install -e ".[dev]"
```
 
---
 
## Usage
 
### Basic Review
 
```bash
terrajev review <path-to-terraform-plan>
```
 
**Example:**
 
```bash
terraform plan -out=tfplan
terrajev review tfplan
```
 
### Full Detailed Analysis
 
```bash
terrajev review tfplan --full
```
 
Use `--full` when you need deeper analysis of configuration details. Note: This mode consumes more API tokens.
 
### Help
 
```bash
terrajev review --help
```
 
---
 
## Analysis Modes
 
`terrajev` supports two analysis modes, each with different levels of detail and API token consumption.
 
### Compact Mode (Default)
 
```bash
terrajev review tfplan
```
 
**Characteristics:**
- Summarized Terraform changes sent to Jev
- Fast overview of planned infrastructure modifications
- Lower API token usage
- Best for: Rapid risk screening in CI/CD pipelines
**Good for:**
- Pre-deployment gates
- Quick risk assessment
- Resource-constrained environments
### Full Mode
 
```bash
terrajev review tfplan --full
```
 
**Characteristics:**
- Full plan details from `terraform show -json`
- Detailed infrastructure configuration analysis
- Higher API token usage
- Best for: Comprehensive risk evaluation
**Good for:**
- Security audits
- Compliance reviews
- Complex infrastructure changes
---
 
## Example Output
 
```
Loading Terraform plan: tfplan
Terraform plan loaded successfully
 
JEV analysis mode: COMPACT
Sending Terraform plan to Jev...
 
============================================================
TERRAFORM JEV REVIEW
============================================================
 
Risk                : HIGH
Confidence          : 71%
 
Security            : YES
Confidence          : 37%
 
Destructive Changes : NO
Confidence          : 89%
 
Availability Impact : YES
Confidence          : 64%
 
------------------------------------------------------------
SECURITY ANALYSIS
------------------------------------------------------------
 
Network Exposure   : YES
Identity / IAM Risk: NO
Secrets Risk       : NO
Encryption Risk    : NO
Data Protection    : NO
 
------------------------------------------------------------
OPERATIONAL ANALYSIS
------------------------------------------------------------
 
Configuration Risk : YES
Operational Risk   : MEDIUM
Review Required    : YES
 
------------------------------------------------------------
RECOMMENDED ACTION
------------------------------------------------------------
 
Action              : REVIEW
 
------------------------------------------------------------
Mode      : COMPACT
Jev Model : jev-1.13.0
Tokens    : 1847 in / 411 out
============================================================
```
 
> **Note:** Output, confidence values, model versions, and token usage vary based on your Terraform plan and Jev response.
 
---
 
## Security & Data Handling
 
### What Terraform Plans Contain
 
Terraform plans can include sensitive information:
 
- Passwords and API tokens
- Access keys and private keys
- Certificates and connection strings
- Internal IP addresses and network configuration
- Cloud resource identifiers and ARNs
- IAM policies and permission details
### terrajev's Sanitization Strategy
 
`terrajev` **attempts** to detect and mask sensitive fields before sending data to Jev:
 
```text
Terraform Plan
      │
      ├─ Detect marked sensitive fields
      ├─ Mask common credential patterns
      ├─ Redact API key-like strings
      └─ Remove internal identifiers
      │
      ▼
Sanitized Terraform State
      │
      ▼
Jev Analysis
```
 
### ⚠️ Important Security Limitations
 
**No sanitizer is 100% effective.** Here's why:
 
| Limitation | Impact |
|-----------|--------|
| **Regex-based detection** | Cannot catch all secret formats |
| **Provider differences** | Providers expose sensitive data differently |
| **Nested structures** | Some secrets hide in nested configurations |
| **Custom resources** | Unknown provider fields may not be sanitized |
 
### Security Best Practices
 
#### Protect Your API Key
 
Do not:
```bash
❌ Hard-code in source code
❌ Commit to Git or version control
❌ Include in Terraform files
❌ Upload to GitHub or public repositories
❌ Include in bug reports or logs
❌ Share via Slack, email, or chat
```
 
Do:
```bash
✅ Use environment variables: export TYPESAFE_API_KEY="..."
✅ Use .env files (NOT tracked by Git)
✅ Use CI/CD secrets management (GitHub Secrets, GitLab CI, etc.)
✅ Use cloud provider secret stores (AWS Secrets Manager, etc.)
✅ Rotate keys regularly
```
 
#### Test Before Production
 
Before using `terrajev` in sensitive environments:
 
1. **Test against representative plans** — Run analysis on non-production Terraform plans
2. **Review sanitized output** — Verify no secrets are exposed
3. **Check confidence scores** — Ensure Jev's confidence aligns with your risk tolerance
4. **Establish review thresholds** — Define when human review is required
#### Compliance & Audit
 
If you have strict compliance requirements:
 
- Audit API logs and token usage
- Monitor which plans are analyzed
- Log all review actions
- Consider on-premise alternatives if data residency is required
---
 
## How It Works
 
### Processing Pipeline
 
```
Terraform Plan File (tfplan / tfplan.json)
      │
      ▼
Parse Terraform Plan
  └─ Read binary or JSON format
  └─ Extract resources, changes, outputs
      │
      ▼
Convert to Structured Format
  └─ terraform show -json (if needed)
  └─ Build configuration view
      │
      ▼
Sanitize Sensitive Data
  └─ Mask credentials and tokens
  └─ Remove internal identifiers
  └─ Redact marked sensitive fields
      │
      ▼
Compact or Full Representation
  └─ Select analysis mode
  └─ Prepare structured data
      │
      ▼
Send to Jev by TypeSafe AI
  ├─ Infrastructure risk assessment
  ├─ Security analysis
  ├─ Destructive change detection
  ├─ Availability impact evaluation
  ├─ Network exposure analysis
  ├─ Identity & permission review
  ├─ Secret handling assessment
  ├─ Encryption & data protection check
  ├─ Operational risk evaluation
  └─ Calibrated confidence scores
      │
      ▼
Receive Structured Results
  └─ Risk classification
  └─ Security concerns
  └─ Confidence scores
  └─ Recommended actions
      │
      ▼
Format CLI Report
  └─ Risk summary
  └─ Detailed analysis
  └─ Token usage
  └─ Recommended actions
      │
      ▼
Display to User
```
 
---
 
## Configuration
 
### Environment Variables
 
| Variable | Required | Description |
|----------|----------|-------------|
| `TYPESAFE_API_KEY` | Yes | Your TypeSafe AI API key for Jev |
 
### Optional Settings
 
Future versions may support:
- `TERRAJEV_CONFIDENCE_THRESHOLD` — Auto-fail on low confidence
- `TERRAJEV_LOG_LEVEL` — Control verbosity
- `TERRAJEV_TIMEOUT` — Request timeout in seconds
---
 
## Contributing
 
Contributions are welcome! Please submit:
 
- **Bug reports** — Use GitHub Issues
- **Feature requests** — Open a discussion
- **Pull requests** — Follow the guidelines below
### Areas for Contribution
 
- 🐛 **Bug fixes** — Security, sanitization, parsing
- ✨ **Features** — New analysis modes, integrations
- 🔒 **Security** — Improved sanitization, data handling
- 🏗️ **Provider support** — Better handling of specific Terraform providers
- 📚 **Documentation** — Examples, guides, best practices
- 🧪 **Tests** — Improve coverage and edge cases
### Development Setup
 
```bash
git clone https://github.com/midhunkrishna-ops/terrajev.git
cd terrajev
pip install -e ".[dev]"
pytest
```
 
---
 
## Roadmap
 
- [ ] GitHub Actions integration
- [ ] GitLab CI integration
- [ ] Terraform Cloud/Enterprise webhook support
- [ ] Policy-as-code definitions
- [ ] Custom risk thresholds and rules
- [ ] JSON/SARIF output formats
- [ ] Provider-specific sanitization rules
---
 
## Troubleshooting
 
### `TYPESAFE_API_KEY not found`
 
```bash
export TYPESAFE_API_KEY="your-api-key"
echo $TYPESAFE_API_KEY  # Verify it's set
```
 
### `Plan file not found`
 
Ensure the Terraform plan file exists:
 
```bash
terraform plan -out=tfplan
ls -la tfplan  # Verify file exists
```
 
### `Jev API error`
 
- Check your API key is valid
- Verify your TypeSafe AI account is active
- Check your API quota and billing
### Sensitive data in output
 
If you suspect sensitive data was exposed:
 
1. **Rotate your API keys immediately**
2. **Review Jev API logs** (TypeSafe AI dashboard)
3. **Test sanitization** on the problematic plan
4. **Open an issue** with anonymized details
---
 
## License
 
This project is licensed under the **Apache License 2.0**.
 
See [LICENSE](LICENSE) for full details.
 
---
 
**Ready to secure your infrastructure?**
 
```bash
pip install terrajev
terraform plan -out=tfplan
terrajev review tfplan
```
