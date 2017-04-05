# -*- coding: utf-8 -*-
version="0.1"
import numpy
import sympy
import math

import scipy.integrate as integrate
import scipy.misc as diff

import zDatabase
import __future__   #the division calculation prolbem!

import logging  

from zEquation import zEquation

class zProperty():
#author=Zheng YX, version v1.0

    def __init__(self,name="H2O",temp=298.15,pres=100000,p0=100000,logname="logger",database="zPro.db"):
          
        self.name=name
        self.temp=temp
        self.pres=pres
        self.p0=p0
        self.logger=logging.getLogger(logname)
        self.database=database        

        #Basic Info, where name is specific

        self._eosr=8.3145

        self._bpset=[
        "API","BWRGMA","CHARGE","CLSK","DCPLS","DGFORM","DGSFRM",
        "DHAQFM","DHFORM","DHSFRM","DHVLB","DLWC","DVBLNC","FREEZEPT",
        "GMUQQ","GMUQQ1","GMUQR","HCOM","HCTYPE","HFUS","MUP","MW","OMEGA","OMGCLS","OMGPR","OMGRAP",
        "PC","PCPR","PCTRAP","PRZRA","RHOM","RKTZRA","S025E","SG","TB","TC","TCBWR","TCCLS","TCPR","TCTRAP","TPT",
        "TREFHL","TREFHS","VB","VC","VCBWR","VCCLS","VCRKT","VCTRAP","VLSTD","ZC","ZCTRAP","ZWITTER"]
        #Basic Property

        self._tpset=["SOLIDV","LIQUIDV","POV","HOV","SOLIDCP","LIQUIDCP","GASCP","VIRIAL"]
        #Temperature Dependent Property Set
        
        self._tplib={
        "SOLIDV":("VSPOLY","DNSDIP","VSPO","DNSTMLPO"),
        "LIQUIDV":("RKTZRA","DNLDIP","DNLPDS","RACKET","VLPO","DNLTMLPO","DNLEXSAT","DNLRACK","DNLCOSTD"),
        "POV":("PLXANT","CPLXP1", "CPLXP2", "CPIXP1","CPIXP2","CPIXP3","WAGNER","LNVPEQ","LNVP1", "LOGVP1", "LNPR1", "LOGPR1", "LNPR2", "LOGPR2","PLPO","PLTDEPOL","WAGNER25"),
        "HOV":("DHVLWT","DHVLDP","DHVLDS","DHVLPO","DHVLTDEW"),
        "SOLIDCP":("CPSPO1","CPSDIP","CPSXP1", "CPSXP2", "CPSXP7","CPSPO","CPSTMLPO"),
        "LIQUIDCP":( "CPLDIP","CPLXP1, CPLXP2","CPLPDS","CPLPO","CPLIKC","CPLTMLPO","CPLTDECS"),
        "GASCP":("CPIG","CPIGDP","CPIXP1","CPIXP2", "CPIXP3","CPIGDS","CPIAPI","CPIGPO","CPITMLPO","CPIALEE"),
        "VIRIAL":(None,)}
        #Temperature Dependent Property Detail Method        
        #Solid Cp is not intact, Virial is not incorporated
        
        self._eoslist=["IDEAL","RK","RKS","PR"]
        #EOS, acutally a temperature dependent property

        self._thermoset=['PHIV','PHIL','HV','HL','GV','GL','SV','SL','VV','VL','PHIS','HS','GS','SS','VS','WSL','HCSL']
        self._thermosubset=['PHILPC','DHV','DHL','DGV','DGL','DSV','DSL','PHISOC']
        
        #self._biset=[]
        #Activity did not belong to a Chemical's property


    def Basic_property_database(self,database="zPro.db",table="Basic"):
        self.bp={}
        #Use _bpset to load bp lib
        
        db=zDatabase.zDatabase()
        for att in self._bpset:
            try:
                self.bp[att]=db.Locate(database,table,self.name,att)[0]

            except Exception, error:
                self.logger.info("Function: %s; Name:%s/nError:%s" % ("Basic_property_database",att,error))
                self.bp[att]=None
                    
            setattr(self,att.lower(),self.bp[att])
        #print self.bp[att]
        #Basic Property
        return self.bp

    def Tdep_property_database(self,database="zPro.db",table="siGENERAL"):
        self.tp={}
        #T-dep property lib
        db=zDatabase.zDatabase()
        for att in self._tpset:
            for member in self._tplib[att]:
                try:
                    #print("Debug tdep member %s %s" % (att,member))
                    result1=db.Locate(database,table,self.name,member)
                    if result1[0]=="X":
                        self.tp[att]=member
                        break
                    elif result1=="D":
                        self.tp[att]=member
                        break
                    else:
                        self.tp[att]=None
                except Exception, error:
                    self.logger.info("Function: %s; Name:%s/nError:%s" % ("Tdep_property_database",att,error))
                    #print("KeyWord:%s;\nTdep_property_database error: %s\n" % (att,error))
                    self.tp[att]=None                    

        #Fix ATT list
        return self.tp

    def Tdep_property_set(self,database="zPro.db"):
        self.tpdata=self.tp
        db=zDatabase.zDatabase()
        #T-dep Property Element
       
        calcfilter=lambda x: isinstance(x,float)
        for btt in self.tp:
            try:
                print self.tp[btt]
                location="si"+self.tp[btt]
                
                result2=db.Locate(database,location,self.name,"*","Field1")
                #!!All the prime key change to "Field1"!!!
                #print("Debug tdep property load member %s %s" % (btt,result2))

                result2=filter(calcfilter,result2)
                result2=list(result2)
                result2.insert(0,self.tp[btt])
                #result2重整为适合计算格式

                self.tpdata[btt]=tuple(result2)
            except Exception,error:
                print("KeyWord:%s;\nTdep_property_load error: %s\n" % (btt,error))
                self.tpdata[btt]=tuple(result2)
                #此处是否恰当？'''

        return self.tpdata


    def Eos_set(self,eos="RK"):
        if eos in self._eoslist:
            self.eos=eos
            #!Database Problem
            self.eosset=(eos,self.tc,self.pc,self.vc,self.omega)
            #Is this enough for EOS tuple?
        else:
            self.eos="RK"
            self.eosset=(eos,self.tc,self.pc,self.vc,self.omega)
            #Is this enough for EOS tuple?
            print "Default Equation is RK"

        return self.eos


    def Method_set(self,database,table="Routes",method='WIL-RK'):

        self.routes={}

        for route in self._thermoset:
            self.routes[route]=db.Locate(database,table,method,route)[0]

        for route in self._thermosubset:
            self.routes[route]=db.Locate(database,table,method,route)[0]

        return self.routes
    

#Detail Calculation
#T-dep Property

    #self._tpset=["SOLIDV","LIQUIDV","POV","HOV","SOLIDCP","LIQUIDCP","GASCP","VIRIAL"]

    def Solid_volume(self,temp,pres,p0=100000):
        equation=zEquation()
        try:
            result=getattr(equation,self.tpdata["SOLIDV"][0])(self.tpdata["SOLIDV"],temp,pres,p0)
            result=1/result
            #DIPPR Returns Density
        except Exception,error:
            print ("KeyWord:%s + %s\nMistake:%s\n"%("Solid_volume",self.tpdata["SOLIDV"][0],error))
            result=None
        return result

    def Liquid_volume(self,temp,pres,p0=100000):

        equation=zEquation()
        try:
            result=getattr(equation,self.tpdata["LIQUIDV"][0])(self.tpdata["LIQUIDV"],temp,pres,p0)
            result=1/result
            #DIPPR Returns Density
        except Exception,error:
            print ("KeyWord:%s + %s\nMistake:%s\n"%("Liquid_Volume",self.tpdata["LIQUIDV"][0],error))
            result=None
        return result


    def Pressure_of_saturation(self,temp,pres,p0=100000):
    #As a demo
        equation=zEquation()
        try:
           
            result=getattr(equation,self.tpdata["POV"][0])(self.tpdata["POV"],temp,pres,p0)
            #! result=100000*result use Pa,not bar now
        except Exception,error:
            print ("KeyWord:%s + %s\nMistake:%s\n"%("Antoine Like",self.tpdata["POV"][0],error))
            result=None

        return result

    def Heat_of_vaporization(self,temp,pres,p0=100000):

        equation=zEquation()
        try:
            result=getattr(equation,self.tpdata["HOV"][0])(self.tpdata["HOV"],temp,pres,p0)
        except Exception,error:
            print ("KeyWord:%s + %s\nMistake:%s\n"%("Vaporization Heat",self.tpdata["HOV"][0],error))
            result=None
        return result


    def Solid_cp(self,temp,pres,p0=100000):
        equation=zEquation()
        try:
            result=getattr(equation,self.tpdata["SOLIDCP"][0])(self.tpdata["SOLIDCP"],temp,pres,p0)
        except Exception,error:
            print ("KeyWord:%s + %s\nMistake:%s\n"%("Solid_cp",self.tpdata["SOLIDCP"][0],error))
            result=None
        return result

    def Liquid_cp(self,temp,pres,p0=100000):
        equation=zEquation()
        try:
            result=getattr(equation,self.tpdata["LIQUIDCP"][0])(self.tpdata["LIQUIDCP"],temp,pres,p0)
        except Exception,error:
            print ("KeyWord:%s + %s\nMistake:%s\n"%("Liquid_cp",self.tpdata["LIQUIDCP"][0],error))
            result=None
        return result


    def Gas_cp(self,temp,pres,p0=100000):
        equation=zEquation()
        try:
            result=getattr(equation,self.tpdata["GASCP"][0])(self.tpdata["GASCP"],temp,pres,p0)
        except Exception,error:
            print ("KeyWord:%s + %s\nMistake:%s\n"%("Gas_cp",self.tpdata["GASCP"][0],error))
            result=None

        return result

    def Virial(self):
       pass

#Detail Calculation
#T-dep Property
#EOS calculation, thermo property

    def Eos_temp(self,pres,volume,p0):
        pass

    def Eos_pres(self,temp,volume,p0):
        pass

    def Phiv(self,temp,pres,p0=100000,route="1"):
    #Pure Thermo has a lot of method
    #This is not similar as T-dep property
    #Phiv has no route definition
        equation=zEquation()
        if route=="1":
            try:
                #function Problem
                eosphivfunction=lambda x:(1/8.3145/temp)*(self.Vv(temp,x,p0)/1000-8.3145*temp/x)
                #Very Important Lambda Function for Fugacity Calc
    
                lnphico=integrate.romberg(eosphivfunction,p0,pres);
                #print("Phiv",lnphico)
                result=math.exp(lnphico)
    
            except Exception,error:
                print ("KeyWord:%s + %s\nMistake:%s\n"%("EOS Phiv",self.eosset[0],error))
                result=1
        
        elif route=="RK":
            lnphico=equation.RK(self.eosset,temp,pres,0,"PHIV")
            print lnphico
            result=math.exp(lnphico)

            #phiv default is 1
        else:
            print("Phiv No proper method")
            result=1
        return result

    def Phil(self,temp,pres,p0=100000,route="2"):
        #4 routes defined in ASPEN

        psat=self.Pressure_of_saturation(temp,pres,p0=100000)
        eosphiv=self.Phiv(temp,psat,p0)

        try:
            if route=="1":
                #Custom defined Phil Method
                pass

            elif route=="2":
                poynting=self.Sub_philpc(temp,psat,pres)

            elif route=="3":
                poynting=1

            elif route=="4":
                #!For water
                pass

            else:
                print("Default Poynting!")
                poynting=1

        except Exception,error:
            print ("KeyWord:%s + %s\nMistake:%s\n"%("EOS Phil",self.eosset[0],error))
            poynting=1

        #print("Phil Test %s %s %s" % (poynting,eosphiv,psat))
        result=poynting*eosphiv*psat/pres


        return result


    def Hv(self,temp,pres,t0=298.15,p0=100000,route="2"):

        hbase=self.dhform
        eoshfunction=lambda x: self.Gas_cp(x,pres,p0=100000)
        htemp=integrate.romberg(eoshfunction,t0,temp)

        try:
            if route=="1":
                pass

            elif route=="2":
                hdeparture=self.Sub_dhv(temp,pres,t0,p0,"2")

            else:
                hdeparture=0
                print("Default Hdeparture!")

        except Exception,error:
            print ("KeyWord:%s + %s\nMistake:%s\n"%("EOS HV",route,error))
            hdeparture=0

        result=hbase+htemp+hdeparture
        print(hbase,htemp,hdeparture)

        return result


    def Hl(self,temp,pres,t0=298.15,p0=100000,route="2",subroute="1"):

        hbase=self.dhform
        eoshfunction=lambda x: self.Gas_cp(x,pres,p0=100000)
        htemp=integrate.romberg(eoshfunction,t0,temp)

        try:

            if route=="1":
                pass

            elif route=="2":
               hdeparture=self.Sub_dhl(temp,pres,t0,p0,subroute)

            else:
               hdeparture=0

        except Exception,error:
            print ("KeyWord:%s + %s\nMistake:%s\n"%("EOS HL",self.eosset[0],error))
            hdeparture=0

        result=hbase+htemp+hdeparture

        return result


    def Gv(self,temp,pres,t0=298.15,p0=100000,route="2",subroute="2"):
        if route=="1":
            pass

        elif route=="2":
            #ASPEN's Gibbs Free Energy Handling Method has severe problem on its definition
            #Just a copy of it is own method
            sbase=self.dgform-self.dhform
            cp=lambda x:self.Gas_cp(x,p0,p0)
            cpt=lambda y:self.Gas_cp(y,p0,p0)/y
            deltaH1=integrate.romberg(cp,t0,temp)
            deltaS1=integrate.romberg(cpt,t0,temp)
            gideal=gbase+deltaH1+temp*(deltaS1+sbase)-sbase*t0
            gdeparture=self.Sub_dgv(temp,pres,t0,p0,subroute)

        result=gideal+gdeparture

        return result

    def Gl(self,temp,pres,t0=298.15,p0=100000,route="2",subroute="2"):
        if route=="1":
                pass

        elif route=="2":

            gbase=self.dgform
            sbase=self.dsform
            cp=lambda x:self.Gas_cp(x,p0,p0)
            cpt=lambda y:self.Gas_cp(x,p0,p0)/x
            deltaH1=integrate.romberg(cp,t0,temp)
            deltaS1=integrate.romberg(cpt,t0,temp)
            gideal=gbase+deltaH1+temp*(deltaS1+sbase)-t0*sbase

            gdeparture=self.Sub_dgl(temp,pres,t0,p0,subroute)

        result=gideal+gdeparture

        return result


    def Sv(self,temp,pres,t0=298.15,p0=100000,route="2"):

        if route=="1":
            pass

        elif route=="2":
            sbase=self.dgform-self.dhform
            sfunction=lambda x: Gas_cp(self,x,pres,p0=100000)/x
            stemp=integrate.romberg(sfunction,t0,temp)
            #spres=8.3145*temp*math.log(pres/p0) this belong to ideal part
            
            sdeparture=self.Sub_dsv(temp,pres,t0=298.15,p0=100000,route="2")

            sv=sbase+stemp+sdeparture
            return sv

    def Sl(self,temp,pres,t0=298.15,p0=100000,route="2"):
        try:
            Sbase=self.dhform
            eossfunction=lambda x: self.Gas_cp(x,pres,p0=100000)/x
            stemp=integrate.romberg(eossfunction,t0,temp)
            spres=8.3145*temp*math.log(pres/p0)
            sdeparture=self.Sub_dsv(temp,pres,t0=298.15,p0=100000,route="2")
        #No Pressure Effect,p0 left
            result=sbase+stemp+spres+sdeparture

        except Exception,error:
            print ("KeyWord:%s + %s\nMistake:%s\n"%("SL",self.eosset[0],error))
            result= None

        return result


    def Vv(self,temp,pres,t0=298.15,p0=100000):
        #No route definition for Vv
        equation=zEquation()
        try:
            
            result=getattr(equation,self.eosset[0])(self.eosset,temp,pres,0,tag="V")
            #print("Vv Debug %s %s %s" %(self.eosset,result,8.3145*temp/pres))
        except Exception, error:
            print ("KeyWord:%s + %s\nMistake:%s\n"%("Vv",self.eosset[0],error))
            result= 0

        return result



    def Vl(self,temp,pres,p0=100000):
        #No rout definition for Vl
        result=self.Liquid_volume(temp,pres,p0=100000)

        return result


    #Solid is not included yet
    def Phis(self):
        pass

    def Hs(self):
        pass

    def Gs(self):
        pass

    def Ss(self):
        pass

    def Vs(self):
        pass


# 计算中间属性
    def Sub_philpc(self,temp,p1,p2):
        try:
            eosphilfunction=lambda x: self.Liquid_volume(temp,x,p0=100000)
            eosintegration=integrate.romberg(eosphilfunction,p1,p2);

            #print ("Pressure Integeration:",1/8.3145/temp*eosintegration/p2)
            #!Poynting Definition
            result=math.exp(1/8.3145/temp*eosintegration/p2)

        except Exception,error:
            print ("KeyWord:%s + %s\nMistake:%s\n"%("Poynting",self.eosset[0],error))
            result=1

        return result


    def Sub_dhv(self,temp,pres,t0=298.15,p0=100000,route="2",step=100):
        #3 routes, 2 are same as ASPEN, 3 is programmed as Textbook

        equation=zEquation()

        if route=="1":

            if self.eosset[0]=="PR":
                pass

            elif self.eosset[0]=="SRK":
                pass


        elif route=="2":
            eosphiv=lambda y:math.log(self.Phiv(y,pres,p0))
            eosdiff=diff.derivative(eosphiv,temp)#,abs(temp-t0)/step)
            #print(eosdiff,"DHV Test")
            dhv=-8.3145*temp*temp*eosdiff
            dhv=dhv*1000
            
        elif route=="3":
            #!Problem,partial pressure
            dhvint=0
            plength=(pres-p0)/100
            pcomb=range(p0,pres,plength)
            
            for pint in pcomb:
                eosv=self.Vv(temp,pint,p0)/1000
                eosdt=lambda x:self.Vv(x,pint,p0)/1000
                eosdiff=eosv-temp*diff.derivative(eosdt,temp,abs(temp-t0)/step)
                dhvstep=eosdiff*plength
                dhvint=dhvint+dhvstep

            dhv=dhvint*1000
            
        elif route=="RK":
            
            dhv=equation.RK(self.eosset,temp,pres,0,"DHV")
      
        else:
            dhv=0
            print("DHV Default")

        result=dhv

        return result




    def Sub_dhl(self,temp,pres,t0=298.15,p0=100000,route="1",step=1000):
        #No default p0 now! For integration
        #Departure Enthalpy,extra parameter p0
        #！Turns out to be a must p0
        #Route change to int?

        equation=zEquation()
        if route=="1":
            try:
                #Use CP and vaporization enthalpy to calculate
                hvap=self.Heat_of_vaporization(temp,pres,p0)
                hlfunction=lambda x:self.Liquid_cp(x,pres,p0)
                hlcp1=integrate.romberg(hlfunction,psat,pres);
                #Liquid Volume Rectification,follow ASPEN use a 0 here
                hlcp2=0
                result=hvap+hlcp1+hlcp2

            except Exception,error:
                print ("KeyWord:%s + %s\nMistake:%s\n"%("DHL","Cp-L method",error))

                result=0

        elif route=="2":
            try:
                #partial ln(phi)/ partial T
                eosphil=lambda x:self.Phil(x,pres,p0=100000,route="1")
                eosdiff=diff.derivative(eosv,temp,abs(temp-t0)/step)

                #数值微分方法,目前只设置了微分步长
                eosresult=8.3145*temp*temp*eosdiff
                #微分后积分
            except Exception,error:
                print ("KeyWord:%s + %s\nMistake:%s\n"%("DHL","Phil Mehtod",error))

                result=0

        elif route=="3":
            #ASPEN has 3-5 method to handle the situation
            #事实上1与3目前思路相同
            pass
        elif route=="4":
            pass

        elif route=="5":
            pass

        elif route=="6":
            #!自定义方法解决液相压力问题
            #Pressure Rectification in Liuqid Phase
            try:
                #Use CP and vaporization enthalpy to calculate
                hvap=self.Heat_of_vaporization(temp,pres,p0)
                hlfunction=lambda x:self.Liquid_cp(x,pres,p0)
                hlcp1=integrate.romberg(hlfunction,psat,pres);
                #Liquid Volume Rectification,follow ASPEN use a 0 here
                eosvi=lambda y:self.Vl(temp,y,p0)
                hlcp2=integrate.romberg(eosvi,psat,pres)
                result=hvap+hlcp1+hlcp2

            except Exception,error:
                print ("KeyWord:%s + %s\nMistake:%s\n"%("DHL","Liquid Pressure Rectification",error))

                result=0

        else:
            result=0
            print("%s has dhl problem" % self.name)

        return result


    def Sub_dsv(self,temp,pres,t0=298.15,p0=100000,route="3"):#!NOW EDITING!!!
        equation=zEquation()

        if route=="1":
            pass

        elif route=="2":
            try:
                gdiff=lambda x:self.Sub_dgv(x,pres,t0,p0,"2")
                eosdiff=lambda y:diff.derivative(eosv,y,abs(pres-p0)/step)-8.314/y
                #数值微分方法,目前只设置了微分步长
                eosintegrate=integrate.romberg(eosdiff,p0,pres);
                #微分后积分
            except Exception,error:
                print ("KeyWord:%s + %s\nMistake:%s\n"%("DSV",self.eosset[0],error))

                eosintegrate=0

        elif route=="3":
            try:
                eosv=lambda x:getattr(equation,self.eosset[0])(self.eosset,temp,x,volume=0,tag="V")
                eosdiff=lambda y:diff.derivative(eosv,y,abs(pres-p0)/step)-8.314/y
                #数值微分方法,目前只设置了微分步长
                eosintegrate=integrate.romberg(eosdiff,p0,pres);
                #微分后积分
            except Exception,error:
                print ("KeyWord:%s + %s\nMistake:%s\n"%("DSV",self.eosset[0],error))

                eosintegrate=0

            #错误时反馈eosintegrate=0!

        #A Specific method for RK
        '''eosa=0.42748*8.3145*8.3145*pow(material.tc,2.5)/material.pc
        eosb=0.08664*8.3145*material.tc/material.pc
        eosv=material.Vvolume(temp,pres,eos)
        eosZ=pres*eosv/8.3145/temp
        eosB=eosb*eosZ/pres/eosv
        eosA=math.sqrt(eosa/eosb/8.3145/pow(temp,1.5)*eosB)
        dsvfactor=0.5*eosA*eosA*math.log(1+eosB*pres/eosZ)-math.log(eosZ-eosB*pres)
        dsv=dsvfactor*8.3145
        return dsv'''

        return eosintegrate

    def Sub_dsl(temp,pres,t0=298.15,p0=100000,route="2"):
        equation=zEquation()
        psat=self.Pressure_of_saturation(temp,pres,p0=100000)
        try:
            eosv=lambda x:getattr(equation,self.eosset[0])(self.eosset,temp,x,volume=0,tag="V")
            eosdiff=lambda y:diff.derivative(eosv,y,abs(pres-p0)/step)-8.314/y
            #数值微分方法,目前只设置了微分步长
            eosintegrate=integrate.romberg(eosdiff,p0,pres);
            #微分后积分
        except Exception,error:
            print ("KeyWord:%s + %s\nMistake:%s\n"%("DSV",self.eosset[0],error))

            eosintegrate=0

            #错误时反馈eosintegrate=0!

        #A Specific method for RK
        '''eosa=0.42748*8.3145*8.3145*pow(material.tc,2.5)/material.pc
        eosb=0.08664*8.3145*material.tc/material.pc
        eosv=material.Vvolume(temp,pres,eos)
        eosZ=pres*eosv/8.3145/temp
        eosB=eosb*eosZ/pres/eosv
        eosA=math.sqrt(eosa/eosb/8.3145/pow(temp,1.5)*eosB)
        dsvfactor=0.5*eosA*eosA*math.log(1+eosB*pres/eosZ)-math.log(eosZ-eosB*pres)
        dsv=dsvfactor*8.3145
        return dsv'''



        psat=self.Pressure_of_saturation(temp,pres,p0=100000)
        #print psat
        #计算气体饱和蒸汽压

        fugsat=self.Phiv(temp,psat,p0,eos,"1")[1]
        #计算气体逸度的route 如何动态化

        #逸度系数龙贝格积分
        try:
            eosphilfunction=lambda x: self.Liquid_volume(temp,pres,p0=100000)
            eosintegration=integrate.romberg(eosphilfunction,psat,pres);
            #print ("Pressure Integeration:",eosintegration)
            poynting=math.exp(1/8.3145/temp*eosintegration)
            #Poynting is in separate Sub_philpc
            phil=poynting*fugsat/pres
            fugacity=phil*pres
            result=(phil,fugacity,pres,poynting)

        except Exception,error:
            print ("KeyWord:%s + %s\nMistake:%s\n"%("EOS Phil",self.eosset[0],error))
            result=(None,None,None)

        return result

        return eosintegrate



    def Sub_dgv(temp,pres,t0=298.15,p0=100000,route="2"):
        #Not yet
        if route=="1":
           pass

        elif route=="2":
           eosphiv=self.Phiv(temp,pres,p0)
           result=8.3145*temp*math.log(eosphiv)+8.3145*temp*math.log(pres/p0)


        return result


    def Sub_dgl(temp,pres,t0=298.15,p0=100000,route="2"):
        #!Use phil not 2,not imbeded
        if route=="1":
           pass

        elif route=="2":
           eosphiv=self.Phil(temp,pres,p0,"2")

           result=8.3145*temp*math.log(eosphiv)+8.3145*temp*math.log(pres/p0)

        elif route=="3":
            pass
        return result








if __name__=="__main__":
    a=zProperty("H2O")
    a.Basic_property_database()
    print("Basic property test OK: %s.api is %s\n" %(a.name,a.api))
    a.Tdep_property_database()
    print("Temp-dep property test OK: %s.LIQUIDCP is %s\n" %(a.name,a.tp["LIQUIDCP"]))
    a.Tdep_property_set()
    print("Temp-dep property load OK: %s.LIQUIDCP is %s\n" %(a.name,a.tpdata["LIQUIDCP"]))
    #Database模块
    b=zDatabase.zDatabase()
    abc=b.Locate("zPro.db","siGENERAL",a.name,"CPIG")
    print("Database test OK\n")
    
    #Property Calc
    '''print a.tpdata
    text=a.Solid_cp(263.15,100000)
    print("Solid CP",text,a.tpdata)
    print a.Liquid_cp(373.15,200000)
    print a.Solid_volume(263.15,100000)
    print a.Liquid_volume(373.15,200000)
    print a.Gas_cp(473.15,200000)
    print a.Heat_of_vaporization(373.15,200000)
    print a.Pressure_of_saturation(373.15,200000)'''
    
    #Pure T-dep Property Test
    #Passed
    '''print a.tpdata
    print ("HOV")
    for f in range(0,201,10):
        print(f,a.Heat_of_vaporization(f+273.15,200000))
    
    print("/n LCP")
    for f in range(0,201,10):
        print(f,a.Liquid_cp(f+273.15,200000))
        
    print("/n GCP")
    for f in range(0,201,10):
        print(f,a.Gas_cp(f+273.15,200000))
    
    print("/n LvO")
    for f in range(0,201,10):
        print(f,a.Liquid_volume(f+273.15,200000))
    
    print("/n pov")
    for f in range(0,201,10):
        print(f,a.Pressure_of_saturation(f+273.15,200000))
        '''
    a.Eos_set(eos="RK")   
    
    '''print("\n Vv")
    for f in range(0,201,10):
        print(f,a.Vv(f+273.15,200000))'''
    
    
    '''print("\n Phiv")
    for f in range(0,201,10):
        #print(f,a.Phiv(f+273.15,200000,100000,"RK"))
        print(f,a.Phiv(f+273.15,200000,100000,"1"))'''
    
    
    '''print("\n Phil")
    for f in range(0,201,10):
        print(f,a.Phil(f+273.15,200000))'''

    print("\n HV")
    for f in range(0,201,10):
        a.Hv(f+273.15,200000,p0=1,route="2")
    
    '''print("\n DHV")
    print(a.Sub_dhv(473.15,200000,route="3"))'''