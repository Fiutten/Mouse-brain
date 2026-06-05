import unittest

from neurotwin_mvp.behavioral_targets import (
    derive_binary_target,
    diagnose_session_targets,
    diagnose_target,
    materialize_target_session,
)
from neurotwin_mvp.data import Session, Trial


def trial(trial_id, metadata, choice=0, reward=0):
    return Trial(
        trial_id=trial_id,
        stimulus=1.0,
        choice=choice,
        reward=reward,
        latency_ms=100.0,
        engagement=1.0,
        region_rates={"visual_cortex": 1.0},
        metadata=metadata,
    )


class BehavioralTargetTests(unittest.TestCase):
    def test_go_response_uses_hit_and_miss_only_on_go_trials(self):
        hit = trial(1, {"go": True, "hit": True, "miss": False})
        miss = trial(2, {"go": True, "hit": False, "miss": True})
        catch = trial(3, {"catch": True, "false_alarm": True})
        self.assertEqual(derive_binary_target(hit, "go_response"), 1)
        self.assertEqual(derive_binary_target(miss, "go_response"), 0)
        self.assertIsNone(derive_binary_target(catch, "go_response"))

    def test_catch_response_uses_false_alarm_and_correct_reject(self):
        false_alarm = trial(1, {"catch": True, "false_alarm": True})
        correct_reject = trial(2, {"catch": True, "correct_reject": True})
        go = trial(3, {"go": True, "hit": True})
        self.assertEqual(derive_binary_target(false_alarm, "catch_response"), 1)
        self.assertEqual(derive_binary_target(correct_reject, "catch_response"), 0)
        self.assertIsNone(derive_binary_target(go, "catch_response"))

    def test_response_made_uses_action_regardless_of_trial_type(self):
        hit = trial(1, {"go": True, "hit": True})
        false_alarm = trial(2, {"catch": True, "false_alarm": True})
        miss = trial(3, {"go": True, "miss": True})
        correct_reject = trial(4, {"catch": True, "correct_reject": True})

        self.assertEqual(derive_binary_target(hit, "response_made"), 1)
        self.assertEqual(derive_binary_target(false_alarm, "response_made"), 1)
        self.assertEqual(derive_binary_target(miss, "response_made"), 0)
        self.assertEqual(derive_binary_target(correct_reject, "response_made"), 0)

    def test_task_success_uses_correctness_across_go_and_catch_trials(self):
        hit = trial(1, {"go": True, "hit": True})
        correct_reject = trial(2, {"catch": True, "correct_reject": True})
        miss = trial(3, {"go": True, "miss": True})
        false_alarm = trial(4, {"catch": True, "false_alarm": True})

        self.assertEqual(derive_binary_target(hit, "task_success"), 1)
        self.assertEqual(derive_binary_target(correct_reject, "task_success"), 1)
        self.assertEqual(derive_binary_target(miss, "task_success"), 0)
        self.assertEqual(derive_binary_target(false_alarm, "task_success"), 0)

    def test_diagnose_target_marks_low_count_as_not_usable(self):
        session = Session(
            session_id="toy",
            animal_id="mouse",
            dataset="toy",
            region_names=["visual_cortex"],
            trials=[
                trial(i, {"go": True, "hit": i % 2 == 0, "miss": i % 2 == 1})
                for i in range(10)
            ],
        )
        diagnostic = diagnose_target(session, "go_response")
        self.assertFalse(diagnostic.usable)
        self.assertIn("Fewer than", " ".join(diagnostic.warnings))

    def test_diagnose_session_targets_reports_all_defaults(self):
        session = Session(
            session_id="toy",
            animal_id="mouse",
            dataset="toy",
            region_names=["visual_cortex"],
            trials=[
                trial(i, {"go": True, "hit": i % 2 == 0, "miss": i % 2 == 1}, choice=i % 2)
                for i in range(100)
            ],
        )
        report = diagnose_session_targets(session)
        names = {item.target_name for item in report.diagnostics}
        self.assertEqual(
            names,
            {
                "choice",
                "go_response",
                "catch_response",
                "rewarded",
                "response_made",
                "task_success",
            },
        )

    def test_materialize_target_session_filters_and_preserves_original_choice(self):
        session = Session(
            session_id="toy",
            animal_id="mouse",
            dataset="toy",
            region_names=["visual_cortex"],
            trials=[
                trial(0, {"go": True, "hit": True}, choice=0),
                trial(1, {"go": True, "miss": True}, choice=1),
                trial(2, {"catch": True, "correct_reject": True}, choice=0),
            ],
        )
        retargeted = materialize_target_session(session, "go_response")

        self.assertEqual([item.choice for item in retargeted.trials], [1, 0])
        self.assertEqual([item.trial_id for item in retargeted.trials], [0, 1])
        self.assertEqual(retargeted.trials[0].metadata["original_choice"], 0)
        self.assertEqual(retargeted.trials[1].metadata["original_choice"], 1)
        self.assertEqual(len(session.trials), 3)


if __name__ == "__main__":
    unittest.main()
