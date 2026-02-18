import pygame
import math


wall_list = pygame.sprite.Group()
radius = 28
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
        gameOver="Attempt failed: Robot Crashed - resetting position"
        self.endsimText=self.font.render(gameOver, True, self.black, self.white)
        self.map.blit(self.endsimText, self.endSimRect)

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((0,125,125))
        self.rect = pygame.Rect(x,y,width,height)
        wall_list.add(self)


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
        self.braking = False
        self.pos = (self.x, self.y)
        self.forward_head = pygame.Vector2(0,0)
        self.left_head = pygame.Vector2(0,0)
        self.right_head = pygame.Vector2(0,0)
        self.origin = pygame.Vector2(0,0)
        self.left_origin = pygame.Vector2(0,0)
        self.right_origin = pygame.Vector2(0,0)
        self.detected = False
        self.turnTimer = 0.3
        self.was_left = False
        self.was_right = False
        self.mode = 0
    def draw(self,map):
        map.blit(self.rotated, self.rect)
    def revert(self, start):
        self.braking = False
        self.x = start[0]
        self.y = start[1]
        self.vl = 0.01*self.m2p
        self.vr = 0.01*self.m2p
        self.theta = 0
    def trajectory(self, surface):
        v = (self.vl+self.vr)/2
        look_ahead_time = 2.0
        forward = pygame.Vector2(math.cos(self.theta), -math.sin(self.theta))
        t_origin = pygame.Vector2(self.rect.center)
        head = t_origin + forward*v*look_ahead_time
        pygame.draw.line(surface, (0,0,0), t_origin, head, 3)
    def raycast(self, surface):
            pred_len = 100.0
            forward = pygame.Vector2(math.cos(self.theta), -math.sin(self.theta))
            right = forward.rotate_rad(-math.pi/2)
            left = forward.rotate_rad(math.pi/2)
            self.origin = pygame.Vector2(self.rect.center)
            self.origin += forward*12
            self.left_origin = self.origin - right*8
            self.right_origin = self.origin+right*8

            self.forward_head = self.origin + forward*pred_len
            self.left_head = self.left_origin + left *pred_len
            self.right_head = self.right_origin + right*pred_len
            pygame.draw.line(surface, (0,225,0), self.origin, self.forward_head, 3)
            pygame.draw.line(surface, (255,0,0), self.left_origin, self.left_head, 3)
            pygame.draw.line(surface, (0,0,255), self.right_origin, self.right_head, 3)
    def move(self):
        if self.mode > 0:
            self.vl = 0.02*self.m2p
            self.vr = -0.02*self.m2p
            self.turnTimer -= dt
            if self.turnTimer <= 0:
                self.mode = 0
        elif self.mode < 0:
            self.vl = -0.02*self.m2p
            self.vr = 0.02*self.m2p
            self.turnTimer -= dt
            if self.turnTimer <= 0:
                self.mode = 0
        else:
            self.vl = 0.01*self.m2p
            self.vr = 0.01*self.m2p

        if abs(self.vl) < 0.1: self.vl =0
        if abs(self.vr) < 0.1: self.vr =0
        if self.braking:
            vr_mult = 2 if self.vr <0 else -2
            vl_mult = 2 if self.vl <0 else -2
            if pygame.time.get_ticks()%200 == 0:
                self.vr += vr_mult*(0.001*self.m2p)
                self.vl += vl_mult*(0.001*self.m2p)
                self.vr = max(self.vr, 0)
                self.vl = max(self.vl, 0)
            if self.vr == 0 and self.vl == 0:
                self.braking = False
        if abs(self.vl)>  self.maxspeed:
            self.vl = self.maxspeed if self.vl>0 else -self.maxspeed
        if abs(self.vr)>  self.maxspeed:
            self.vr = self.maxspeed if self.vr>0 else -self.maxspeed
        self.x += ((self.vl+self.vr)/2)*math.cos(self.theta)*dt
        self.y -= ((self.vl+self.vr)/2)*math.sin(self.theta)*dt
        self.theta += (self.vr -self.vl)/self.w*dt
        self.rotated =pygame.transform.rotozoom(self.img, math.degrees(self.theta),1)
        self.rect = self.rotated.get_rect(center=(self.x,self.y))
        self.pos = (self.x, self.y)
pygame.init()

start=(100,120)

dims=(600,1200)

running = True

top = Wall(0, 0 , 1200 ,40)
bottom = Wall(0, 565, 1200,40)
left = Wall(0, 0, 40, 600)
right = Wall(1165, 0, 40, 600)
maze1 = Wall(0, 200, 500, 40)
maze2 = Wall(700, 0, 40, 600)
maze3 = Wall(500, 200, 40, 240)
maze4 = Wall(0, 400, 350, 40)

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
    dt=(pygame.time.get_ticks()-lasttime)/1000
    v = (robot.vl + robot.vr)/2
    omega = (robot.vr - robot.vl)/wheelDist
    theta_prediction = robot.theta + omega*dt
    x_pred = robot.x + v *math.cos(theta_prediction) *dt
    y_pred = robot.y + v*math.sin(theta_prediction)*dt
    collision_rect = pygame.Rect(0,0, radius*2, radius*2)
    collision_rect.center = (x_pred,y_pred)
    robot.raycast(environment.map)
    robot.trajectory(environment.map)


    left = pygame.sprite.spritecollide(
        robot,
        wall_list,
        False,
        collided=lambda s1, s2: s2.rect.clipline(s1.left_origin, s1.left_head)
    )
    left_dist = None
    right_dist = None
    for wall in left:
        hit = wall.rect.clipline(robot.left_origin, robot.left_head)
        if hit:
            entry = pygame.Vector2(hit[0], hit[1])
            dist = entry.distance_to(robot.left_origin)

            if left_dist is None or dist < left_dist:
                left_dist = dist
    right = pygame.sprite.spritecollide(
        robot,
        wall_list,
        False,
        collided=lambda s1, s2: s2.rect.clipline(s1.right_origin, s1.right_head)
    )
    for wall in right:
        hit = wall.rect.clipline(robot.right_origin, robot.right_head)
        if hit:
            entry = pygame.Vector2(hit[0], hit[1])
            dist = entry.distance_to(robot.right_origin)
            if right_dist is None or dist < right_dist:
                right_dist = dist
    ray_length_L = (robot.left_head - robot.left_origin).length()
    ray_length_R = (robot.right_head - robot.right_origin).length()
    distFromR = ray_length_R
    distFromL = ray_length_L
    if left_dist is not None:
        distFromL = left_dist
    if right_dist is not None:
        distFromR = right_dist
    print(str(distFromL) + " " + str(distFromR))
    robot.mode = (-(distFromL/ray_length_L) +
                      (distFromR/ray_length_R))
    robot.mode = max(-1, min(1,robot.mode))
    print(str(robot.mode))
    robot.was_right = bool(right)
    robot.was_left = bool(left)

    hits = pygame.sprite.spritecollide(
        robot,
        wall_list,
        False,
        collided=lambda s1, s2: collision_rect.colliderect(s2.rect)
    )
    if hits:
        print(str(robot.mode))
        robot.vr =0
        robot.vl = 0
        environment.gameOver()
        pygame.display.update()
        pygame.time.delay(1000)
        robot.revert(start)
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


