import pygame

class vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return str((self.x, self.y, self.z))
        
    def __str__(self):
        return str((self.x, self.y, self.z))
        

      
class triangle:
    def __init__(self, p1, p2, p3):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p = [
                    (p1.x , p1.y), 
                    (p2.x , p2.y), 
                    (p3.x , p3.y)
                ]
        self.luminance = 0

    def add_z(self, z):
        self.p1.z += z
        self.p2.z += z
        self.p3.z += z
        

    def draw_fill(self, surface):
        color = abs(self.luminance * 255)
        pygame.draw.polygon(surface, (color, color, color), self.p, 0)
    
    def draw_wire(self, surface, color, width):
        pygame.draw.polygon(surface, color, self.p, width)

    def __repr__(self):
        return str((self.p1, self.p2, self.p3))

    def __str__(self):
        return str((self.p1, self.p2, self.p3))
        
       
class mesh:
    def __init__(self, file = None):

        self.triangles = []

        
        with open(file) as f:
            vecs = []
            for line in f.readlines():
                if line[0] == 'v':
                    coords =  line[2:].split()
                    
                    vec = vector(float(coords[0]), 
                                 float(coords[1]), 
                                 float(coords[2]))
                    vecs.append(vec)

                elif line[0] == 'f':
                    vec_index =  line[2:].split()

                    tris = triangle(vecs[int(vec_index[0]) - 1], 
                                    vecs[int(vec_index[1]) - 1], 
                                    vecs[int(vec_index[2]) - 1])
                    self.triangles.append(tris)
        
        print(len(self.triangles))
        
        #print('could not open file')
        #self.triangles = []


    def add_triangle(self, triangle):
        self.triangles.append(triangle)

class mat4x4:
    def __init__(self):
        self.m = [[0,0,0,0], 
                  [0,0,0,0], 
                  [0,0,0,0], 
                  [0,0,0,0]]

    def multiplyVector(self, v):

        o = vector(

            # new x
            (v.x * self.m[0][0] + v.y * self.m[1][0] + v.z * self.m[2][0] + self.m[3][0]),

            # new y
            (v.x * self.m[0][1] + v.y * self.m[1][1] + v.z * self.m[2][1] + self.m[3][1]),

            # new z
            (v.x * self.m[0][2] + v.y * self.m[1][2] + v.z * self.m[2][2] + self.m[3][2]),

        )

        w = (v.x * self.m[0][3] + v.y * self.m[1][3] + v.z * self.m[2][3] + self.m[3][3])

        if w != 0:
            o.x /= w
            o.y /= w
            o.z /= w

        return o

