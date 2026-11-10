import json
import unittest
from pathlib import Path

from campaign_check.rules import validate_config


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def rule_ids(filename):
    with (EXAMPLES / filename).open(encoding="utf-8") as handle:
        return {issue.rule_id for issue in validate_config(json.load(handle))}


class CampaignRuleTests(unittest.TestCase):
    def test_clean_example_passes(self):
        self.assertEqual(rule_ids("clean.json"), set())

    def test_schedule_order(self):
        self.assertIn("CFG001", rule_ids("broken-schedule.json"))

    def test_contact_window(self):
        self.assertIn("CFG002", rule_ids("broken-contact-window.json"))

    def test_sms_opt_out(self):
        self.assertIn("CFG003", rule_ids("broken-opt-out.json"))

    def test_merge_field(self):
        self.assertIn("CFG004", rule_ids("broken-merge-field.json"))

    def test_start_step(self):
        self.assertIn("CFG005", rule_ids("broken-start-step.json"))

    def test_reachable_step(self):
        self.assertIn("CFG006", rule_ids("broken-unreachable.json"))

    def test_next_step(self):
        self.assertIn("CFG007", rule_ids("broken-next-step.json"))

    def test_segment_reference(self):
        self.assertIn("CFG008", rule_ids("broken-segment.json"))

    def test_unique_step_ids(self):
        self.assertIn("CFG009", rule_ids("broken-duplicate-step.json"))


if __name__ == "__main__":
    unittest.main()
