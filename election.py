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
        seats.iloc[np.argmax(votes // (seats + 1))] += 1
    return seats


def read_data(url):
    """
    Read the election results into pandas DataFrame
    
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
    if dfs[2].shape[1] == 5:
        results = dfs[2].iloc[:,[0,1,4]]
    else:
        results = dfs[2].iloc[:,[0,1,3]]
    results.columns = ['Party_name', 'letters', 'votes']
    return results

def margin(results, threshold):
    """
    Remove parties which didn't pass the required threshold
    
    Parameters
    ----------
    results : pandas DataFrame
        election results.
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
    Make the names shorter in the 'Party_name' Series 

    Parameters
    ----------
    results : pd DataFrame
        the election results.

    Returns
    -------
    results : pd DataFrame
        the results with shrter parties names.

    """
    results['Party_name'] = (results['Party_name'].str.split()
                             .str[0:2].str.join(' '))
    return results

def merge_agreements(results, agreements):
    merged_results = results[~results['letters']
                             .isin(np.array(agreements).flatten())]
    sub_results = []
    for agreement in agreements:
        agreements_results = results[results['letters'].isin(agreement)]
        merged_results = pd.concat([merged_results,
                    pd.DataFrame(agreements_results.sum()).transpose()],
                                   ignore_index=True)
        sub_results.append(agreements_results)
    return merged_results, sub_results

def allocate(results, agreements, threshold):
    results = margin(results, threshold)
    merged_results, sub_results = merge_agreements(results, agreements)
    merged_results['seats'] = bader_ofer(merged_results['votes'], 120)
    for i in range(len(sub_results)):
        seats = int(merged_results[merged_results['letters'] 
                                   == sub_results[i]['letters'].sum()]['seats'])
        sub_results[i]['seats'] = bader_ofer(sub_results[i]['votes'], seats)
        #TODO: check reason for warnning
    results = pd.concat([pd.merge(results, merged_results)]
                        + [pd.merge(results, i) for i in sub_results],
                        ignore_index=True).sort_values(by=['seats'],
                                                       ascending=False,
                                                       ignore_index=True)
    return results

def read_agreements():
    agreements = pd.read_csv('agreements.csv', header=None).to_numpy()
    return agreements

def main():
    url = 'https://votes23.bechirot.gov.il/nationalresults'
    results = read_data(url)
    agreements = read_agreements()
    results = allocate(results, agreements, 3.25)
    print(results[['letters', 'seats']])


if __name__ == '__main__':
    main()
    
    