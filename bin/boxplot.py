import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


import tkinter as tk
from tkinter import filedialog
import os



def main():
    # todo: load the "results.csv" file from the mia-results directory
    # todo: read the data into a list
    # todo: plot the Dice coefficients per label (i.e. white matter, gray matter, hippocampus, amygdala, thalamus) in a boxplot

    # alternative: instead of manually loading/reading the csv file you could also use the pandas package
    # but you will need to install it first ('pip install pandas') and import it to this file ('import pandas as pd')
    
    data = pd.read_csv("./bin/mia-result/2020-11-10-16-45-44whitestripe/results.csv",sep=';') 
    data.boxplot(by='LABEL', column=['DICE'], grid = False)
    plt.show()
    data.boxplot(by='LABEL', column=['HDRFDST'], grid = False)
    plt.show()


def plot_all(show = False, save=False):

    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askdirectory()
    files = os.listdir(file_path)
    
    data_all = []

    for name in files:
        print('****************** '+name+' ******************')
        data_path = os.path.join(file_path, name, 'results.csv')
        data = pd.read_csv(data_path, sep=';') 
        
        if save:
            data.boxplot(by='LABEL', column=['DICE'], grid = False)
            plt.savefig(os.path.join(file_path, f"result_Dice_{name}.png"), dpi=300)
        if show:
            data.boxplot(by='LABEL', column=['DICE'], grid = False)
            plt.show()

        
        if save:
            data.boxplot(by='LABEL', column=['HDRFDST'], grid = False)
            plt.savefig(os.path.join(file_path, f"result_HDRFDST_{name}.png"), dpi=300)
        if show:
            data.boxplot(by='LABEL', column=['HDRFDST'], grid = False)
            plt.show() 

        data[''] = name[19:]
        data_all.append(data)
    
    data_all = pd.concat(data_all)
    data_all = data_all.groupby(by=["LABEL"])
    data_all.boxplot(by='', column=['DICE'], fontsize=8)
    plt.suptitle('')
    plt.subplots_adjust(hspace=0.5)
    plt.show()
    


if __name__ == '__main__':
    plot_all()
    #main()

