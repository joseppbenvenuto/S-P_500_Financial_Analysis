#!/usr/bin/env python
# coding: utf-8

# Project Functions
# 
# Description
# 
# Below are the different statistics functions to help describe and visualize data.

# Imported necessary packages
from scipy import stats
import math

import seaborn as sns 
sns.set()

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import random as rnd

import numpy as np


###########################################################################################################################################
# NEW CODE BLOCK - Confidence Interval Function
###########################################################################################################################################

# T_test confidence intervals
def get_95_ci(array_1, array_2):
    sample_1_n = array_1.shape[0]
    sample_2_n = array_2.shape[0]
    sample_1_mean = array_1.mean()
    sample_2_mean = array_2.mean()
    sample_1_var = array_1.var()
    sample_2_var = array_2.var()
    mean_difference = sample_1_mean - sample_2_mean 
    std_err_difference = math.sqrt((sample_1_var/sample_1_n) + (sample_2_var/sample_2_n))
    margin_of_error = 1.96 * std_err_difference
    ci_lower = mean_difference - margin_of_error
    ci_upper = mean_difference + margin_of_error
    return (round(ci_lower,2), round(ci_upper,2))


# * **df** = data frame


###########################################################################################################################################
# NEW CODE BLOCK - T-test With Supporting Bar Plots and Error Bars Function
###########################################################################################################################################

# Descriptive stats, t-tests, confidence intervals, and bar plots for two columns
def series_stats_gen(string, column, string2, column2, title, y_axis, compound_years, length, width, font):
    
    # Legend
    print('\n')
    legend = [
        ('Legend',''),
        ('',''),
        ('Decade1','years >= 1979 & < 1989'),
        ('Decade2','years >= 1989 & < 1999'),
        ('Decade3','years >= 1999 & < 2009'),
        ('Decade4','years >= 2009 & < 2019')
        ]

    for label, value in legend:
        print(f"{label:{25}} {value:.{25}}")
    
    print('\n')
    print(string, column.name, 'Treatment                 ', string2, column2.name, 'Control')
    
    # Tuple unpacking to show descriptive stats
    mode = round(sum(column.mode())/len(column.mode()),2)
    mode2 = round(sum(column2.mode())/len(column2.mode()),2)
    discriptives = [(
        
        'Mean:',round(column.mean(),2),
        '   Mean:',round(column2.mean(),2)
    ),
        (
            'Standard Error:',round(math.sqrt(column.var()/column.count()),2),
            '   Standard Error:',round(math.sqrt(column2.var()/column2.count()),2)
        ),
        
        (
            'Median:',round(column.median(),2),
            '   Median:',round(column2.median(),2)
        ),

        (
            'Mode:',mode,
            '   Mode:',mode2
        ),

        (
            'Std:',round(column.std(),2),
            '   Std:',round(column2.std(),2)
        ),

        (
            'Variance:',round(column.var(),2),
            '   Variance:',round(column2.var(),2)
        ),

        (
            'Range:',round(column.max()-column.min(),2),
            '   Range:',round(column2.max()-column2.min(),2)
        ),

        (
            'Min:',round(column.min(),2),
            '   Min:',round(column2.min(),2)
        ),

        (
            'Max:',round(column.max(),2),
            '   Max:',round(column2.max(),2)
        ),
            
        (
            'Sum:',round(column.sum(),2),
            '   Sum:',round(column2.sum(),2)
        ),

        (
            'Count:',round(column.count(),2),
            '   Count:',round(column2.count(),2)
        )]

    for label, value, label2, value2 in discriptives:
        print(f"{label:{25}} {value:.>{25}} {label2:{30}} {value2:.>{25}}")

    print('\n')

    # T-test stats
    diff = round(column.mean()-column2.mean(),2)

    t_stat = stats.ttest_ind(
        column, 
        column2, 
        equal_var = False
        )
        
    t_stat = round(t_stat[0],2)

    p_value = stats.ttest_ind(
        column, 
        column2, 
        equal_var = False
        )
        
    p_value = round(p_value[1],2)

    ci = get_95_ci(column, column2)
    lower = ci[0]
    upper = ci[1]

    dist = (
        round(lower + column2.mean(), 2), 
        round(((column.mean() - column2.mean()) + column2.mean()), 2), 
        round(upper + column2.mean(), 2)
        )

    cost_of_book = column.tolist()[0]
    book_value = column2.tolist().pop()
    compound_return = round(((book_value/cost_of_book)**(1/compound_years)-1)*100, 2)

    ci1 = [
        ('Difference in Means:', diff),
        ('T-Stat:', t_stat),
        ('P-Value:', p_value), 
        ('95% CI (two-tail):', str(ci)),
        ('Dist:', str(dist)),
        (str(compound_years) + 'Yrs Compound Return:', str(str(compound_return) + '%'))
        ]

    for label, value in ci1:
        print(f"{label:{28}} {value:.>{28}}")

    print('\n')
    
    # Bar plot with error bars for t-test supportive visualization
    col1 = column
    col2 = column2

    mean1 = col1.mean()
    var1 = col1.var()
    count1 = col1.count()
    upper1 = round((math.sqrt(var1/count1))*1.96,2)
    lower1 = round((math.sqrt(var1/count1))*1.96,2)

    mean2 = col2.mean()
    var2 = col2.var()
    count2 = col2.count()
    upper2 = round((math.sqrt(var2/count2))*1.96,2)
    lower2 = round((math.sqrt(var2/count2))*1.96,2)

    means = [mean1,mean2] 
    ci = [(lower1,lower2),(upper1,upper2)]

    sns.set(font_scale = font)
    plt.figure(figsize = (length, width))
    sns.set_style('white')
    blue_patch = mpatches.Patch(color = 'b', label=string)
    orange_patch = mpatches.Patch(color = 'darkorange', label=string2)
    plt.legend(handles=[blue_patch,orange_patch])
    plt.bar([0,1], means, yerr = ci, alpha = 1, align = 'center',color = ("b","darkorange"))
    plt.xticks(range(len(means)), [str(x) for x in ['Treatment','Control']])
    plt.ylabel(y_axis)
    plt.title(title)
    return plt.show()


###########################################################################################################################################
# NEW CODE BLOCK - Line Plots for Five Columns Function
###########################################################################################################################################

# Line plots for five columns
def line_plot(
    string1, string2, string3, string4, string5, string6, 
    column, column2, column3, column4, column5, column6, 
    data, font, length, width
):
    
    # Line plots (sub plots)
    print('\n')
    
    sns.set(font_scale = font, style = 'white')

    fig, axs = plt.subplots(2, 3, figsize = (length, width))
    axs[0,0].grid(False)
    axs[0,0].set_title(string2 + ' by ' + string1)
    axs[0,0].plot(data[column], data[column2], color = 'darkblue')
    axs[0,0].set_xlabel(string1)
    axs[0,0].set_ylabel(string2)

    axs[0,1].grid(False)
    axs[0,1].set_title(string3 + ' by ' + string1)
    axs[0,1].plot(data[column], data[column3], color = 'darkorange')
    axs[0,1].set_xlabel(string1)
    axs[0,1].set_ylabel(string3)

    axs[0,2].grid(False)
    axs[0,2].set_title(string4+' by ' + string1)
    axs[0,2].plot(data[column], data[column4], color = 'darkgreen')
    axs[0,2].set_xlabel(string1)
    axs[0,2].set_ylabel(string4)

    axs[1,0].grid(False)
    axs[1,0].set_title(string5 + ' by ' + string1)
    axs[1,0].plot(data[column], data[column5], color = 'darkred')
    axs[1,0].set_xlabel(string1)
    axs[1,0].set_ylabel(string5)

    axs[1,1].grid(False)
    axs[1,1].set_title(string6 + ' by ' + string1)
    axs[1,1].plot(data[column], data[column6], color = 'blueviolet')
    axs[1,1].set_xlabel(string1)
    axs[1,1].set_ylabel(string6)

    # Plot to delete due to odd number of plots
    fig.delaxes(axs[1,2])

    # set the spacing between subplots
    plt.subplots_adjust(
        left = 0.1,
        bottom = 0.1, 
        right = 0.7, 
        top = 0.9, 
        wspace = 0.4, 
        hspace = 0.4
    )

    return plt.show()
