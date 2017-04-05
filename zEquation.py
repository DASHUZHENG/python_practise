# -*- coding: utf-8 -*-
version="0.1"
import numpy
import sympy
import math

import scipy.integrate as integrate
import scipy.misc as diff

import zDatabase
import __future__   #the division calculation prolbem!

class zEquation():

    def __init__(self):
        pass
    #"SOLIDV":("VSPOLY","DNSDIP","VSPO","DNSTMLPO"),
    # Solid Volume Method

    #Start with EOS
    def RK(self,para,temp,pres,volume=0,tag="V"):

            #RK para=["RK",tc,pc,omega] omega is not useful in RK
            eosa=0.42748*8.3145*8.3145*pow(para[1],2.5)/para[2]
            eosb=0.08664*8.3145*para[1]/para[2]
            
            #Test Polar RK
            #eosa=0.43808*8.3145*8.3145*pow(para[1],2.5)/para[2]
            #eosb=0.0814*8.3145*para[1]/para[2]
            
            if tag=="V":

                eospara=[1,-8.3145*temp/pres,eosa/pres/math.sqrt(temp)-eosb*8.3145*temp/pres-eosb*eosb,-eosa/math.sqrt(temp)*eosb/pres]
                
                try:
                    #RK Equation
                    eosv=numpy.poly1d(eospara)
                    eosr=eosv.r

                    #print("EOS Debug 1 %s" % eosr)
                    vreal=lambda x:x>0
                    eosr=filter(vreal,eosr)
                    #print("EOS Debug 1 %s" % eosr)
                    eosr=sorted(eosr)
                    result=float(eosr[-1])
                    #!The result is marked in m3/mol
                    
                    result=1000*result
                    #numpy的数据类型问题
                
                except Exception,error:
                    print ("KeyWord:%s + %s\nMistake:%s\n"%("RK",category,error))
                    result=None

            elif tag=="P":

                result=8.3145*temp/(volume-eosb)-eosa/(math.sqrt(temp)*volume*(volume-eosb))

            elif tag=="T":

                eospara=[8.314/(volume-eosb),0,-pres,eosa/(volume+b)/volume]
                tstandard=pres*volume/8.3145
                try:
                    #RK Equation
                    eost=numpy.poly1d(eospara)
                    eosr=eosv.r
                    positvefilter=lambda x:(x-tstandard)>0
                    eosr=filter(positivefilter,eosr)
                    result1=sorted(eosr)[0]

                    negativefilter=lambda x:(x-tstandard)<0
                    eosr=filter(negativefilter,eosr)
                    result2=sorted(eosr)[-1]

                    if (result1+result2)/2>tstandard:
                        result=result2
                    else:
                        result=result1

                except Exception,error:
                    print ("KeyWord:%s + %s\nMistake:%s\n"%("RK",category,error))
                    result=None
            
            elif tag=="PHIV":
                
                intev=self.RK(para,temp,pres,volume,"V")/1000
                #m3/kmol!
                #print intev
                eosZ=pres*intev/8.3145/temp
                
                #print("A: %s;B: %s,Z: %s" %(eosa,eosb,eosZ))
                lnphi=eosZ-1-math.log(eosZ-eosb*pres/8.3145/temp)-eosa/eosb/8.3145/pow(temp,1.5)*math.log(1+eosb/intev)
                result=lnphi
            
            elif tag=="DHV":
                
                intev=self.RK(para,temp,pres,volume,"V")/1000
                #print intev
                eosZ=pres*intev/8.3145/temp
                #m3/kmol!
                #print("V: %s;Z: %s" %(intev,eosZ))
                dhvrt=eosZ-1-1.5*eosa/eosb/8.3145/pow(temp,1.5)*math.log(1+eosb/intev)
                dhv=dhvrt*8.3145*temp
                result=dhv*1000
                
            else:
                print ("KeyWord:%s + %s\nMistake:%s\n"%("RK-Input Mistake",category,error))
                result=None
            
            
            
            
            return result
            #RK Result


    def VSPOLY():
        pass

    def DNSDIP(self,para,temp,pres,p0=100000):
        if len(para)==8:
            result=self.Dippr(para,temp,pres,p0,"100")
        else:
            print("%s equation is ilegal" % para[0])
            result=None
        return result

    def VSPO():
        pass

    def DNSTMLPO():
        pass

     #"LIQUIDV":("RKTZRA","DNLDIP","DNLPDS","RACKET","VLPO","DNLTMLPO","DNLEXSAT","DNLRACK","DNLCOSTD"),
     # Liquid Volume Method

    def RKTZRA():
        pass

    def DNLDIP(self,para,temp,pres,p0=100000):
    #105&116 DIPPR are used to calculate density, water 116
        if len(para)==8:
            result=self.Dippr(para,temp,pres,p0,"105")
        else:
            print("%s equation is ilegal" % para[0])
            result=None
        #!!Water is Special
        return result

    def DNLPDS():
        pass

    def RACKET():
        pass

    def VLPO():
        pass

    def DNLTMLPO():
        pass

    def DNLEXSAT():
        pass

    def DNLRACK():
        pass

    def DNLCOSTD():
        pass


    #"POV":("PLXANT","CPLXP1", "CPLXP2", "CPIXP1","CPIXP2","CPIXP3","WAGNER","LNVPEQ","LNVP1", "LOGVP1", "LNPR1", "LOGPR1", "LNPR2", "LOGPR2","PLPO","PLTDEPOL","WAGNER25"),
    # POV ASPEN METHOD
    def PLXANT(self,para,temp,pres,p0=100000):
        if len(para)==10:
            equation=para[1]+para[2]/(temp+para[3])+para[4]*temp+para[5]*math.log(temp)+para[6]*pow(temp,para[7])
            result=math.exp(equation)
        else:
            print("%s equation is ilegal" % para[0])
            result=None

        return result

    def CPLXP1():
        pass

    def CPLXP2():
        pass

    def CPIXP1():
        pass

    def CPIXP2():
        pass

    def CPIXP3():
        pass

    def WAGNER():
        pass

    def WAGNER25():
        pass

    def LNVPEQ():
        pass

    def LOGVP1():
        pass

    def LNPR1():
        pass

    def LOGPR1():
        pass

    def LNPR2():
        pass

    def PLPL():
        pass

    def PLTDEPOL():
        pass

    #"HOV":("DHVLWT","DHVLDP","DHVLDS","DHVLPO","DHVLTDEW"),

    def DHVLWT():
        pass

    def DHVLDP(self,para,temp,pres,p0=100000):
        if len(para)==8:
            result=self.Dippr(para,temp,pres,p0,"106")
        else:
            print("%s equation is ilegal" % para[0])
            result=None

        return result

    def DHVLDS():
        pass

    def DHVLPO():
        pass

    def DHVLTDEW():
        pass


    #"SOLIDCP":("CPSPO1","CPSDIP","CPSXP1", "CPSXP2", "CPSXP7","CPSPO","CPSTMLPO"),
    # Solid CPSXP1-7

    def CPSPO1():
        pass

    def CPSDIP(self,para,temp,pres,p0=100000):
        if len(para)==8:
            result=self.Dippr(para,temp,pres,p0,"100")
        else:
            print("%s equation is ilegal" % para[0])
            result=None
        return result

    def CPSXP1():
        pass


    def CPSXP2():
        pass

    def CPSXP7():
        pass

    def CPSPO():
        pass

    def CPSTMLPO():
        pass

    #"LIQUIDCP":( "CPLDIP","CPLXP1, CPLXP2","CPLPDS","CPLPO","CPLIKC","CPLTMLPO","CPLTDECS"),

    def CPLDIP(self,para,temp,pres,p0=100000):
        if len(para)==8:
            result=self.Dippr(para,temp,pres,p0,"100")
        else:
            print("%s equation is ilegal" % para[0])
            result=None
        return result

    def CPLXP1():
        pass

    def CPLXP2():
        pass

    def CPLPDS():
        pass


    def CPLIKC():
        pass

    def CPLTMLPO():
        pass

    def CPLTDECS():
        pass


    #"GASCP":("CPIG","CPIGDP","CPIXP1","CPIXP2", "CPIXP3","CPIGDS","CPIAPI","CPIGPO","CPITMLPO","CPIALEE")

    def CPIG(self,para,temp,pres,p0=100000):

        if len(para)==12:
            if temp>=para[7]:
                result=para[1]+ para[2]*temp+para[3]*pow(temp,2)+para[4]*pow(temp,3)+para[5]*pow(temp,4)+para[6]*pow(temp,5)
            else:
                result=para[9]+para[10]*pow(temp,para[11])
        else:
            print("%s equation is ilegal" % para[0])
            result=None

        return result

    def CPIGDP(self,para,temp,pres,p0=100000):
        #Sometimes Dippr 124 is used!
        if len(para)==8:
            result=self.Dippr(para,temp,pres,p0,"107")
        else:
            print("%s equation is ilegal" % para[0])
            result=None
        return result

    def CPIXP1():
        pass

    def CPIXP2():
        pass

    def CPIXP3():
        pass

    def CPIGDS():
        pass

    def CPIAPI():
        pass

    def CPIGPO():
        pass

    def CPITMLPO():
        pass

    def CPIALEE():
        pass


    #"VIRIAL":(None,)}

    def VIRIAL():
        pass


    # All DIPPR

    def Dippr(self,para,temp,pres,p0=100000,tag="100"):
        #test阶段tc定义
        tc=673.15
        #Mistake
        tr=temp/tc
        tx=1-tr
        #As the t defination is ASPEN

        if tag=="100":
            dippr=para[1]+para[2]*temp+para[3]*pow(temp,2)+para[4]*pow(temp,3)+para[5]*pow(temp,4)

        elif tag=="101":
            dippr=math.exp(para[1]+para[2]/temp+para[3]*math.log(temp)+para[4]*pow(temp,para[5]))

        elif tag=="102":
            dippr=para[1]*pow(temp,para[2])/(1+para[3]/temp+para[4]/temp/temp)

        elif tag=="103":
            dippr=para[1]+para[2]*math.exp(-para[3]/pow(temp,para[4]))

        elif tag=="104":
            dippr=para[1]+para[2]/temp+para[3]/pow(temp,3)+para[4]/pow(temp,8)+para[5]/pow(temp,9)

        elif tag=="105":
            dippr=para[1]/pow(para[2],1+pow((1-temp/para[3]),para[4]))

        elif tag=="106":
            #Only for Dippr calc
            dippr=para[1]*pow(tx,para[2]+para[3]*tr+para[4]*pow(tr,2)+para[5]*pow(tr,3))

        elif tag=="107":
            dippr=para[1]+para[2]*pow(para[3]/temp/math.sinh(para[3]/temp),2)+para[4]*pow(para[5]/temp/math.cosh(para[5]/temp),2)

        elif tag=="114":
            dippr=para[1]*para[1]/tx+para[2]-2*para[1]*para[3]*tx-para[1]*para[4]*tx*tx-para[3]*para[3]*pow(tx,3)/3-para[3]*para[4]/2*pow(tx,4)-para[4]*para[4]*pow(tx,5)/5

        elif tag=="115":
            dippr=math.exp(para[1]+para[2]/temp+para[3]*math.log(temp)+para[4]*temp*temp+para[5]/temp/temp)

        elif tag=="116":
            dippr=para[1]+para[2]*pow(tx,0.35)+para[3]*pow(tx,2/3)+para[4]*tx+para[5]*pow(tx,4/3)

        elif tag=="127":
            dippr=para[1]+para[2]*pow(para[3]/temp,2)*math.exp(para[3]/temp)/pow(math.exp(para[3]/temp)-1,2)+\
            para[4]*pow(para[5]/temp,2)*math.exp(para[5]/temp)/pow(math.exp(para[5]/temp)-1,2)+para[6]*pow(para[7]/temp,2)*math.exp(para[7]/temp)/pow(math.exp(para[7]/temp)-1,2)

        else:
            print "Costom DIPPR equation"
            pass

        return dippr

    def Dipprdiff(self,material,temp,para,tag="100"):#finish 100,101,105
        if tag=="100":
        #Diff against temp
            dipprdiff=para[2]+para[3]*temp*2+para[4]*pow(temp,2)*3+para[5]*pow(temp,3)*4

        elif tag=="101":
        #Diff against temp
            dipprdiff=math.exp(para[1]+para[2]/temp+para[3]*math.log(temp)+para[4]*pow(temp,para[5]))*(-para[2]/pow(temp,2)+para[3]/temp+para[4]*pow(temp,para[5]-1)*para[5])

        elif tag=="102":
        #a*b*x**b/(x*(c/x + d/x**2 + 1)) + a*x**b*(c/x**2 + 2*d/x**3)/(c/x + d/x**2 + 1)**2
        #dippr=para[1]*pow(temp,para[2])/(1+para[3]/temp+para[4]/temp/temp）
            pass

        elif tag=="103":
            dippr=para[1]+para[2]*math.exp(-para[3]/pow(temp,para[4]))

        elif tag=="104":
            dippr=para[1]+para[2]/temp+para[3]/pow(temp,3)+para[4]/pow(temp,8)+para[5]/pow(temp,9)

        elif tag=="105":
        #ASPEN Default Liquid Volume!
        #dippr=para[1]/pow(para[2],1+pow((1-temp/para[3]),para[4]),dippr
        #a*b**(-(1 - x/c)**d - 1)*d*(1 - x/c)**d*log(b)/(c*(1 - x/c))先后顺序较为混乱
        #Dippr系数2必须为正数
            dipprdiff=self.dippr(material,temp,para,"105")*math.log(para[2])*(para[4]/para[3])\
            *(1-temp/para[3])**(para[4]-1)

        elif tag=="106":
            #Only for Dippr calc
            dippr=para[1]*pow(tx,para[2]+para[3]*tr+para[4]*pow(tr,2)+para[5]*pow(tr,3))

        elif tag=="107":
            dippr=para[1]+para[2]*pow(para[3]/temp/math.sinh(para[3]/temp),2)+para[4]*pow(para[5]/temp/math.cosh(para[5]/temp),2)

        elif tag=="114":
            dippr=para[1]*para[1]/tx+para[2]-2*para[1]*para[3]*tx-para[1]*para[4]*tx*tx-para[3]*para[3]*pow(tx,3)/3-para[3]*para[4]/2*pow(tx,4)-para[4]*para[4]*pow(tx,5)/5

        elif tag=="115":
            dippr=math.exp(para[1]+para[2]/temp+para[3]*math.log(temp)+para[4]*temp*temp+para[5]/temp/temp)

        elif tag=="116":
            dippr=para[1]+para[2]*pow(tx,0.35)+para[3]*pow(tx,2/3)+para[4]*tx+para[5]*pow(tx,4/3)

        elif tag=="127":
            dippr=para[1]+para[2]*pow(para[3]/temp,2)*math.exp(para[3]/temp)/pow(math.exp(para[3]/temp)-1,2)+\
            para[4]*pow(para[5]/temp,2)*math.exp(para[5]/temp)/pow(math.exp(para[5]/temp)-1,2)+para[6]*pow(para[7]/temp,2)*math.exp(para[7]/temp)/pow(math.exp(para[7]/temp)-1,2)

        else:
            print "Costom DIPPR equation"
            pass

        return dipprdiff

   
    





