import math

def gap(g, m, n):

    an=None

    def prime(a):
        result=True
        for x in range(2,max(4,int(math.sqrt(a))+2)):
            if a%x==0:
                print x
                result=False
                break

        return result

    c=range(m,n)

    d=filter(prime,range(2,6))

    #print d
    print filter(prime,[916133, 916141])

    for y in d:

        #print "heihei",c

        t=lambda x: x%y!=0 or x<=y

        c=filter(t,c)

    #print "haha",c


    if len(c)>=2:
        for a in range(1,len(c)):
            if (c[a]-c[a-1])==g:
                an=[c[a-1],c[a]]
                break

    return an

print gap(4,30000,30001)



---------------

import math

def gap(g, m, n):

    an=None

    def prime(a):
        result=True
        for x in range(2,int(math.sqrt(a))+1):
            if a%x==0:
                result=False
                break

        return result


    d=filter(prime,range(2,10))



    #print d
    #print filter(prime,(30067,30071))
    def prime2(c,d):

        for y in d:

            #print "heihei",c

            t=lambda x: x%y!=0 or x<=y

            c=filter(t,c)

        return c


    #print "haha",c
    c=prime2(range(1,1000),d)

    c=prime2(range(m,n),c)

    if len(c)>=2:
        for a in range(1,len(c)):
            if (c[a]-c[a-1])==g:
                an=[c[a-1],c[a]]
                break

    return an

#print gap(4,30000,31000)



