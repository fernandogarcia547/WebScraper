def extractNumbers(xStr):
    xDigits = [int(d) for d in xStr if d.isdigit()]
    xNum = np.sum([digit*(10**exponent) for digit, exponent in 
                    zip(xDigits[::-1], range(len(xDigits)))])
    return xNum
    