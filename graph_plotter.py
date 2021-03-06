import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator

import constants


def plot_population_rates(N, history, backgrounds):
    plt.clf()
    history = np.array(history)
    ax = plt.gca()
    ax.set_ylim([0, N])
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    plt.plot(history, 'o-', label='silver')
    plt.plot(N - history, 'o-', label='grey')
    for (start, end, color) in backgrounds:
        plt.axvspan(start, end, facecolor=np.array(constants.bg_list[color]) / 255, alpha=1)
    if len(backgrounds) > 0:
        plt.axvspan(backgrounds[-1][1], len(history),
                    facecolor=np.array(constants.bg_list[1 - backgrounds[-1][2]]) / 255)
    plt.legend(loc='best')
    plt.xlabel('Generation')
    plt.ylabel('Population size')
    plt.savefig('generated_plots/graph.pdf', dpi=300)
