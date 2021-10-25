WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
SILVER = (192, 192, 192)
LIGHT_GREY = (211, 211, 211)
GREY = (128, 128, 128)
DIM_GREY = (105, 105, 105)

color_list = [SILVER, DIM_GREY]
bg_list = [LIGHT_GREY, GREY]

(width, height) = (1200, 600)

N_population = 20
NEW_POPULATION = 1
ELIMINATION = 2
ENV_CHANGE = 3
MUTATION = 4
MUTATION_RATE = 0.4
elimination_probs = [
    [0.3, 0.7],
    [0.8, 0.2]
]
