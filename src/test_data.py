'''Tests for data.py'''

from . import data

def test_SKOL():
    '''Test get_data function'''
    skol = data.SKOL('../../skol/data/annotated/journals/Mycotaxon/Vol054/n1.txt.ann', 'description')
    assert skol.df['description'].iloc[0] == 'APOTHECIA se...8\nµm wide.\n'
    
    