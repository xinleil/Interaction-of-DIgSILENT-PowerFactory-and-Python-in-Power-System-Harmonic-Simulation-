Python 3.8.0 (v3.8.0:fa919fdf25, Oct 14 2019, 10:23:27) 
[Clang 6.0 (clang-600.0.57)] on darwin
Type "help", "copyright", "credits" or "license()" for more information.
>>> #original code from jupyter notebook, a couple of python packs need to be installed 

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
from scipy import fftpack
import glob
import os


def import_file(file = '/Users/xinleil/Desktop/*.csv'):
    #import the csv file
    df = pd.read_csv(file, header = 1).reset_index(drop = True)

    # read time
    time = df['Time in s'].values

    # load phase A voltage 
    dataVoltage = df['Phase Voltage A in kV'].values

    # load phase A current
    #dataCurrent = df['Phase Current A/HV-Side in kA'].values
    dataCurrent = df['Phase Current A in kA'].values
    return time, dataVoltage, dataCurrent

# fft transfer of V and C
def fft_preprocess(dataVoltage, dataCurrent, tstep = 0.0001):
    
    dataVoltage_fft = pd.DataFrame(fftpack.fft(dataVoltage))
    dataCurrent_fft = pd.DataFrame(fftpack.fft(dataCurrent))

    #define time and frequency interval
    tstep = 0.0001 #sample time interval

    N = len(dataCurrent) # length of the sample N = len(dataVoltage)

    t = np.linspace(0, (N-1)*tstep, N) #time steps

    Fs = 1 / tstep
    fstep = Fs / N #freqency interval

    f = np.linspace(0, (N-1)*fstep, N) #freq steps
    
    return dataVoltage_fft, dataCurrent_fft, f, N, t

def vol_cur_plot(dataVoltage_fft, dataCurrent_fft, N, f):
    # Voltage
    #normalize the ampitude by divided N: number of sample
    Voltage = (2 * dataVoltage_fft)/N 
    Voltage_mag = Voltage.values.squeeze(axis = 1)
    
    # Current
    #normalize the ampitude by divided N: number of sample
    Current = (2 * dataCurrent_fft)/N 
    Current_mag = Current.values.squeeze(axis = 1)

    # modify the DC component by 2 and the x-axis
    f_plot = f[0:int(N/2+1)]
    Voltage_mag_plot = Voltage_mag[0:int(N/2+1)]
    Voltage_mag_plot[0] = Voltage_mag_plot[0] / 4
    
    Current_mag_plot = Current_mag[0:int(N/2+1)]
    Current_mag_plot[0] = Current_mag_plot[0] / 4
    
    return f_plot, Voltage_mag_plot, Current_mag_plot
    
    
def Voltage_time_domain():
    # plot Voltage-time domain
    plt.figure(figsize = (100,20))
    #plt.rcParams['figure.dpi'] = 300

    plt.xlabel('time')
    plt.ylabel('Voltage Amplitue[kV]')
    plt.title('Time Domain')
    plt.plot(t, dataVoltage, linestyle = '-', marker = '*', color='red')
    plt.show()
    
def Current_time_domain():
    # plot Current-time domain
    plt.figure(figsize = (100,20))
    #plt.rcParams['figure.dpi'] = 300 #export for paper work

    plt.xlabel('time')
    plt.ylabel('Current Amplitue[kA]')
    plt.title('Time Domain')
    plt.plot(t, dataCurrent, linestyle = '-', marker = '*', color='blue')
    plt.show()    
    
def freq_domain_vol():
    #plot frequency domain (Voltage)
    plt.figure(figsize = (10,5))
    #plt.rcParams['figure.dpi'] = 300 #export for paper work
    #plt.ylim([0,400])
    plt.xlim([0,1000])

    plt.xlabel('frequency')
    plt.ylabel('Voltage_mag')
    plt.title('Freq Domain')
    plt.plot(f_plot, abs(Voltage_mag_plot), linestyle = '-', marker = '*', color='red')
    plt.grid()
    #plt.tight_layout()
    plt.show()
    
def freq_domain_cur(): 
    #plot frequency domain (Current)
    plt.figure(figsize = (10,5))
    #plt.rcParams['figure.dpi'] = 300
    #plt.ylim([0,10])
    plt.xlim([0,1000])

    plt.xlabel('frequency')
    plt.ylabel('Current_mag')
    plt.title('Freq Domain')
    plt.plot(f_plot, abs(Current_mag_plot), linestyle = '-', marker = '*', color='blue')
    plt.grid()
    #plt.tight_layout()
    plt.show()
    
def vol_harm_fft(f_plot, Voltage_mag_plot, Current_mag_plot, file_num = None, down_limit = 0.85, up_limit = 0.85):
    # extract the voltage harmonics fft value
    df_V = pd.DataFrame({'f': f_plot, f'V_{file_num}': Voltage_mag_plot})
    file_num = int(file_num)
    data_Voltage = df_V[((file_num - down_limit) < df_V['f']) & (df_V['f'] < (file_num + up_limit))] # extract the voltage near harmonic frequency 
    print(data_Voltage.head(10))
    
    # extract the current harmonics fft value
    df_C = pd.DataFrame({'f': f_plot, f'C_{file_num}': Current_mag_plot})

    data_Current = df_C[((file_num - down_limit) < df_C['f']) & (df_C['f'] < (file_num + up_limit))] # extract the current near harmonic frequency
    print(data_Current.head(10))
    
    return data_Voltage, data_Current

# define RMS function
def rms(y):
    return np.sqrt(np.mean(y**2))

def get_rms(data_Voltage, data_Current, file_num):
    # RMS V_500 and C_500,to get Impedance_500
    rms_V = rms(data_Voltage[f'V_{file_num}']) #Voltage

    rms_C = rms(data_Current[f'C_{file_num}']) #Current

    Impedance = rms_V / rms_C #Impedence

    return Impedance


#visualisation part csv data from the PowerFactory EMT Simulation 

path = '/Users/xinleil/Desktop/aggregated'
files = glob.glob(path + '/*.csv')


Num = []
Imped = []
for file in files:
    print('The csv file is: '+ file)
    file_num = file.split('Current')[1].split('.')[0]
    print('Extracted number: ' + file_num)
    
    time, dataVoltage, dataCurrent = import_file(file)
    dataVoltage_fft, dataCurrent_fft, f, N, t = fft_preprocess(dataVoltage, dataCurrent, tstep = 0.0001)
    
    f_plot, Voltage_mag_plot, Current_mag_plot = vol_cur_plot(dataVoltage_fft = dataVoltage_fft, 
                                                              dataCurrent_fft = dataCurrent_fft, 
                                                              N = N, 
                                                              f = f)
    Voltage_time_domain()
    Current_time_domain()
    freq_domain_vol()
    freq_domain_cur()
    
    #extract the values near the harmonic frequency
    data_Voltage, data_Current = vol_harm_fft(f_plot = f_plot, 
                                              Voltage_mag_plot = Voltage_mag_plot, 
                                              Current_mag_plot = Current_mag_plot, 
                                              file_num = file_num, 
                                              down_limit = 1, 
                                              up_limit = 1)
    
    Impedance = get_rms(data_Voltage, data_Current, file_num)
    
    Num.append(int(file_num))
    Imped.append(Impedance)

    
#Impedance magnitude and degree visulization in different frequency sweep

df = pd.DataFrame(list(zip(Num, Imped)), columns = ['Num', 'Imped']).sort_values(by = 'Num', ascending = True)#.set_index('Num')
df['Deg'] = np.angle(df.Imped, deg = True)

#plot Magnitude in db with frequency
plt.plot(df.Num, np.multiply(20, np.log10(abs(df.Imped))),linestyle = '-', marker = '.', color='blue') 

plt.xlim([0,1000])
plt.rcParams['figure.dpi'] = 300

plt.xlabel('frequency')
plt.ylabel('Magnitude dB')
plt.title('Harmonic Impedance in Decibel')
plt.grid()
plt.show()
plt.plot(df.Num, df.Deg,linestyle = '-', marker = '.', color='blue')

#plot Phase in degree with frequency         

#plt.ylim([0,100])
plt.xlim([0,1000])
plt.rcParams['figure.dpi'] = 300

plt.xlabel('frequency')
plt.ylabel('Degree angle')
plt.title('Harmonic Impedance in Degree')
plt.grid()
plt.show()


