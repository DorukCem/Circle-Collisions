import pygame
from sys import exit
import random
import math

BALL_COLOR = "#ffc845"
EDGE_COLOR = "#d6d2c4"
BACKGROUND_COLOR = "#000000"

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
      self.mass = radius/10
      self.is_fake_ball = False
   
   def get_coordinate(self):
      return (self.x, self.y)

   def draw_ball(self):
      color = BALL_COLOR
      if selected_ball is self : color = (255,0,0) 
      pygame.draw.circle(screen, color, (self.x, self.y), self.radius, 1 )

   def update_ball(self):
      #Imitate friction
      self.acc_x = -self.velocity_x*0.006
      self.acc_y = -self.velocity_y*0.006

      self.velocity_x += self.acc_x
      self.velocity_y += self.acc_y
      self.x += self.velocity_x
      self.y += self.velocity_y

      #Balls stay on screen 
      if self.x < 0: ball.x += WIDTH
      if self.x >= WIDTH: ball.x -= WIDTH
      if self.y < 0: self.y += HEIGHT
      if self.y >HEIGHT: self.y -= HEIGHT

      #Balls eventually stop
      if self.velocity_x**2 + self.velocity_y**2 < 0.02:
         self.velocity_y = 0
         self.velocity_x = 0

class Edge:
   def __init__(self, start_coordinate, end_coordinate):
      self.sx, self.sy = start_coordinate
      self.ex, self.ey = end_coordinate
      self.radius = 12
      self.selected_node = None

   def update_starting_node(self, coordinate):
      #Nodes can not overlap
      new_sx, new_sy = coordinate
      if new_sx == self.ex and new_sy == self.ey:
         self.ey += 0.5
      self.sx = new_sx
      self.sy = new_sy

   def update_end_node(self, coordiante):
      new_ex, new_ey = coordiante
      if new_ex == self.sx and new_ey == self.sy:
         self.sy += 0.5
      self.ex = new_ex
      self.ey = new_ey

   def draw_edge(self):
      color = EDGE_COLOR
      pygame.draw.circle(screen, color, (self.sx, self.sy), self.radius, 0 )
      pygame.draw.circle(screen, color, (self.ex, self.ey), self.radius, 0 )

      #Normal unit vector
      nx = (self.sy - self.ey)
      ny = -(self.sx - self.ex)
      distance = math.sqrt(nx**2 + ny**2)
      nx /= distance
      ny /= distance

      #The edge is two circles connected by 2 lines 
      #Here we get the coordinates for those lines
      line1_start_x = self.sx + nx*self.radius 
      line1_start_y = self.sy + ny * self.radius
      line1_end_X = self.ex + nx*self.radius
      line1_end_y = self.ey + ny * self.radius
      line2_start_x = self.sx - nx*self.radius 
      line2_start_y = self.sy - ny * self.radius
      line2_end_X = self.ex - nx*self.radius
      line2_end_y = self.ey - ny * self.radius

      pygame.draw.line(screen, color, (line1_start_x, line1_start_y) ,(line1_end_X, line1_end_y), 1)
      pygame.draw.line(screen, color, (line2_start_x, line2_start_y) ,(line2_end_X, line2_end_y), 1)


#Functions to determine if a point inside the given shape
def is_point_inside_a_circle(point, ball):
   px, py = point
   return (ball.x - px) **2 + (ball.y - py)**2 < ball.radius**2

def is_point_in_edge_node(point, edge):
   px, py = point
   if (edge.sx - px)**2 + (edge.sy - py)**2 < edge.radius**2:
      edge.selected_node = 1 #first node is selected
      return True
   if (edge.ex - px)**2 + (edge.ey - py)**2 < edge.radius**2:
      edge.selected_node = 2 #second node is selected
      return True

#Function to handle objects occupiying the same position
def resolve_static_collision(colliding_pair):
   ball, target = colliding_pair
   distance = math.sqrt((ball.x - target.x)**2 + (ball.y - target.y)**2)
   #If the balls share the same coordinates 
   # we slightly move one of the balls to avoid divison by zero
   if distance == 0:
      distance = 0.1
      ball.x += 0.1
   overlap = (distance - ball.radius - target.radius)/2

   #Only the actual ball must move if an edge collision happens
   if target.is_fake_ball:
      ball.x -= 2 * overlap * (ball.x - target.x)/distance
      ball.y -= 2 * overlap * (ball.y - target.y)/distance
      return

   #displace ball
   ball.x -= overlap * (ball.x - target.x)/distance
   ball.y -= overlap * (ball.y - target.y)/distance

   #displace target ball
   target.x += overlap * (ball.x - target.x )/distance
   target.y += overlap * (ball.y - target.y)/distance

#Function to simulate elastic collision 
def resolve_dynamic_collision(colliding_pair):
   ball, target = colliding_pair
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

   #Formula for velocity after impact
   ball.velocity_x = (tgt_vel_ball * tx + nx*(norm_vel_ball * (m1-m2) + 2 * m2 * norm_vel_target)/(m1+m2))/1.25
   ball.velocity_y = (tgt_vel_ball * ty + ny*(norm_vel_ball * (m1-m2) + 2 * m2 * norm_vel_target)/(m1+m2))/1.25
   target.velocity_x = (tgt_vel_target * tx + nx*(norm_vel_target * (m2 - m1) + 2 * m1 * norm_vel_ball)/(m1+m2))/1.25
   target.velocity_y = (tgt_vel_target * ty + ny*(norm_vel_target * (m2 - m1) + 2* m1 * norm_vel_ball)/(m1+m2))/1.25
   #We presevere a percentage of the speed so a little enertfy is lost at impact

#We will temporarily create a fake ball at the location of impact when an edge collision happens
#The fake ball allows us to simulate a collision at that location
def get_fake_ball(edge, ball, closest_x, closest_y):
   fake_ball = Ball(closest_x, closest_y, edge.radius)
   fake_ball.mass = ball.mass
   fake_ball.velocity_x = -ball.velocity_x
   fake_ball.velocity_y = -ball.velocity_y
   fake_ball.is_fake_ball = True
   return fake_ball

#check for collision for every ball againts every other ball
def get_circle_collisions(balls):
   list_of_collisions = []
   for i in range(len(balls)):
      for  j in range(i+1, len(balls)):
         ball = balls[i]
         target = balls[j]
         #comparision if distance between circles is smaller than the sum of their raidius
         if (ball.radius + target.radius)**2 >= (ball.x - target.x)**2 + (ball.y - target.y)**2:
            list_of_collisions.append((ball, target))

   return list_of_collisions

#Check for collision for every ball againts every edge
def get_edge_collisions(balls, edges):
   fake_balls = []
   for ball in balls:
      for edge in edges:
         linex1 = edge.ex - edge.sx
         liney1 = edge.ey - edge.sy
         linex2 = ball.x - edge.sx
         liney2 = ball.y - edge.sy

         edge_length = linex1 ** 2 + liney1 **2

         # t is the the closest point on the edge to the ball
         t = max(0, min(edge_length, (linex1 * linex2 + liney1 * liney2))) / edge_length

         #the x and y values of the balls closest point on the edge
         closest_x = edge.sx + t * linex1
         closest_y = edge.sy + t * liney1

         #distance between midpoint of ball to the closest point on edge
         distance = math.sqrt((ball.x - closest_x)**2 + (ball.y - closest_y)**2)

         if distance <= (ball.radius + edge.radius):
            fake_balls.append( (ball, get_fake_ball(edge, ball, closest_x, closest_y)) )
   
   return fake_balls
      
def add_some_balls_to_screen():  
   temp = []
   for i in range(1200, 1800, 55):
      temp.append(Ball(i//3, i//5, random.randint(20,60)))
   return temp

colliding_balls = []
fake_balls = []
balls_list = add_some_balls_to_screen()
edge_list = [Edge((90,80), (90, 500)) , Edge((170,80), (900, 80)), Edge((170, 600), (900, 600)), Edge((1000,80), (1000, 500))]
selected_ball = None
selected_edge = None 
cue_ball = None

while True:
   for event in pygame.event.get():
      if event.type == pygame.QUIT:
         pygame.quit()
         exit()

      #select ball or edge if mouse get pressed
      if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
         for ball in balls_list:
            if is_point_inside_a_circle(pygame.mouse.get_pos(), ball):
               selected_ball = ball
               break
         for edge in edge_list:
            if is_point_in_edge_node(pygame.mouse.get_pos(), edge):
               selected_edge = edge
               break        

      # Remove selection if mouse is released
      if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
         selected_ball = None
         if selected_edge: selected_edge.selected_node = None
         selected_edge = None
      
      # move selected ball or edge with mouse
      if selected_ball:
         selected_ball.velocity_x = 0 ; selected_ball.velocity_y = 0
         selected_ball.x, selected_ball.y = pygame.mouse.get_pos()

      if selected_edge:
         if selected_edge.selected_node == 1:
            selected_edge.update_starting_node(pygame.mouse.get_pos()) 
         if selected_edge.selected_node == 2:
            selected_edge.update_end_node(pygame.mouse.get_pos()) 

      # Launch ball with right mouse button
      if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
         for ball in balls_list:
            if is_point_inside_a_circle(pygame.mouse.get_pos(), ball):
               cue_ball = ball
               break
               
      if event.type == pygame.MOUSEBUTTONUP and event.button == 3 and cue_ball:
         cue_ball.velocity_x = 0.03* (cue_ball.x - pygame.mouse.get_pos()[0])
         cue_ball.velocity_y = 0.03* (cue_ball.y - pygame.mouse.get_pos()[1])
         cue_ball = None         

   
   #Background Color
   screen.fill(BACKGROUND_COLOR)
   #Draw balls and edges
   for edge in edge_list:
      edge.draw_edge()    
   for ball in balls_list:
      ball.update_ball() 
      ball.draw_ball() 
   #Draw the cue that is used for launching the ball
   if cue_ball: 
         pygame.draw.line(screen, (255,255,0), cue_ball.get_coordinate(), pygame.mouse.get_pos())
   

   #Get the list of all collisions
   colliding_balls.clear()
   fake_balls = get_edge_collisions(balls_list, edge_list) 
   #Fake balls are used to resolve edge collisions
   colliding_balls.extend(fake_balls)
   colliding_balls.extend(get_circle_collisions(balls_list))
   
   #Resolve all collisions
   for pair in colliding_balls:
      resolve_static_collision(pair)
      resolve_dynamic_collision(pair)

   pygame.display.update() 
   clock.tick(120) #Set fps

