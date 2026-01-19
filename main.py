import pygame
import math

class Envir:
    def __init__(self,dimentions):
        self.black = (0,0,0)
        self.white =(255,255,255)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)
        self.red = (255,0,0)
        self.yel = (255, 255, 0)
        self.height=dimentions[0]
        self.width = dimentions[1]
        pygame.display.set_caption("Robotic Simulation")
        self.map = pygame.display.set_mode((self.width, self.height))

class Robot:
    def __init__(self, startpos, robotImg, width):
        self.m2p=3779.52 #meters to pixel conversion
        self.w=width
        self.x=startpos[0]
        self.y=startpos[1]
        self.theta=0
        self.vl=0.01*self.m2p #left velocity
        self.vr=0.01*self.m2p #right velocity
        self.maxspeed=0.02*self.m2p
        self.minspeec=0.02*self.m2p
        self.img=pygame.image.load(robotImg)
        self.rotated=self.img
        self.rect=self.rotated.get_rect(center=(self.x,self.y))
    def draw(self,map):
        map.blit(self.rotated, self.rect)


pygame.init()

start=(200,200)

dims=(600,1200)

running = True

environment=Envir(dims)

robot = Robot(start, r"C:\Users\Athar\PycharmProjects\RoboticSimulationProject\graphics\RobotImage-1.png",
            0.0001)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.display.update()
    environment.map.fill(environment.black)
    robot.draw(environment.map)

