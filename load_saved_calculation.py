'''
preprocess_spectrum.py

version 1.0
last updated: June 2019

by Trevor Arp
Quantum Materials Optoelectronics Laboratory
Department of Physics and Astronomy
University of California, Riverside, USA

All rights reserved.

Description:
A script to load and display saved data generated by qnttenna.py

See accompanying README.txt for instructions on using this code
'''

from qnttenna import load_spectrum_data, find_optimum_peaks, gauss

from matplotlib.colorbar import ColorbarBase
import matplotlib.colors as colors
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1.inset_locator import InsetPosition

import numpy as np
import matplotlib.pyplot as plt
from os.path import join, exists
import argparse

'''
Loads the calculation data found in directory, saved in the standard format by qnttenna.save_calculation

If it can't find the directory will search local 'calculations' directory for autosave

returns in standard format: calc_data, spectrum
Where calc_data is an array containing: [l0, dl, w, Delta]
Where l0, dl, w are all parameters, and Delta is the power bandwidth with dl for rows,
l0 for columns and w for the third axis.
Spectrum is the input spectrum data as two columns
'''
def load_calculated_data(directory):
    if not exists(directory):
        if exists(join('calculations', directory)):
            directory = join('calculations', directory)
        else:
            print('Error could not find ' + str(directory))
            return
    l0 = np.loadtxt(join(directory, 'l0.txt'))
    dl = np.loadtxt(join(directory, 'dl.txt'))
    w = np.loadtxt(join(directory, 'w.txt'))
    spectrum = np.loadtxt(join(directory, 'spectrum.txt'))
    rows = dl.size
    cols = l0.size
    N = w.size
    Delta = np.zeros((rows, cols, N))
    for i in range(N):
        Delta[:,:,i] = np.loadtxt(join(directory, 'Delta_' + str(i) + '.txt'))
    return [l0, dl, w, Delta], spectrum
#

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    helpstr = "Path to directory of saved output files, by default search to local calculations directory"
    parser.add_argument("savefile", help=helpstr)
    parser.add_argument("-w", "--width", type=float, help="Absorber width to display, by default displays the maximum")
    parser.add_argument("-n", "--npeaks", type=float, help="Number of peaks to search for in the Delta parameter space")
    args = parser.parse_args()
    directory = args.savefile

    xinches = 5.0
    yinches = 8.75
    fig1 = plt.figure(directory+' Delta', figsize=(xinches, yinches), facecolor='w')

    width = 3.75
    xmargin = 0.7
    height = width
    ymargin = 0.5
    yint = 0.5

    ax1 = plt.axes([xmargin/xinches, (ymargin + height + yint)/yinches, width/xinches, height/yinches])
    ax2 = plt.axes([xmargin/xinches, ymargin/yinches, width/xinches, height/yinches])

    calc_data, spectrum = load_calculated_data(directory)
    [l0, dl, w, Delta] = calc_data

    if args.width is None:
        display_width = np.max(w)
    else:
        display_width = args.width

    if args.npeaks is None:
        npeaks = 2
    else:
        npeaks = int(args.npeaks)

    clrs = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5']

    peak = find_optimum_peaks(l0, dl, w, Delta, npeaks)
    wi = np.searchsorted(w, display_width)

    print("Displaying w = " + str(w[wi]) + " nm")
    print("Calculated values of w:")
    print(list(w))

    cmap = plt.get_cmap('viridis')
    cnorm  = colors.Normalize(vmin=0.0, vmax=1.0)
    scalarMap = cm.ScalarMappable(norm=cnorm, cmap=cmap)
    scalarMap.set_array(Delta)

    d = Delta[:,:,wi]/np.max(Delta[:,:,wi]) # normalized data

    # np.flipud is used to get the vertical axis into the normal orientation
    ax1.imshow(np.flipud(d), cmap=cmap, norm=cnorm, extent=(np.min(l0), np.max(l0), np.min(dl), np.max(dl)), aspect='auto')
    for j in range(npeaks):
        ax1.plot(peak[j][wi,1], peak[j][wi,2], 'o', c=clrs[j])

    ax1.set_ylabel(r'$\Delta \lambda$ (nm)')
    ax1.set_xlabel(r'$\lambda_{0}$ (nm)')
    ax1.set_title(r'$\Delta$ at w =' + str(w[wi]) + ' nm for ' + directory)

    axpbar = plt.axes([0, 0, 101, 101], zorder=2)
    axpbar.spines['bottom'].set_color('w')
    axpbar.spines['top'].set_color('w')
    axpbar.spines['left'].set_color('w')
    axpbar.spines['right'].set_color('w')
    axpbar.tick_params(axis='x', colors='w')
    axpbar.tick_params(axis='y', colors='w')
    axpbar.set_axes_locator(InsetPosition(ax1, [0.45, 0.91, 0.45, 0.05]))
    cb1 = ColorbarBase(axpbar, cmap=cmap, norm=cnorm, orientation='horizontal', ticks=[0.0, 0.25, 0.5, 0.75, 1.0])
    cb1.outline.set_edgecolor('w')
    cb1.set_label(r'$\Delta = A-B$ (arb.)', color='w')

    ax2.plot(spectrum[:,0], spectrum[:,1]/np.max(spectrum[:,1]), '-k')

    xs = np.linspace(np.min(l0), np.max(l0), 400)
    norm = w[wi]*np.sqrt(2*np.pi)
    for j in range(npeaks):
        ax2.plot(xs, norm*gauss(xs, w[wi], peak[j][wi,1]-peak[j][wi,2]/2), color=clrs[j])
        ax2.plot(xs, norm*gauss(xs, w[wi], peak[j][wi,1]+peak[j][wi,2]/2), color=clrs[j])
        ax2.text(peak[j][wi,1]-peak[j][wi,2]/2, 1.12, r'$\lambda_0 = $' + str(peak[j][wi,1]) + ' nm', color=clrs[j], ha='left')
        ax2.text(peak[j][wi,1]-peak[j][wi,2]/2, 1.07, r'$\Delta \lambda = $' + str(peak[j][wi,2]) + ' nm', color=clrs[j], ha='left')
    ax2.text(0.5, 0.95, r'w = '+ str(w[wi]) + ' nm', color='black', ha='center', transform=ax2.transAxes)

    ax2.set_xlim(np.min(l0), np.max(l0))
    ax2.set_ylim(0.0, 1.25)
    ax2.set_xlabel('wavelength (nm)')
    ax2.set_ylabel('spectral irradience (arb.)')

    fig1.show()

    plt.show()
#
