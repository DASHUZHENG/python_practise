# -*- coding: utf-8 -*-
version="0.1"
import numpy
import sympy
import math

import scipy.integrate as integrate
import scipy.misc as diff

import zDatabase
import __future__   #the division calculation prolbem!

class zProperty():
#author=Zheng YX, version v1.0
    def __init__(self,name="H2O",temp=298.15,pres=100000,p0=100000):
        self.name=name
        self.temp=temp
        self.pres=pres
        self.p0=p0
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
        self._tplib={
        "SOLIDV":("VSPOLY","DNSDIP","VSPO","DNSTMLPO"),
        "LIQUIDV":("RKTZRA","DNLDIP","DNLPDS","RACKET","VLPO","DNLTMLPO","DNLEXSAT","DNLRACK","DNLCOSTD"),
        "POV":("PLXANT","CPLXP1", "CPLXP2", "CPIXP1","CPIXP2","CPIXP3","WAGNER","LNVPEQ","LNVP1", "LOGVP1", "LNPR1", "LOGPR1", "LNPR2", "LOGPR2","PLPO","PLTDEPOL","WAGNER25"),
        "HOV":("DHVLWT","DHVLDP","DHVLDS","DHVLPO","DHVLTDEW"),
        "SOLIDCP":("CPSPO1","CPSDIP","CPSXP1", "CPSXP2", "CPSXP7","CPSPO","CPSTMLPO"),
        "LIQUIDCP":( "CPLDIP","CPLXP1, CPLXP2","CPLPDS","CPLPO","CPLIKC","CPLTMLPO","CPLTDECS"),
        "GASCP":("CPIG","CPIGDP","CPIXP1","CPIXP2", "CPIXP3","CPIGDS","CPIAPI","CPIGPO","CPITMLPO","CPIALEE"),
        "VIRIAL":(None,)}
        #Solid Cp is not intact, Virial is not incorporated
        self._eoslist=["IDEAL","RK","RKS","PR"]

        self._biset=[]

    def Basic_property_scala(self,prop):
        self.api=prop[0]
        self.bwrgma=prop[1]
        self.charge=prop[2]
        self.clsk=prop[3]
        self.dcpls=prop[4]
        self.dgform=prop[5]
        self.dgsfrm=prop[6]
        self.dhaqfm=prop[7]
        self.dhform=prop[8]
        self.dhsfrm=prop[9]
        self.dhvlb=prop[10]
        self.dlwc=prop[11]
        self.dvblnc=prop[12]
        self.freezept=prop[13]
        self.gmuqq=prop[14]
        self.gmuqq1=prop[15]
        self.gmuqr=prop[16]
        self.hcom=prop[17]
        self.hctype=prop[18]
        self.hfus=prop[19]
        self.mup=prop[20]
        self.mw=prop[21]
        self.omega=prop[22]
        self.omgcls=prop[23]
        self.omgpr=prop[24]
        self.omgrap=prop[25]
        self.pc=prop[26]
        self.pcpr=prop[27]
        self.pctrap=prop[28]
        self.przra=prop[29]
        self.rhom=prop[30]
        self.rktzra=prop[31]
        self.s025e=prop[32]
        self.sg=prop[33]
        self.tb=prop[34]
        self.tc=prop[35]
        self.tcbwr=prop[36]
        self.tccls=prop[37]
        self.tcpr=prop[38]
        self.tctrap=prop[39]
        self.tpt=prop[40]
        self.trefhl=prop[41]
        self.trefhs=prop[42]
        self.vb=prop[43]
        self.vc=prop[44]
        self.vcbwr=prop[45]
        self.vccls=prop[46]
        self.vcrkt=prop[47]
        self.vctrap=prop[48]
        self.vlstd=prop[49]
        self.zc=prop[50]
        self.zctrap=prop[51]
        self.zwitter=prop[52]

    def Basic_property_database(self,database="zPro.db"):
        self.bp={}
        db=zDatabase.zDatabase()
        for att in self._bpset:
            self.bp[att]=db.Locate(database,"Basic",self.name,att)[0]
            setattr(self,att.lower(),self.bp[att])
        #print self.bp[att]
        #Basic Property
        return self.bp

    def Tdep_property_database(self,database="zPro.db"):
        self.tp={}
        #T-dep property lib
        db=zDatabase.zDatabase()
        for att in self._tpset:
            for member in self._tplib[att]:
                try:
                    #print("Debug tdep member %s %s" % (att,member))
                    result1=db.Locate(database,"siGENERAL",self.name,member)
                    if result1[0]=="X":
                        self.tp[att]=member
                        break
                    elif result1=="D":
                        self.tp[att]=member
                        break
                    else:
                        self.tp[att]=None
                except Exception, error:
                    print("KeyWord:%s;\nTdep_property_database error: %s\n" % (att,error))
                    self.tp[att]=None
                    #此处是否恰当？
        #Fix ATT list
        return self.tp

    def Tdep_property_load(self,database="zPro.db"):
        self.tpdata=self.tp
        db=zDatabase.zDatabase()
        #T-dep Property Element
        calcfilter=lambda x: isinstance(x,float)
        for btt in self.tp:
            try:
                location="si"+self.tp[btt]
                result2=db.Locate(database,location,self.name,"*","Component")
                #print("Debug tdep property load member %s %s" % (btt,result2))

                result2=filter(calcfilter,result2)
                result2=list(result2)
                result2.insert(0,self.tp[btt])
                #result2重整为适合计算格式

                self.tpdata[btt]=tuple(result2)
            except Exception,error:
                print("KeyWord:%s;\nTdep_property_load error: %s\n" % (btt,error))
                self.tpdata[btt]=tuple(result2)
                #此处是否恰当？

        return self.tpdata

    #self._tpset=["SOLIDV","LIQUIDV","POV","HOV","SOLIDCP","LIQUIDCP","GASCP","VIRIAL"]

    def Solid_volume(self,temp,pres,p0=100000):
        equation=zEquation()
        try:
            result=getattr(equation,self.tpdata["SOLIDV"][0])(self.tpdata["SOLIDV"],temp,pres,p0)
        except Exception,error:
            print ("KeyWord:%s + %s\nMistake:%s\n"%("Solid_volume",self.tpdata["SOLIDV"][0],error))
            result=None
        return result

    def Liquid_volume(self,temp,pres,p0=100000):

        equation=zEquation()
        try:
            result=getattr(equation,self.tpdata["LIQUIDV"][0])(self.tpdata["LIQUIDV"],temp,pres,p0)

        except Exception,error:
            print ("KeyWord:%s + %s\nMistake:%s\n"%("Liquid_Volume",self.tpdata["LIQUIDV"][0],error))
            result=None
        return result


    def Pressure_of_saturation(self,temp,pres,p0=100000):
    #As a demo
        equation=zEquation()
        try:
            #! Now give a bar result!
            result=getattr(equation,self.tpdata["POV"][0])(self.tpdata["POV"],temp,pres,p0)
            result=100000*result
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


    def Eos_set(self,eos="RK"):
        if eos in self._eoslist:
            self.eos=eos
            #!Database Problem
            self.eosset=(eos,self.tc+273.15,self.pc*100000,self.vc,self.omega)
            #Is this enough for EOS tuple?
        else:
            self.eos="RK"
            self.eosset=(eos,self.tc,self.pc,self.vc,self.omega)
            #Is this enough for EOS tuple?
            print "Default Equation is RK"

        return self.eos


    def Eos_volume(self,temp,pres,p0):

        result=getattr(zEquation,self.eos)(temp,pres,p0,args=("V",self.pc,self.tc))

        return result

    def Eost(self,pres,volume,p0):
        pass

    def Eosp(self,temp,pres,p0):
        pass

#20170323 Pure Thermo integrated

    def Phiv(self,temp,pres,p0=100000):
    #Pure Thermo has a lot of method
    #This is not similar as T-dep property
    #Phiv has no route definition

        equation=zEquation()

        try:
            #function Problem
            eosphivfunction=lambda x:self.Vv(temp,pres,p0)
            #Very Important Lambda Function for Fugacity Calc

            eosintegration=integrate.romberg(eosphivfunction,p0,pres);
            lnphico=1/8.3145/temp*eosintegration-math.log(pres/p0)
            #print("Phiv",lnphico)
            result=math.exp(lnphico)

        except Exception,error:
            print ("KeyWord:%s + %s\nMistake:%s\n"%("EOS Phiv",self.eosset[0],error))
            result=1

            #phiv default is 1

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


    def Hv(self,temp,pres,t0=298.15,p0=100000,route="2",subroute="2"):

        hbase=self.dhform
        eoshfunction=lambda x: self.Gas_cp(x,pres,p0=100000)
        htemp=integrate.romberg(eoshfunction,t0,temp)

        try:
            if route=="1":
                pass

            elif route=="2":
                hdeparture=self.Sub_dhv(temp,pres,t0,p0,subroute)

            else:
                hdeparture=0
                print("Default Hdeparture!")

        except Exception,error:
            print ("KeyWord:%s + %s\nMistake:%s\n"%("EOS HV",route,error))
            hdeparture=0

        result=hbase+htemp+hdeparture

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

            gbase=self.dgform
            sbase=self.dsform
            cp=lambda x:self.Gas_cp(x,p0,p0)
            cpt=lambda y:self.Gas_cp(x,p0,p0)/x
            deltaH1=integrate.romberg(cp,t0,temp)
            deltaS1=integrate.romberg(cpt,t0,temp)
            gideal=gbase+deltaH1+temp*(deltaS1+sbase)-t0*sbase

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
        sbase=self.dsform
        sfunction=lambda x: Gas_cp(self,x,pres,p0=100000)/x
        stemp=integrate.romberg(sfunction,t0,temp)
        spres=8.3145*temp*math.log(pres/p0)
        sdeparture=self.Sub_dsv(temp,pres,t0=298.15,p0=100000,route="2")
        sv=sbase+stemp+spres+sdeparture
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
            #print ("KeyWord:%s + %s\nMistake:%s\n"%("Vv",self.eosset[0],error))
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


    def Sub_dhv(self,temp,pres,t0=298.15,p0=100000,route="2",step=10000):
        #3 routes, 2 are same as ASPEN, 3 is programmed as Textbook

        equation=zEquation()

        if route=="1":
            if self.eosset[0]=="RK":
                eosa=0.42748*8.3145*8.3145*pow(self.tc,2.5)/self.pc
                eosb=0.08664*8.3145*self.tc/self.pc
                eosv=self.Vv(temp,pres,p0)
                eosZ=pres*eosv/8.3145/temp
                eosB=eosb*eosZ/pres/eosv
                eosA=math.sqrt(eosa/eosb/8.3145/pow(temp,1.5)*eosB)
                dhvfactor=eosZ-1-1.5*eosA*eosA/eosB*math.log(1+eosB*pres/eosZ)
                dhv=8.3145*temp*dhvfactor

            elif self.eosset[0]=="PR":
                pass

            elif self.eosset[0]=="SRK":
                pass


        elif route=="2":
            eosphiv=lambda y:self.Phiv(y,pres,p0)
            print("EOS PHIV",eosphiv(200))
            eosdiff=diff.derivative(eosphiv,temp,abs(temp-t0)/step)
            print(eosdiff,"DHV Test")
            dhv=-8.3145*temp*temp*eosdiff

        elif route=="3":

            try:
                eosv=lambda x:self.Vv(temp,x,p0)
                eosdiff=lambda y:eosv(y)-temp*diff.derivative(eosv,y,abs(pres-p0)/step)
                dhv=integrate.romberg(eosdiff,psat,pres);

            except Exception,error:
                print ("KeyWord:%s + %s\nMistake:%s\n"%("DHV General Method",route,error))
                dhv=0
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


    def Sub_dsv(temp,pres,t0=298.15,p0=100000,route="2"):
        equation=zEquation()
        try:
            eosv=lambda x:getattr(equation,self.eosset[0])(self.eosset,temp,x,p0,volume=0,tag="V")
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
            eosv=lambda x:getattr(equation,self.eosset[0])(self.eosset,temp,x,p0,volume=0,tag="V")
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







class zEquation():

    def __init__(self):
        pass
    #"SOLIDV":("VSPOLY","DNSDIP","VSPO","DNSTMLPO"),
    # Solid Volume Method

    #Start with EOS
    def RK(self,para,temp,pres,volume,tag="V"):

            #RK para=["RK",tc,pc,omega] omega is not useful
            eosa=0.42748*8.3145*8.3145*pow(para[1],2.5)/para[2]
            eosb=0.08664*8.3145*para[1]/para[2]
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

    #Below are all EOSes





if __name__=="__main__":
    a=zProperty("H2O")
    a.Basic_property_database()
    print("Basic property test OK: %s.api is %s\n" %(a.name,a.api))
    a.Tdep_property_database()
    print("Temp-dep property test OK: %s.LIQUIDCP is %s\n" %(a.name,a.tp["LIQUIDCP"]))
    a.Tdep_property_load()
    print("Temp-dep property load OK: %s.LIQUIDCP is %s\n" %(a.name,a.tpdata["LIQUIDCP"]))
    #Database模块
    b=zDatabase.zDatabase()
    abc=b.Locate("zPro.db","siGENERAL",a.name,"CPIG")
    print("Database test OK\n")

    #Property Calc
    print a.Solid_cp(263.15,100000)
    print a.Liquid_cp(373.15,200000)
    print a.Solid_volume(263.15,100000)
    print a.Liquid_volume(373.15,300000)
    print a.Gas_cp(373.15,80000)
    print a.Heat_of_vaporization(373.15,100000)
    print a.Pressure_of_saturation(373.15,100000)

    a.Eos_set()
    print "EOS Test"
    print a.Phiv(400,110000)
    print a.Phil(373.15,110000)
    print a.Hv(373.15,50000)
