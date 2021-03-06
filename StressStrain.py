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
    cutOff=None#This holds the Cuttoff value between Elastic and Plastic regions
    #This Cuttoff should be inputted by the user
    stiffness=0.0
    stiffness_error=0.0
    cylinder=False
    def __init__(self, data,loadDeflection=False,cylinder=False):
        '''
        Data needs to be passed in as a pandas dataframe with the following column
        order: Load(N),Displacement(mm), and Voltage(mV),L(mm),b(mm),h(mm). If the
        Data is instead in the Load-Displacement Form then it needs to be given in the
        Time,Displacement(mm), Load(N) order. Indicate Load-Deflection by inputing True.
        For Cylindrical Load testing indicate both cylindrical and Load-Deflection
        are true and input a data frame with columns in the following order
        Time,Displacement,Load,inner Diameter, Outer Diameter, Length
        '''
        self.data=data#Store the users input
        self.loadDeflection=loadDeflection
        self.cylinder=cylinder
        #We first want to check if we have a cylinder loadDeflection data
        if self.cylinder:
            columns=["Time","Displacement(mm)","Load(N)","d(mm)","D(mm)","L(mm)"]
        elif self.loadDeflection:
            #If we infact have a load-deflection problem we input the data
            #in the follow way
            columns=["Time","Displacement(mm)","Load(N)","L(mm)","b(mm)","h(mm)"]
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
        if self.cylinder:
            #If we are dealing with a cylinder
            self.data['Moment of Inertia(m^4)']=(np.pi/64)*((self.data['D(mm)']/1000)**4-(self.data['d(mm)']/1000)**4)
        else:
            self.data['Moment of Inertia(m^4)']=((self.data['b(mm)']/1000)*(self.data['h(mm)']/1000)**3)/12
        return self.data['Moment of Inertia(m^4)']

    def maxStress(self):
        #Calculates the Max stress
        if self.cylinder:
            #If we indeed have a cylinder
            self.data['Max Stress(Pa)']=(self.maxMoment()*self.data['D(mm)']/1000)/(2*self.momentOfInertia())
        else:
            self.data['Max Stress(Pa)']=(self.maxMoment()*self.data['h(mm)']/1000)/(2*self.momentOfInertia())
        return self.data['Max Stress(Pa)']
    def strain(self):
        if self.loadDeflection:
            self.data['Strain']=self.maxStress()/self.youngsModulus()

        else:
            self.data['Strain']=(self.data['Voltage(mV)']*10)/1000000

        return self.data['Strain']


    def youngsModulus(self):
        #This will return the youngsModulus
        if self.loadDeflection:
            s=self.getStiffness()*(-1)#Run the stiffness method

            #we only want to output the first element of this array since they
            #are all the same element
            return ((s*(self.data['L(mm)']/1000)**3)/(48*self.momentOfInertia()))[0]
        else:
            self.maxMoment()
            self.momentOfInertia()
            self.maxStress()
            self.youngsModulus,b,self.youngError,b_error=self.linReg(self.strain(),self.maxStress())
        return self.data, self.youngsModulus,b, self.youngError,b_error

    def getStiffness(self):
        if self.cutOff==None:
            print("A Cuttoff was not enterred")
        elif not (self.loadDeflection):
            print("You have not declared this as a Load-Deflection Problem")
        else:
            x=[]#This will hold the Displacement values we want based on the Cuttoff
            y=[]#This will hold the Load Values we want based on the cutoffs we want
            for i in range(0,len(self.data['Load(N)'])):
                if self.data['Displacement(mm)'][i]/1000 >= self.cutOff:
                    x.append(self.data['Displacement(mm)'][i]/1000)#Append the value
                    y.append(self.data['Load(N)'][i])#Append the y value
            #Now we can run a linear regression and get the stiffnessa
            self.stiffness,b,self.stiffness_error,b_error=self.linReg(np.array(x),np.array(y))
        return self.stiffness






    def setCutOff(self,cut):
        #this method will set the cuttoff for the stiffness Calculation
        self.cutOff=cut
    def getDeltaLoad(self):
        #Will return the delta vs load
        return (self.data['Displacement(mm)']/1000),self.data['Load(N)']
    def getStressStrain(self):
        #Will return the stress Strain
        return (self.strain(),self.maxStress())




    def linReg(self,x,y):
        '''This function will take as an input two 1D numpy arrays and
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
    def getData(self):
        #This method will return back the data dataframe
        return self.data

if __name__ == '__main__':
    # input=pd.read_csv('./Procedure1/Procedure1Brass3.csv',nrows=10)
    # print(input.head())
    # test=StressStrain(input)
    # out,youngsMod,b,youngError,b_error=test.youngsModulus()
    # print(out.head(5))
    # print(youngsMod)

    #Test for Procedure 2
    # input=pd.read_csv('./Procedure2/Brass1.csv',nrows=92)
    # test=StressStrain(input,loadDeflection=True)
    # test.setCutOff(-0.001)#Just to test
    # stiff=test.getStiffness()
    # ymod=test.youngsModulus()
    # print(ymod)
    # print(test.strain())

    #Test for Procedure 4
    input=pd.read_csv('./Procedure4/Radius-A.csv',nrows=226)
    test=StressStrain(input,loadDeflection=True,cylinder=True)
    test.setCutOff(-0.001)#Just to test
    stiff=test.getStiffness()

    ymod=test.youngsModulus()
    strain=test.strain()

    print(stiff)
