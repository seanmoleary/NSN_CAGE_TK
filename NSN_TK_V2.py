# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 09:20:31 2019

@author: seoleary
"""

import os
from tkinter import filedialog, Frame, Entry, Button, Tk, messagebox,ttk
import pandas as pd
from re import match
import time
from bs4 import BeautifulSoup
import requests
import sys

sys.setrecursionlimit(5000)

class NSN_TK_V2:   
    
    def __init__(self, master):
        self.master = master
        self.createWidets()
        self.packWidgets()
        self.value = None
    
    def createWidets(self):   
        self.nb = ttk.Notebook(self.master)
        
        self.page1 = ttk.Frame(self.nb)
        self.p1f1 = Frame(self.page1,width = 100)
        self.p1f2 = Frame(self.page1, width = 100)
        
        self.page2 = ttk.Frame(self.nb, width = 100)
        self.p2f1 = Frame(self.page2,width = 100)
        self.p2f2 = Frame(self.page2, width = 100)
        
        self.trackerEntry1 = Entry(self.p1f1, width = 100)
        self.trackerButton1 = Button(self.p1f1,text='NSN File', width = 15, command = self.get_tracker_value1)
        self.okButton1 = Button(self.p1f2,text='OK', width = 10,command = self.ok_button1)
        self.cancelButton1 = Button(self.p1f2, text='Cancel', width = 10, command = self.master.destroy)
        
        self.trackerEntry2 = Entry(self.p2f1, width = 100)
        self.trackerButton2 = Button(self.p2f1,text='CAGE File', width = 15, command = self.get_tracker_value2)
        self.okButton2 = Button(self.p2f2,text='OK', width = 10,command = self.ok_button2)
        self.cancelButton2 = Button(self.p2f2, text='Cancel', width = 10, command = self.master.destroy)
       
        self.nb.add(self.page1,text = 'NSN Search')
        self.nb.add(self.page2,text = 'CAGE Search')
        
    def packWidgets(self):
        self.p1f1.pack()
        self.p1f2.pack()
        self.p2f1.pack()
        self.p2f2.pack()
        self.trackerEntry1.pack(side = 'left', padx = 10, pady = 10)
        self.trackerButton1.pack(side = 'right', padx = 10, pady = 10)
        self.okButton1.pack(side = 'left', padx = 10, pady = 10)
        self.cancelButton1.pack(side = 'right', padx = 10, pady = 10)
        self.trackerEntry2.pack(side = 'left', padx = 10, pady = 10)
        self.trackerButton2.pack(side = 'right', padx = 10, pady = 10)
        self.okButton2.pack(side = 'left', padx = 10, pady = 10)
        self.cancelButton2.pack(side = 'right', padx = 10, pady = 10)
        self.nb.pack(expand=1, fill="both")
        
    def get_tracker_value1(self):
        self.trackerEntry1.delete(0,'end')
        self.trackerFile1 = filedialog.askopenfilename(initialdir = os.getcwd().replace('\\','//'))
        self.trackerEntry1.insert(0,  self.trackerFile1)
        
    def get_tracker_value2(self):
        self.trackerEntry2.delete(0,'end')
        self.trackerFile2 = filedialog.askopenfilename(initialdir = os.getcwd().replace('\\','//'))
        self.trackerEntry2.insert(0,  self.trackerFile2) 
        
    def ok_button1(self):
        
        global trackerFile1
        
        self.trackerFile1 = self.trackerEntry1.get()
        '''
        while not self.check_file(self.trackerFile):
            self.trackerEntry.forget()
            self.get_tracker_value()
            self.trackerFile = self.trackerEntry.get()
        '''
        time1 = time.time()
        frame = NSN_frame(self.trackerFile1)
        result = frame.read_file()
        final_time = round(time.time()-time1,2)
        if not result:
            messagebox.showinfo('Error!','Didn\'t work')
        else:
            messagebox.showinfo('Success!','That took '+str(final_time)+' seconds.\n it was written to file '+frame.out_file)
            
    def ok_button2(self):
        
        global trackerFile2
        
        self.trackerFile2 = self.trackerEntry2.get()
        '''
        while not self.check_file(self.trackerFile):
            self.trackerEntry.forget()
            self.get_tracker_value()
            self.trackerFile = self.trackerEntry.get()
        '''
        time1 = time.time()
        frame = CAGE_frame(self.trackerFile2)
        result = frame.read_file()
        final_time = round(time.time()-time1,2)
        if not result:
            messagebox.showinfo('Error!','Didn\'t work')
        else:
            messagebox.showinfo('Success!','That took '+str(final_time)+' seconds.\n it was written to file '+frame.out_file)

class NSN_frame():
    def __init__(self, input_file):
        self.file = input_file
        self.columns = ['Tracker NSN',
                        'Normalized NSN',
                        'Manufacturer Part Number',
                        'RNCC',
                        'RNVC',
                        'Company Name',
                        'Cage']
        
    def read_file(self):
        if '.xlsx' not in self.file:
            return False 
        else:
            frame = pd.read_excel(self.file)
            return_frame = pd.DataFrame()
            if 'NSN' in frame.columns:
                NSN_codes = frame['NSN'].astype('str')
                for i in list(dict.fromkeys(NSN_codes)):
                    rows = get_NSN(i.strip()).rows
                    for j in rows:
                        return_frame = return_frame.append([j],ignore_index = True)
                
                self.out_file = self.file.replace('.xlsx','')
                self.out_file = self.out_file+'_out.xlsx'
                return_frame.columns = self.columns
                return_frame.to_excel(self.out_file, index = False)

                return True
                
            else:
                return False        

class get_NSN():
    
    def __init__(self,NSN):
        self.tracker_NSN = NSN
        self.normalized_NSN = self.normalize(NSN)
        self.rows = self.get_rows(self.normalized_NSN)

    #Tests to make sure the NSN is the right number of digits and right format
    def normalize(self,NSN):
        r= r'\d{4}[-]\d{2}[-]\d{3}[-]\d{4}'
        if match(r,NSN) == None:
            if len(NSN) == 13:
                code = NSN[:4]+'-'+NSN[4:6]+'-'+NSN[6:9]+'-'+NSN[9:13]
            else:
                #This is the case where NSN is the wrong number of digits
                #In this case, the scraper returns nothing
                code = "0"
        else:
            #This is the case where NSN is in the right format
            code = NSN    
        return code
    
    def get_rows(self, normalized_NSN):
        #get sources html
        site =  r'https://www.nsncenter.com/NSN/'
        http = site + normalized_NSN
        get = requests.get(http)
        source = get.text
        
        #make the soup
        soup = BeautifulSoup(source,'lxml')
        table  = soup.find_all('table',{'class':'table table-condensed table-striped table-hover'})
        
        #rows will ultimately be the return value
        #rows consists of a list of lists
        rows = []
        
        try:
            #case where the table isn't found
            if len(table) == 0:   
                rows.append([self.tracker_NSN,normalized_NSN,'','','','',''])           
            elif len(table) == 1:
                #retrieves the multiple rows in the table, indicating all prior and current
                #manufacturers of the part
                for i in table[0].find_all('tr')[1:]:
                    row = []
                    row.append(self.tracker_NSN)
                    row.append(normalized_NSN)
                    for k in i.find_all('td')[:5]:
                        row.append(k.text.replace('\xa0',''))
                    rows.append(row)
            else:
                #if, for some reason there are multiple tables, return nothing
                rows.append([self.tracker_NSN,normalized_NSN,'','','','',''])
            return rows
        except:
            return [[self.tracker_NSN,normalized_NSN,'','','','','']]

class CAGE_frame():
    def __init__(self, input_file):
        self.file = input_file
        self.rows = []
        self.columns = ['Tracker Code',
                   'Cage Code',
                   'Company Name',
                   'Address 1','Address 2',
                   'City',
                   'State',
                   'Zip',
                   'Country',
                   'Status Code',
                   'Type Code']
        
    def read_file(self):
        if '.xlsx' not in self.file:
            return False 
        else:
            frame = pd.read_excel(self.file)
            return_frame = pd.DataFrame()
            if 'CAGE' in frame.columns:
                CAGE_codes = frame['CAGE']
                row = []
                for code in list(dict.fromkeys(CAGE_codes)):
                    table = get_CAGE(code).table
                    if table == None:
                        row.append(code)
                        for k in range(10):
                            row.append('')
                        self.rows.append(row)
                        row = []
                    else:
                        row.append(code)
                        for i in table.find_all('td'):
                            row.append(i.text)
                        self.rows.append(row)
                        row = []
                    
                for j in self.rows:
                    return_frame = return_frame.append([j],ignore_index = True)
                
                self.out_file = self.file.replace('.xlsx','')
                self.out_file = self.out_file+'_out.xlsx'
                return_frame = pd.DataFrame(self.rows, columns = self.columns)
                return_frame.to_excel(self.out_file, index = False)
                return True
            else:
                return False 
        
        
class get_CAGE():
    
    def __init__(self,code):
        self.site =  r'http://www.govcagecodes.com/?code='
        self.final = r'&company=#results'
        self.code = code
        self.table = self.getReq(self.code)
    

    def getReq(self, code):
        http = self.site + code + self.final
        get = requests.get(http)
        source = get.text
        
        soup = BeautifulSoup(source,'lxml')
        try:
            table = soup.find('table',{'id':'rt'})
            table = table.find('tbody')
        except:
            table = None
        return table
    

root = Tk()
NSN_TK_V2(master = root)
root.title("Write NSN/CAGE Codes to Excel File")
root.mainloop()
    
