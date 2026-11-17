"""Two-body orbital mechanics; AU, days, degrees. No graphics dependency."""
from dataclasses import dataclass
import math

# Gaussian gravitational constant squared: solar GM in AU^3/day^2.
SOLAR_MU = 0.0002959122082855911

@dataclass(frozen=True)
class Orbit:
    a: float
    e: float
    inclination: float = 0.0
    node: float = 0.0
    perihelion: float = 0.0  # longitude of perihelion
    longitude: float = 0.0  # mean longitude at J2000

    @property
    def period(self):
        return 2 * math.pi * math.sqrt(self.a ** 3 / SOLAR_MU)

    def position(self, days):
        mean = math.radians(self.longitude - self.perihelion) + 2 * math.pi * days / self.period
        return self.at_mean_anomaly(mean)

    def at_mean_anomaly(self, mean):
        mean = (mean + math.pi) % math.tau - math.pi
        eccentric = mean
        for _ in range(20):
            step = (eccentric - self.e * math.sin(eccentric) - mean) / (1 - self.e * math.cos(eccentric))
            eccentric -= step
            if abs(step) < 1e-13:
                break
        x = self.a * (math.cos(eccentric) - self.e)
        y = self.a * math.sqrt(1 - self.e ** 2) * math.sin(eccentric)
        w, n, i = map(math.radians, (self.perihelion - self.node, self.node, self.inclination))
        u, v = x * math.cos(w) - y * math.sin(w), x * math.sin(w) + y * math.cos(w)
        # Ecliptic Z is mapped to scene Y; preserve a right-handed frame.
        return (u * math.cos(n) - v * math.cos(i) * math.sin(n),
                v * math.sin(i), -(u * math.sin(n) + v * math.cos(i) * math.cos(n)))

@dataclass(frozen=True)
class Body:
    name: str
    orbit: Orbit
    radius: float  # deliberately exaggerated display units
    spin_hours: float  # positive about tilted north pole (tilt encodes retrograde)
    tilt: float
    color: tuple

# Rounded JPL J2000 mean elements; fixed, not a present-day ephemeris.
BODIES = (
    Body('Mercury', Orbit(.38709927,.20563593,7.004979,48.330766,77.457796,252.250324), .09,1407.6,.034,(145,139,132)),
    Body('Venus', Orbit(.72333566,.00677672,3.394676,76.679843,131.602467,181.979100), .14,5832.5,177.4,(218,185,120)),
    Body('Earth', Orbit(1.00000261,.01671123,-.000015,0,102.937682,100.464572), .15,23.9345,23.4,(30,91,171)),
    Body('Mars', Orbit(1.52371034,.09339410,1.849691,49.559539,-23.943630,-4.553432), .11,24.623,25.2,(183,83,43)),
    Body('Jupiter', Orbit(5.202887,.04838624,1.304397,100.473909,14.728480,34.396441), .45,9.925,3.1,(193,155,119)),
    Body('Saturn', Orbit(9.536676,.05386179,2.485992,113.662424,92.598878,49.954244), .38,10.7,26.7,(209,190,143)),
    Body('Uranus', Orbit(19.189165,.04725744,.772638,74.016925,170.954276,313.238105), .27,17.2,97.8,(137,204,215)),
    Body('Neptune', Orbit(30.069923,.00859048,1.770043,131.784226,44.964762,-55.120030), .26,16.1,28.3,(54,96,198)),
)

def spin_angle(days, hours):
    return (days * 24 / hours * 360) % 360
