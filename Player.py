"""
Player Class
The code here creates and controls the player and their movement
"""

# Import necessary packages
import math
import pyglet
from pyglet.gl import *
from pyglet.window import mouse, key


# Define global variables
GRAVITY = 20
TERMINAL_VELOCITY = 40
JUMP_SPEED = 10
# Fluid velocity multiplier makes the player fall slower in water
FLUID_VELOCITY_MULT = 1


class Player:
    """Player class defines the Player so that they can move around the Window"""
    
    """Define the Players original position and Orientation (Rotation)"""
    def __init__(self, SEEDX, SEEDZ):

        # Players coordinates on the map in the x, y, z direction
        self.pos = [SEEDX,6,SEEDZ]

        # Player rotation is in the y,x form
        self.rot = [0,0]

        # Define the speed at which the player will move and the movement in the direction currently going
        self.speed = 4
        self.right = True
        self.forward = True
        self.left = True
        self.back = True
        self.up = True

        # Variables used in determining players falling speed
        self.vert_velocity = 0
        self.GROUND_BENEATH_PLAYER = False
        self.IN_FLUID = False


    def get_sight_vector(self):
        """ Returns 3D unit vector representing where the player is looking. """
        rz, rx = self.rot
        rx = -rx
        mult = math.cos(math.radians(rz))

        dz = math.sin(math.radians(rx-90)) * mult
        dy = math.sin(math.radians(rz))
        dx = math.cos(math.radians(rx-90)) * mult

        return dx, dy, dz

    
    def mouse_motion(self, dx, dy):
        """mouse_motion adjusts the rotation of the player
        It is called from the window when the mouse is moved"""
        dx/= 8
        dy/= 8
        self.rot[0] += dy
        self.rot[1] -= dx
        
        # Lock the rotation of the y plane to looking straight up and straight down
        if self.rot[0]>90:
            self.rot[0] = 90
        elif self.rot[0] < -90:
            self.rot[0] = -90


    def update_movement(self,dt,keys):
        """updates the movement of the player in the world"""
        # d is the distance covered this tick
        d = dt * self.speed

        # rotY converted to radians
        rotY = math.radians(self.rot[1])

        # dx is the distance the player moves in the x direction and dy the distance in the y direction
        dx, dz = d*math.sin(rotY), d*math.cos(rotY)


        if self.GROUND_BENEATH_PLAYER or self.IN_FLUID:
            if keys[key.SPACE]:
                self.vert_velocity += JUMP_SPEED
        if keys[key.LSHIFT]:
            pass

        # Account for affects of gravity, stop player from falling faster than at the set Terminal Velocity
        # Only in affect when the player does not have a block beneath them or if the player is going up
        if not self.GROUND_BENEATH_PLAYER or (self.vert_velocity > 0):
            self.vert_velocity -= dt * GRAVITY
            self.vert_velocity = max(self.vert_velocity, -TERMINAL_VELOCITY)
            self.pos[1] += self.vert_velocity * dt * FLUID_VELOCITY_MULT

        return dx, dz


    def update_location(self, keys, dx, dz):
        """update_location is called after we have checked the blocks around the player
        and ensured they are allowed to move in the desired direction"""
        
        if keys[key.W] and self.forward:
            self.pos[0] -= dx
            self.pos[2] -= dz
        if keys[key.S] and self.back:
            self.pos[0] += dx
            self.pos[2] += dz
        if keys[key.A] and self.left:
            self.pos[0] -= dz
            self.pos[2] += dx
        if keys[key.D] and self.right:
            self.pos[0] += dz
            self.pos[2] -= dx
            

    
    def update(self,dt,keys):
        """The Player update function called everytime the window is updated"""
        return self.update_movement(dt, keys)
