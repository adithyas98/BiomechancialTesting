import numpy as np
import pandas as pd

class StressStrain:
    """This class will house all the data and do all the analysis for the various
        experiments completed in the ;ab procedures. There are some dependencies
        that this class uses, namely numpy and pandas"""
        #0 is a placeholder for now, this will hold the dataframe with raw data
    data=0
    youngsModulus=0.0
    youngError=0.0
    loadDeflection=False
    cutOff=0.0#This holds the Cuttoff value between Elastic and Plastic regions
    #This Cuttoff should be inputted by the user
    def __init__(self, data,loadDeflection=False):
        '''
        Data needs to be passed in as a pandas dataframe with the following column
        order: Load(N),Displacement(mm), and Voltage(mV),L(mm),b(mm),h(mm). If the
        Data is instead in the Load-Displacement Form then it needs to be given in the
        Delta(mm), Load(N) order. Indicate Load-Deflection by inputing True
        '''
        self.data=data#Store the users input
        self.loadDeflection=loadDeflection
        if self.loadDeflection:
            #If we infact have a load-deflection problem we input the data
            #in the follow way
            columns=["Delta(mm)","Load(N)"]
        else:
            #Make sure to set the data correctly
            columns=["Load(N)","Displacement(mm)","Voltage(mV)","L(mm)","b(mm)","h(mm)"]

        self.data.columns=columns

    def maxMoment(self):
        #This will calculate the maximum moment
        self.data['Max Moment(Nm)']=self.data['Load(N)']*self.data['L(mm)']/1000/4
        return self.data['Max Moment(Nm)']

    def momentOfInertia(self):
        #Calculates the Moment of Inertia
        self.data['Moment of Inertia(m^4)']=((self.data['b(mm)']/1000)*(self.data['h(mm)']/1000)**3)/12
        return self.data['Moment of Inertia(m^4)']

    def maxStress(self):
        #Calculates the Max Max Strain
        self.data['Max Stress(Pa)']=(self.maxMoment()*self.data['h(mm)']/1000)/(2*self.momentOfInertia())
        return self.data['Max Stress(Pa)']

    def strain(self):
        #This will return the Strain
        self.data['Strain']=(self.data['Voltage(mV)']*10)/1000000
        return self.data['Strain']



    def youngsModulus(self):
        #This will return the youngsModulus
        self.maxMoment()
        self.momentOfInertia()
        self.maxStress()
        self.youngsModulus,b,self.youngError,b_error=self.linReg(self.strain(),self.maxStress())
        return self.data, self.youngsModulus,b, self.youngError,b_error

    def stiffness(self):




    def linReg(self,x,y):
        '''this function will take as an input two 1D numpy arrays and
    will output the linear regression model with errors. Will return a tuple
    of the slope, y-intercept, error of the slope, and error of the y-intercept'''
    #First we will calculate X,Z,N,Y,B
        N=x.size

        Z=(x**2).sum()
        X=x.sum()
        Y=y.sum()
        B=(x*y).sum()
        delta=(N*Z)-(X**2)

        #Now calculate m and b
        m=(N*B-X*Y)/delta
        b=(Z*Y-X*B)/delta

        #now calculate the errors
        predicts=m*x+b

        errorSquared=(y-predicts)**2
        errorSquaredSum=errorSquared.sum()
        sigmaSquared=errorSquaredSum/N

        m_error=np.sqrt((N*sigmaSquared)/delta)
        b_error=np.sqrt((Z*sigmaSquared)/delta)
        return m,b,m_error,b_error

if __name__ == '__main__':
    # input=pd.read_csv('./Procedure1/Procedure1Brass3.csv',nrows=10)
    # print(input.head())
    # test=StressStrain(input)
    # out,youngsMod,b,youngError,b_error=test.youngsModulus()
    # print(out.head(5))
    # print(youngsMod)

    #Test for Procedure 2
    input=pd.read_csv('./Procedure2/Brass1.csv',nrows=10)
