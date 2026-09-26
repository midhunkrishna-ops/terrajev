import argparse

from terra_jev.parser import load_plan
from terra_jev.jev import analyze_with_jev


def print_answer(answers, key, label):
    if key not in answers:
        return

    answer = answers[key]

    choice = answer.get("choice", "unknown")
    confidence = answer.get("confidence", 0)

    print(f"\n{label:<20}: {choice.upper()}")
    print(f"{'Confidence':<20}: {confidence:.0%}")


def main():
    parser = argparse.ArgumentParser(
        prog="terrajev",
        description="AI-assisted Terraform plan risk and security analyzer",
    )

    subparsers = parser.add_subparsers(dest="command")

    review_parser = subparsers.add_parser(
        "review",
        help="Analyze a Terraform plan",
    )

    review_parser.add_argument(
        "plan",
        help="Path to Terraform plan file",
    )

    review_parser.add_argument(
        "--full",
        action="store_true",
        help="Send full Terraform plan for detailed analysis",
    )

    args = parser.parse_args()

    if args.command == "review":
        print(f"\nLoading Terraform plan: {args.plan}")

        plan = load_plan(args.plan)

        print("Terraform plan loaded successfully")

        mode = "FULL" if args.full else "COMPACT"

        print(f"\nJEV analysis mode: {mode}")
        print("Sending Terraform plan to JEV...")

        result = analyze_with_jev(plan, full=args.full)

        answers = result.get("answers", {})

        print("\n" + "=" * 60)
        print("TERRAFORM JEV REVIEW")
        print("=" * 60)

        # ---------------------------------------------------------
        # Overall assessment
        # ---------------------------------------------------------

        print_answer(answers, "risk", "Risk")
        print_answer(answers, "security", "Security")
        print_answer(answers, "destructive", "Destructive Changes")
        print_answer(answers, "availability", "Availability Impact")

        # ---------------------------------------------------------
        # Security analysis
        # ---------------------------------------------------------

        print("\n" + "-" * 60)
        print("SECURITY ANALYSIS")
        print("-" * 60)

        print_answer(
            answers,
            "network_exposure",
            "Network Exposure",
        )

        print_answer(
            answers,
            "identity_risk",
            "Identity / IAM Risk",
        )

        print_answer(
            answers,
            "secrets_risk",
            "Secrets Risk",
        )

        print_answer(
            answers,
            "encryption",
            "Encryption Risk",
        )

        print_answer(
            answers,
            "data_protection",
            "Data Protection",
        )

        # ---------------------------------------------------------
        # Operational analysis
        # ---------------------------------------------------------

        print("\n" + "-" * 60)
        print("OPERATIONAL ANALYSIS")
        print("-" * 60)

        print_answer(
            answers,
            "configuration_risk",
            "Configuration Risk",
        )

        print_answer(
            answers,
            "operational_risk",
            "Operational Risk",
        )

        print_answer(
            answers,
            "review_required",
            "Review Required",
        )

        # ---------------------------------------------------------
        # Final action
        # ---------------------------------------------------------

        print("\n" + "-" * 60)
        print("RECOMMENDED ACTION")
        print("-" * 60)

        print_answer(
            answers,
            "action",
            "Action",
        )

        # ---------------------------------------------------------
        # Usage
        # ---------------------------------------------------------

        usage = result.get("usage", {})

        print("\n" + "-" * 60)
        print(f"Mode      : {mode}")
        print(f"JEV Model : {result.get('model', 'unknown')}")
        print(
            f"Tokens    : "
            f"{usage.get('input_tokens', 0)} in / "
            f"{usage.get('output_tokens', 0)} out"
        )
        print("=" * 60)

        return

    parser.print_help()


if __name__ == "__main__":
    main()