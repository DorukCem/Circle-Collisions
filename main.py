import pygame
from sys import exit
import random
import math

WIDTH = 1200
HEIGHT = 700

pygame.init()
screen = pygame.display.set_mode(( WIDTH , HEIGHT ))
clock = pygame.time.Clock()


class Ball:
   def __init__(self, x, y, radius):
      self.x = x
      self.y = y
      self.velocity_x = 0
      self.velocity_y = 0
      self.acc_x = 0
      self.acc_y = 0
      self.radius = radius
      self.angle = 180
      self.mass = (radius **2) /100


   #Function to get end positions of the radius line in order to draw it
   def get_radius_line_end_position(self):
      angle = (math.pi)/180
      end_x = self.x + self.radius * math.cos(angle)
      end_y = self.y + self.radius * math.sin(angle)
      return (end_x, end_y)

   def draw(self):
      color = (255,255,255)
      end = self.get_radius_line_end_position()
      if selected_ball is self : color = (255,0,0)
      pygame.draw.circle(screen, color, (self.x, self.y), self.radius, 1 )
      pygame.draw.line(screen, color, (self.x, self.y), end )

   def get_coordinate(self):
      return (self.x, self.y)

   def update_ball(self):
      self.acc_x = -self.velocity_x*0.01
      self.acc_y = -self.velocity_y*0.01
      self.velocity_x += self.acc_x
      self.velocity_y += self.acc_y
      self.x += self.velocity_x
      self.y += self.velocity_y
      

      if self.x < 0: ball.x += WIDTH
      if self.x >= WIDTH: ball.x -= WIDTH
      if self.y < 0: self.y += HEIGHT
      if self.y >HEIGHT: self.y -= HEIGHT

      if self.velocity_x**2 + self.velocity_y**2 < 0.03:
         self.velocity_y = 0
         self.velocity_x = 0


def is_point_in_circle(point, ball):
   px, py = point
   return (ball.x - px) **2 + (ball.y - py)**2 < ball.radius**2


def resolve_static_collision(ball, target):
   distance = math.sqrt((ball.x - target.x)**2 + (ball.y - target.y)**2)
   overlap = (distance - ball.radius - target.radius)/2

   #displace ball
   ball.x -= overlap * (ball.x - target.x)/distance
   ball.y -= overlap * (ball.y - target.y)/distance

   #displace target ball
   target.x += overlap * (ball.x - target.x )/distance
   target.y += overlap * (ball.y - target.y)/distance

def resolve_dynamic_collision(ball, target):
   distance = ball.radius + target.radius
   m1 = ball.mass
   m2 = target.mass

   # Normal unit vector
   nx = (target.x- ball.x) / distance
   ny = (target.y- ball.y) / distance

   # Tanget unit vector
   tx = -ny
   ty = nx

   #normal velocity vectors 
   norm_vel_ball = ball.velocity_x * nx + ball.velocity_y * ny
   norm_vel_target = target.velocity_x * nx + target.velocity_y * ny

   #tangetial velocity vectors
   tgt_vel_ball = ball.velocity_x * tx + ball.velocity_y * ty
   tgt_vel_target = target.velocity_x * tx + target.velocity_y * ty

   ball.velocity_x = tgt_vel_ball * tx + nx*(norm_vel_ball * (m1-m2) + 2 * m2 * norm_vel_target)/(m1+m2)
   ball.velocity_y = tgt_vel_ball * ty + ny*(norm_vel_ball * (m1-m2) + 2 * m2 * norm_vel_target)/(m1+m2)
   target.velocity_x = tgt_vel_target * tx + nx*(norm_vel_target * (m2 - m1) + 2 * m1 * norm_vel_ball)/(m1+m2)
   target.velocity_y = tgt_vel_target * ty + ny*(norm_vel_target * (m2 - m1) + 2* m1 * norm_vel_ball)/(m1+m2)


#check for collision for every ball againts every other ball
def collision_check(balls):
   list_of_collisions = []
   for i in range(len(balls)):
      for  j in range(i+1, len(balls)):
         ball = balls[i]
         target = balls[j]
         #comparision if distance between circles is smaller than the sum of their raidius
         if (ball.radius + target.radius)**2 >= (ball.x - target.x)**2 + (ball.y - target.y)**2:
            list_of_collisions.append((ball, target))

   return list_of_collisions


colliding_balls = []
balls_list = [Ball(300, 400, 60), Ball(500, 400, 60), Ball(600, 400, 20), Ball(700, 400, 20), Ball(900, 400, 40)]
selected_ball = None
cue_ball = None

while True:
   for event in pygame.event.get():
      if event.type == pygame.QUIT:
         pygame.quit()
         exit()

      #select ball if mouse get pressed
      if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
         for ball in balls_list:
            if is_point_in_circle(pygame.mouse.get_pos(), ball):
               selected_ball = ball
               break
      if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
         selected_ball = None
      
      if selected_ball:
         selected_ball.velocity_x = 0 ; selected_ball.velocity_y = 0
         selected_ball.x, selected_ball.y = pygame.mouse.get_pos()

      if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
         for ball in balls_list:
            if is_point_in_circle(pygame.mouse.get_pos(), ball):
               cue_ball = ball
               break
               
      if event.type == pygame.MOUSEBUTTONUP and event.button == 3 and cue_ball:
         cue_ball.velocity_x = 0.1* (cue_ball.x - pygame.mouse.get_pos()[0])
         cue_ball.velocity_y = 0.1* (cue_ball.y - pygame.mouse.get_pos()[1])
         cue_ball = None         

   
   #Background Color
   screen.fill((10 ,10 ,10))
   
   for ball in balls_list:
      ball.update_ball()
      ball.draw()
      
      
      colliding_balls = collision_check(balls_list)
      for pair in colliding_balls:
         pygame.draw.line(screen, (200,0,0), pair[0].get_coordinate(), pair[1].get_coordinate()) 
         resolve_static_collision(pair[0], pair[1])
         resolve_dynamic_collision(pair[0], pair[1])

   if cue_ball: 
      pygame.draw.line(screen, (255,255,0), cue_ball.get_coordinate(), pygame.mouse.get_pos())

   
   pygame.display.update()
   clock.tick(60)
