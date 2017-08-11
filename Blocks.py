"""
Block functions
These are used to get cubes and create them in the world class
"""

def vertices(x,y,z,edgelength):
        """x,y,z are 3d coordinates of the cube and n is the edge length
        The function returns the vertices of the cube in a tuple
        """

        #Make n half the edgelength
        n = edgelength*0.5
        
        return (
        x-n,y+n,z-n, x-n,y+n,z+n, x+n,y+n,z+n, x+n,y+n,z-n,  # top
        x-n,y-n,z-n, x+n,y-n,z-n, x+n,y-n,z+n, x-n,y-n,z+n,  # bottom
        x-n,y-n,z-n, x-n,y-n,z+n, x-n,y+n,z+n, x-n,y+n,z-n,  # left
        x+n,y-n,z+n, x+n,y-n,z-n, x+n,y+n,z-n, x+n,y+n,z+n,  # right
        x-n,y-n,z+n, x+n,y-n,z+n, x+n,y+n,z+n, x-n,y+n,z+n,  # front
        x+n,y-n,z-n, x-n,y-n,z-n, x-n,y+n,z-n, x+n,y+n,z-n,  # back
        )

def fluid_cube_vertices(x,y,z,edgelength):
        """x,y,z are 3d coordinates of the cube and n is the edge length
        returns the vertices of the cube

        The function returns the vertices of the cube with the y position shifted down
        on the top vertice to give fluids their unique look
        """

        #Make n half the edgelength
        n = edgelength*0.5
        # fluid drop level
        d = 0.2
        
        return (
        x-n,y+n-d,z-n, x-n,y+n-d,z+n, x+n,y+n-d,z+n, x+n,y+n-d,z-n,  # top
        x-n,y-n,z-n, x+n,y-n,z-n, x+n,y-n,z+n, x-n,y-n,z+n,  # bottom
        x-n,y-n,z-n, x-n,y-n,z+n, x-n,y+n-d,z+n, x-n,y+n-d,z-n,  # left
        x+n,y-n,z+n, x+n,y-n,z-n, x+n,y+n-d,z-n, x+n,y+n-d,z+n,  # right
        x-n,y-n,z+n, x+n,y-n,z+n, x+n,y+n-d,z+n, x-n,y+n-d,z+n,  # front
        x+n,y-n,z-n, x-n,y-n,z-n, x-n,y+n-d,z-n, x+n,y+n-d,z-n,  # back
        )



def tex_coord(x, y, n=8):
        """ Returns 2D coordinates for a square. This represents a single face from
        the texture atlas. """
        m = 1.0/n
        dx = x * m
        dy = y * m
        return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m


def tex_coords(top, bottom, side):
        """ Returns 2D coordinates for 6 squares in the form of a 48 float tuple. Each
        group of 4 coordinates represents a square face. """
        top = tex_coord(*top)
        bottom = tex_coord(*bottom)
        side = tex_coord(*side)
        return top + bottom + side*4


def tex_coords_oneDifSide(top, bottom, side, diffSide):
        """ Returns 2D coordinates for 6 squares in the form of a 48 float tuple. Each
        group of 4 coordinates represents a square face.
        ----------
        Works the same as tex_coords except for one side of the block that is different
        """
        top = tex_coord(*top)
        bottom = tex_coord(*bottom)
        side = tex_coord(*side)
        diff_side = tex_coord(*diffSide)
        
        return top + bottom + side + diff_side + side*2

"""
The coordinates of each type of block in the texture png image
The first tuple is for the top, second for the bottom, and third for the sides
This is the same for each type of block except grass
"""
GRASS = tex_coords((1, 0), (0, 1), (0, 0))
SAND = tex_coords((1, 1), (1, 1), (1, 1))
BRICK = tex_coords((2, 0), (2, 0), (2, 0))
STONE = tex_coords((2, 1), (2, 1), (2, 1))
SMOOTHSTONE = tex_coords((4,3), (4,3), (4,3))
WOOD = tex_coords((3,0), (3,0), (3,1))
PLAINS_LEAVES = tex_coords((1,2), (1,2), (1,2))
MOUNTAIN_LEAVES = tex_coords((6, 2), (6, 2), (6, 2))
PLANK = tex_coords((3,2), (3,2), (3,2))
GLASS = tex_coords((2,2), (2,2), (2,2))
CACTUS = tex_coords((2,3),(1,3),(3,3))
DOORTOP = tex_coords((0, 3), (0, 3), (0, 3))
DOORBOTTOM = tex_coords((0, 2), (0, 2), (0, 2))
WATER = tex_coords((4,0), (4,0), (4,6))
BUSH = tex_coords((4,1), (4,1), (4,1))
REDBRICK = tex_coords((4,2), (4,2), (4,2))
FURNACE = tex_coords_oneDifSide((5,2), (5,2), (5,1), (5,0))
MOUNTAINGRASS = tex_coords((6, 1), (0, 1), (6, 0))
BOOKSHELF = tex_coords((7, 2), (7, 2), (7, 2))
LAVA = tex_coords((7, 0), (7, 0), (7, 0))
OBSIDIAN = tex_coords((5,3), (5,3), (5,3))
PINK_GLASS = tex_coords((6,3), (6,3), (6,3))
BLUE_GLASS = tex_coords((7,3), (7,3), (7,3))



def closest_int_position(position):
    """
    Given a position returns it's closest integer position
    """
    
    x, y, z = position
    x, y, z = (int(round(x)), int(round(y)), int(round(z)))
    return (x, y, z)


