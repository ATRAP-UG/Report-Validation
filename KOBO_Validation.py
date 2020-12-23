# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 09:55:49 2020

@author: jbrees
"""

#%%FUNCTIONS AND LIBRARIES
import numpy as np
import pandas as pd
from PIL import Image
from os import path

#%%FILES AND LOCATIONS

#Folder path where all files and sub-folders are located
folder = 'C:/Users/jbrees/Documents/MEGAsync/PhD/Data/KOBO/'

#Sub-Folder path within the newly downloaded picture-folder from the KOBO website
pics = '18december2020/atrap_ug/attachments/03cd08daadc747a1a9817f98ea5fd935/'

#Name of the last checked excel sheet from the KOBO website ('empty.xlsx' for first check)
previous = '04december2020_200m.xlsx' 

#Name of the newly downloaded excel sheet from the KOBO website
current = '18december2020_Unchecked.xlsx'

#Name of the new excel file to save too (= 'current_Temp')
temp = '18december2020_Temp.xlsx'

#Name of the csv-file containing the true coordinates of all the sites
coordinates = 'ContactPoints_Updated.csv'

#Name of the xlsx-file containing ID's and device ID's
device_IDs = 'CS_Device_ID.xlsx'

#If a Temp-file is already present, then this one will be the 'previous'
if path.exists(folder + temp):
    previous = temp
    
#%%SETTING PARAMETERS

##LATITUDE OF THE AREA (APPROX.)
Lat = 1 #in decimal degrees

##SCOOPING TIME LIMITS
tmin=pd.to_timedelta('0 days 00:20:00') #minimum time to scoop
tmax=pd.to_timedelta('0 days 00:40:00') #maximum time to scoop

##TEMPERATURE WARNING THRESHOLDS
Tmin = 10 #minimum temp
Tmax = 35 #maximum temp

##DISTANCE FROM TRUE LOCATION THRESHOLD 
Dmax = 200 #in meters

Dmax_x = Dmax/(111320*np.cos(np.radians(Lat))) #converts to decimal degrees 
Dmax_y = Dmax/111320

##FULL CHECK (1) OR AUTO CHECK (0)? 
check_user = 1

#%%MAKE DATAFRAMES AND ADD COLUMNS FOR NEW DATA
df_prev = pd.read_excel(folder + previous)
df = pd.read_excel(folder + current)
coordinates = pd.read_csv(folder + coordinates)
device_IDs = pd.read_excel(folder + device_IDs)

##ONLY CREATE COLUMNS IF NOT YET THERE
if not 'NO3' in df.columns:
    df['NO3']=np.nan
    df['GH']=np.nan
    df['KH']=np.nan
    df['pH']=np.nan
    df['Cl2']=np.nan
    df['_validation_status']=0
    df['ID_Error']=0
    df['Date_warning']=0
    df['Location_Error']=0
    df['Scoop_Time_Error']=0
    df['Strip_Error']=0
    df['Bio_Error']=0
    df['Bul_Error']=0
    df['Lym_Error']=0
    df['Pool_Error']=0
    df['Temp_Warning']=0
    df['Probe_Warning']=0

#%%LOOP THROUGH ALL PROTOCOLS
for i in range(0,df.shape[0]):
    
    ##CHECK IF PROTOCOL IS NOT ALREADY CHECKED
    if df_prev.loc[df_prev['_id']==df.loc[i,'_id'],['_validation_status']].empty:
    
        print('NEW PROTOCOL FROM ID ' + str(df.loc[i,'ID']) + ': ' + df.loc[i,'Watercontactsite'] )
        
        ##CHECK SCOOPER-ID WITH DEVICE-ID
        if df.loc[i,'deviceid'] != device_IDs.loc[df.loc[i,'ID']-1,'Device_ID']:
            print('!!DEVICE AND ID DO NOT MATCH!!')
            df.loc[i,'ID_Error'] = 1
        else:
            print('DEVICE ID OK')
        
        ##USER CHECK OF DATE
        if check_user == 1:
            stop = 0
            while stop == 0:
                date_ok = input('Is the following date realistic: ' + str(df.loc[i,'Select the date']) + '?')
                if date_ok == '0':
                    print('!!DATE NOT OK!!')
                    df.loc[i,'Date_warning'] = 1
                    stop = 1
                elif date_ok == '':
                    print('DATE OK')
                    stop = 1
                else:
                    print('!!INPUT NOT OK!!')
            
        ##CHECK DISTANCE FROM TRUE LOCATION   
        x_dist = df.loc[i,'_Take a GPS point_longitude'] - coordinates.loc[coordinates['Full_Name'] == df.loc[i,'Watercontactsite'],['xcoord']]
        y_dist = df.loc[i,'_Take a GPS point_latitude'] - coordinates.loc[coordinates['Full_Name'] == df.loc[i,'Watercontactsite'],['ycoord']]
    
        if abs(x_dist.iloc[0,0]) > Dmax_x or abs(y_dist.iloc[0,0]) > Dmax_y :
            print('!!LOCATION NOT OK!!')
            df.loc[i,'Location_Error'] = 1
        else:
            print('LOCATION OK')    
        
        ##CHECK FOR 'NO WATER' OPTION
        if df.loc[i,'Why was the water site not used this week?/There is NO water '] !=1:
        
            ##CHECKING SCOOP-TIME
            start = pd.to_datetime(df.loc[i,'What is the time now?'])
            stop = pd.to_datetime(df.loc[i,'You are done scooping. What is the time now?'])
            duration = stop - start
            if duration < tmin or duration > tmax:
                print('!!SCOOP-TIME NOT OK!!')
                df.loc[i,'Scoop_Time_Error'] = 1
            else:
                print('SCOOP-TIME OK')
            
            ##SHOWING AND READING TEST STRIP DATA
            if check_user == 1:
                if path.exists(folder + pics + df.loc[i,'_uuid'] + '/' + df.loc[i,'Place the test strip on the left side of the color chart (indicated in gray) and take a clear photograph.']):
                    strip = Image.open(folder + pics + df.loc[i,'_uuid'] + '/' + df.loc[i,'Place the test strip on the left side of the color chart (indicated in gray) and take a clear photograph.'])
                    strip.show()
                    stop = 0
                    while stop == 0:
                        strip_ok = input('Strip OK?')
                        if strip_ok == '0':
                            print('!!STRIP NOT OK!!')
                            df.loc[i,'Strip_Error'] = 1
                            stop = 1
                        elif strip_ok == '':
                            print('STRIP OK')
                            ##Keep asking for NO3 until a correct value is entered
                            stop = 0
                            while stop == 0: 
                                NO3 = input('NO3=  ')
                                if NO3 in ['0','10','25','50','100','250','500']:
                                    df.loc[i,'NO3'] = float(NO3)
                                    stop = 1
                                else:
                                    print('!!INPUT NOT OK!!')
                            ##Keep asking for GH until a correct value is entered
                            stop = 0
                            while stop == 0:
                                GH = input('GH=  ')
                                if GH in ['3','4','7','14','21']:
                                    df.loc[i,'GH'] = float(GH)
                                    stop = 1
                                else:
                                    print('!!INPUT NOT OK!!')
                            ##Keep asking for KH until a correct value is entered        
                            stop = 0
                            while stop == 0:
                                KH = input('KH=  ')
                                if KH in ['0','3','6','10','15','20']:
                                    df.loc[i,'KH'] = float(KH)
                                    stop = 1
                                else:
                                    print('!!INPUT NOT OK!!')  
                            ##Keep asking for pH until a correct value is entered        
                            stop = 0
                            while stop == 0:
                                pH = input('pH=  ')
                                if pH in ['6.4','6.8','7.2','7.6','8.0','8.4']:
                                    df.loc[i,'pH'] = float(pH)
                                    stop = 1
                                else:
                                    print('!!INPUT NOT OK!!')     
                            ##Keep asking for Cl2 until a correct value is entered
                            stop = 0
                            while stop == 0:
                                Cl2 = input('Cl2=  ')
                                if Cl2 in ['0','0.8','1.5','3.0']:
                                    df.loc[i,'Cl2'] = float(Cl2)
                                    stop = 1
                                else:
                                    print('!!INPUT NOT OK!!')                                     
                            stop = 1
                        else:
                            print('!!INPUT NOT OK!!')                           
                else:
                    print('!!STRIP PIC MISSING!!')
                    df.loc[i,'Strip_Error'] = 1
                    
            ##SHOWING AND CHECKING SNAIL PICTURES        
            if check_user == 1:
                
                #Biomphalaria
                if df.loc[i,'What is the number of Biomphalaria specimens? (example shown below)'] > 0:
                    if path.exists(folder + pics + df.loc[i,'_uuid'] + '/' + df.loc[i,'Place all Biomphalaria specimens on the scale paper and take a photograph.']):
                        bio = Image.open(folder + pics + df.loc[i,'_uuid'] + '/' + df.loc[i,'Place all Biomphalaria specimens on the scale paper and take a photograph.'])
                        bio.show()
                        stop = 0
                        while stop == 0:
                            bio_ok = input('Number of Bio is ' + str(df.loc[i,'What is the number of Biomphalaria specimens? (example shown below)']) + '?')
                            if bio_ok == '0':
                                print('!!BIOMPHALARIA NOT OK!!')
                                df.loc[i,'Bio_Error'] = 1
                                stop = 1
                            elif bio_ok == '':
                                print('BIOMPHALARIA OK')
                                stop = 1
                            else:
                                print('!!INPUT NOT OK!!')                               
                    else:
                        print('!!BIOMPHALARIA PIC MISSING!!')
                        df.loc[i,'Bio_Error'] = 1
                
                #Bulinus
                if df.loc[i,'What is the number of Bulinus specimens? (example shown below)'] > 0:
                    if path.exists(folder + pics + df.loc[i,'_uuid'] + '/' + df.loc[i,'Place all Bulinus specimens on the scale paper and take a photograph.']):
                        bul = Image.open(folder + pics + df.loc[i,'_uuid'] + '/' + df.loc[i,'Place all Bulinus specimens on the scale paper and take a photograph.'])
                        bul.show()
                        stop = 0
                        while stop == 0:
                            bul_ok = input('Number of Bul is ' + str(df.loc[i,'What is the number of Bulinus specimens? (example shown below)']) + '?')
                            if bul_ok == '0':
                                print('!!BULINUS NOT OK!!')
                                df.loc[i,'Bul_Error'] = 1
                                stop = 1
                            elif bul_ok == '':
                                print('BULINUS OK')
                                stop = 1
                            else:
                                print('!!INPUT NOT OK!!')
                    else:
                        print('!!BULINUS PIC MSSING!!')
                        df.loc[i,'Bul_Error'] = 1
                        
                #Lymnea
                if df.loc[i,'What is the number of Lymnea specimens? (example shown below)'] > 0:
                    if path.exists(folder + pics + df.loc[i,'_uuid'] + '/' + df.loc[i,'Place all Lymnea specimens on the scale paper and take a photograph.']):
                        lym = Image.open(folder + pics + df.loc[i,'_uuid'] + '/' + df.loc[i,'Place all Lymnea specimens on the scale paper and take a photograph.'])
                        lym.show()
                        stop = 0
                        while stop == 0:
                            lym_ok = input('Number of Lym is ' + str(df.loc[i,'What is the number of Lymnea specimens? (example shown below)']) + '?')
                            if lym_ok == '0':
                                print('!!LYMNEA NOT OK!!')
                                df.loc[i,'Lym_Error'] = 1
                                stop = 1
                            elif lym_ok == '':
                                print('LYMNEA OK')
                                stop = 1
                            else:
                                print('!!INPUT NOT OK!!')
                    else:
                        print('!!LYMNEA PIC MISSING!!')
                        df.loc[i,'Lym_Error'] = 1
                        
                #Pool
                if df.loc[i,'Did you find any other snails? (NO Biomphalaria, Bulinus or Lymnaea)'] == 'YES':
                    if path.exists(folder + pics + df.loc[i,'_uuid'] + '/' + df.loc[i,'Place all other specimens on the scale paper and take a photograph.']):
                        pool = Image.open(folder + pics + df.loc[i,'_uuid'] + '/' + df.loc[i,'Place all other specimens on the scale paper and take a photograph.'])
                        pool.show()
                        stop = 0
                        while stop == 0:
                            pool_ok = input('Pool is OK?')
                            if pool_ok == '0':
                                print('!!POOL NOT OK!!')
                                df.loc[i,'Pool_Error'] = 1
                                stop = 1
                                stop2 = 0
                                while stop2 == 0:
                                    pool_correction = input('Wrongly assigned to pool: Biomph (1), Bulinus (2), Lymnaea (3)')
                                    if pool_correction == '1':
                                        df.loc[i,'Bio_Error'] = 1
                                        print('!!BIO WAS ASSIGNED TO POOL!!')
                                        stop2 = 1
                                    elif pool_correction == '2':
                                        df.loc[i,'Bul_Error'] = 1
                                        print('!!BUL WAS ASSIGNED TO POOL!!')
                                        stop2 = 1
                                    elif pool_correction == '3':
                                        df.loc[i,'Lym_Error'] = 1
                                        print('!!LYMNAEA WAS ASSIGNED TO POOL!!')
                                        stop2 = 1
                                    else:
                                        print('INPUT NOT OK')
                            elif pool_ok == '':
                                print('POOL OK')
                                stop = 1
                            else:
                                print('!!INPUT NOT OK!!')                                
                    else:
                        print('!!POOL PIC MSSING!!')
                        df.loc[i,'Pool_Error'] = 1
                        
            ##CHECK TEMPERATURE
            if df.loc[i,'Take the thermometer out of the water and note the temperature.'] < Tmin or df.loc[i,'Take the thermometer out of the water and note the temperature.'] > Tmax:
                print('!!TEMPERATURE WARNING!!')
                df.loc[i,'Temp_Warning']=1
            else:
                print('TEMPERATURE OK')
        
            ##CHECK PROBE PARAMETERS
            if df.loc[i,'What is the temperature? (if you could not take the measurement, please enter 0)'] == 0 or df.loc[i,'What is the pH? (if you could not take the measurement, please enter 0)'] == 0 or df.loc[i,'What is the µS? (if you could not take the measurement, please enter 0)'] == 0 or df.loc[i,'What is the ppm? (if you could not take the measurement, please enter 0)'] == 0:
                print('!!PROBE WARNING!!')        
                df.loc[i,'Probe_Warning']=1
            else:
                print('PROBE OK')
        
        else:
            print('THERE WAS NO WATER')
            
        ##SET STATUS TO VALIDATED (1)        
        df.loc[i,'_validation_status'] = 1
                    
        ##ADD CHECKED PROTOCOL TO PREVIOUS DATAFRAME (comment out for first ever check, no 'previous')
        df_prev = pd.concat([df_prev,pd.DataFrame([df.loc[i,:]])], sort=False)       
        
        ##ASK TO CONTINUE
        if check_user == 1:
            go = input('CONTINUE?')
            if go == '0':
                break

        ##SAVE TO TEMP EXCEL
        df_prev.to_excel(folder + temp, index=False)

