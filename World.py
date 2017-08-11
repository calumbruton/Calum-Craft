"""
The World Class 

"""

from random import randint
import pyglet
from pyglet.gl import *
from pyglet.window import mouse, key
import math
from noise import pnoise2

from Blocks import *


#Biome's are 80x80 cubes
BIOME_SIZE = 40
CUBESIZE = 1


class World:

    def get_tex(self,file):
        """
        load the texture file and return the texture
        group to be used in block creation
        """
        tex = pyglet.image.load(file).texture
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,GL_NEAREST)
        return pyglet.graphics.TextureGroup(tex)


    def __init__(self, SEEDX, SEEDZ):

        # Import the texture pack to be used in the world
        # 2 choices currently -- texturepack and texturePack2
        self.textures = self.get_tex('texturePackBig.png')
        
        # Create a collection of vertex lists for batched rendering
        self.batch = pyglet.graphics.Batch()

        # Create a dictionary containing all of the blocks on the map
        # The key is the block position in the form (x,y,z) and the value is the block type
        self.block_map = {}

        # Mapping from position to a pyglet `VertextList` for all shown blocks.
        # When an object is removed from here it should be no longer rendered
        self._shownBlocks = {}

        # Create the landscape
        self.create_world(SEEDX,0,SEEDZ)
    
        # render the map to display the blocks in the block map
        self.renderMap()

        
    def draw(self):
        """draws the batch in the World"""
        self.batch.draw()

    def add_block(self, position, block_type):
        """add_block adds a blocks position and it's type to the map of all blocks in the World
        """
        if position in self.block_map:
            del self.block_map[position]
        self.block_map[position] = block_type



    def del_block(self, position):
        """del_block removes a block from the map of all blocks in the World
        """
        if position in self.block_map:
            # returns the pyglet vertex list associated with the position and deletes it from the render batch
            self._shownBlocks.pop(position).delete()
            # Then remove the position key from all of the blocks in the world
            del self.block_map[position]
        

    def renderMap(self):
        """
        renderMap takes all of the blocks in the world and and adds them to the pyg vertex dictionary and batch 
        This is used at initalization of the world
        """
        for position, block_type in self.block_map.items():
            if block_type in [WATER, LAVA]:
                self._shownBlocks[position] = self.batch.add(24, GL_QUADS, self.textures, ('v3f', fluid_cube_vertices(*position, CUBESIZE)), ('t2f', block_type))               
            else:
                self._shownBlocks[position] = self.batch.add(24, GL_QUADS, self.textures, ('v3f', vertices(*position, CUBESIZE)), ('t2f', block_type))
        

    
    def place_block(self, position, block_type):
        """
        place_block is called whenever the player tries to place a block
        unlike add_block, place_block adds it to the batch to be rendered immediately
        """
        #delete a block if it is already in this position
        if position in self.block_map:
            self.del_block(position)
        
        self.block_map[position] = block_type
        if block_type in [WATER, LAVA]:
            self._shownBlocks[position] = self.batch.add(24, GL_QUADS, self.textures, ('v3f', fluid_cube_vertices(*position, CUBESIZE)), ('t2f', block_type))
        else:
            self._shownBlocks[position] = self.batch.add(24, GL_QUADS, self.textures, ('v3f', vertices(*position, CUBESIZE)), ('t2f', block_type))


    def hit_test(self, origin, vector, distance=20, increments=10):
        """ Hit test for first block. Returns coordinates of first block that 
        is hit, in addition to the empty space before it. """
        x, y, z = origin
        dx, dy, dz = vector
        dx, dy, dz = dx/increments, dy/increments, dz/increments
        for k in range(increments*distance):
            block_loc = (x + k*dx, y + k*dy, z + k*dz)
            block_loc = closest_int_position(block_loc)
            if (block_loc in self.block_map):
                j = k-1
                empty_loc = closest_int_position((x+j*dx, y+j*dy, z+j*dz))
                return block_loc, empty_loc
        return None, None


    def create_world(self, x, y, z):
        """Create the map in which the player explores
        This function randomly chooses different biomes to create a map for the player

        The map is currently created by making a square of 9 biomes with the centre being the spawn landscape
        """
        d = BIOME_SIZE
        
        self.create_spawn_landscape(x,y,z)
        self.mountains_biome(x+d,y,z)
        self.rolling_hills_biome(x,y,z+d)
        self.mountains_biome(x+d,y,z+d)
        self.mountains_biome(x-d,y,z)
        self.mountains_biome(x,y,z-d)
        self.desert_biome(x+d,y,z-d)
        self.mountains_biome(x-d,y,z+d)
        self.mountains_biome(x-d,y,z-d)

        w = int(BIOME_SIZE * 1.5)

        # Create an open topped box of indestructible obsidian on the bottom and pink glass as walls
        for xPos in range(x-w-1, x+w+2, 1):
            for zPos in range(z-w-1, z+w+2,1):
                self.add_block((xPos, y-8, zPos), OBSIDIAN)
                if (zPos in [z-w-1, z+w+1]) or (xPos in [x-w-1, x+w+1]):
                    for yPos in range(y-7, y+10, 1):
                        self.add_block((xPos, yPos, zPos), BLUE_GLASS)




    def create_spawn_landscape (self, xPos, yPos, zPos):
        """Create a landscape across the map using perlin noise"""
        
        r = int(BIOME_SIZE/2)
        Map_Depth = yPos-8
        octaves = 1
        freq = 10*octaves


        for x in range(xPos-r, xPos+r+1, 1):
            for z in range(zPos-r, zPos+r+1, 1):

                #Make Land Flat around Spawn House
                if (x in range(xPos-7, xPos+13, 1)) and (z in range(zPos-9, zPos+9, 1)):
                    for y in range(Map_Depth, yPos+1, 1):
                        self.add_block((x, y, z), GRASS)

                #Otherwise use perlin noise to determine height map
                else:
                    height = int(pnoise2(x/freq, z/freq, octaves, 0.25)*6)
                    groundLevel = yPos + height
                    for y in range(Map_Depth, groundLevel, 1):
                        if y > yPos-2:
                            self.add_block((x, y, z), GRASS)
                        else:
                            self.add_block((x, y, z), SAND)

                    for space in range (groundLevel, groundLevel + 2):
                        if space < yPos -1:
                            self.add_block((x, space, z), WATER)
                
                
                    # Give every square of the landscape that is grass give a 1 in 40 chance of having a tree
                    if randint(1,60) == 1 and yPos+height-1 > yPos-3:
                        self.create_Tree(x, yPos+height, z, 'plains')


        #Create a House
        self.create_House(xPos, yPos, zPos)


    def rolling_hills_biome(self, xPos, yPos, zPos):
        """Use perlin noise to create a rolling hills biome
        """
        r = int(BIOME_SIZE/2)
        Map_Depth = yPos-8
        octaves = 1
        freq = 10*octaves
        
        for x in range(xPos-r, xPos+r+1, 1):
            for z in range(zPos-r, zPos+r+1, 1):
        
                height = int(pnoise2(x/freq, z/freq, octaves, 0.25)*6)
                groundLevel = yPos + height
                for y in range(Map_Depth, groundLevel, 1):
                    if y > yPos-2:
                        self.add_block((x, y, z), GRASS)
                    else:
                        self.add_block((x, y, z), SAND)

                for space in range (groundLevel, groundLevel + 2):
                    if space < yPos -1:
                        self.add_block((x, space, z), WATER)
            
    
                # Give every square of the landscape that is grass  a 1 in 60 chance of having a tree
                if randint(1,60) == 1 and yPos+height-1 > yPos-3:
                    self.create_Tree(x, yPos+height, z, 'plains')


    def desert_biome(self, xPos, yPos, zPos):
        """Use perlin noise to create a rolling hills biome
        """
        r = int(BIOME_SIZE/2)
        Map_Depth = yPos-8
        octaves = 1
        freq = 10*octaves
        
        for x in range(xPos-r, xPos+r+1, 1):
            for z in range(zPos-r, zPos+r+1, 1):
        
                height = int(pnoise2(x/freq, z/freq, octaves, 0.25)*3)
                groundLevel = yPos + height
                for y in range(Map_Depth, groundLevel, 1):
                    self.add_block((x, y, z), SAND)


                for space in range (groundLevel, groundLevel + 2):
                    if space < yPos -1:
                        self.add_block((x, space, z), WATER)
            

                # Give every square of the landscape that is grass a 1 in 70 chance of having a cactus
                if randint(1,70) == 1 and yPos+height-1 > yPos-3:
                    self.create_cactus(x, yPos+height, z)


    def mountains_biome(self, xPos, yPos, zPos):
        """Use perlin noise to create a mountains biome with high peaks
        """
        r = int(BIOME_SIZE/2)
        Map_Depth = yPos-8
        octaves = 6
        freq = 11*octaves

        # for all x, z in the biome
        for x in range(xPos-r, xPos+r+1, 1):
            for z in range(zPos-r, zPos+r+1, 1):
        
                height = int(pnoise2(x/freq, z/freq, octaves, 0.5)*80)+2
                groundLevel = yPos + height
                for y in range(Map_Depth, groundLevel, 1):
                    # Add Mountain Grass above certain height
                    if y > yPos-2:
                        self.add_block((x, y, z), MOUNTAINGRASS)
                    # Otherwise add SmoothStone
                    else:
                        self.add_block((x, y, z), SMOOTHSTONE)

                #Add Water to any holes of space below yPos-2
                for space in range (groundLevel, yPos-2):
                    if space < yPos -1:
                        self.add_block((x, space, z), WATER)
            
    
                # Give every square of the landscape that is grass a 1 in 60 chance of having a tree
                if randint(1,60) == 1 and yPos+height-1 > yPos-2:
                    self.create_Tree(x, yPos+height, z, 'mountains')

        
            
    """create a tree of random height from 4 to 7 blocks"""
    def create_Tree(self,xPos, yPos, zPos, biome):
        treeHeight = randint(4,6)

        if biome == 'plains':
            LEAF_TYPE = PLAINS_LEAVES
        elif biome == 'mountains':
            LEAF_TYPE = MOUNTAIN_LEAVES
        
        
        # For every y position of the height of the tree add a wood block
        for y in range (yPos, yPos+treeHeight, 1):
            self.add_block((xPos, y, zPos), WOOD)
        # For every block around the top wood block add leaves and for 2 block positions above
        for x in range(xPos-1, xPos+2, 1):
            for z in range(zPos-1, zPos+2, 1):
                if x==xPos and z==zPos:
                    pass
                self.add_block((x, yPos+treeHeight-1, z),LEAF_TYPE)
                self.add_block((x, yPos+treeHeight, z),LEAF_TYPE)
                self.add_block((x, yPos+treeHeight+1, z),LEAF_TYPE)


    """create a cactus of random height from 3 to 4 blocks tall"""
    def create_cactus(self, xPos, yPos, zPos):
        cactusHeight = randint(3,4)
        # For every y position of the height of the cactus add a block
        for y in range (yPos, yPos+cactusHeight, 1):
            self.add_block((xPos, y, zPos), CACTUS)


    """create a house! 10 squares long and 13 squares wide
    Where the selected location is the center of the house
    xPos - 5 = BackWall, +5 is FrontWall
    zPos + 6 = LeftWall, -7 is rightWall (when looking at door)"""
    def create_House(self, xPos, yPos, zPos):
        for x in range(xPos-5, xPos+6, 1):
            for z in range(zPos-7, zPos+7, 1):

                # Create Floor and Ceiling
                self.add_block((x, yPos, z), PLANK)
                self.add_block((x, yPos+6, z), WOOD)

                # Create Pillars on each inside corner
                if (z == zPos-6 or z == zPos+5) and (x == xPos-4 or x == xPos+4):
                    for y in range(yPos, yPos+6, 1):
                       self.add_block((x, y, z), WOOD)

                # Create Counter Tops and Furnaces on Inside edge of house
                if (z == zPos-6) and (x in range(xPos-3, xPos+4,1)) or (x == xPos-4) and (z in range(zPos-5, zPos+1,1)):
                    if z in [zPos-3, zPos-2]:
                        self.add_block((x, yPos+1, z), FURNACE)
                    else:
                       self.add_block((x, yPos+1, z), STONE)

                # Create Bookshelves inside house
                if (z == zPos+5) and (x in range(xPos-1, xPos+2,1)):
                    for y in range(yPos+1, yPos+4, 1):
                        self.add_block((x, y, z), BOOKSHELF)                                     

                # Create Walls, Windows and other objects on walls
                if z == zPos-7 or z == zPos+6 or x == xPos-5 or x == xPos+5:
                    for y in range(yPos, yPos+6, 1):

                        # Create Pillars on each corner otherwise wall is Brick
                        if (z == zPos-7 or z == zPos+6) and (x == xPos-5 or x == xPos+5):
                            self.add_block((x, y, z), WOOD)
                        
                        # Create Windows on each side
                        elif (y in [yPos+2, yPos+3, yPos+4]) and ((x in [xPos-2, xPos-3, xPos+2,xPos+3]) or (z in [zPos-3, zPos-4, zPos-5, zPos+2,zPos+3, zPos+4])):            
                            self.add_block((x, y, z), GLASS)
                              
                        # Make a Big Window on back side of house
                        elif (x == xPos-5) and (y in [yPos+2, yPos+3, yPos+4]) and (z in range (zPos-5, zPos+5, 1)):
                            self.add_block((x, y, z), GLASS)

                        # Create Doorway 
                        elif (x == xPos+5 ) and (y in [yPos+1, yPos+2, yPos+3]) and (z in [zPos-1, zPos]):
                            if y == yPos+1:
                                self.add_block((x, y, z), DOORBOTTOM)
                            if y == yPos+2:
                                self.add_block((x, y, z), DOORTOP)
                            if y == yPos+3:
                                self.add_block((x, y, z), GLASS)

                        # Create DoorFrame
                        elif (x == xPos+5 ) and (y in [yPos+1, yPos+2, yPos+3, yPos+4]) and (z in [zPos-2, zPos+1]):
                            self.add_block((x, y, z), WOOD)

                        else:
                            self.add_block((x, y, z), BRICK)

        # Create Table Inside
        self.add_block((xPos-1, yPos+1, zPos+1), WOOD)
        self.add_block((xPos, yPos+1, zPos+2), WOOD)
        self.add_block((xPos, yPos+1, zPos+1), WOOD)
        self.add_block((xPos-1, yPos+1, zPos+2), WOOD)


        
        # Create Bushes around house
        for x in range(xPos-6, xPos+7, 1):
            for z in range(zPos-8, zPos+8, 1):
                
                # Don't create bushes at corners of house
                if x == xPos-6:
                    if (z not in [zPos-8, zPos-7, zPos+6, zPos+7]):
                        self.add_block((x, yPos+1, z), BUSH)

                elif z == zPos-8 or z == zPos+7:
                    if (x not in [xPos-6, xPos-5, xPos+5, xPos+6]):
                        self.add_block((x, yPos+1, z), BUSH)                                 
                              

                # Don't create pushes infront of doorway
                elif x == xPos+6:
                    if (z not in [zPos-2, zPos+1, zPos-1, zPos, zPos-8, zPos-7, zPos+6, zPos+7]):
                       self.add_block((x, yPos+1, z), BUSH)
                

        # Create Entrance Path
        for i in range(0,3):
            self.add_block((xPos+6+i, yPos+1, zPos-2), WOOD)
            self.add_block((xPos+6+i, yPos, zPos-1), WOOD)
            self.add_block((xPos+6+i, yPos, zPos), WOOD)
            self.add_block((xPos+6+i, yPos+1, zPos+1), WOOD)
        self.add_block((xPos+9, yPos, zPos-1), WOOD)
        self.add_block((xPos+9, yPos, zPos), WOOD)



