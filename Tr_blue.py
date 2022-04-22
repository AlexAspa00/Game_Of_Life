import pickle

import numpy as np
import pygame
import os
import math
import sys
import random
import neat
import time
import threading

from neat import Checkpointer

import visualize

screen_width = 1500
screen_height = 800
generation = 0
total_criatures = [[], []]
clock = 0
food = []
food2 = []

winner = 0


class Food:
    def __init__(self, rad, x, y):
        self.radius = rad
        self.pos = [x,y]

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 0, 100), self.pos, self.radius)

class Food2:
    def __init__(self, rad, x, y):
        self.radius = rad
        self.pos = [x,y]

    def draw(self, screen):
        pygame.draw.circle(screen, (200, 50, 0), self.pos, self.radius)


food = [Food(20, 300, 50), Food(20, 350, 320), Food(20, 350, 520), Food(20, 300, 300), Food(20, 300, 700), Food(20, 500, 150), Food(20, 500, 350), Food(20, 500, 650), Food(20, 700, 200), Food(20, 700, 400), Food(20, 700, 600),
        Food(20, 900, 50), Food(20, 900, 300), Food(20, 900, 700),Food(20, 1100, 50), Food(20, 1100, 300), Food(20, 1100, 700), Food(20, 1300, 150), Food(20, 1300, 350), Food(20, 1300, 650),
        Food(20, 1400, 200), Food(20, 1400, 400), Food(20, 1400, 600), Food(20, 1450, 50), Food(20, 1450, 300), Food(20, 1450, 700),
        Food(20, 350, 50), Food(20, 350, 520), Food(20, 250, 720), Food(20, 320, 780), Food(20, 100, 440),
        Food(20, 300, 150), Food(20, 700, 650), Food(20, 200, 950), Food(20, 100, 500), Food(20, 800, 200),
        Food(20, 100, 600),Food(20, 300, 520), Food(20, 900, 390), Food(20, 1100, 800), Food(20, 1100, 530), Food(20, 1200, 300),
        Food(20, 1300, 500), Food(20, 1400, 190), Food(20, 1400, 340), Food(20, 1450, 600), Food(20, 1250, 300), Food(20, 1250, 400),
        Food(20, 1250, 700), Food(20, 1250, 100), Food(20, 1150, 300),Food(20, 1150, 700),Food(20, 300, 200), Food(20, 400, 300),
        Food(20, 150, 300), Food(20, 350, 200), Food(20, 550, 100), Food(20, 300, 100), Food(20, 350, 200), Food(20, 450, 200)
        ]

food2 = [Food2(20, 400 , 200), Food2(20, 700, 200), Food2(20, 1000, 600), Food2(20, 1120, 500)]

class Criatura1:
    def __init__(self, rad, x, y, id):
        self.radius = rad
        self.pos = [x,y]
        self.id = id
        self.is_alive = True

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), self.pos, self.radius)

    def get_alive(self):
        return self.is_alive

total_criatures[0] = [Criatura1(40,50,400,1),Criatura1(40,150,300,2),Criatura1(40,1250,600,3),Criatura1(40,600,400,4),Criatura1(40,650,500,5),Criatura1(40,850,200,6),
                         Criatura1(40,950,600,7),Criatura1(40,1150,800,8), Criatura1(40,500,400,9),Criatura1(40,650,300,10),Criatura1(40,450,600,11),Criatura1(40,900,700,12),Criatura1(40,850,400,13),Criatura1(40,250,300,14),
                         Criatura1(40,1250,600,15),Criatura1(40,1450,400,16),Criatura1(40,300,100,17),Criatura1(40,350,200,18),Criatura1(40,1450,100,19), Criatura1(40,1350,250,20), Criatura1(40,1100,150,21), Criatura1(40,1050,250,20), Criatura1(40,1200,200,20)]

class Criatura2:
    def __init__(self, screen, start_time, id, rad, r, g, b, food):
        self.id = id
        self.radius = rad
        self.pos = [200,400]
        self.angle = 0
        self.speed = 0
        self.radars = []
        self.radars_for_draw = []
        self.is_alive = True
        self.time = start_time
        self.hungry = 200
        self.color = [r, g, b]
        self.total_ate = 0
        self.radars_colors = []
        self.time_after_eating = 0
        self.shield = 0
        self.protected = 0
        self.food = food

    def getPos(self):
        if self.id % 2 == 0:
            return int(random.randint(self.radius + 1200, (screen_width - self.radius)))
        else:
            return int(random.randint(self.radius , (screen_width - self.radius - 1200)))

    def update(self, cri, screen):
        # check speed
        # self.speed = 8

        # move
        self.pos[0] += math.cos(self.angle) * self.speed
        self.pos[1] += math.sin(self.angle) * self.speed

        self.check_collision(cri, screen)
        self.radars.clear()
        self.radars_colors.clear()

        self.check_radar(self.angle + math.radians(-45), screen)
        self.check_radar(self.angle + math.radians(-10), screen)
        #self.check_radar(self.angle + math.radians(-5), screen)
        #self.check_radar(self.angle + math.radians(0), screen)
        #self.check_radar(self.angle + math.radians(5), screen)
        self.check_radar(self.angle + math.radians(10), screen)
        self.check_radar(self.angle + math.radians(45), screen)

        self.check_hungry()

    def check_collision(self, cri, screen):
        self.is_alive = True

        for i, f in enumerate(self.food):
            dist = math.dist([self.pos[0], self.pos[1]], [f.pos[0], f.pos[1]])
            if dist < (self.radius + f.radius):
                if self.shield < 0.5:
                    self.hungry = self.hungry + 200
                    self.total_ate += 1
                    self.food.pop(i)
                    #food_aux.append(Food(20))
                    if self.total_ate == 1:
                        self.time_after_eating = time.time()
                    break
                else:
                    self.protected -= 0.5
                    self.hungry -= 10

        for c in cri:
            if (not (self.id == c.id)) and (c.get_alive()):
                dist = math.dist([self.pos[0], self.pos[1]], [c.pos[0], c.pos[
                    1]])  # https://stackoverflow.com/questions/22135712/pygame-collision-detection-with-two-circles
                # dist  = math.hypot(car.pos[0] - self.pos[0], car.pos[1] - self.pos[1])
                if dist < (self.radius + c.radius):
                    if self.radius < c.radius:
                        if self.shield < 0.5:
                            self.is_alive = False
                        else:
                            self.protected += 1
                            self.pos[0] = self.pos[0] - 20

        if (self.pos[0] + self.radius >= screen_width) or (self.pos[0] < self.radius) or (
                self.pos[1] + self.radius >= screen_height) or (self.pos[1] < self.radius):
            self.is_alive = False
        else:
            '''
            x1, y1, x2, y2 = 1200, 0, 1300, 380
            if self.FindPoint(x1, y1, x2, y2, self.pos[0], self.pos[1]):
                self.is_alive = False
            '''

    def isInside(self, circle_x, circle_y, rad, x, y):
        # Compare radius of circle
        # with distance of its center
        # from given point
        if ((x - circle_x) * (x - circle_x) +
                (y - circle_y) * (y - circle_y) <= rad * rad):
            return True;
        else:
            return False;

    def check_radar(self, degree, map):
        len = 0
        x = int(self.pos[0] + math.cos(degree) * len + math.cos(degree) * self.radius)
        y = int(self.pos[1] + math.sin(degree) * len + math.sin(degree) * self.radius)

        while len < 1500 and (x < (screen_width - self.radius) and y < (screen_height - self.radius)) and (
                x > 0 and y > 0):

            if x >= (screen_width - self.radius) or y >= (screen_height - self.radius):
                break

            if (map.get_at((x, y)) != (25, 25, 25, 255)) and (map.get_at((x, y)) != (0, 255, 0, 255)) and (
                    map.get_at((x, y)) != (self.color[0], self.color[1], self.color[2], 255)) or (map.get_at((x, y)) == (0, 0, 100, 255)):
                if (map.get_at((x, y)) == (0, 0, 100, 255)):
                    trobat = 0
                    for i, f in enumerate(self.food):
                        if self.isInside(f.pos[0], f.pos[1], 20, x,y) == True:
                            trobat = 1
                            break

                    if trobat == 0:
                        len = len + 1
                        x = int(self.pos[0] + math.cos(degree) * len + math.cos(degree) * self.radius)
                        y = int(self.pos[1] + math.sin(degree) * len + math.sin(degree) * self.radius)
                    else:
                        x = int(self.pos[0] + math.cos(degree) * len + math.cos(degree) * self.radius)
                        y = int(self.pos[1] + math.sin(degree) * len + math.sin(degree) * self.radius)
                        break
                else:
                    x = int(self.pos[0] + math.cos(degree) * len + math.cos(degree) * self.radius)
                    y = int(self.pos[1] + math.sin(degree) * len + math.sin(degree) * self.radius)
                    break
            else:
                len = len + 1
                x = int(self.pos[0] + math.cos(degree) * len + math.cos(degree) * self.radius)
                y = int(self.pos[1] + math.sin(degree) * len + math.sin(degree) * self.radius)

        dist = int(math.sqrt(math.pow(x - (self.pos[0] + math.cos(degree) * self.radius), 2) + math.pow(
            y - (self.pos[1] + math.sin(degree) * self.radius), 2)))
        self.radars.append([(x, y), dist])

        if (x < (screen_width - self.radius) and y < (screen_height - self.radius)) and (x > 0 and y > 0):
            if (map.get_at((x, y))[0] == 25 and map.get_at((x, y))[1] == 25 and map.get_at((x, y))[2] == 25): #black
                self.radars_colors.append(0)
            if (map.get_at((x, y))[0] == 255 and map.get_at((x, y))[1] == 0 and map.get_at((x, y))[2] == 0): #red
                self.radars_colors.append(1)
            if (map.get_at((x, y))[0] == 0 and map.get_at((x, y))[1] == 0 and map.get_at((x, y))[2] == 255):  #blue
                self.radars_colors.append(2)
            if (map.get_at((x, y))[0] == 0 and map.get_at((x, y))[1] == 0 and map.get_at((x, y))[2] == 100): #blue food
                self.radars_colors.append(3)
            if (map.get_at((x, y))[0] == 0 and map.get_at((x, y))[1] == 100 and map.get_at((x, y))[2] == 200): #blue shield
                self.radars_colors.append(4)
        else:
            self.radars_colors.append(0)

    def draw_radar(self, screen):

        for r in self.radars:
            pos, dist = r
            pygame.draw.line(screen, (0, 255, 0), self.pos, pos, 1)
            pygame.draw.circle(screen, (0, 255, 0), pos, 5)

    def draw(self, screen):
        if self.shield <= 0.5:
            pygame.draw.circle(screen, (self.color[0], self.color[1], self.color[2]), (self.pos[0], self.pos[1]),
                               self.radius, 0)
        else:
            pygame.draw.circle(screen, (0, 100, 200), (self.pos[0], self.pos[1]),
                               self.radius, 0)

        generation_font = pygame.font.SysFont("Arial", 24)
        text = generation_font.render(str(self.total_ate), True, (0, 255, 0))
        text_rect = text.get_rect()
        text_rect.center = [self.pos[0] - 10, self.pos[1]]
        screen.blit(text, text_rect)

        self.draw_radar(screen)

    def get_alive(self):
        return self.is_alive

    def get_reward(self):
        #dist = math.dist([self.pos[0], self.pos[1]], [food[0].pos[0], food[0].pos[1]])
        #dist2 = math.dist([self.pos[0], self.pos[1]], [food[1].pos[0], food[1].pos[1]])
        #dist = min(dist2, dist)
        #dist = dist / 1700

        aux = 0

        if self.total_ate > 1:
            aux = 1

        #return (self.total_ate + self.protected * self.total_ate + self.get_time())
        #return self.get_time() * 0.25 + self.total_ate
        #return self.get_time() * 0.4 + self.total_ate * 40 + self.protected * aux
        return  self.total_ate

    def get_time(self):
        return (time.time() - self.time)

    def get_data(self):
        radars = self.radars
        ret = [0, 0, 0, 0, 0, 0, 0, 0]
        for i, r in enumerate(radars):
            ret[i] = int(r[1] / 1000)

        for i in range(len(self.radars_colors)):
            ret[4 + i] = self.radars_colors[i] / 5

        return ret

    def check_hungry(self):
        self.hungry = self.hungry - 1

        if self.hungry <= 0:
            self.is_alive = False
        if self.get_time() > 300:
            self.is_alive = False

def run_sp2(genomes, config):
    # Init NEAT
    nets = []

    total_criatures[1] = []

    i = 0
    for id, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        food_aux = []

        for i in range(0, len(food)):
            food_aux.append(food[i])

        # Init my cars
        total_criatures[1].append(Criatura2(screen, time.time(), i + 100, 25, 0, 0, 255, food_aux))
        i = i + 1

    # Main loop
    global generation
    generation += 1

    while True:

        # Input my data and get result from network
        for index, criatura in enumerate(total_criatures[1]):
            output = nets[index].activate(criatura.get_data())

            criatura.angle += output[0]

            '''
            criatura.speed += output[1]
            if criatura.speed <= 0:
                criatura.speed = 0.2
            elif criatura.speed > 20:
                criatura.speed = 20
            '''
            criatura.speed = 15

            criatura.shield += 0
            if criatura.shield <= 0:
                criatura.shield = 0
            if criatura.shield > 1:
                criatura.shield = 1

        # Update car and fitness
        remain_cri = 0
        cri_aux = []

        for i in range(len(total_criatures)):
            cri_aux += total_criatures[i]

        for i, criatura in enumerate(total_criatures[1]):
            if criatura.get_alive():
                remain_cri += 1
                criatura.update(cri_aux, screen)
                genomes[i][1].fitness = 0
                genomes[i][1].fitness = criatura.get_reward()

        # check
        if remain_cri == 0:
            break

        bg = 25, 25, 25
        screen.fill(bg)

        # Scenario
        # pygame.draw.rect(screen, (100, 100, 0, 255), (screen_width - 300, 0, 10, screen_height / 2))
        # pygame.draw.rect(screen, (100, 100, 0, 255),(screen_width - 300, (screen_height / 2) + 40, 100, (screen_height / 2) - 40))

        for f in food:
            f.draw(screen)

        pygame.display.flip()

        # Criatures
        if len(total_criatures) > 0:
            for i in range(len(total_criatures)):
                for criatura in total_criatures[i]:
                    if criatura.get_alive():
                        criatura.draw(screen)

            pygame.display.flip()
            clock.tick(0)

def run_neat(config):
    # Create core evolution algorithm class
    p = neat.Population(config)
    test = "120"

    try:
        os.mkdir("Results_Sp2/" + test)
    except OSError:
        print("Creation of the directory %s failed" % test)

    try:
        os.mkdir("Results_Sp2/" + test + "/Checkpoints")
    except OSError:
        print("Creation of the directory %s failed" % test)

    # Add reporter for fancy statistical result
    #p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(neat.Checkpointer(generation_interval=100, time_interval_seconds=1200,
                                     filename_prefix="Results_Sp2/" + test + "/Checkpoints/neat-checkpoint-"))
    p.add_reporter(stats)
    winner = p.run(run_sp2, 5000)
    win = p.best_genome

    # Show output of the most fit genome against training data.
    print('\nOutput:')
    print('\nBest genome:\n{!s}'.format(winner))
    f = open("Results_Sp2/" + test + "/Results_Sp2.txt", "w+")
    f.write('\nBest genome:\n{!s}'.format(winner))
    f.close()

    node_names = {-1: 'Radar1', -2: 'Radar2', -3: 'Radar3', -4: 'Radar4', -5: 'C1', -6: 'C2', -7: 'C3', -8: 'C4', 0: 'Angle', 1: 'Shield'}
    visualize.draw_net(config, winner, True, node_names=node_names, filename="Results_Sp2/" + test + "/Net")
    visualize.plot_stats(stats, ylog=False, view=True, filename="Results_Sp2/" + test + "/avg_fitness.svg")
    visualize.plot_species(stats, view=True, filename="Results_Sp2/" + test + "/speciation.svg")
    with open("Results_Sp2/" + test + "/winner.pkl", "wb") as f:
        pickle.dump(winner, f)
        f.close()
    with open("Results_Sp2/" + test + '/real_winner.pkl', "wb") as f:
        pickle.dump(win, f)
        f.close()


if __name__ == "__main__":

    config_path = "./config-feedforward-2.txt"
    config2 = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                 neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Init my game
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()

    pygame.display.flip()

    t = threading.Thread(target=run_neat, args=(config2,))
    t.start()

    while True:
        time.sleep(0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
