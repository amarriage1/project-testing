# -*- coding: utf-8 -*-
"""
Created on Sat May 13 08:58:26 2017

@author: dlemarchand
"""

from datetime import date
from calendar import monthrange
import calendar


class DayCountConvention(object):
    
    def count(self, first,end):
        pass
    

class DayCountConventionISDA(DayCountConvention):
    def __init__(self,method):      
        self.method=method
    
    def count(self,first,end):
        time=end-first
        y1=float(first.year)
        y2=float(end.year)
        m1=float(first.month)
        m2=float(end.month)
        d1=float(first.day)
        d2=float(end.day)
        #Non conventionnal case, if the two dates are on the same dd/MM but different year, we compute directly the number of years
        if (first.month==end.month):
            if (first.day==end.day):
                return float(end.year-first.year)
            f=monthrange(first.year,first.month)[1]
            e=monthrange(end.year,end.month)[1]          
            if (first.day==f) and (end.day==e) :
                #Same month and each time, end of month
                return float(end.year-first.year)
        if (self.method=="1/1") :
            return 1.0
        if (self.method=="1/4") :
            return 0.25
        if (self.method=="1/12") :
            return (1.0/12.0)
        if (self.method=="1/2") :
            return 0.5
        if (self.method=="Act/365") or (self.method=="Actual/365") :  
            l=float(time.days)
            return l/float(365)
        if (self.method=="Act/360") or (self.method=="Actual/360") :  
            l=float(time.days)
            return l/float(360)
        if (self.method=="Act/365.25") or (self.method=="Actual/365.25") :  
            l=float(time.days)
            return l/365.25
        if (self.method=="30/360") or (self.method=="Bond Basis") :  
            if (first.day==31):
                d1=float(30)
            if (end.day==31) and (first.day>29) :
                d2=float(30)
            num=(360.0*(y2-y1))+(30.0*(m2-m1))+(d2-d1)    
            return num/float(360)
        if (self.method=="Act/Act") or (self.method=="Actual/Actual") :
            denLeap=0
            denNotLeap=0
            dem=365
            num=float(time.days)
            if (y1==y2) :
                if (calendar.isleap(first.year)) :
                    dem=366
                return num/float(dem)
            eoy=date(first.year,12,31)
            t1=eoy-first
            if (calendar.isleap(first.year)) :   
                denLeap=float(t1.days)
            else :
                denNotLeap=float(t1.days)
            eoy=date(1+eoy.year,12,31) 
            delta=end-eoy
            while (delta.days>0) :
                if (calendar.isleap(eoy.year)) :   
                    denLeap=denLeap+366
                else :
                    denNotLeap=denNotLeap+365
                eoy=date(1+eoy.year,12,31)
                delta=end-eoy
            if (eoy.year==end.year) :
                boy=date(eoy.year,1,1)
                t1=end-boy
                if (calendar.isleap(boy.year)) :   
                    denLeap=denLeap+float(t1.days)
                else :
                    denNotLeap=denNotLeap+float(t1.days)
            return (denLeap/float(366))+ (denNotLeap/float(365))
        

