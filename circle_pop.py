#!/usr/bin/env python
#this is just a message
# following: https://liluo.io/games/1c884201-9038-4da4-833f-3dd2d9a44d27
import pygame
import random
import math
from datetime import datetime

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BACKGROUND_COLOR = [50, 50, 50]
CIRCLE_SIZES = [40, 80]
NR_OF_CIRCLES = 9


class Circle:
    def __init__(self):
        # going to be assigned randomly when circle is made
        self.color = [random.randrange(0, 256), random.randrange(0, 256), random.randrange(0, 256)]
        # also assigned randomly at creation
        self.radius = random.randrange(CIRCLE_SIZES[0], CIRCLE_SIZES[1])
        # set border equal to radius, so that entire circle is filled in with color when drawing
        self.border_radius = self.radius
        # random position, but requires check to see if circles do not overlap
        self.position = [random.randrange(0, WINDOW_WIDTH), random.randrange(0, WINDOW_HEIGHT)]
        # keeps track of how often circle is clicked
        self.times_clicked = 0
        # two variables for direction, changed every time circle bumps in to other circle
        self.x_direction = (random.randrange(10, 100) / 100) - 0.5
        self.y_direction = (random.randrange(10, 100) / 100) - 0.5

    # if point is inside this circle, return true, false otherwise
    def has_point_inside(self, point):
        distance = math.dist(self.position, point)
        if distance < self.radius:
            return True
        else:
            return False

    # handles the color change and sets the circle's number of clicks
    def click(self):
        # if it's clicked less than two times
        if self.times_clicked < 2:
            self.times_clicked += 1
            if self.color[0] < (255 - 20):
                self.color[0] += 20
            if self.color[1] < (255 - 20):
                self.color[1] += 20
            if self.color[2] < (255 - 20):
                self.color[2] += 20
        # if it's clicked more than two times, nothing changes.
        # The times clicked stays at three, and color and radius are fixed
        else:
            self.times_clicked = 3
            self.color = [255, 255, 255]
            self.border_radius = 3

    # draw this circle
    def draw(self, display):
        pygame.draw.circle(display, self.color, self.position, self.radius, self.border_radius)

    # checks if collision occurs with other circle, true if true, false otherwise
    def collides_with(self, other_circle):
        # copy pasted math, magic to me
        d = math.sqrt((self.position[0] - other_circle.position[0]) * (self.position[0] - other_circle.position[0]) + (self.position[1] - other_circle.position[1]) * (self.position[1] - other_circle.position[1]))
        if(d <= self.radius - other_circle.radius):
            # I am inside other_circle
            return True
        elif(d <= other_circle.radius - self.radius):
            # other circle is inside me
            return True
        elif(d < self.radius + other_circle.radius):
            # I intersect other circle
            return True
        elif(d == self.radius + other_circle.radius):
            # i just touch other circle
            return True
        else:
            # Yee not touching anything
            return False

    # move 1 unit of length away from some other circle, to be called the moment two circles collide
    def move_away_from(self, other_circle, display):
        # math from https://gamefromscratch.com/gamedev-math-recipes-rotating-one-point-around-another-point/
        # i want to move away from some circle, so i want to go towards a point rotated 180 degrees from where other point is
        angle = 180
        angle = (angle) * (math.pi/180)
        rotatedX = math.cos(angle) * (other_circle.position[0] - self.position[0]) - math.sin(angle) * (other_circle.position[1]-self.position[1]) + self.position[0]
        rotatedY = math.sin(angle) * (other_circle.position[0] - self.position[0]) + math.cos(angle) * (other_circle.position[1] - self.position[1]) + self.position[1]

        # i now want to move towards that point
        point_to_move_to = [rotatedX, rotatedY]

        # get angle to that point
        dx = point_to_move_to[0] - self.position[0]
        dy = point_to_move_to[1] - self.position[1]

        # store the new angle
        anglu = math.atan2(dx, dy)
        magnitude = 1.0

        # get the change needed in x and y direction in order to move towards that angle with given magnitude
        velX = math.cos(anglu) * magnitude
        velY = math.sin(anglu) * magnitude

        # position is set so that this circle and the other circle no longer intersect, and the direction is
        # set so that it's moving away from the other circle
        self.position[0] += velY
        self.x_direction = velY
        self.y_direction = velX
        self.position[1] += velX

    # checks for collisions, and updates position and direction accordingly
    def update(self):
        # if i've passed the left side of the screen
        if self.position[0] - self.radius < 0:
            # reverse my direction
            self.x_direction *= -1
            # put me back in the field
            self.position[0] += 1
        # if i've pased the right side
        elif self.position[0] + self.radius >= WINDOW_WIDTH:
            # do the same thing
            self.x_direction *= -1
            self.position[0] -= 1
        # if i went out the top
        if self.position[1] - self.radius < 0:
            self.y_direction *= -1
            self.position[1] += 1
        # if i went out the bottom
        elif self.position[1] + self.radius >= WINDOW_HEIGHT:
            self.y_direction *= -1
            self.position[1] -= 1
        # update my position
        self.position[0] += self.x_direction
        self.position[1] += self.y_direction


class Game:
    def __init__(self):
        # initialize the game and the font thing, because i want to use fonts too
        pygame.init()
        pygame.font.init()

        # use a clock to make speed dependent on framerate and keep it constant
        self.clock = pygame.time.Clock()
        # create a pygame display
        self.display = pygame.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT])

        # list will contain all circles, to easily loop over them
        self.list_of_circles = []
        for i in range(0, NR_OF_CIRCLES):
            # create new circles, add them to the list
            self.list_of_circles.append(Circle())

        # when the game is initialized, all circles are unclicked
        self.unclicked_circles_left = True
        # both start time and endtime are not set at the beginning, start time will be set when first circle is clicked
        self.startTime = False
        # endtime will be set when last circle is fully clicked
        self.endTime = False

    def run(self):
        # run forever
        while True:
            # this unwieldy code is called once so we don't have to send the entire
            # list of events to every object in our game. For performance reasons
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return
                # when the mouse button has been pressed
                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.unclicked_circles_left:
                        # get the mouse position
                        mousepos = pygame.mouse.get_pos()
                        
                        # then,for every circle
                        # remember that at this point all circles could have been clicked
                        potential_finish = True
                        for circle in self.list_of_circles:
                           
                            # check if that circle has been clicked
                            if circle.has_point_inside(mousepos):
                                if not self.startTime:
                                    self.startTime = datetime.now()
                                # forward the click to the button
                                circle.click()
                                
                            if circle.times_clicked < 3:
                                potential_finish = False
                        if potential_finish:
                            # haven't seen a single circle that hasn't been clicked 3 times
                            self.endTime = datetime.now()
                            # no more unclicked circles left!
                            self.unclicked_circles_left = False

            if self.unclicked_circles_left:
                # make the screen black for every new frame
                self.display.fill(BACKGROUND_COLOR)
                
                # the game loop itself, for every circle
                for circle in self.list_of_circles:
                    # for every other circle
                    for other_circle in self.list_of_circles:
                        # check if circle collides with other circle, and if it does
                        if circle.collides_with(other_circle):
                            # check if this circle is not itself, and if it's not
                            if circle is not other_circle:
                                circle.move_away_from(other_circle, self.display)
                                other_circle.move_away_from(circle, self.display)
                    circle.update()
                    circle.draw(self.display)
            else:  # if no unclicked circles left
                # game finished, turn the screen black
                self.display.fill(BACKGROUND_COLOR)
                # calculate the time it took from clicking the first circle to the last
                total_seconds = (self.endTime - self.startTime).total_seconds()

                # pygame requirements: define the fond
                my_font = pygame.font.SysFont('Open Sans, Semibold', 30)
                
                text_surface = my_font.render("It took you "+str(float(f'{total_seconds:.3f}'))+" seconds", False, (255, 255, 255))
                self.display.blit(text_surface, (0,0))

            

            # make sure the game runs at the same speed for slow as well as fast computers
            self.clock.tick(144)
            # https://www.pygame.org/docs/ref/display.html#pygame.display.flip
            # This will update the contents of the entire display.
            pygame.display.flip()


g = Game()
g.run()
