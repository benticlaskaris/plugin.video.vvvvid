import urllib2

def f(m):
    l = list()
    o = 0
    b = None
    while not b and o < len(m):
        n = m[o] <<2
        o +=1
        k = -1
        j = -1
        if o < len(m):
            n += m[o] >> 4
            o += 1
            if o < len(m):
                k = (m[o - 1] << 4) & 255;
                k += m[o] >> 2;
                o += 1
                if o < len(m):
                    j = (m[o - 1] << 6) & 255;
                    j += m[o]
                    o += 1
                else:
                    b = True
            else:
                b = True
        else:
            b = True
        
        l.append(n)
        
        if k != -1:
            l.append(k)
            
        if j != -1:
            l.append(j)
            
    return l


def dec_ei(h):
    g = 'MNOPIJKL89+/4567UVWXQRSTEFGHABCDcdefYZabstuvopqr0123wxyzklmnghij'
    c = list()
    for e in range(0,len(h)):
        c.append(g.find(h[e]))
    for e in range(len(c)*2-1,-1,-1):
        #print 'e=' + str(e)
        a = c[e % len(c)] ^ c[(e+1)%len(c)]
        #print 'a='+str(a)
        c[e%len(c)] = a
        #print 'c['+str(e % len(c))+']='+ str(c[e % len(c)])
    c = f(c)
    d = ''
    for e in range(0,len(c)):
        d += '%'+ (('0'+ (str(format(c[e],'x'))))[-2:])
    return urllib2.unquote(d)