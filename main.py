import pygame
import math

class Envir:
    def __init__(self,dimentions):
        self.black = (0,0,0)
        self.gray = (125,125,125)
        self.white =(255,255,255)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)
        self.red = (255,0,0)
        self.yel = (255, 255, 0)
        self.height=dimentions[0]
        self.width = dimentions[1]
        pygame.display.set_caption("Robotic Simulation")
        self.map = pygame.display.set_mode((self.width, self.height))
        self.font=pygame.font.Font("graphics/Pixel Game.otf", 25)
        self.text=self.font.render('default', True, self.white, None)
        self.textRect=self.text.get_rect()
        self.textRect.center=(dimentions[1]-1100,
                              dimentions[0] -550)

    def write_info(self, Vl, Vr, theta):
        txt=f"Left Wheel Vel = {Vl} Right Wheel Vel = {Vr} theta = {int(math.degrees(theta))} degrees"
        self.text=self.font.render(txt, True, self.black, self.gray)
        self.map.blit(self.text, self.textRect)
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
        self.img=pygame.image.load(robotImg)
        self.rotated=self.img
        self.rect=self.rotated.get_rect(center=(self.x,self.y))
    def draw(self,map):
        map.blit(self.rotated, self.rect)
    def move(self,event=None):
        if event is not None:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP4:
                    self.vl +=0.001*self.m2p
                elif event.key == pygame.K_KP1:
                    self.vl -= 0.001*self.m2p
                elif event.key == pygame.K_KP6:
                    self.vr += 0.001*self.m2p
                elif event.key == pygame.K_KP3:
                    self.vr -= 0.001*self.m2p

        if abs(self.vl) < 0.1: self.vl =0
        if abs(self.vr) < 0.1: self.vr =0

        if abs(self.vl)>  self.maxspeed:
            self.vl = self.maxspeed if self.vl>0 else -self.maxspeed
        if abs(self.vr)>  self.maxspeed:
            self.vr = self.maxspeed if self.vr>0 else -self.maxspeed

        self.x += ((self.vl+self.vr)/2)*math.cos(self.theta)*dt
        self.y -= ((self.vl+self.vr)/2)*math.sin(self.theta)*dt
        self.theta += (self.vr -self.vl)/self.w*dt
        self.rotated =pygame.transform.rotozoom(self.img, math.degrees(self.theta),1)
        self.rect = self.rotated.get_rect(center=(self.x,self.y))
pygame.init()

start=(200,200)

dims=(600,1200)

running = True

environment=Envir(dims)

robot = Robot(start, r"C:\Users\Athar\PycharmProjects\RoboticSimulationProject\graphics\RobotImage-1.png",
            0.01*3779.52)
dt =0
lasttime = pygame.time.get_ticks()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        robot.move(event)
    dt=(pygame.time.get_ticks()-lasttime)/1000
    lasttime = pygame.time.get_ticks()
    pygame.display.update()
    environment.map.fill(environment.gray)
    robot.move()
    robot.draw(environment.map)
    environment.write_info(int(robot.vl),
                           int(robot.vr),
                           robot.theta)


