import math
import unittest
from physics import BODIES, Orbit, SOLAR_MU, spin_angle

class OrbitalTests(unittest.TestCase):
    def test_apsides(self):
        for body in BODIES:
            orbit = body.orbit
            for anomaly, radius in ((0, orbit.a * (1-orbit.e)), (math.pi, orbit.a * (1+orbit.e))):
                self.assertAlmostEqual(math.sqrt(sum(v*v for v in orbit.at_mean_anomaly(anomaly))), radius, places=10)

    def test_period_and_closure(self):
        self.assertAlmostEqual(BODIES[2].orbit.period, 365.256, delta=.01)
        for body in BODIES:
            for a, b in zip(body.orbit.position(0), body.orbit.position(body.orbit.period)):
                self.assertAlmostEqual(a, b, places=10)

    def test_acceleration_obeys_solar_gravity(self):
        for body in BODIES:
            orbit, t, h = body.orbit, 17.0, .02
            before, p, after = orbit.position(t-h), orbit.position(t), orbit.position(t+h)
            r = math.sqrt(sum(v*v for v in p))
            for a, b, c in zip(before, p, after):
                actual = (c - 2*b + a) / h**2
                expected = -SOLAR_MU * b / r**3
                self.assertAlmostEqual(actual, expected, delta=max(1e-10, abs(expected)*1e-5))

    def test_rotation(self):
        for body in BODIES:
            self.assertAlmostEqual(spin_angle(body.spin_hours/48, body.spin_hours), 180)
        self.assertGreater(BODIES[1].tilt, 90)
        self.assertGreater(BODIES[6].tilt, 90)

    def test_kepler_second_law(self):
        orbit = Orbit(1, .4)
        h = .001
        angular_momenta = []
        for t in (0, 40, 160):
            p = orbit.position(t)
            lo, hi = orbit.position(t-h), orbit.position(t+h)
            velocity = [(b-a)/(2*h) for a,b in zip(lo, hi)]
            angular_momenta.append(p[2]*velocity[0]-p[0]*velocity[2])
        for value in angular_momenta:
            self.assertAlmostEqual(value, angular_momenta[0], places=9)

if __name__ == '__main__':
    unittest.main()
