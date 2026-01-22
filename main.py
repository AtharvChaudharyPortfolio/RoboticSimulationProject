import pygame
import math


wall_list = pygame.sprite.Group()
radius = 20
wheelDist = 40
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
        self.text=self.font.render('default', True, self.white)
        self.textRect=self.text.get_rect()
        self.textRect.center=(dimentions[1]-1150,
                              dimentions[0] -585)
        self.endSimText = self.font.render('default', True, self.white)
        self.endSimRect = self.endSimText.get_rect()
        self.endSimRect.center = (600, 300)

    def write_info(self, Vl, Vr, theta):
        txt=f"Left Wheel Vel = {Vl} Right Wheel Vel = {Vr} theta = {int(math.degrees(theta))} degrees"
        self.text=self.font.render(txt, True, self.black)
        self.map.blit(self.text, self.textRect)
    def gameOver(self):
        gameOver="Simulation failed: Robot Crashed - quitting application"
        self.endsimText=self.font.render(gameOver, True, self.black, self.white)
        self.map.blit(self.endsimText, self.endSimRect)

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((0,125,125))
        self.rect = (x,y,width,height)


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
                elif event.key == pygame.K_KP8:
                    self.vr = (self.vr + self.vl)/2
                    self.vl = self.vr
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

top = Wall(0, 0 , 1200 ,40)
bottom = Wall(0, 565, 1200,40)
left = Wall(0, 0, 40, 600)
right = Wall(1165, 0, 40, 600)
wall_list.add(right)
wall_list.add(left)
wall_list.add(bottom)
wall_list.add(top)

environment=Envir(dims)

robot = Robot(start, r"C:\Users\Athar\PycharmProjects\RoboticSimulationProject\graphics\RobotImage-1.png",
            0.01*3779.52)
dt =0
v = 0
robot_radius = 20
lasttime = pygame.time.get_ticks()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        robot.move(event)
    dt=(pygame.time.get_ticks()-lasttime)/1000
    v = (robot.vl + robot.vr)/2
    omega = (robot.vr - robot.vl)/wheelDist
    theta_prediction = robot.theta + omega*dt
    x_pred = robot.x + v *math.cos(theta_prediction) *dt
    y_pred = robot.y + v*math.sin(theta_prediction)*dt
    collision_rect = pygame.Rect(0,0, radius*2, radius*2)
    collision_rect.center = (x_pred,y_pred)
    hits = pygame.sprite.spritecollide(
        robot,
        wall_list,
        False,
        collided=lambda s1, s2: collision_rect.colliderect(s2.rect)
    )
    if hits:
        robot.vr =0
        robot.vl = 0
        environment.gameOver()
        pygame.display.update()
        pygame.time.delay(1000)
        running = False
    else:
        robot.move()
    lasttime = pygame.time.get_ticks()
    pygame.display.update()
    environment.map.fill(environment.gray)
    robot.draw(environment.map)
    wall_list.draw(environment.map)
    environment.write_info(int(robot.vl),
                           int(robot.vr),
                           robot.theta)


