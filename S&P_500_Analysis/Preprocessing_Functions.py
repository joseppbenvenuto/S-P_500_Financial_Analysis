# Project Functions
#
# Description
#
# Below are the different functions used in the analysis.

# Import libraries
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from patsy import dmatrices
from scipy import stats
from statsmodels.stats.outliers_influence import variance_inflation_factor


###########################################################################################################################################
# NEW CODE BLOCK - Histogram Plots and Descriptive Stats Function
###########################################################################################################################################

# Histogram plots for all numeric data minus target value followed by supporting stats
def num_univariate_histogram(df, length, width, rows, col, font, kind):
    if kind == 1:
        X_num = df
        X_num = X_num[X_num.columns[0:-1]]

        sns.set(font_scale = font, style = 'white')
        
        X_num.hist(
            bins = 50, 
            figsize = (width, length), 
            layout = (rows, col), 
            grid = False
        )
        
        plt.show()

        print('\n' + 'X continuous descriptive stats:')
        describe = X_num.describe().T
        display(describe)

    if kind == 2:
        X_num = df

        sns.set(font_scale = font, style = 'white')
        
        X_num.hist(
            bins = 50, 
            figsize = (width, length), 
            layout = (rows, col), 
            grid = False
        )
        
        plt.show()

        print('\n' + 'X continuous descriptive stats:')
        describe = X_num.describe().T
        display(describe)


# * **df** = data frame
# * **length** = legnth of plot (int)
# * **width** = width of plot (int)
# * **rows** = number of rows for subplots (int)
# * **col** = number of columns for subplts (int)
# * **font** = font size ranging from 1-3 (int)
# * **kind** = '1' for all numeric variables outside the target variable and '2' for all numeric variables (int)


###########################################################################################################################################
# NEW CODE BLOCK - Frequency Plots and Descriptive Stats Function
###########################################################################################################################################

# frequency plot for all categorical data followed by supporting stats
def cat_univariate_freq(df, length, width, col_start, col_end, font):
    X_cat = df.select_dtypes(include = ['object'])
    X_cat = X_cat.columns[col_start : col_end]

    for X in X_cat:
        series = round((df[X].value_counts(normalize = True)) * 100, 0)
        series = series.sort_values(ascending = True)

        sns.set(font_scale = font, style = 'white')
        series.plot.barh(figsize = (width, length))
        plt.title(X + ' frequencies')
        plt.xlabel('percent')
        plt.ylabel(X)
        plt.show()


# * **df** = data frame
# * **length** = legnth of plot (int)
# * **width** = width of plot (int)
# * **col_start** = start of columns index to use in functions (int)
# * **col_end** = end of columns index to use in functions (int)
# * **font** = font size ranging from 1-3 (int)


###########################################################################################################################################
# NEW CODE BLOCK - Target Scatter Plot and Descriptive Stats Function
###########################################################################################################################################

# Individual scatter plot with set x and y labels followed by supporting stats
def target_univariate_scatter(df, x, y, length, width, font):
    df = df.reset_index()

    sns.set(font_scale = font, style = 'white')
    plt.figure(figsize = (width, length))
    
    sns.scatterplot(
        data = df, 
        x = x, 
        y = y
    )
    
    plt.title('season ' + y + ' by ' + x)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.show()


# * **df** = data frame
# * **x** = x variable in scatter plot (str)
# * **y** = y variable in scatter plot (str)
# * **length** = legnth of plot (int)
# * **width** = width of plot (int)
# * **font** = font size ranging from 1-3 (int)


###########################################################################################################################################
# NEW CODE BLOCK - Scatter Plots By Many X Variables and One y Variable Function
###########################################################################################################################################

# Scatter plots for numeric data when x is set to an index of columns and the target vairable for y
def num_bivariate_scatter(df, y, x, font, length, width):
    X_num = df.select_dtypes(include = ['float64', 'int64'])

    sns.set(font_scale = font, style = 'white')
    
    plot = sns.pairplot(
        data = df, 
        y_vars = y, 
        x_vars = x, 
        diag_kind = None
    )
    
    plot.fig.set_size_inches(width, length)
    plt.show()


# * **df** = data frame
# * **x** = x variable in scatter plot (str)
# * **y** = y variable in scatter plot (list of column names or str)
# * **font** = font size ranging from 1-3 (int)
# * **length** = legnth of plot (int)
# * **width** = width of plot (int)


###########################################################################################################################################
# NEW CODE BLOCK - Corrolation Heat Map With Corrolation Scores to Target Function
###########################################################################################################################################

# Corrolation heat map for all variables against target variable followed by supporting stats
def num_bivariate_corr_target(df, target, threshold, font, length, width):
    X_corr = df.corr(method = 'pearson')
    X_corr = X_corr[[target]].sort_values(by = [target], ascending = False)

    sns.set(font_scale = font, style = 'white')
    fig, ax = plt.subplots()
    fig.set_size_inches(width, length)
    sns.heatmap(X_corr)
    plt.title('corrolation matrix')
    plt.show()

    display(X_corr)

    X_corr = X_corr.reset_index()
    X_corr[target] = abs(X_corr[target])
    X_corr = X_corr.loc[X_corr[target] < threshold]
    X_corr = list(X_corr['index'])

    print('\n' + 'features to remove: ')
    print(X_corr)


# * **df** = data frame
# * **target** = target variable (str)
# * **threshold** = threshold correlation before suggesting removal of varibale (int)
# * **font** = font size ranging from 1-3 (int)
# * **length** = legnth of plot (int)
# * **width** = width of plot (int)


###########################################################################################################################################
# NEW CODE BLOCK - Average Numeric Data Per Categorical Data Bar Chart and Stats Function
###########################################################################################################################################

# Bar plot to visulaize the average of a given numeric data to a given categorical target followed by supporting stas
def cat_bivariate_avg_target(df, col_start, col_end, target, length, width, font):
    X_cat = df.select_dtypes(include = ['object'])
    X_cat = X_cat.columns[col_start : col_end]

    for X in X_cat:
        label = X
        label = df[[X, target]]
        label = label.sort_values(by = [target], ascending = False)
        label = round(label.groupby([X]).mean(), 0)
        label = label.sort_values(by = [target], ascending = True)
        label['positive'] = label[target] > 0

        sns.set(font_scale = font, style = 'white')
        
        label[target].plot(
            kind = 'barh',
            figsize = (width, length),
            color = label.positive.map({True:'b', False:'r'})
        )
        
        plt.title('average ' + target + ' per ' + X)
        plt.xlabel('average '+ target)
        plt.ylabel(X)
        plt.show()

        label = label.sort_values(by = [target], ascending = False)
        display(label)


# * **df** = data frame
# * **col_start** = start of columns index to use in functions (int)
# * **col_end** = end of columns index to use in functions (int)
# * **length** = legnth of plot (int)
# * **width** = width of plot (int)
# * **font** = font size ranging from 1-3 (int)


###########################################################################################################################################
# NEW CODE BLOCK - Outlier Function
###########################################################################################################################################

# Provides high and low gate for outliers per given column
def remove_outliers(df, col):
    p_25 = df[col].quantile(.25)
    p_75 = df[col].quantile(.75)
    iqr = (p_75 - p_25) * 1.5
    low_outliers = p_25 - iqr
    high_outliers = p_75 + iqr
    df = df.loc[(df[col] > low_outliers) & (df[col] < high_outliers)]
    return ('low end outliers:', low_outliers, 'high end outliers', high_outliers)


# * **df** = data frame
# * **col** = column to analyze for outliers (str)


###########################################################################################################################################
# NEW CODE BLOCK - Sum of Categorical Variables Per Categorical Variable Bar Chart <br> and Stats Function
###########################################################################################################################################

# Counts binary target vairable as a percent per given cetegorical variable followed by supporting stats
def class_cat_bivariate(df, flag, length, width, col_start, col_end):
    X_cat = df.select_dtypes(include = ['object'])
    X_cat = X_cat.columns[col_start : col_end]

    for X in X_cat:
        label1 = df[[X, flag]]
        label1 = round(label1.groupby([X]).sum(), 0)

        label2 = df[[X, flag]]
        label2 = round(label2.groupby([X]).count(), 0)

        label3 = pd.concat([label1, label2], axis = 1)
        label3.columns = ['sum', 'count']
        label3['rate'] = round((label3['sum'] / label3['count']) * 100, 0)
        label3 = label3.sort_values(by = ['rate'], ascending = True)

        label3['rate'].plot.barh(figsize = (width, length))
        plt.title('average ' + flag + ' per ' + X)
        plt.xlabel('rate of '+ flag)
        plt.ylabel(X)
        plt.show()
        label3 = label3.sort_values(by = ['rate'], ascending = False)
        return print(label3)


# * **df** = data frame
# * **flag** = target variable for classification
# * **length** = legnth of plot (int)
# * **width** = width of plot (int)
# * **col_start** = start of columns index to use in functions (int)
# * **col_end** = end of columns index to use in functions (int)


###########################################################################################################################################
# NEW CODE BLOCK - VIF Scores Function
###########################################################################################################################################

# Drops features one at a time until VIF scores are appropriate
def calculate_vif(X, target, threshold, feature_elim):
    feature_list = []
    Feature_vif_list = []
    max = feature_elim
    min = 0

    while min <= max:
        X = X.drop(feature_list, axis = 1, errors = 'ignore')
        features = '+'.join(X.columns[0:len(X.columns)-1])
        y, X1 = dmatrices(target + ' ~' + features, X, return_type = 'dataframe')

        vif = pd.DataFrame()
        vif['vif'] = [variance_inflation_factor(X1.values, i) for i in range(X1.shape[1])]
        vif['features'] = X1.columns
        vif = vif.sort_values(by = ['vif'], ascending = False).reset_index(drop = True)

        vif['vif2'] = vif['vif']
        vif.loc[vif.features == 'Intercept', 'vif2'] = 0
        maxloc = vif.loc[vif['vif2'][0:].idxmax()][1]
        maxloc_num = vif.loc[vif['vif2'][0:].idxmax()][0]

        if maxloc_num > threshold and maxloc != 'Intercept':
            feature_list.append(maxloc)
            Feature_vif_list.append(maxloc_num)
            min += 1
        else:
            min += 1

    vif = vif.drop(['vif2'], axis = 1, errors = 'ingore')
    display(vif)
    print('\n' + 'dropped features: ')

    return [feature_list,Feature_vif_list]


# * **X** = X variables data frame
# * **target** = traget variable (str)
# * **threhold** =  variance inflation factor (int)**
# * **feature_elim** = number of columns (int)
