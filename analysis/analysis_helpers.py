# analysis helper functions

import numpy as np


def organize_data(data):
    '''
    input : original data df
    output: data df with:  - exp_version
                           - score
                           - confidence rating
    '''
    
    # organize scores
    data['proportion_correct'] = np.nan
    
    data.loc[(data['responses'].str.contains('judgement'))
            &(data['responses'].str.contains('0'))
            &(data['correct_answer']==0), 'proportion_correct']=1

    data.loc[(data['responses'].str.contains('judgement'))
            &(data['responses'].str.contains('1'))
            &(data['correct_answer']==1), 'proportion_correct']=1

    data.loc[(data['responses'].str.contains('judgement'))
            &(data['responses'].str.contains('1'))
            &(data['correct_answer']==0), 'proportion_correct']=0

    data.loc[(data['responses'].str.contains('judgement'))
            &(data['responses'].str.contains('0'))
            &(data['correct_answer']==1), 'proportion_correct']=0
    
    # organize confidence ratings
    data['confidence'] = np.nan
    
    for idx,x in data[data['proportion_correct'].notna()].iterrows():
        for a in range(0,4):
            data.loc[idx,'confidence']=int(data.loc[idx+1]['responses'][-2])
    
    return(data)