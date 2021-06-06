import pygame, sys
from math import tan, sin, cos, sqrt
from data_structures import *
from pygame.locals import *

pygame.init()
pygame.display.set_caption("3D Projection")
clock = pygame.time.Clock()

black_color = (0, 0, 0)
white_color = (255, 255, 255)
grey_color = (25, 25, 25)
red_color = (255, 100, 100)
teal_color = (100, 255, 255)
green_color = (100, 255, 100)
default_color = white_color

FPS = 24
surface_scale = 1
surface_w, surface_h = 512, 512
window_w, window_h = surface_w * surface_scale, surface_h * surface_scale
surface = pygame.Surface((surface_w, surface_h))
window = pygame.display.set_mode((window_w, window_h))

vCamera = vector(0, 0, 0)

mesh = mesh('bunnystanford2.obj')
matProj = mat4x4()

# Projection Matrix
fNear = 0.1
fFar = 1000
fFov = 90
fAspectRatio = surface_h / surface_w
fFovRad = 1 / tan(fFov * 0.5 / 180 * 3.14159) # radians inside

matProj.m[0][0] = fAspectRatio * fFovRad
matProj.m[1][1] = fFovRad
matProj.m[2][2] = fFar / (fFar - fNear)
matProj.m[3][2] = (- fFar * fNear) / (fFar - fNear)
matProj.m[2][3] = 1

# Rotation Matrixes
matRotX = mat4x4()
matRotZ = mat4x4()
fTheta = 0

#it = 0

# initialize unit square

def init_square():
    # one square has 8 vertices, 6 faces, 12 triangles
    triangles = []
    triangles.append([

        # SOUTH 
        triangle(vector(0,0,0), vector(1,0,0), vector(0,1,0)),
        triangle(vector(1,0,0), vector(1,1,0), vector(0,1,0)),

        # WEST 
        triangle(vector(0,1,1), vector(0,0,1), vector(0,0,0)),
        triangle(vector(0,0,0), vector(0,1,0), vector(0,1,1)),

        # NORTH 
        triangle(vector(1,1,1), vector(1,0,1), vector(0,0,1)),
        triangle(vector(0,0,1), vector(0,1,1), vector(1,1,1)),

        # EAST 
        triangle(vector(1,0,0), vector(1,0,1), vector(1,1,0)),
        triangle(vector(1,0,1), vector(1,1,1), vector(1,1,0)),

        # TOP 
        triangle(vector(0,0,0), vector(0,0,1), vector(1,0,1)),
        triangle(vector(1,0,1), vector(1,0,0), vector(0,0,0)),
        
        # BOTTOM 
        triangle(vector(0,1,1), vector(0,1,0), vector(1,1,0)),
        triangle(vector(1,1,0), vector(1,1,1), vector(0,1,1))

    ])

    global mesh
    for tris in triangles[0]:
        mesh.add_triangle(tris)

def update_rotation_matrixes():
    global fTheta, matRotZ, matRotX

    fTheta += 0.05

    matRotZ.m[0][0] = cos(fTheta)
    matRotZ.m[0][1] = sin(fTheta)
    matRotZ.m[1][0] = -sin(fTheta)
    matRotZ.m[1][1] = cos(fTheta)
    matRotZ.m[2][2] = 1
    matRotZ.m[3][3] = 1

    matRotX.m[0][0] = 1
    matRotX.m[1][1] = cos(fTheta * 0.5)
    matRotX.m[1][2] = sin(fTheta * 0.5)
    matRotX.m[2][1] = -sin(fTheta * 0.5)
    matRotX.m[2][2] = cos(fTheta * 0.5)
    matRotX.m[3][3] = 1


def draw_mesh():

    update_rotation_matrixes()

    to_draw = []

    for tri in mesh.triangles:
        
        # rotate
        rotZ_p1 = matRotZ.multiplyVector(tri.p1)
        rotZ_p2 = matRotZ.multiplyVector(tri.p2)
        rotZ_p3 = matRotZ.multiplyVector(tri.p3)

        rotZX_p1 = matRotX.multiplyVector(rotZ_p1)
        rotZX_p2 = matRotX.multiplyVector(rotZ_p2)
        rotZX_p3 = matRotX.multiplyVector(rotZ_p3)
        

        triRotated = triangle(rotZX_p1, rotZX_p2, rotZX_p3)

        # translate
        triRotated.add_z(25)

        # faces in view
        line1 = vector(
            triRotated.p2.x - triRotated.p1.x,
            triRotated.p2.y - triRotated.p1.y,
            triRotated.p2.z - triRotated.p1.z
        )

        line2 = vector(
            triRotated.p3.x - triRotated.p1.x,
            triRotated.p3.y - triRotated.p1.y,
            triRotated.p3.z - triRotated.p1.z
        )

        normal = vector(
            line1.y * line2.z - line1.z * line2.y,
            line1.z * line2.x - line1.x * line2.z,
            line1.x * line2.y - line1.y * line2.x
        )

        l = sqrt(normal.x * normal.x + normal.y * normal.y + normal.z * normal.z) # normalizing normal
        if l != 0:
            normal.x /= l
            normal.y /= l
            normal.z /= l

        #if normal.z > 0:
        if (
            normal.x * (triRotated.p1.x - vCamera.x) + 
            normal.y * (triRotated.p1.y - vCamera.y) + 
            normal.z * (triRotated.p1.z - vCamera.z) < 0
        ):
            # Illumination
            light_dir = vector(0, 0, -1)
            l = sqrt(light_dir.x * light_dir.x + light_dir.y * light_dir.y + light_dir.z * light_dir.z)
            
            light_dir.x /= l
            light_dir.y /= l
            light_dir.z /= l

            dot_prod = normal.x * light_dir.x + normal.y * light_dir.y + normal.z * light_dir.z

            # project
            new_p1 = matProj.multiplyVector(triRotated.p1)
            new_p2 = matProj.multiplyVector(triRotated.p2)
            new_p3 = matProj.multiplyVector(triRotated.p3)

            # scale to view
            new_p1.x += 1
            new_p1.y += 1

            new_p2.x += 1
            new_p2.y += 1

            new_p3.x += 1
            new_p3.y += 1

            new_p1.x *= (0.5 * surface_w)
            new_p1.y *= (0.5 * surface_h)

            new_p2.x *= (0.5 * surface_w)
            new_p2.y *= (0.5 * surface_h)

            new_p3.x *= (0.5 * surface_w)
            new_p3.y *= (0.5 * surface_h)

            new_tri = triangle(new_p1, new_p2, new_p3)
            new_tri.luminance = dot_prod

            to_draw.append(new_tri)

    # sort triangles back to front (painter's algorithm)
    to_draw.sort(key=lambda x: (x.p1.z + x.p2.z + x.p3.z)/3, reverse=True)

    for tris in to_draw:
        tris.draw_fill(surface)
        #tris.draw_wire(surface, black_color, 1)

    #global it    
    #pygame.image.save(window,"gif/" +  str(it) + "_iteration.jpeg")
    #it += 1

#init_square()
#update_rotation_matrixes()

while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    
    surface.fill(black_color)

    #update_screen()
    draw_mesh()

    window.blit(pygame.transform.scale(surface, window.get_rect().size), (0, 0))

    pygame.display.update()
    clock.tick(FPS)


