import pygame
import numpy as np
import time
import random

class criatura:
    def __init__(self,nxC, nyC):
        x = random.randint(1, nxC)
        y = random.randint(1, nyC)

        self.xPoints = [x,x+1,x+2]
        self.yPoints = [y,y,y]
        self.brain = ""
        self.radars = []
        self.is_alive = True

    def draw(self, gameState):
        for i in range (0, len(self.xPoints)):
            gameState[self.xPoints[i], self.yPoints[i]] = 1

        return gameState

    def check_radar(self,map):
        self.is_alive = True

def game(name):
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    pygame.init()

    #screen
    width = 1500
    height = 1000
    screen = pygame.display.set_mode((width, height))
    bg = 25,25,25
    screen.fill(bg)

    #celdas
    nxC = 37
    nyC = 25
    dimCW = width / nxC
    dimCH = height / nyC

    gameState = np.zeros((nxC, nyC))

    #Critura inical
    c = criatura(nxC,nyC)
    gameState = c.draw(gameState)

    pauseExect = False

    #bucle ejecución
    while True:

        newGameState = np.copy(gameState)

        #refrescar pantalla
        screen.fill(bg)
        time.sleep(0.2)

        #Eventos de teclado y ratón

        ev = pygame.event.get()

        for event in ev:
            if event.type == pygame.KEYDOWN:
                pauseExect = not pauseExect

            mouseClick = pygame.mouse.get_pressed()

            if sum(mouseClick) > 0:
                posX, posY = pygame.mouse.get_pos()
                celX, celY = int(np.floor(posX / dimCW)), int(np.floor(posY / dimCH))
                newGameState[celX,celY] = not mouseClick[2]

        for x in range (0, nxC):
            for y in range(0,nyC):

                if not pauseExect:


                    #Calculamos el número de vecions cercanos
                    n_neigh = gameState[(x-1) % nxC,(y-1) % nyC] + \
                              gameState[(x) % nxC,(y-1) % nyC] + \
                              gameState[(x+1) % nxC,(y-1) % nyC] + \
                              gameState[(x-1) % nxC,(y) %nyC] + \
                              gameState[(x + 1) % nxC, (y) % nyC] + \
                              gameState[(x - 1) % nxC, (y + 1) % nyC] + \
                              gameState[(x) % nxC, (y + 1) % nyC] + \
                              gameState[(x + 1) % nxC, (y + 1) % nyC]

                    #Rule 1:
                    if gameState[x,y] == 0 and n_neigh == 3:
                        newGameState[x,y] = 1

                    #Rule 2
                    elif gameState[x,y] == 1 and (n_neigh < 2 or n_neigh > 3):
                        newGameState[x,y] = 0



                #vertices
                poly = [((x) * dimCW, y * dimCH),
                        ((x+1)* dimCW, y * dimCH),
                        ((x+1)* dimCW, (y+1) * dimCH),
                        ((x)* dimCW, (y+1) * dimCH)]

                if newGameState[x,y] == 0:
                    pygame.draw.polygon(screen,(128,128,128), poly, 1)
                else:
                    pygame.draw.polygon(screen, (255, 255, 255), poly, 0)

        #actualizamos matriz

        gameState = np.copy(newGameState)

        pygame.display.flip()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    game('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
