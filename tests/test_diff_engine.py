import unittest
from pathlib import Path

from driftsense import diff_engine, manifest_loader


FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "sample_manifests"


class DriftReportTests(unittest.TestCase):
    def test_sample_manifests_produce_expected_drift_report(self) -> None:
        desired = manifest_loader.load_manifests(FIXTURE_ROOT / "desired")
        actual = manifest_loader.load_manifests(FIXTURE_ROOT / "actual")

        report = diff_engine.compare(desired, actual)

        self.assertTrue(report.has_drift())
        self.assertTrue(any(rec.key.kind == "Service" for rec in report.missing))
        self.assertTrue(any(rec.key.kind == "Secret" for rec in report.extra))
        changed_kinds = sorted(change.key.kind for change in report.changed)
        self.assertEqual(changed_kinds, ["ConfigMap", "Deployment"])


if __name__ == "__main__":
    unittest.main()
