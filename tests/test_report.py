import unittest

from tfplan_summary import summarize_plan


class SummarizePlanTests(unittest.TestCase):
    def test_classifies_standard_and_replacement_actions(self):
        summary = summarize_plan(
            {
                "resource_changes": [
                    {"address": "aws_instance.new", "change": {"actions": ["create"]}},
                    {"address": "aws_instance.edit", "change": {"actions": ["update"]}},
                    {"address": "aws_instance.old", "change": {"actions": ["delete"]}},
                    {"address": "aws_instance.same", "change": {"actions": ["no-op"]}},
                    {
                        "address": "aws_instance.replace",
                        "change": {"actions": ["delete", "create"]},
                    },
                ]
            }
        )

        self.assertEqual(
            summary.counts,
            {"create": 1, "update": 1, "delete": 1, "replace": 1},
        )
        self.assertEqual(
            [change.address for change in summary.destructive_changes],
            ["aws_instance.old", "aws_instance.replace"],
        )

    def test_accepts_empty_resource_changes(self):
        self.assertEqual(summarize_plan({}).changes, ())

    def test_rejects_malformed_resource_changes(self):
        with self.assertRaisesRegex(ValueError, "resource_changes must be a list"):
            summarize_plan({"resource_changes": {}})


if __name__ == "__main__":
    unittest.main()