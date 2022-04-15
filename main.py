#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 08:42:29 2022

@author: glj
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from CornerReg import get_corners, rotate_crop


def get_films(f_dir, f_ext, r_thresh, plot_check):
    '''
    Main function for cropping and rotating all images in a directory.
    Parameters
    ----------
    f_dir : name of the directory containing scanned image files (str)
    f_ext : file extension to identify images (str)
    r_thresh : percent threshold (0-1) to use for defining r-edge pixels.
               0.5 seems to work well for the scanned films.
               0.05 works well for the provided 'imgs/example.jpg'.
    plot_check : whether to plot the original vs. cropped/rotated images (bool)

    Returns
    -------
    films : a list of 2D numpy arrays, the cropped and rotated film scans.
            the arrays may have different dimensions.

    '''
    
    files = [os.path.join(f_dir, fname) for fname in os.listdir(f_dir) if f_ext in fname]
    
    films = []
    for fname in files:
        print(fname)
    
        # open image
        img = Image.open(fname)
        arr = np.mean(np.asarray(img), axis=2)/2.55  # 0 to 100
    
        # process image
        xc, yc = get_corners(img, r_thresh, show_plot=False)  # x,y corner coordinates
        arr_final = rotate_crop(img, xc, yc)                  # rotated + cropped array
        films.append(arr_final)                               # append array to total list

        # plot check
        if plot_check:
            Ny, Nx = arr_final.shape
            fig,ax=plt.subplots(1,2,figsize=[8,4], dpi=150)
            ax[0].imshow(arr, cmap='gray')
            ax[0].plot(np.tile(xc,2), np.tile(yc,2), markersize=10, color='r', lw=1, marker='x')
            ax[0].set_title('Original image')
            ax[1].imshow(arr_final, cmap='gray')
            ax[1].set_title(f'Final image {Nx}x{Ny}')
            plt.show()
            
    return films


if __name__ == '__main__':
    
    r_thresh = 0.5       # threshold for the edges (default 50%)
    f_dir = './films'    # path to the images 
    f_ext = '.tif'       # file extension for the images
    plot_check = True    # whether to plot original vs. final images

    get_films(f_dir, f_ext, r_thresh, plot_check)
    
