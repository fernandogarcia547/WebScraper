import numpy as np
import pandas

def extractNumbers(xStr):
    xDigits = [int(d) for d in xStr if d.isdigit()]
    xNum = np.sum([digit*(10**exponent) for digit, exponent in 
                    zip(xDigits[::-1], range(len(xDigits)))])
    return xNum
    
def extractNumbersYear(xStr):
    xDigits = [int(d) for d in xStr if d.isdigit()]
    xNum = np.sum([digit*(10**exponent) for digit, exponent in 
                    zip(xDigits[::-1], range(4))])
    return xNum
    
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
        
def encode(df):
    for column in df.columns:
        for idx in df[column].index:
            x = df.get_value(idx,column)
            try:
                x = unicode(x.encode('utf-8','ignore'),errors ='ignore') if type(x) == unicode else unicode(str(x),errors='ignore')
                df.set_value(idx,column,x)
            except Exception:
                print 'encoding error: {0} {1}'.format(idx,column)
                df.set_value(idx,column,'')
                continue
    return df