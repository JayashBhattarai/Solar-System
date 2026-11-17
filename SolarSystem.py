"""Interactive textured solar-system orrery. Run: python SolarSystem.py."""
import math
from pathlib import Path
import random
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from physics import BODIES, Orbit, spin_angle

AU_SCALE = 4.0
ASSETS = Path(__file__).resolve().parent / 'textures'


def surface_texture(name, color):
    """Optional equirectangular JPEG/PNG, otherwise a deterministic artistic map."""
    for suffix in ('.jpg', '.png'):
        path = ASSETS / (name.lower() + suffix)
        if path.exists():
            return pygame.image.load(str(path)).convert()
    rng = random.Random(name)
    width, height = 512, 256
    surface = pygame.Surface((width, height))
    for y in range(height):
        latitude = math.pi * (y / (height - 1) - .5)
        for x in range(width):
            longitude = math.tau * x / width
            noise = rng.uniform(-.035, .035)
            waves = (math.sin(3 * longitude + 2 * math.sin(latitude * 5)) +
                     .5 * math.cos(7 * longitude - latitude * 9))
            factor = .85 + .13 * waves + noise
            rgb = color
            if name in ('Jupiter', 'Saturn', 'Venus', 'Uranus', 'Neptune'):
                strength = .16 if name in ('Jupiter', 'Saturn') else .045
                factor = .9 + strength * math.sin(latitude * 35 + .5 * math.sin(longitude * 4)) + noise
                if name == 'Jupiter' and ((longitude - 4.2) / .33) ** 2 + ((latitude + .35) / .13) ** 2 < 1:
                    rgb = (170, 78, 48)
            elif name == 'Earth':
                rgb = (61, 119, 59) if waves + .55 * math.sin(latitude * 7) > .65 else color
                if abs(latitude) > 1.3 or math.sin(longitude * 9 + latitude * 17) + waves > 1.8:
                    rgb = (223, 232, 235)
            elif name == 'Mars' and abs(latitude) > 1.4:
                rgb = (225, 217, 199)
            surface.set_at((x, y), tuple(max(0, min(255, int(c * factor))) for c in rgb))
    if name in ('Mercury', 'Mars'):
        for _ in range(140):
            x, y, r = rng.randrange(width), rng.randrange(height), rng.randrange(2, 9)
            pygame.draw.circle(surface, tuple(int(c * .60) for c in color), (x, y), r, 1)
    return surface


def upload_texture(surface):
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGB, *surface.get_size(), GL_RGB, GL_UNSIGNED_BYTE,
                     pygame.image.tostring(surface, 'RGB', True))
    return texture


class SolarSystem:
    def __init__(self):
        self.days = 0.0
        self.speed = 10.0
        self.paused = False
        self.distance = 340.0
        self.yaw, self.pitch = 0.0, 35.0
        self.focus = 0
        self.paths = True
        self.belt_visible = True
        self.quadric = gluNewQuadric()
        gluQuadricNormals(self.quadric, GLU_SMOOTH)
        gluQuadricTexture(self.quadric, GL_TRUE)
        self.textures = {b.name: upload_texture(surface_texture(b.name, b.color)) for b in BODIES}
        self.textures['Sun'] = upload_texture(surface_texture('Sun', (255, 207, 89)))
        rng = random.Random(42)
        self.asteroids = [Orbit(rng.uniform(2.15, 3.3), rng.uniform(.01,.12), rng.uniform(0,12),
                                rng.uniform(0,360), rng.uniform(0,360), rng.uniform(0,360)) for _ in range(1000)]
        self.orbit_paths = [[orbit.at_mean_anomaly(math.tau * j / 256) for j in range(256)]
                            for orbit in (b.orbit for b in BODIES)]

    def sphere(self, name, radius):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.textures[name])
        glColor3f(1, 1, 1)
        gluSphere(self.quadric, radius, 48, 32)
        glDisable(GL_TEXTURE_2D)

    def rings(self, body):
        # Same translated and tilted frame as planet, around its local Z spin axis.
        glDisable(GL_LIGHTING)
        for inner, outer, color in ((1.25,1.5,(.43,.39,.30)), (1.55,1.95,(.72,.66,.51)), (2.02,2.3,(.54,.49,.39))):
            if body.name == 'Uranus':
                inner, outer, color = 1.8, 1.84, (.30,.38,.39)
            glColor3f(*color)
            glBegin(GL_QUAD_STRIP)
            for j in range(129):
                a = math.tau * j / 128
                for radius in (inner * body.radius, outer * body.radius):
                    glVertex3f(radius * math.cos(a), radius * math.sin(a), 0)
            glEnd()
            if body.name == 'Uranus':
                break
        glEnable(GL_LIGHTING)

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        target = (0, 0, 0) if not self.focus else BODIES[self.focus - 1].orbit.position(self.days)
        target = tuple(v * AU_SCALE for v in target)
        yaw, pitch = math.radians(self.yaw), math.radians(self.pitch)
        eye = (target[0] + self.distance * math.cos(pitch) * math.sin(yaw),
               target[1] + self.distance * math.sin(pitch),
               target[2] + self.distance * math.cos(pitch) * math.cos(yaw))
        gluLookAt(*eye, *target, 0, 1, 0)
        # Set after camera transform so the point light stays at the world-space Sun.
        glLightfv(GL_LIGHT0, GL_POSITION, (0, 0, 0, 1))
        glDisable(GL_LIGHTING)
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        glRotatef(spin_angle(self.days, 25.38 * 24), 0, 0, 1)
        self.sphere('Sun', .65)
        glPopMatrix()
        if self.paths:
            glColor3f(.17, .21, .29)
            for path in self.orbit_paths:
                glBegin(GL_LINE_LOOP)
                for p in path:
                    glVertex3f(*(v * AU_SCALE for v in p))
                glEnd()
        if self.belt_visible:
            glColor3f(.48, .44, .37)
            glPointSize(1.5)
            glBegin(GL_POINTS)
            for asteroid in self.asteroids:
                glVertex3f(*(v * AU_SCALE for v in asteroid.position(self.days)))
            glEnd()
        glEnable(GL_LIGHTING)
        for body in BODIES:
            glPushMatrix()
            glTranslatef(*(v * AU_SCALE for v in body.orbit.position(self.days)))
            # Orient relative to orbital plane; pole azimuth is illustrative.
            glRotatef(body.orbit.node, 0, 1, 0)
            glRotatef(body.orbit.inclination, 1, 0, 0)
            glRotatef(-90 + body.tilt, 1, 0, 0)
            if body.name in ('Saturn', 'Uranus'):
                self.rings(body)
            glRotatef(spin_angle(self.days, body.spin_hours), 0, 0, 1)
            self.sphere(body.name, body.radius)
            glPopMatrix()
        pygame.display.flip()
        name = 'Sun' if not self.focus else BODIES[self.focus - 1].name
        pygame.display.set_caption(f'Solar System | {name} | J2000 + {self.days:.2f} days | '
                                   f'{self.speed:g} days/s {"PAUSED" if self.paused else ""} | '
                                   '0-8 focus, +/- speed, Space pause, arrows orbit, wheel zoom, O orbits, B belt, R reset')

    def close(self):
        glDeleteTextures(list(self.textures.values()))
        gluDeleteQuadric(self.quadric)


def reshape(width, height):
    glViewport(0, 0, width, max(1, height))
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / max(1, height), .01, 1200)
    glMatrixMode(GL_MODELVIEW)


def main():
    pygame.init()
    pygame.display.set_mode((1280, 850), pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHT0)
    glEnable(GL_NORMALIZE)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (.025, .025, .025, 1))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0, 0, 0, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, .97, .91, 1))
    reshape(1280, 850)
    system = SolarSystem()
    clock = pygame.time.Clock()
    running = True
    try:
        while running:
            dt = clock.tick(60) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    reshape(event.w, event.h)
                elif event.type == pygame.MOUSEWHEEL:
                    system.distance = max(1, min(450, system.distance * .88 ** event.y))
                elif event.type == pygame.KEYDOWN:
                    key = event.key
                    if key == pygame.K_ESCAPE:
                        running = False
                    elif key == pygame.K_SPACE:
                        system.paused = not system.paused
                    elif key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                        system.speed = min(10000, system.speed * 2)
                    elif key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                        system.speed = max(.0001, system.speed / 2)
                    elif pygame.K_0 <= key <= pygame.K_8:
                        system.focus = key - pygame.K_0
                        system.distance = 5 if system.focus else 340
                    elif key == pygame.K_o:
                        system.paths = not system.paths
                    elif key == pygame.K_b:
                        system.belt_visible = not system.belt_visible
                    elif key == pygame.K_r:
                        system.days, system.speed = 0, 10
                        system.focus, system.distance = 0, 340
                        system.yaw, system.pitch = 0, 35
            keys = pygame.key.get_pressed()
            system.yaw += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 45 * dt
            system.pitch = max(-85, min(85, system.pitch + (keys[pygame.K_UP] - keys[pygame.K_DOWN]) * 45 * dt))
            if not system.paused:
                system.days += dt * system.speed
            system.draw()  # camera and resize continue to work while paused
    finally:
        system.close()
        pygame.quit()


if __name__ == '__main__':
    main()
