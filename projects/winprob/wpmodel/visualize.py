import numpy as np
import matplotlib.pyplot as plt
import StringIO
from matplotlib.pylab import figure



def plot_winprobability(timestamps, winprob, filename="winprob.png"):
    """Plot and save win probability

    Keyword arguments
    winprob - vector of win probabilities
    filename - name of the file where the plot will be saved
    """
    fig = create_winprobability_fig(timestamps, winprob)
    fig.savefig(filename)
#    fig.close()
    return filename


def fig_to_png_string(fig):
    canvas=FigureCanvas(fig)
    png_output = StringIO.StringIO()
    canvas.print_png(png_output)
    png_output = png_output.getvalue().encode("base64")
    print png_output
    return png_output
    


def create_winprobability_fig(timestamps, winprob):
    """Plot and save win probability

    Keyword arguments
    winprob - vector of win probabilities
    filename - name of the file where the plot will be saved
    """
    fig = figure(figsize = (24, 12))
    ## color for plot
    bg_color = np.array([2, 32, 39]) / float(255)
    match_durance = max(timestamps)

    wp_plt = fig.add_subplot(111, axisbg = bg_color)
    #ax.append(aPlot)
    wp_plt.plot(timestamps, winprob,
                color = 'goldenrod', linewidth=4,
                marker="o", markersize=14, markeredgecolor="goldenrod")
    ## Set meaningful x and y limits
    wp_plt.set_ylim(-0.01, 1.01)
    wp_plt.set_xlim(1, match_durance + 1)
    ## Label the axes
    time_steps = np.arange(0, match_durance, 10)
    time_steps = np.append(time_steps, match_durance)
    time_step_labels = [str(x) + ":00" for x in time_steps]
    wp_plt.set_xticks(time_steps)
    wp_plt.set_xticklabels(labels = time_step_labels, size = 25)
    wp_plt.set_yticks([0, 0.25, 0.5, 0.75, 1])
    wp_plt.set_yticklabels(labels = ["0%", "25%", "50%", "75%", "100%"], size = 25)
    ## Add a grid
    wp_plt.grid(color="lightgrey", linewidth=1)
    wp_plt.plot((1, match_durance + 1), (0.5, 0.5), 'k-', color = "tomato", linestyle='-')
    return fig


