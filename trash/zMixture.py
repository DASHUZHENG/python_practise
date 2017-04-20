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

from zChemical import zChemical
from zEquation import zEquation

class zMixture():
    def __init__(self,*args):
        self.vector={}
        for arg in args:
            if isinstance(arg,zChemical):
                self.vector[arg.name]=arg
        
        self._thermoset=['PHIVMX','PHILMX','HVMX','HLMX','GVMX','GLMX','SVMX','SLMX','VVMX','VLMX','PHISMX','HSMX','GSMX','SSMX','VSMX','WSLMX','HCSLMX']
        self._thermosubset=['PHILPCMX','DHVMX','DHLMX','DGVMX','DGLMX','DSVMX','DSLMX','PHISOCMX']

        self.concentration={}

        for comp in self.vector:
            self.concentration[comp]=0