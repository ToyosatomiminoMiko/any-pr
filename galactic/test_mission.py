import contextlib
import io
import json
import math
import random
import unittest

from galactic.mission import galaxy, main, mission, render, route


class MissionTests(unittest.TestCase):
    def test_reproducible_unique_galaxy(self):
        stars = galaxy("epic", 200)
        self.assertEqual(stars, galaxy("epic", 200))
        self.assertEqual(len({(s['x'], s['y']) for s in stars}), 200)
        self.assertNotEqual(stars, galaxy("other", 200))

    def test_global_random_state_untouched(self):
        state = random.getstate()
        galaxy()
        self.assertEqual(state, random.getstate())

    def test_invalid_count(self):
        for count in (0, 1, 201):
            with self.assertRaises(ValueError):
                galaxy(count=count)

    def test_shortest_route_and_boundary(self):
        stars = [dict(name="a", x=0, y=0), dict(name="b", x=3, y=4),
                 dict(name="c", x=6, y=8), dict(name="detour", x=0, y=5)]
        self.assertEqual(route(stars, "a", "c", 5),
                         dict(path=["a", "b", "c"], distance=10.0, hops=2))
        self.assertIsNone(route(stars, "a", "c", 4.9))
        self.assertEqual(route(stars, "a", "a", 1)['hops'], 0)

    def test_invalid_route_inputs(self):
        stars = galaxy()
        for jump in (0, -1, math.inf, math.nan):
            with self.assertRaises(ValueError):
                route(stars, "S000", "S001", jump)
        with self.assertRaises(ValueError):
            route(stars, "missing", "S001")
        with self.assertRaises(ValueError):
            route(stars + stars, "S000", "S001")

    def test_report_fingerprint(self):
        data = mission("epic", jump=150)
        self.assertEqual(data, mission("epic", jump=150))
        self.assertEqual(len(data['fingerprint']), 64)
        self.assertNotEqual(data['fingerprint'], mission("other")['fingerprint'])
        self.assertIsNotNone(data['route'])
        self.assertEqual(json.loads(json.dumps(data)), data)

    def test_chart_dimensions_and_highlight(self):
        stars = galaxy()
        chart = render(stars, ["S000"], 30, 10)
        self.assertEqual(len(chart.splitlines()), 12)
        self.assertTrue(all(len(line) == 32 for line in chart.splitlines()))
        self.assertIn("@", chart)
        with self.assertRaises(ValueError):
            render(stars, width=1)

    def test_cli_json_and_exit_codes(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(["--json", "--jump", "150"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue())['version'], 1)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--jump", "0.001"]), 2)
            self.assertEqual(main(["--destination", "S000"]), 0)

    def test_cli_invalid_input(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as caught:
                main(["--stars", "1"])
        self.assertEqual(caught.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
