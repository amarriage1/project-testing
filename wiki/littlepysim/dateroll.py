# -*- coding: utf-8 -*-
"""
Created on Fri May 12 17:09:01 2017

@author: dlemarchand
"""
#from abc import ABC, abstractmethod
from datetime import date
from calendar import monthrange
from datetime import timedelta

#Global dictionnary, purpose to hold already defined rolls

existingRoll={}

class Roll(object):
    def __init__(self):
        self.predecessor=None
        
    def roll(self,dt):
        if self.predecessor is not None:
            return self.simpleRoll(self.predecessor.roll(dt))
        return self.simpleRoll(dt)
        
    #@abstractmethod
    def simpleRoll(self,dt):
        return dt

class EndOfYearRoll(Roll):
    def __init__(self,offset=0):
        super(EndOfYearRoll, self).__init__()
        #super().__init__()
        self.offset=offset 
    def simpleRoll(self,dt):
        return date(dt.year+self.offset,12,31)

class EndOfQuarterRoll(Roll):
    def __init__(self,offset=0):
        super(EndOfQuarterRoll, self).__init__()
        #super().__init__()
        self.offset=offset
    def simpleRoll(self,dt):
        ts=timedelta(days=1)
        e=dt+ts
        m=3
        if e.month>3:
            m=6
        if e.month>6:
            m=9
        if e.month>9:
            m=12
        lastDay=monthrange(e.year,m)[1]    
        eoq=date(e.year,m,lastDay)
        if (self.offset==0) :
            return eoq
        else:
            mr=MonthRoll(3*self.offset)
            return mr.simpleRoll(eoq)

class YearRoll(Roll):
    def __init__(self,year):
        super(YearRoll, self).__init__()
        #super().__init__()
        self.year=year
    
    def simpleRoll(self,dt):
        return date(dt.year+self.year,dt.month,dt.day)
        
class MonthRoll(Roll):
    def __init__(self,month,keepEndOfMonth=True):
        super(MonthRoll, self).__init__()
        #super().__init__()
        self.month=month    
        self.keepEndOfMonth=keepEndOfMonth
    
    def addMonth(self,dt):
        m=self.month
        temp=dt
        if m>12:
            k=m//12
            m=m-(12*k)
            temp=date(k+temp.year,temp.month,temp.day)
        lm=m+temp.month
        if lm>12:
            lm=lm-12
            temp=date(1+temp.year,lm,temp.day)
        else:
            temp=date(temp.year,temp.month+m,temp.day)
        return temp   
        
    def simpleRoll(self,dt):
        if self.keepEndOfMonth==False:
            return self.addMonth(dt)
        else :
            newdt=self.addMonth(dt)
            lastDay=monthrange(dt.year,dt.month)[1]
            endOfMonth=(lastDay==dt.day)
            if (endOfMonth) :
                lastDay=monthrange(newdt.year,newdt.month)[1]   
                newdt=date(newdt.year,newdt.month,lastDay)
            return newdt

class CalendarDayRoll(Roll):
    def __init__(self,offset=0):
        super(CalendarDayRoll, self).__init__()
        super().__init__()
        self.offset=offset
    def simpleRoll(self,dt):
        ts=timedelta(days=self.offset)
        return dt+ts



def build_simple_roll(token):
    pos=0
    status=0
    concat=True
    word=""
    sign=""
    functionName=""
    numericPart=""
    calendars=""
    for current in token:
        concat=True
        signPosition=False
        if pos==0 :
            if ((current=='+') or (current=='-')) :
                sign=current
                concat=False
                signPosition=True
        if ((not signPosition) and (not current.isnumeric()) and (status==0) ) :
            if word :
                numericPart=word
                word=""
            status=1
        if ((current=='[') and (status==1) and (word)) :
            functionName=word
            word=""
            status=2
        if concat:
            word=word+current
        pos=pos+1    
    if status==1 :
        functionName=word
    if status==2 :
        calendars=word
    numericParameter=0
    if numericPart :
        if sign :
            numericPart=sign+numericPart
        else :
            numericPart='+'+numericPart  
        numericParameter=int(numericPart)
    if functionName=='D' :
        return CalendarDayRoll(numericParameter)    
    if functionName=='M' :
        return MonthRoll(numericParameter)
    if functionName=='Y' :
        return YearRoll(numericParameter)
    if functionName=='EOQ' :
        return EndOfQuarterRoll(numericParameter)
    if functionName=='EOY' :
        return EndOfYearRoll(numericParameter)
    raise TypeError("unknown roll "+token)

def build_roll(template):
    if template in existingRoll :
        return existingRoll[template]
    else :
        roll=None
        tokens=template.split('|')
        for token in tokens:
            current =build_simple_roll(token)
            if roll is not None :
                current.predecessor=roll
            roll=current
        existingRoll[template]=roll 
        return roll  
             
        
if __name__ == "__main__":
    str=""
    print (str)
    #print (str.isspace())  
    #print (str=="") 
    dr=build_roll("EOQ|1Y")
    dt=date(2017,4,20)
    dt1=dr.roll(dt)
    print(dt1)
    dr=build_roll("1M")
    print (dr)
    dt=date(2017,2,28)
    dt1=dr.roll(dt)
    print(dt1)

