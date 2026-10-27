# Terraform Plan Summary

A small Python CLI that reads Terraform plan JSON and reports resource changes,
including replacements and deletions that will destroy existing resources.
It only reads the plan file; it does not run Terraform or change infrastructure.

## Requirements

- Python 3.10 or later
- Terraform, only if you need to generate a plan file

## Use

Generate a saved plan and convert it to JSON:

```sh
terraform plan -out=tfplan
terraform show -json tfplan > plan.json
```

Run the summarizer from this repository:

```sh
python -m tfplan_summary plan.json
```

Or install the command locally:

```sh
python -m pip install .
tf-plan-summary plan.json
```

Run the test suite with:

```sh
python -m unittest discover -s tests
```