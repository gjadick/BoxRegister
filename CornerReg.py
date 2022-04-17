#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 08:43:38 2022

@author: glj
"""


import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import convolve2d


def get_corners(img, r_thresh, c_edge=3, show_plot=True):
    '''
    Returns x,y corners of scanned film, assuming plain background.
    Inputs:
     - img: PIL image object, input.
     - r_thresh: % threshold for sobel-filtered image, 
                 for choosing coordinates.
     - c_edge: N pixels to cut off from edge consideration,
               to remove edge detection from image bounds.
     - show_plot: bool, whether to plot result.
    '''
    #arr = np.mean(np.asarray(img), axis=2)  # 0 to 255
    arr = np.asarray(img)[:,:,0]/2.55  # 0 to 100

    sobel_y = np.array([[-1,-2,-3,-2,-1],
                        [ 0, 0, 0, 0, 0],
                        [ 1, 2, 3, 2, 1]])

    sobel_x = sobel_y.T
    arr_dx = convolve2d(arr, sobel_x, mode='same')
    arr_dy = convolve2d(arr, sobel_y, mode='same')
    arr_dr = np.sqrt(arr_dx**2 + arr_dy**2)
    arr_dr = (arr_dr - np.min(arr_dr))/(np.max(arr_dr) - np.min(arr_dr)) # rescale to range 0-1

    arr_dr_thresh = np.zeros(arr_dr.shape)
    arr_dr_thresh[arr_dr > r_thresh] = 1

    arr_dr_mask = arr_dr_thresh.astype(bool)
    Ny, Nx = arr_dr.shape
    c = c_edge  # cutoff edges
    yvec, xvec = np.arange(c,Ny-c), np.arange(c,Nx-c)
    xcoord, ycoord = np.meshgrid(xvec, yvec)

    ycoord = ycoord[arr_dr_mask[c:-c, c:-c]]
    xcoord = xcoord[arr_dr_mask[c:-c, c:-c]]

    ## get the four corners

    q1_mask = np.all([[xcoord >= Nx/2],[ycoord < Ny/2]], axis=0)[0]
    q2_mask = np.all([[xcoord < Nx/2],[ycoord < Ny/2]], axis=0)[0]
    q3_mask = np.all([[xcoord < Nx/2],[ycoord >= Ny/2]], axis=0)[0]
    q4_mask = np.all([[xcoord >= Nx/2],[ycoord >= Ny/2]], axis=0)[0]

    xcorners, ycorners = [], []
    for qmask in [q1_mask, q2_mask, q3_mask, q4_mask]:
        imax = np.argmax((xcoord[qmask]-Nx/2)**2 + (ycoord[qmask]-Ny/2)**2)
        xcorners.append(xcoord[qmask][imax])
        ycorners.append(ycoord[qmask][imax])
    xcorners, ycorners = np.array(xcorners), np.array(ycorners)
    
    # plot check: show the corners
    if show_plot:
        fig,ax=plt.subplots(1,2,figsize=[8,4], dpi=150)
        ax[0].imshow(arr_dr_thresh, cmap='gray')
        ax[0].plot(xcoord, ycoord, ls='', marker='.', color='None', markeredgecolor='r', markeredgewidth=.5, alpha=0.02)   
        ax[0].set_title('Threshold coordinates detected')
        ax[1].imshow(arr, cmap='gray')
        ax[1].plot(np.tile(xcorners,2), np.tile(ycorners,2), markersize=10, color='r', lw=1, marker='x')
        ax[1].set_title('Final corners identified')
        plt.show()

    return xcorners, ycorners


def rotate_crop(img, xcorners, ycorners):
    '''
    Rotate img with known corners to match x,y axes.
    Returns a numpy array of the image.
    Inputs:
     - img: PIL image object
     - xcorners/ycorners: coordinates of 4 corners.
    '''
    # get rotate angle
    theta = np.arctan((ycorners[1]-ycorners[0])/(xcorners[1]-xcorners[0]))*180/np.pi
    theta_rad = theta*np.pi/180.0

    # rotate about center, convert to np object
    #arr_rot = np.mean(np.asarray(img.rotate(theta)),axis=2)
    arr_rot = np.asarray(img.rotate(theta))[:,:,0] # red channel, 0 to 255
    Ny, Nx = arr_rot.shape
    
    # get rotated corners
    rvec = np.array([xcorners, ycorners])
    cvec = np.array([Nx/2*np.ones(4), Ny/2*np.ones(4)])  # center vec
    crvec = rvec - cvec
    A = np.array([[np.cos(theta_rad),  np.sin(theta_rad)], 
                  [-np.sin(theta_rad), np.cos(theta_rad)]])
    xrot, yrot = A@crvec + cvec

    # crop to min/max x,y coordinates
    x0, xf = int(np.min(xrot)), int(np.max(xrot)) + 1
    y0, yf = int(np.min(yrot)), int(np.max(yrot)) + 1
    
    return arr_rot[y0:yf, x0:xf]

