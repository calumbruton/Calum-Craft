"""
Created By Calum Bruton on May 27th 2017
A minecraft remake
enjoy
"""

#imports
from random import randint
from pyglet.gl import *
from pyglet.window import mouse, key
from noise import pnoise2

# import Player and World class
from Player import *
from World import *


# By changing the seed values you will spawn with a new map using perlin noise!
SEEDX = 50
SEEDZ = 50


PLAYER_HEIGHT = 1.75

class Window(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # set the minimum screen size at 300x200
        self.set_minimum_size(300,200)
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)

        # schedule periodic updates to the window
        pyglet.clock.schedule(self.update)

        # Initialize the World and the Player
        self.world = World(SEEDX, SEEDZ)
        self.player = Player(SEEDX, SEEDZ)

        # The players block type in hand for placement
        self.PLAYER_BLOCK_CHOICE = BRICK
        

        
    def push(self, pos, rot):
        glPushMatrix()
        rot = self.player.rot
        pos = self.player.pos
        glRotatef(-rot[0],1,0,0)
        glRotatef(-rot[1],0,1,0)
        glTranslatef(-pos[0], -pos[1], -pos[2])
    

    def Projection(self): glMatrixMode (GL_PROJECTION); glLoadIdentity()
    def World(self): glMatrixMode(GL_MODELVIEW); glLoadIdentity()


    def set3d(self):
        """Prepare the window to be used for 3d graphics"""
        self.Projection()
        # 70 is the FOV, the width/height is the aspect ration, 0.05 is the minimum render distance and 1000 is the max render distance
        gluPerspective(70,self.width/self.height,0.05,1000)
        self.World()
  

    def set2d(self):
        """
        Prepare the window to be used for 2d graphics
        This is called before drawing the reticle
        """
        self.Projection()
        glOrtho(0, 600, 0, 600, -1, 1)
        self.World()


    """A function and variable that set the mouse to lock in the screen"""
    lock = False
    def setLock(self,state):
        self.lock = state
        self.set_exclusive_mouse(state)
    mouse_lock = property(lambda self:self.lock, setLock)


    def on_mouse_motion(self,x,y,dx,dy):
        """on_mouse_motion is dispatched every time the mouse moves, it calls the windows player objects mouse_motion function"""
        if self.mouse_lock:
            self.player.mouse_motion(dx,dy)

    
    def on_mouse_release(self, x, y, button, modifiers):
        """dispatched when a the mouse button is pressed"""
        playerSightVec = self.player.get_sight_vector()
        bloc_loc, placement_location = self.world.hit_test(self.player.pos, playerSightVec)

        # Get the block type at the block location
        block_type = self.world.block_map[bloc_loc] 
    
        if self.mouse_lock:
            if bloc_loc and ((button == mouse.RIGHT) or ((button == mouse.LEFT) and (modifiers & key.MOD_CTRL))):
                self.world.place_block((placement_location),self.PLAYER_BLOCK_CHOICE)
        
            elif (button == mouse.LEFT):
                if block_type not in [OBSIDIAN, PINK_GLASS, BLUE_GLASS, WATER, LAVA]:
                    self.world.del_block((bloc_loc))
                    

    def on_key_press(self, KEY, MOD):
        """on_key_press is dispatched everytime a key is pressed"""
        if KEY == key.ESCAPE: self.close()
        elif KEY == key.L: self.mouse_lock = not self.mouse_lock
        
        # Give the user shortcuts to pick different block types from Inventory
        # THERES A CLEANER WAY TO IMPLEMENT THIS
        elif KEY == key._1: self.PLAYER_BLOCK_CHOICE = GRASS
        elif KEY == key._2: self.PLAYER_BLOCK_CHOICE = WOOD
        elif KEY == key._3: self.PLAYER_BLOCK_CHOICE = STONE
        elif KEY == key._4: self.PLAYER_BLOCK_CHOICE = BRICK
        elif KEY == key._5: self.PLAYER_BLOCK_CHOICE = PLANK
        elif KEY == key._6: self.PLAYER_BLOCK_CHOICE = GLASS
        elif KEY == key._7: self.PLAYER_BLOCK_CHOICE = LAVA
        elif KEY == key._8: self.PLAYER_BLOCK_CHOICE = BOOKSHELF
        elif KEY == key._9: self.PLAYER_BLOCK_CHOICE = REDBRICK
        elif KEY == key._0: self.PLAYER_BLOCK_CHOICE = WATER

    
    def draw_reticle(self):
        """ Draw the crosshairs in the center of the screen.
        """
        self.set2d()
        glLineWidth(2.0)
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2i', (300,306,300,294)))
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2i', (295,300,305,300)))

    def check_collisions(self, dx, dz):
        """
        Check collisions makes sure the player is not in the same space as a block
        The function is called every time the window is updated
        """
        playerPosition = self.player.pos

        # x,y,z coordinates of the player
        x,y,z = playerPosition


        # VERTICAL COLLISIONS
        # Adjust Player position for height to get feet level
        playerFeetPosition = closest_int_position((x, y-PLAYER_HEIGHT, z))

        # If the players position is the same as a blocks position then move the player a spot up
        # This is to walk on top of blocks
        if playerFeetPosition in self.world.block_map:
            # whenever there is ground underneath the player that isn't water revert their falling velocity to 0
            if self.world.block_map[playerFeetPosition] != WATER:
                self.player.vert_velocity = 0
                self.player.GROUND_BENEATH_PLAYER = True
                self.player.IN_FLUID = False
                FLUID_VELOCITY_MULT = 1

            # If it is water 
            else:
                self.player.GROUND_BENEATH_PLAYER = False
                self.player.vert_velocity = -3
                self.player.IN_FLUID = True
                FLUID_VELOCITY_MULT = 0.30
                
        else:
            FLUID_VELOCITY_MULT = 1
            self.player.GROUND_BENEATH_PLAYER = False
            self.player.IN_FLUID = False

        # DIRECTIONAL COLLISIONS

        # dx > dz so player moving forward more in the dx direction
        if dx > dz:
            dx_padding = 0.40
            dz_padding = 0.25
            if dx > 0: dx += dx_padding
            else: dx -= dx_padding
            if dz > 0: dz += dz_padding               
            else: dz -= dz_padding

        else:
            dx_padding = 0.25
            dz_padding = 0.40
            if dx > 0: dx += dx_padding
            else: dx -= dx_padding
            if dz > 0: dz += dz_padding               
            else: dz -= dz_padding
                
        # Check locations arount the player 2 locations for each side because
        # a block above waist or below waist height can stop player movement in said direction
        f1, f2 = closest_int_position((x-dx, y, z-dz)), closest_int_position((x-dx, y-1, z-dz)) #Forward
        b1, b2 = closest_int_position((x+dx, y, z+dz)), closest_int_position((x+dx, y-1, z+dz)) #Back
        l1, l2 = closest_int_position((x-dz, y, z+dx)), closest_int_position((x-dz, y-1, z+dx)) #Left
        r1, r2 = closest_int_position((x+dz, y, z-dx)), closest_int_position((x+dz, y-1, z-dx)) #Right

        # Check if there is a block on the map in one of the specified position for each block and movement respectively
        if any(i in self.world.block_map for i in [f1, f2]):
                self.player.forward = False
        else: self.player.forward = True

        if any(i in self.world.block_map for i in [b1, b2]):
                self.player.back = False
        else: self.player.back = True

        if any(i in self.world.block_map for i in [l1, l2]):
                self.player.left = False
        else: self.player.left = True


        if any(i in self.world.block_map for i in [r1, r2]):
                self.player.right = False
        else: self.player.right = True
                
            

    def draw_focused_block(self):
        """ Draw black edges around the block that is currently under the
        crosshairs.
        """
        vector = self.player.get_sight_vector()
        block = self.world.hit_test(self.player.pos, vector)[0]
        if block:
            x, y, z = block
            vertex_data = vertices(x, y, z, 1)
            #glColor3d(0, 0, 0)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            pyglet.graphics.draw(24, GL_QUADS, ('v3f', vertex_data))
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    
    def update(self, dt):
        """
        The update function is called on a scheduled timer
        every window update calls the player update function
        """
        dx, dz = self.player.update(dt,self.keys)
        self.check_collisions(dx,dz)
        self.player.update_location(self.keys, dx, dz)
        self.world.batch.draw()

        
    def on_draw(self):
        """The EventLoop class (you use it by pyglet.app.run()) dispatches the on_draw event regulary."""
        self.clear()
        self.set3d()
        self.push(self.player.pos, self.player.rot)
        self.world.draw()
        self.draw_focused_block()
        self.draw_reticle()
        glPopMatrix()


    def window_setup(self):
        """Prepare the window for the application
        """
        glClearColor(0.5, 0.7, 1, 1)
        # Enable transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)



    def prepare_fog(self): 
        """ Configure the OpenGL fog properties.
        """
        # Enable fog. Fog "blends a fog color with each rasterized pixel fragment's
        # post-texturing color."
        glEnable(GL_FOG)
        # Set the fog color.
        glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5, 0.69, 1.0, 1))
        # Say we have no preference between rendering speed and quality.
        glHint(GL_FOG_HINT, GL_DONT_CARE)
        # Specify the equation used to compute the blending factor.
        glFogi(GL_FOG_MODE, GL_LINEAR)
        # How close and far away fog starts and ends. The closer the start and end,
        # the denser the fog in the fog range.
        glFogf(GL_FOG_START, 40.0)
        glFogf(GL_FOG_END, 60.0)





if __name__ == '__main__':
    game_window = Window(width=600, height=480, caption='CalumCraft', resizable=True)
    game_window.window_setup()
    game_window.prepare_fog()
    print("WELCOME TO CALUMCRAFT \n"
          "INSTRUCTIONS: MOVE WITH WASD, JUMP WITH SPACE BAR, RIGHT CLICK TO PLACE BLOCKS, LEFT CLICK TO REMOVE THEM \n"
          "EACH NUMBER 1..9 AND 0 CAN BE CLICKED TO USE A DIFFERENT BLOCK TYPE \n"
          "CLICK 'L' TO LOCK YOUR MOUSE IN THE SCREEN AND AGAIN TO UNLOCK IT, CLICK ESCAPE TO QUIT \n"
          "HAVE FUN!")

    """Calling run begins the application event loop, which processes operating system events, calls pyglet.clock.tick to call scheduled
    functions and calls pyglet.window.Window.on_draw and pyglet.window.Window.flip to update window contents."""
    pyglet.app.run()
