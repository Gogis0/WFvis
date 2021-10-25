import sys
import pygame
import random
import copy
import graph_plotter
import numpy as np
from pygame.locals import *
from constants import *


class Environment:
    def __init__(self, color_list, elimination_probs):
        self.color_list = color_list
        self.elimination_probs = elimination_probs
        self.N = len(color_list)
        self.color_id = 0
        self.background = pygame.Surface((width, height))
        self.background.fill(self.get_env_color())

    def get_env_color(self):
        return self.color_list[self.color_id]

    def change_env(self):
        self.color_id = (self.color_id + 1) % self.N
        self.background.fill(self.get_env_color())

    def get_elim_probs(self):
        return self.elimination_probs[self.color_id]

    def get_background(self):
        return self.background


class Specimen:
    def __init__(self, color):
        self.color = color
        self.is_alive = True

    def __deepcopy__(self, memo):
        return Specimen(self.color)


class Population:
    def __init__(self, screen, env, N=20, row_height=10, specimen_list=None):
        self.N = N
        self.screen = screen
        self.env = env
        self.screen_width, self.screen_height = screen.get_size()
        self.row_height = row_height

        image_dim = (self.row_height // 4, self.row_height // 4)
        self.lightImg = pygame.transform.scale(pygame.image.load('images/light.png'), image_dim)
        self.darkImg = pygame.transform.scale(pygame.image.load('images/dark.png'), image_dim)

        self.specimen_list = []
        self.parents_list = None
        if specimen_list is None:
            for i in range(N):
                color = random.randint(0, len(color_list) - 1)
                print(color)
                self.specimen_list.append(Specimen(color))
        else:
            self.parents_list = []
            for parent, specimen in specimen_list:
                self.parents_list.append(parent)
                self.specimen_list.append(specimen)

        self.row = pygame.Surface((self.screen_width, row_height))
        self.row.fill(self.env.get_env_color())
        self.margin_size = self.screen_width // (N + 1)
        self.redraw()

    def eliminate(self, num=5):
        alive_specimens = list(filter(lambda x: x.is_alive, self.specimen_list))
        sample_weights = [
            elimination_probs[self.env.color_id][s.color] for s in alive_specimens
        ]
        for s in random.choices(alive_specimens, weights=sample_weights, k=num):
            s.is_alive = False
        self.redraw()

    def change_background(self):
        self.row.fill(self.env.get_env_color())

    def redraw(self):
        self.row.fill(self.env.get_env_color())
        for i in range(len(self.specimen_list)):
            s = self.specimen_list[i]
            if s.is_alive:
                position = (self.margin_size * (i + 1), self.row_height // 2)
                pygame.draw.circle(self.row, color_list[s.color], position, self.row_height // 8)
                # if s.color == 0:
                #    self.row.blit(self.lightImg, position)
                # else:
                #    self.row.blit(self.darkImg, position)
        self.y = height // 2

    def generate_offspring(self):
        alive_indices = list(filter(lambda i: self.specimen_list[i].is_alive, range(self.N)))
        chosen_indices = random.choices(alive_indices, k=self.N)
        chosen_specimen = sorted([
            (i, copy.deepcopy(self.specimen_list[i])) for i in chosen_indices
        ], key=lambda x: x[0])
        return chosen_specimen

    def mutate(self):
        pygame.display.flip()
        for i in range(self.N):
            if np.random.rand() < MUTATION_RATE:
                self.specimen_list[i].color = (self.specimen_list[i].color + 1) % len(color_list)
        self.redraw()


def population_shift(screen, population_list, offset, row_height):
    for p in population_list:
        p.y -= offset
        screen.blit(p.row, (0, p.y))
    for p in population_list[1:]:
        for i, s in enumerate(p.specimen_list):
            if s.is_alive:
                position = (p.margin_size * (i + 1), p.y + (row_height // 2))
                pygame.draw.line(p.screen, BLACK, position,
                                 (p.margin_size * (p.parents_list[i] + 1), p.y - (row_height // 2)))


def main():
    fps = 60
    fpsClock = pygame.time.Clock()

    screen = pygame.display.set_mode((width, height))
    N_rows = 5
    row_height = height // N_rows

    env = Environment(bg_list, elimination_probs)
    population_list = [Population(screen, env, N_population, row_height)]
    history_color_0 = []
    history_background_0 = []
    last_background_change = 0

    absolute_offset = 0
    max_y = 0

    # Game loop.
    while True:
        offset_y = 0
        state = 0

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    state = ELIMINATION
                if event.key == pygame.K_LEFT:
                    offset_y -= row_height
                if event.key == pygame.K_RIGHT:
                    offset_y += row_height
                if event.key == pygame.K_DOWN:
                    state = NEW_POPULATION
                if event.key == pygame.K_b:
                    state = ENV_CHANGE
                if event.key == pygame.K_m:
                    state = MUTATION

        absolute_offset += offset_y
        screen.blit(env.get_background(), (0, 0))

        if state == ELIMINATION:
            population_list[-1].eliminate()

        if state == MUTATION:
            population_list[-1].mutate()

        if state == NEW_POPULATION:
            max_y += row_height
            population_shift(screen, population_list, max_y - absolute_offset, row_height)
            absolute_offset = max_y
            population_list.append(
                Population(screen,
                           env,
                           N_population,
                           row_height,
                           population_list[-1].generate_offspring())
            )
            pygame.display.flip()
            pygame.time.delay(1000)
            pygame.display.flip()
            # pygame.time.delay(1000)
            history_color_0.append(
                np.sum([color_list[x.color] == color_list[0] for x in population_list[-1].specimen_list])
            )
            graph_plotter.plot_population_rates(N_population, history_color_0, history_background_0)
        else:
            population_shift(screen, population_list, offset_y, row_height)

        if state == ENV_CHANGE:
            history_background_0.append((last_background_change, len(population_list), env.color_id))
            last_background_change = len(population_list)
            env.change_env()
            population_shift(screen, population_list, offset_y, row_height)

        pygame.display.flip()
        fpsClock.tick(fps)


if __name__ == '__main__':
    main()
