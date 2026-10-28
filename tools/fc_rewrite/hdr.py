
def D(*a): return [(i,None,None,None,None) for i in a]
def T(i,q,c,d1,d2,e=None): return (i,q,c,[d1,d2],e or c[0].upper()+c[1:]+('' if c.endswith('.') else '.'))
