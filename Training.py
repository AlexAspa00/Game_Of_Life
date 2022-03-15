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
import visualize

screen_width = 1500
screen_height = 800
generation = 0
total_criatures = [[], []]
clock = 0
food = []

semaforo = threading.Semaphore(1);


class Food:
    def __init__(self, rad):
        self.radius = rad
        # self.pos = [int(random.randint((screen_width - 10) - 100, (screen_width - 10))), int(random.randint(10, screen_height - 10))]
        self.pos = [int(random.randint((screen_width - rad) - 300, (screen_width - rad))),
                    int(random.randint(rad, screen_height - rad))]

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 0, 100), self.pos, self.radius)


food = [Food(20), Food(20), Food(20), Food(20), Food(20), Food(20)]


class Criatura1:
    def __init__(self, screen, start_time, id, rad, r, g, b):
        self.id = id
        self.radius = rad
        self.pos = [int(random.randint(self.radius, (screen_width - self.radius) - 300)),
                    int(random.randint(self.radius, screen_height - self.radius))]
        self.angle = 0
        self.speed = 0
        self.radars = []
        self.radars_for_draw = []
        self.is_alive = True
        self.time = start_time
        self.hungry = 50
        self.color = [r, g, b]
        self.total_ate = 0
        self.radars_colors = []
        self.end = 0

    def update(self, cri, screen):
        # check speed
        # self.speed = 8

        # move
        self.pos[0] += math.cos(self.angle) * self.speed
        self.pos[1] += math.sin(self.angle) * self.speed

        self.check_collision(cri, screen)
        self.radars.clear()
        self.radars_colors.clear()

        self.check_radar(self.angle + math.radians(-10), screen)
        self.check_radar(self.angle + math.radians(-5), screen)
        self.check_radar(self.angle + math.radians(0), screen)
        self.check_radar(self.angle + math.radians(5), screen)
        self.check_radar(self.angle + math.radians(10), screen)

        self.check_hungry()

    def check_collision(self, cri, screen):
        self.is_alive = True

        for c in cri:
            if (not (self.id == c.id)) and (c.get_alive()):
                dist = math.dist([self.pos[0], self.pos[1]], [c.pos[0], c.pos[
                    1]])  # https://stackoverflow.com/questions/22135712/pygame-collision-detection-with-two-circles
                # dist  = math.hypot(car.pos[0] - self.pos[0], car.pos[1] - self.pos[1])
                if dist < (self.radius + c.radius):
                    if (self.radius < c.radius):
                        self.is_alive = False
                    elif self.radius > c.radius:
                        # print("Eat")
                        # print(self.id)
                        self.hungry = self.hungry + 100
                        self.total_ate += 1

        if (self.pos[0] + self.radius >= 1200) or (self.pos[0] < self.radius) or (
                self.pos[1] + self.radius >= screen_height) or (self.pos[1] < self.radius):
            self.is_alive = False
        else:
            if screen.get_at((int(self.pos[0]), int(self.pos[1]))) == (100, 100, 0, 255):
                self.is_alive = False

    def check_radar(self, degree, map):
        len = 0
        x = int(self.pos[0] + math.cos(degree) * len + math.cos(degree) * self.radius)
        y = int(self.pos[1] + math.sin(degree) * len + math.sin(degree) * self.radius)

        while len < 1000 and (x < (screen_width - self.radius) and y < (screen_height - self.radius)) and (
                x > 0 and y > 0):

            if x >= (screen_width - self.radius) or y >= (screen_height - self.radius):
                break

            if (map.get_at((x, y)) != (25, 25, 25, 255)) and (map.get_at((x, y)) != (0, 255, 0, 255)) and (
                    map.get_at((x, y)) != (self.color[0], self.color[1], self.color[2], 255)):
                x = int(self.pos[0] + math.cos(degree) * len + math.cos(degree) * self.radius)
                y = int(self.pos[1] + math.sin(degree) * len + math.sin(degree) * self.radius)
                break
            else:
                len = len + 0.5
                x = int(self.pos[0] + math.cos(degree) * len + math.cos(degree) * self.radius)
                y = int(self.pos[1] + math.sin(degree) * len + math.sin(degree) * self.radius)

        dist = int(math.sqrt(math.pow(x - (self.pos[0] + math.cos(degree) * self.radius), 2) + math.pow(
            y - (self.pos[1] + math.sin(degree) * self.radius), 2)))
        self.radars.append([(x, y), dist])

        if (x < (screen_width - self.radius) and y < (screen_height - self.radius)) and (x > 0 and y > 0):
            self.radars_colors.append(map.get_at((x, y))[0])
            self.radars_colors.append(map.get_at((x, y))[1])
            self.radars_colors.append(map.get_at((x, y))[2])
        else:
            self.radars_colors.append(25)
            self.radars_colors.append(25)
            self.radars_colors.append(25)

    def draw_radar(self, screen):

        for r in self.radars:
            pos, dist = r
            if self.radius == 40:
                pygame.draw.line(screen, (0, 255, 0), self.pos, pos, 1)
                pygame.draw.circle(screen, (0, 255, 0), pos, 5)

    def draw(self, screen):
        pygame.draw.circle(screen, (self.color[0], self.color[1], self.color[2]), (self.pos[0], self.pos[1]),
                           self.radius, 0)
        '''
        generation_font = pygame.font.SysFont("Arial", 10)
        text = generation_font.render(str(self.id), True, (255, 255, 0))
        text_rect = text.get_rect()
        text_rect.center = (self.pos)
        screen.blit(text, text_rect)
        '''
        self.draw_radar(screen)

    def get_alive(self):
        return self.is_alive

    def get_reward(self):
        return (((time.time() - self.time)) * (self.total_ate / 10))

    def get_time(self):
        return (time.time() - self.time)

    def get_data(self):
        radars = self.radars
        ret = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, self.pos[0] / 1500]
        for i, r in enumerate(radars):
            ret[i] = int(r[1] / 100)

        for i in range(len(self.radars_colors)):
            ret[5 + i] = self.radars_colors[i] / 25

        return ret

    def check_hungry(self):
        self.hungry = self.hungry - 1

        if self.hungry <= 0:
            self.is_alive = False
        if ((time.time() - self.time)) * (self.total_ate / 10) > 3000:
            print(((time.time() - self.time)) * (self.total_ate / 10))
            self.is_alive = False

class Criatura2:
    def __init__(self, screen, start_time, id, rad, r, g, b):
        self.id = id
        self.radius = rad
        self.pos = [int(random.randint(self.radius, (screen_width - self.radius) - 300)),
                    int(random.randint(self.radius, screen_height - self.radius))]
        self.angle = 0
        self.speed = 0
        self.radars = []
        self.radars_for_draw = []
        self.is_alive = True
        self.time = start_time
        self.hungry = 100
        self.color = [r, g, b]
        self.total_ate = 0
        self.radars_colors = []
        self.time_after_eating = 0

    def update(self, cri, screen):
        # check speed
        # self.speed = 8

        # move
        self.pos[0] += math.cos(self.angle) * self.speed
        self.pos[1] += math.sin(self.angle) * self.speed

        self.check_collision(cri, screen)
        self.radars.clear()
        self.radars_colors.clear()

        self.check_radar(self.angle + math.radians(-10), screen)
        self.check_radar(self.angle + math.radians(-5), screen)
        self.check_radar(self.angle + math.radians(0), screen)
        self.check_radar(self.angle + math.radians(5), screen)
        self.check_radar(self.angle + math.radians(10), screen)

        self.check_hungry()

    def check_collision(self, cri, screen):
        self.is_alive = True
        global food

        for i, f in enumerate(food):
            dist = math.dist([self.pos[0], self.pos[1]], [f.pos[0], f.pos[1]])
            if dist < (self.radius + f.radius):
                self.hungry = self.hungry + 100
                self.total_ate += 1
                food.pop(i)
                food.append(Food(20))
                if self.total_ate == 1:
                    self.time_after_eating = time.time()
                break

        for c in cri:
            if (not (self.id == c.id)) and (c.get_alive()):
                dist = math.dist([self.pos[0], self.pos[1]], [c.pos[0], c.pos[
                    1]])  # https://stackoverflow.com/questions/22135712/pygame-collision-detection-with-two-circles
                # dist  = math.hypot(car.pos[0] - self.pos[0], car.pos[1] - self.pos[1])
                if dist < (self.radius + c.radius):
                    if (self.radius < c.radius):
                        self.is_alive = False

        if (self.pos[0] + self.radius >= screen_width) or (self.pos[0] < self.radius) or (
                self.pos[1] + self.radius >= screen_height) or (self.pos[1] < self.radius):
            self.is_alive = False
        else:
            '''
            x1, y1, x2, y2 = 1200, 0, 1300, 380
            if self.FindPoint(x1, y1, x2, y2, self.pos[0], self.pos[1]):
                self.is_alive = False
            '''

    def FindPoint(self, x1, y1, x2, y2, x, y):
        if (x > x1 and x < x2 and y > y1 and y < y2):
            return True
        else:
            return False

    def check_radar(self, degree, map):
        len = 0
        x = int(self.pos[0] + math.cos(degree) * len + math.cos(degree) * self.radius)
        y = int(self.pos[1] + math.sin(degree) * len + math.sin(degree) * self.radius)

        while len < 1000 and (x < (screen_width - self.radius) and y < (screen_height - self.radius)) and (
                x > 0 and y > 0):

            if x >= (screen_width - self.radius) or y >= (screen_height - self.radius):
                break

            if (map.get_at((x, y)) != (25, 25, 25, 255)) and (map.get_at((x, y)) != (0, 255, 0, 255)) and (
                    map.get_at((x, y)) != (self.color[0], self.color[1], self.color[2], 255)):
                x = int(self.pos[0] + math.cos(degree) * len + math.cos(degree) * self.radius)
                y = int(self.pos[1] + math.sin(degree) * len + math.sin(degree) * self.radius)
                break
            else:
                len = len + 0.5
                x = int(self.pos[0] + math.cos(degree) * len + math.cos(degree) * self.radius)
                y = int(self.pos[1] + math.sin(degree) * len + math.sin(degree) * self.radius)

        dist = int(math.sqrt(math.pow(x - (self.pos[0] + math.cos(degree) * self.radius), 2) + math.pow(
            y - (self.pos[1] + math.sin(degree) * self.radius), 2)))
        self.radars.append([(x, y), dist])

        if (x < (screen_width - self.radius) and y < (screen_height - self.radius)) and (x > 0 and y > 0):
            self.radars_colors.append(map.get_at((x, y))[0])
            self.radars_colors.append(map.get_at((x, y))[1])
            self.radars_colors.append(map.get_at((x, y))[2])
        else:
            self.radars_colors.append(25)
            self.radars_colors.append(25)
            self.radars_colors.append(25)

    def draw_radar(self, screen):

        for r in self.radars:
            pos, dist = r
            pygame.draw.line(screen, (0, 255, 0), self.pos, pos, 1)
            pygame.draw.circle(screen, (0, 255, 0), pos, 5)

    def draw(self, screen):
        pygame.draw.circle(screen, (self.color[0], self.color[1], self.color[2]), (self.pos[0], self.pos[1]),
                           self.radius, 0)
        '''
        generation_font = pygame.font.SysFont("Arial", 10)
        text = generation_font.render(str(self.id), True, (255, 255, 0))
        text_rect = text.get_rect()
        text_rect.center = (self.pos)
        screen.blit(text, text_rect)
        '''
        self.draw_radar(screen)

    def get_alive(self):
        return self.is_alive

    def get_reward(self):
        dist = math.dist([self.pos[0], self.pos[1]], [food[0].pos[0], food[0].pos[1]])
        dist2 = math.dist([self.pos[0], self.pos[1]], [food[1].pos[0], food[1].pos[1]])
        dist = min(dist2, dist)
        dist = dist / 1700

        aux = self.total_ate

        if aux <= 1:
            aux = 0

        return (((time.time() - self.time_after_eating) * (aux)) / 100 + (time.time() - self.time) * 0.01)

    def get_time(self):
        return (time.time() - self.time)

    def get_data(self):
        radars = self.radars
        ret = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, self.pos[0] / 1500]
        for i, r in enumerate(radars):
            ret[i] = int(r[1] / 1000)

        for i in range(len(self.radars_colors)):
            ret[5 + i] = self.radars_colors[i] / 255

        return ret

    def check_hungry(self):
        self.hungry = self.hungry - 1

        if self.hungry <= 0:
            self.is_alive = False
        if self.get_time() > 300:
            self.is_alive = False

def run_sp1(genomes, config):
    bg = 25, 25, 25
    screen.fill(bg)

    # Scenario
    # pygame.draw.rect(screen, (100, 100, 0, 255), (screen_width - 300, 0, 100, (screen_height / 2) - 20))
    # pygame.draw.rect(screen, (100, 100, 0, 255), (screen_width - 300, 0, 10, screen_height / 2))
    # pygame.draw.rect(screen, (100, 100, 0, 255),(screen_width - 300, (screen_height / 2) + 40, 100, (screen_height / 2) - 40))

    for f in food:
        f.draw(screen)

    pygame.display.flip()

    # Init NEAT
    nets = []
    total_criatures[0] = []

    i = 0
    for id, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        # Init my cars
        total_criatures[0].append(Criatura1(screen, time.time(), i, 40, 255, 0, 0))
        i = i + 1

    # Main loop
    global generation
    generation += 1

    while True:
        semaforo.acquire()

        # Input my data and get result from network
        for index, criatures in enumerate(total_criatures[0]):
            output = nets[index].activate(criatures.get_data())

            criatures.angle += output[0]

            criatures.speed += output[1]
            if criatures.speed < 0:
                criatures.speed = 0
            elif criatures.speed > 20:
                criatures.speed = 20

        # Update car and fitness
        remain_cri = 0
        cri_aux = []
        i = 0
        for i in range(len(total_criatures)):
            cri_aux += total_criatures[i]

        i = 0
        for i, criatures in enumerate(total_criatures[0]):
            if criatures.get_alive():
                remain_cri += 1
                criatures.update(cri_aux, screen)
                genomes[i][1].fitness = criatures.get_reward()

        # check
        if remain_cri == 0:
            semaforo.release()
            break

        bg = 25, 25, 25
        screen.fill(bg)

        # Scenario
        # pygame.draw.rect(screen, (100, 100, 0, 255), (screen_width - 300, 0, 100, (screen_height / 2) - 20))
        # pygame.draw.rect(screen, (100, 100, 0, 255), (screen_width - 300, 0, 10, screen_height / 2))
        # pygame.draw.rect(screen, (100, 100, 0, 255),(screen_width - 300, (screen_height / 2) + 40, 100, (screen_height / 2) - 40))

        for f in food:
            f.draw(screen)

        pygame.display.flip()

        # Criatures
        if len(total_criatures) > 0:
            for i in range(len(total_criatures)):
                for criatures in total_criatures[i]:
                    if criatures.get_alive():
                        criatures.draw(screen)

            pygame.display.flip()
            clock.tick(0)

        semaforo.release()
        time.sleep(0.01)

def run_sp2(genomes, config):
    # Init NEAT
    nets = []
    total_criatures[1] = []

    i = 0
    for id, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        # Init my cars
        total_criatures[1].append(Criatura2(screen, time.time(), i + 100, 25, 0, 0, 255))
        i = i + 1

    # Main loop
    global generation
    generation += 1

    while True:

        semaforo.acquire()

        # Input my data and get result from network
        for index, criatura in enumerate(total_criatures[1]):
            output = nets[index].activate(criatura.get_data())

            criatura.angle += output[0]

            criatura.speed += output[1]
            if criatura.speed <= 0:
                criatura.speed = 0.2
            elif criatura.speed > 20:
                criatura.speed = 20

        # Update car and fitness
        remain_cri = 0
        cri_aux = []
        i = 0
        for i in range(len(total_criatures)):
            cri_aux += total_criatures[i]

        i = 0
        for i, criatura in enumerate(total_criatures[1]):
            if criatura.get_alive():
                remain_cri += 1
                criatura.update(cri_aux, screen)
                genomes[i][1].fitness += criatura.get_reward()

        # check
        if remain_cri == 0:
            semaforo.release()
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

        semaforo.release()
        time.sleep(0.01)


def run_neat(config, id_specie):
    # Create core evolution algorithm class
    p = neat.Population(config)
    test = "20"

    # Run NEAT
    if (id_specie == 0):
        try:
            os.mkdir("Results_Sp1/" + test)
        except OSError:
            print("Creation of the directory %s failed" % test)

        # Add reporter for fancy statistical result
        # p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)

        winner = p.run(run_sp1, 300)

        # Show output of the most fit genome against training data.
        print('\nOutput:')
        print('\nBest genome:\n{!s}'.format(winner))
        f = open("Results_Sp1/" + test + "/Results_Sp1.txt", "w+")
        f.write('\nBest genome:\n{!s}'.format(winner))
        f.close()

        node_names = {-1: 'Radar1', -2: 'Radar2', -3: 'Radar3', -4: 'Radar4', -5: 'Radar5', -6: 'R1', -7: 'G1',
                      -8: 'B1', -9: 'R2', -10: 'G2',
                      -11: 'B2', -12: 'R3', -13: 'G3', -14: 'B3', -15: 'R4', -16: 'G4', -17: 'B4', -18: 'R5', -19: 'G5',
                      -20: 'B5', -21: 'PosX', 0: 'Angle', 1: 'Speed'}
        visualize.draw_net(config, winner, True, node_names=node_names, filename="Results_Sp1/" + test + "/Net")
        visualize.plot_stats(stats, ylog=False, view=True, filename="Results_Sp1/" + test + "/avg_fitness.svg")
        visualize.plot_species(stats, view=True, filename="Results_Sp1/" + test + "/speciation.svg")
        with open("Results_Sp1/" + test + "/winner.pkl", "wb") as f:
            pickle.dump(winner, f)
            f.close()

    else:
        try:
            os.mkdir("Results_Sp2/" + test)
        except OSError:
            print("Creation of the directory %s failed" % test)

        # Add reporter for fancy statistical result
        p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)

        winner = p.run(run_sp2, 300)

        # Show output of the most fit genome against training data.
        print('\nOutput:')
        print('\nBest genome:\n{!s}'.format(winner))
        f = open("Results_Sp2/" + test + "/Results_Sp2.txt", "w+")
        f.write('\nBest genome:\n{!s}'.format(winner))
        f.close()

        node_names = {-1: 'Radar1', -2: 'Radar2', -3: 'Radar3', -4: 'Radar4', -5: 'Radar5', -6: 'R1', -7: 'G1',
                      -8: 'B1', -9: 'R2', -10: 'G2',
                      -11: 'B2', -12: 'R3', -13: 'G3', -14: 'B3', -15: 'R4', -16: 'G4', -17: 'B4', -18: 'R5', -19: 'G5',
                      -20: 'B5', -21: 'PosX', 0: 'Angle', 1: 'Speed'}
        visualize.draw_net(config, winner, True, node_names=node_names, filename="Results_Sp2/" + test + "/Net")
        visualize.plot_stats(stats, ylog=False, view=True, filename="Results_Sp2/" + test + "/avg_fitness.svg")
        visualize.plot_species(stats, view=True, filename="Results_Sp2/" + test + "/speciation.svg")
        with open("Results_Sp2/" + test + "/winner.pkl", "wb") as f:
            pickle.dump(winner, f)
            f.close()


if __name__ == "__main__":
    # Set configuration file
    config_path = "./config-feedforward.txt"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Init my game
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()

    pygame.display.flip()

    threads = list()

    for i in range(2):
        t = threading.Thread(target=run_neat, args=(config, i))
        threads.append(t)
        t.start()

    while True:
        time.sleep(0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
