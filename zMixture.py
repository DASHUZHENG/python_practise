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

from zChemical import zProperty
from zEquation import zEquation
from zEquation import zEquationMX



class zComponent():
    
    def __init__(self,*args):
        
        #args is zProperty
        
        self.logger=logging.getLogger("test.txt")
        
        #Basic Setting
        self.vector=[]
        self.matrix=[]
        
        for arg in args:
            if isinstance(arg,zProperty):
                self.composition[arg.name]=arg
        
        self.vector=[x for x in self.composition]
        self.matrix=["(%s,%s)" %(x,y) for x in self.vector for y in self.vector]
        
class zMethod():
    pass



class zStream():
    
    def __init__(self,zcomponent,temp=298.15,pres=100000,vfrac=0,lfrac=0,sfrac=0):
        #zcomponent is an example of zComponent
        
        self.vector=zcomponent.vector
        
        self.omega=zcomponent.omega
        
        self.temp=temp
        self.pres=pres
        
        self.vfrac=vfrac
        self.lfrac=lfrac
        self.sfrac=sfrac
        
        self.mass_flow={}
        self.mole_flow={}
        self.mass_conc={}
        self.mole_conc={}
        
        
    def stream_setting(self,temp,pres,t0=298.15,p0=100000,method="MASS-FLOW"):
        
        if method=="MASS-FLOW":
            
            overall_mass_flow=0
            overall_mole_flow=0
            
            for vec in self.vector:
                self.mass_flow[vec]=5
                self.mole_flow[vec]=self.massflow[vec]/self.omega[vec]        
                overall_mass_flow=overall_mass_flow+self.mass_flow[vec]
                overall_mole_flow=overall_mole_flow+self.mole_flow[vec]
            
            overall_flow=overall_mass_flow
            
            conc_calc=lambda x:x/overall_flow
            
            self.mass_conc=map(conc_calc,self.mass_flow)
            
            overall_flow=overall_mole_flow
            
            self.mole_conc=map(conc_calc,self.mole_flow)
        
    def stream_calc(zmixture):
        
        

class zMixture():
    
    def __init__(self,*args):
        
        self.logger=logging.getLogger("test.txt")
        
        #Basic Setting
        self.vector=[]
        self.matrix=[]
        self.composition={}
        
        for arg in args:
            if isinstance(arg,zProperty):
                self.composition[arg.name]=arg
        
        self.vector=[x for x in self.composition]
        self.matrix=["(%s,%s)" %(x,y) for x in self.vector for y in self.vector]
        
        #Concentration Setting
        self.mole_content={}
        self.mass_content={}
        
        self.mass_conc={}
        self.mole_conc={}
        
        #Special Treatment setting
        self.henry_list={}
        self.inert_list={}
        self.scale_mole_conc={}
        
        
        #Equation Info Setting
        self._eoslist=["IDEAL","RK","RKS","PR"]
        self._activitylist=["WILSON","NTRL","UNIQUAC"]
        
        #Designed for gamma method retrieve
        self._default_activity={\
        "WILSON":(0,0,0,0,0,0,0,0,0,1024,0,0),\
        "NRTL":(0,0,0,0,0,0,0,0,0,0,0,1024),\
        "UNIQUAC":(0,0,0,0,0,0,0,0,0,0,0,1024)}
        
        self._activity_para_number={\
        "WILSON":(6,5),\
        "NRTL":(5,5),\
        "UNIQUAC":(5,5)}
        
        #!Wilson Database need an update
        #Database Structure Dependent
        
        
        self._thermoset=['PHIVMX','PHILMX','HVMX','HLMX','GVMX','GLMX','SVMX','SLMX','VVMX','VLMX','PHISMX','HSMX','GSMX','SSMX','VSMX','WSLMX','HCSLMX']
        self._thermosubset=['PHILPCMX','DHVMX','DHLMX','DGVMX','DGLMX','DSVMX','DSLMX','PHISOCMX']
        
        __slot__=[]
        

        
    def eos_set(self,eos="RK",activity="WILSON",database="zPro.db",location="biWILSON1"):
        
        self.eosset={}
        
        db=zDatabase.zDatabase()
        
        if eos in self._eoslist:
            self.eos=eos
            #!Database Problem
            for comp in self.vector:
                self.eosset=(eos,self.composition[comp].tc,self.composition[comp].pc,self.composition[comp].vc,self.composition[comp].omega)
            #Is this enough for EOS tuple?
        else:
            self.eos="RK"
            for comp in self.vector:
                self.eosset=(eos,self.composition[comp].tc,self.composition[comp].pc,self.composition[comp].vc,self.composition[comp].omega)
            #Is this enough for EOS tuple?
            print "Default Equation is RK"
        
        if activity in self._activitylist:
            
            self.activity=activity
            self.gamma_method={}
            
            calcfilter=lambda x: isinstance(x,float)
            
            for comp in self.vector:
                
                for subcomp in self.vector:
                    pair1="(%s,%s)" % (comp,subcomp)
                    pair2="(%s,%s)" % (subcomp,comp)
                    
                   
                    try:
                        search_activity=db.Locate(database,location,pair1,"*","Field1")
                    
                        #print "Search Result",search_activity
                        #Rectify a coupled pair
                        
                        if search_activity==None:
                            
                            search_activity=db.Locate(database,location,pair2,"*","Field1")
                            
                            #print "Extra Search Result",search_activity
                            
                            if search_activity!=None:
                                
                                #print "Switch",search_activity
                                
                                search_activity=list(search_activity)
                                
                                switch_start=self._activity_para_number[self.activity][0]
                                switch_group=self._activity_para_number[self.activity][1]
                                
                                #print "Test Switch", switch_start,switch_group
                                
                                for switch_num in range(0,switch_group):
                                    
                                    switch_rank=2*switch_num+switch_start
                                    search_activity[switch_rank],search_activity[switch_rank+1]=\
                                    search_activity[switch_rank+1],search_activity[switch_rank]
                                    
                                
                                #print "Switch Result",search_activity
                                    
                                search_activity=tuple(search_activity)
                                
                                
                        
                        if search_activity==None:
                            search_activity=self._defaultactivity[self.activity]
                        
                        #!!All the prime key change to "Field1"!!!
                        #print("Debug tdep property load member %s %s" % (btt,result2))
                        
                        filtered_activity=filter(calcfilter,search_activity)
                        activity_coef=list(filtered_activity)
                        activity_coef.insert(0,self.activity)
                        self.gamma_method[pair1]=tuple(activity_coef)
                    
                    except Exception,error:
                        #print "Activilty Load Error", error
                        self.logger.info("Activilty Load Error")
                        #print("KeyWord:%s;\nTdep_property_database error: %s\n" % (att,error))
                        search_activity=self._default_activity[self.activity]
                        filtered_activity=filter(calcfilter,search_activity)
                        activity_coef=list(filtered_activity)
                        activity_coef.insert(0,self.activity)
                        self.gamma_method[pair1]=tuple(activity_coef)
                        
                        #!Not Finish Yet
    

    def Gamma(self,temp,pres,t0=298.15,p0=100000,route="1"):
        
        gamma_list={}
        lam_list={}
        
        if route=="1":
            for comp in self.vector:
                gamma_list[comp]=1
                
        
        elif route=="WILSON":
            
            for comb in self.matrix:
                
                para=self.gamma_method[comb]
               
                ln_lam=para[1]+para[3]/temp+para[5]*math.log(temp)+para[7]*temp+para[11]/temp/temp
                
                lam_list[comb]=math.exp(ln_lam)
        
                
                #print "Wilson Para", para
                #print "Wilson Lam Result",lam_list[comb]
                #print comb,para[1],para[3],para[5],para[7],para[11]
            
            #After Wilson Update, it will be para[9]       
                
            
            for count_i in self.vector:
                
                sum_ij1=0
                
                for count_j1 in self.vector:
                    
                    pair_ij1="(%s,%s)" % (count_i,count_j1)
                    sum_ij1=sum_ij1+self.mole_conc[count_j1]*lam_list[pair_ij1]
                
                #The first Wilson Sum Item
                
                #print "sum_ij1:",pair_ij1,sum_ij1
                
                sum_ik=0
                
                for count_k in self.vector:
                    
                    pair_ki="(%s,%s)" % (count_k,count_i)

                    sum_kj2=0
                    
                    for count_j2 in self.vector:
                        
                        pair_kj2="(%s,%s)" % (count_k,count_j2)
                        
                        sum_kj2=sum_kj2+lam_list[pair_kj2]*self.mole_conc[count_j2]
                    
                    sum_ik=sum_ik+self.mole_conc[count_k]*lam_list[pair_ki]/sum_kj2
                
                
                ln_gamma_i=1-math.log(sum_ij1)-sum_ik
                
                gamma_list[count_i]=math.exp(ln_gamma_i)
            
        #print "lam_List",lam_list                
                
        return gamma_list
        
    def Henry(self,temp,pres,t0=298.15,p0=100000,route="Henry"):
        pass
    
    
    
    def Vvmx(self,temp,pres,t0=298.15,p0=100000,route="RK"):
        
        if route=="1":
            pass
        
        elif route=="2":
            pass
        
        elif route=="RK":
            
            equation=zEquationMX()
            
            try:
                result=getattr(equation,"RKMX")(self.vector,self.matrix,self.composition,self.mole_conc,temp,pres,0,tag="V")
                
                #print("Vv Debug %s %s %s" %(self.eosset,result,8.3145*temp/pres))
            except Exception, error:
                print ("KeyWord:%s + %s\nMistake:%s\n"%("Vvmx","Test",error))
                result= 0
        else:
            
            pass
            
            
        return result
        
    def Vlmx(self,temp,pres,t0=298.15,p0=100000,route="2"):
        
        if route=="1":
            pass
        
        elif route=="2":
            vl_list={}
            vlmx=0
            
            for comp in self.vector:
                vl_list[comp]=self.composition[comp].Vl(temp,pres)
                vlmx=vlmx+vl_list[comp]*self.mole_conc[comp]
            
        result=vlmx
        
        return result
            
    def Phivmx(self,temp,pres,t0=298.15,p0=100000,route="RK"):
        
        if route=="1":
            pass
        
        elif route=="RK":
            
            equation=zEquationMX()
            
            try:
                result=getattr(equation,"RKMX")(self.vector,self.matrix,self.composition,self.mole_conc,temp,pres,0,tag="PHIV")
                
                #print("Vv Debug %s %s %s" %(self.eosset,result,8.3145*temp/pres))
            
            except Exception, error:
                print ("KeyWord:%s + %s\nMistake:%s\n"%("Phivmx","Test",error))
                result= 0
                #!Not Yet Finished
        
        return result
    
    def Philmx(self,temp,pres,t0=298.15,p0=100000,route="2"):
        
        phil_list={}
        philmx_list={}
        
        if route=="1":
            pass
        
        if route=="2":
            #Default Lewis-Randall or Rault Law
            
            gamma_list=self.Gamma(temp,pres,t0,p0,route=self.activity)
            #!This method:uses self.activity to set gamma method, OK or NOT
            
            #print "PHIL DEBUG",gamma_list
            
            for comp in self.vector:
                phil_list[comp]=self.composition[comp].Phil(temp,pres)
                para_phil=phil_list[comp]
                para_gama=gamma_list[comp]
                philmx_list[comp]=para_phil*para_gama
        
        
        return philmx_list
                
                
            
            
        
        
        

        
if __name__=="__main__":
    #a initiated
    a=zProperty("H2O")
    #b initiated
    b=zProperty("H2O")
    b.name="ACETIC"
    
    test=zMixture(a,b)
    print test.vector
    print test.matrix
    print test.composition

    test.mole_content["H2O"]=5
    test.mole_content["ACETIC"]=5
    test.mole_conc["H2O"]=0.5
    test.mole_conc["ACETIC"]=0.5
    
    print test.mole_content
    
    print "Vvmx",test.Vvmx(500,300000)
    print "Vlmx",test.Vlmx(298.15,100000)
    print "Phiv",test.Phivmx(500,30000)
    print "Eosset",test.eos_set(eos="RK",activity="WILSON",database="zPro.db",location="biWILSON1")
    #print test.gamma_method
    print "Gamma",test.Gamma(298.15,100000,route="WILSON")
    print "Phil",test.Philmx(298.15,100000,route="2")
    

