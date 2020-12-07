import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


import tkinter as tk
from tkinter import filedialog
import os




def plot_all(show = False, save=False):

    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askdirectory()
    files = os.listdir(file_path)
    
    data_all = {'Amygdala Mean':[], 'GrayMatter Mean':[], 'Hippocampus Mean':[], 'Thalamus Mean': [], 'WhiteMatter Mean':[], 'Mean all':[], 'Run':[]}

    for name in files:
        print('****************** '+name+' ******************')
        data_path = os.path.join(file_path, name, 'results_summary.csv')
        data = pd.read_csv(data_path, sep=';') 

        data_all['Amygdala Mean'].append(data.values[0][3])
        data_all['GrayMatter Mean'].append(data.values[4][3])
        data_all['Hippocampus Mean'].append(data.values[8][3])
        data_all['Thalamus Mean'].append(data.values[12][3])
        data_all['WhiteMatter Mean'].append(data.values[16][3])
        data_all['Run'].append(name[20:])
        data_all['Mean all'].append(np.mean(np.array( [data.values[0][3], data.values[4][3], data.values[8][3], data.values[12][3], data.values[16][3]] )))
        
    plt.plot(data_all['Run'], data_all['Amygdala Mean'], 'o', label='Amygdala Mean')
    plt.plot(data_all['Run'], data_all['GrayMatter Mean'], 'x', label='GrayMatter Mean')
    plt.plot(data_all['Run'], data_all['Hippocampus Mean'], '+', label='Hippocampus Mean')
    plt.plot(data_all['Run'], data_all['Thalamus Mean'], '*', label='Thalamus Mean')
    plt.plot(data_all['Run'], data_all['WhiteMatter Mean'], '^', label='WhiteMatter Mean')
    plt.plot(data_all['Run'], data_all['Mean all'], 's', label='Mean all')
    plt.xlabel('Run Parameters')
    plt.ylabel('Dice')
    plt.legend()

    plt.xticks(rotation=90, fontsize=8)
    plt.show()

if __name__ == '__main__':
    plot_all()
    #main()

