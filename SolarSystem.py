# Solar System Animation


import sys
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

# Sun class to handle the properties and rendering of the sun
class Sun:
    def __init__(self):
        self.radius = 0.8
        self.color = (1.0, 1.0, 0.0)  # Set Yellow color
        self.angle = 0.0

    # Draw the sun
    def draw(self):
        glDisable(GL_LIGHTING)  # Disable lighting for the Sun
        glColor3f(*self.color)

        glPushMatrix()
        glRotatef(self.angle, 0.0, 1.0, 0.0)
        self.draw_sphere(self.radius, 50, 50)
        glPopMatrix()

        glEnable(GL_LIGHTING)  # Re-enable lighting for other objects

    # Update the rotation of the sun
    def update(self):
        self.angle += 0.05  # Adjust speed of rotation
        if self.angle >= 360:
            self.angle -= 360

    # Helper method to draw a sphere
    def draw_sphere(self, radius, slices, stacks):
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)
        gluSphere(quadric, radius, slices, stacks)
        gluDeleteQuadric(quadric)

# Planet class to handle the properties and rendering of the planets
class Planet:
    def __init__(self, distance, radius, speed, color, has_ring=False):
        self.distance = distance
        self.radius = radius
        self.speed = speed
        self.color = color
        self.has_ring = has_ring
        self.angle = 0.0
        self.ring_color = (0.8, 0.8, 0.8)  # Default ring color

    # Draw the planet and its ring (if it has one)
    def draw(self, cast_shadows=True):
        glColor3f(*self.color)

        # Revolve around the sun
        glPushMatrix()
        glRotatef(self.angle, 0.0, 1.0, 0.0)
        # Move to the planet's position
        glTranslatef(self.distance, 0.0, 0.0)
        # Rotate to make the plane vertical
        glRotatef(90.0, 1.0, 0.0, 0.0)
        # Draw the planet
        if cast_shadows:
            glEnable(GL_LIGHTING)
        else:
            glDisable(GL_LIGHTING)
        self.draw_sphere(self.radius, 50, 50)
        glPopMatrix()

        # Draw the planet's ring if it has one
        if self.has_ring:
            self.draw_ring()

    # Update the rotation and revolution of the planet
    def update(self):
        self.angle += self.speed
        if self.angle >= 360:
            self.angle -= 360

    # Helper method to draw a sphere
    def draw_sphere(self, radius, slices, stacks):
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)
        gluSphere(quadric, radius, slices, stacks)
        gluDeleteQuadric(quadric)

    # Draw the ring of the planet
    def draw_ring(self):
        glColor4f(*self.ring_color, 0.6)  # Adjust alpha to make it more visible
        inner_radius = self.radius * 1.5  # Adjust size of inner radius
        outer_radius = self.radius * 2.0  # Adjust size of outer radius
        sides = 50

        glPushMatrix()
        glRotatef(90.0, 1.0, 0.0, 0.0)  # Rotate to make the plane vertical (x-axis)
        glRotatef(self.angle, 0.0, 1.0, 0.0)  # Rotate along with the planet

        glBegin(GL_QUAD_STRIP)
        for i in range(sides + 1):
            angle = i * 2.0 * math.pi / sides
            x = math.cos(angle)
            y = math.sin(angle)

            glTexCoord2f(0.0, 1.0 * i / sides)
            glVertex3f((self.distance + inner_radius) * x, inner_radius * y, 0.0)

            glTexCoord2f(1.0, 1.0 * i / sides)
            glVertex3f((self.distance + outer_radius) * x, outer_radius * y, 0.0)
        glEnd()

        glPopMatrix()

# SolarSystem class to handle the entire solar system
class SolarSystem:
    def __init__(self):
        self.sun = Sun()
        self.planets = [
            Planet(0.7, 0.06, 2.4, (0.7, 0.7, 0.7)),   # Mercury (Gray)
            Planet(1.1, 0.12, 1.7, (0.9, 0.7, 0.4)),   # Venus (Brownish-Yellow)
            Planet(1.5, 0.14, 1.0, (0.2, 0.5, 1.0)),   # Earth (Blue)
            Planet(2.0, 0.08, 0.8, (1.0, 0.3, 0.3)),   # Mars (Reddish)
            Planet(6.0, 0.3, 0.4, (0.7, 0.5, 0.3)),    # Jupiter (Light Brown)
            Planet(10.0, 0.25, 0.25, (0.9, 0.8, 0.6), True),   # Saturn (Pale Yellow) with ring
            Planet(20.0, 0.2, 0.15, (0.6, 0.8, 0.9), True),   # Uranus (Pale Blue) with ring
            Planet(30.0, 0.18, 0.1, (0.4, 0.4, 0.9), True)     # Neptune (Dark Blue) with ring
            # Add other planets here...
        ]

        self.camera_distance = 50.0
        self.camera_angle = 0.0

        # Light position
        self.light_position = (0.0, 0.0, 0.0, 1.0)

    # Draw the solar system
    def draw(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        glLightfv(GL_LIGHT0, GL_POSITION, self.light_position)

        self.sun.draw()

        for planet in self.planets:
            planet.draw(planet != self.sun)  # Enable shadows for planets only
            if planet.has_ring:
                planet.draw_ring()

    # Update the solar system (sun and planets)
    def update(self):
        self.sun.update()
        for planet in self.planets:
            planet.update()

# Initialize OpenGL settings
def init():
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)  # Enable transparency
    glDepthFunc(GL_LEQUAL)  # Set depth test function
    glShadeModel(GL_SMOOTH)  # Enable smooth shading
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, 1, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

# Display the solar system
def display(solar_system):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(0.0, 0.0, solar_system.camera_distance,  # Camera position
              0.0, 0.0, 0.0,                           # Look at origin
              0.0, 1.0, 0.0)                           # Up vector

    glRotatef(solar_system.camera_angle, 0.0, 1.0, 0.0)  # Rotate camera around y-axis

    solar_system.draw()

    pygame.display.flip()

# Adjust the viewport and perspective when the window is resized
def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (w / h), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

# Update the solar system and render the display
def update(solar_system):
    solar_system.update()
    display(solar_system)

# Handle user input and events
def handle_events(solar_system):
    global paused
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                solar_system.camera_angle += 5.0
            elif event.key == pygame.K_RIGHT:
                solar_system.camera_angle -= 5.0
            elif event.key == pygame.K_UP:
                solar_system.camera_distance -= 5.0
            elif event.key == pygame.K_DOWN:
                solar_system.camera_distance += 5.0
            elif event.key == pygame.K_SPACE:
                paused = not paused

    return True

# Main function to set up and run the simulation
def main():
    global paused
    pygame.init()
    pygame.display.set_mode((1000, 800), DOUBLEBUF | OPENGL)
    pygame.display.set_caption('Solar System Simulation')
    init()

    solar_system = SolarSystem()

    clock = pygame.time.Clock()
    running = True
    paused = False
    while running:
        running = handle_events(solar_system)
        if not paused:
            update(solar_system)

        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
