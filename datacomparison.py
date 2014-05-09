"""
Lets work with different metrics

"""

__author__ = "a_melnikov"

from collections import Counter as ctr


def compare_singles(e1, e2):
    if e1 == e2:
        return 0
    else:
        return 1


def compare_arrays(a1, a2, coeff=1):
    """
    (Union - max_len) / min_len [with hyperbolic weights]:
    ABCDE : FGH -> (8-5)/3 = 1
    ABCDE : ABC -> (5-5)/3 = 0
    ABCDE : AFG -> (7-5)/3 = 0.29
    ABCDE : AFG coeff=100000 -> (7-5)/3 = 0.665
    """   
    sa1 = set(a1)
    sa2 = set(a2)
    l1 = len(sa1)
    l2 = len(sa2)
    sa1.update(sa2)
    l_union = len(sa1)
    l_l = len(a1 + a2)
    intersects = l_l - l_union
    m = min(l1, l2)

    # pss.. you want some magic
    sq_d = (m*m + 4*coeff*m)**0.5
    a = (m - sq_d)/2
    b = coeff / (m - a)
    return coeff/(intersects - a) - b
    #return (l_union - max(l1, l2))*1.0 / min(l1, l2)       its not cool


def get_centroid(arr):
    """
    Find most resent element of plain array
    """
    if len(arr) == 0:
        return -1
    return ctr(arr).most_common(1)[0][0]


def get_array_centroid(arr, part, ofAll=True):
    """
    Find some most resent elements of array of arrays
    part : 0-1 : filter of frequency
    ofAll = True : find some most recent elements of all
    ofAll = False: find elements with frequency of appear in rows greater then part -> maybe empty
    """
    rows_amount = len(arr)
    if rows_amount == 0:
        return -1
    plain_array = []
    for a in arr:
        plain_array += a
    counter = ctr(plain_array)
    el_amount = len(counter)
    res = []
    if ofAll:
        # Find min frequency
        p = int(part*el_amount)
        for el in counter.most_common(p):
            res.append(el[0])
    else:
        p = int(part*rows_amount)
        for cort in counter.most_common():
            if cort[1] >= p:
                res.append(cort[0])
    return res


def main():
    print "main"
    print compare_arrays([1, 2, 3, 4, 5], [6, 7, 1], 100000)
    print get_centroid([1, 9, 5, 4, 1, 3, 9, 7, 5, 4, 9, 7])
    print get_array_centroid([[1, 9], [1, 4], [4, 7, 9], [8, 9]], 0.5, False)


if __name__ == "__main__":
    main()
