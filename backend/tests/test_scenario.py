import unittest

from pydantic import ValidationError

from game.scenario import Scenario
from schemas import ScenarioModel

PARTNER = {"name": "Lucy", "bio": "A barista.", "language": "english", "level": "A1"}


def make_model(objectives: list[dict]) -> ScenarioModel:
    return ScenarioModel.model_validate({"partner": PARTNER, "setting": "A café.", "objectives": objectives})


class TestScenario(unittest.TestCase):
    def test_from_model_nests_checklists(self):
        model = make_model([{"text": "Order a drink", "checklist": [{"kind": "say", "text": "Hi!"}]}])
        objective = Scenario.from_model(model).objectives[0]
        self.assertEqual("Order a drink", objective.text)
        self.assertEqual(("say", "Hi!"), (objective.checklist[0].kind, objective.checklist[0].text))

    def test_objective_without_checklist(self):
        scenario = Scenario.from_model(make_model([{"text": "Order a drink"}]))
        self.assertEqual([], scenario.objectives[0].checklist)

    def test_empty_objective_text_rejected(self):
        with self.assertRaises(ValidationError):
            make_model([{"text": ""}])


if __name__ == "__main__":
    unittest.main()
