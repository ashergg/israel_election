# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 12:46:36 2020

@author: Asher
"""

import numpy as np
import pandas as pd

def bader_ofer(votes, mandates):
    """
    Allocate seats to Parliament according to the Bader-Ofer Law
    
    Parameters
    ----------
    votes : np array
        A (x,) array of the number of votes for each party.
    mandates : int
        Number of seats to be allocated.

    Returns
    -------
    seats: np array.
        An array of the allocated seats

    """
    moded = votes.sum()//mandates
    seats = votes // moded
    while seats.sum() < mandates:
        seats[np.argmax(votes // (seats + 1))] += 1
    return seats


def read_data(url):
    """
    Reads the election results into pandas DataFrame
    
    Parameters
    ----------
    url : string
        url for the official Israeli election results.

    Returns
    -------
    results : pandas DataFrame 
        DataFrame of the election results.
        the DataFrame has with two columns:
            'Party_name' and 'votes'
        the returned results include the data for all the participated parties,
        including parties which didn't get to the election threshold.
        Use 

    """
    
    dfs = pd.read_html(url)
    results = dfs[2].iloc[:,[0,3]]
    results.columns = ['Party_name', 'votes']
    return results

def margin(results, threshold):
    """
    Removes parties which didn't pass the required threshold
    
    Parameters
    ----------
    results : pandas DataFrame
        DESCRIPTION.
    threshold : float
        the required percentage threshold for entering the parliament (not decimal).

    Returns
    -------
    results : pandas DataFrame
        the results DataFrame without parties which didn't pass the threshold.

    """
    if threshold < 1:
        raise ValueError('Enter threshold as percentage')
    return results[results['votes'] > (threshold/100)*results['votes'].sum()]

def short_names(results):
    """
    makes the names shorter in the 'Party_name' Series 

    Parameters
    ----------
    results : pd DataFrame
        the election results.

    Returns
    -------
    results : pd DataFrame
        the results with shrter parties names.

    """
    results['Party_name'] = results['Party_name'].str.split().str[0:2].str.join(' ')
    return results


def main():
    url = 'https://votes23.bechirot.gov.il/nationalresults'
    results = short_names(margin(read_data(url), 2.5))
    results['seats'] = bader_ofer(results['votes'], 120)
    print(results[['Party_name', 'seats']])


if __name__ == '__main__':
    main()
    
    