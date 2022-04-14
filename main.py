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


r_thresh = 0.5       # threshold for the edges (default 50%)
f_dir = './films'    # path to the images 
f_ext = '.tif'       # file extension for the images
plot_check = True    # whether to plot original vs. final images


if __name__ == '__main__':

    files = [os.path.join(f_dir, fname) for fname in os.listdir(f_dir) if f_ext in fname]
    
    films = []
    for fname in files:
        print(fname)
    
        # open image
        img = Image.open(fname)
        arr = np.mean(np.asarray(img), axis=2)/2.55  # 0 to 100
    
        # process image
        xc, yc = get_corners(img, r_thresh, show_plot=False)
        arr_final = rotate_crop(img, xc, yc)
        films.append(arr_final)

        # plot check
        if plot_check:
            Ny, Nx = arr_final.shape
            fig,ax=plt.subplots(1,2,figsize=[8,4], dpi=150)
            ax[0].imshow(arr, cmap='gray')
            ax[0].set_title('Original image')
            ax[0].plot(np.tile(xc,2), np.tile(yc,2), markersize=10, color='r', lw=1, marker='x')
            ax[1].imshow(arr_final, cmap='gray')
            ax[1].set_title(f'Final image {Nx}x{Ny}')
            plt.show()
