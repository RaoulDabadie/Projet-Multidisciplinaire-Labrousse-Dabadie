# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 15:36:51 2021

@author: Matteo & Raoul
"""
import tkinter as tk
from tkinter import ttk

from Class_CM110 import CM110
from laser_515 import Laser_515
from translation_stage import Stage
from filter_wheel import Wheel
import camera

from Fonctions_etapes import Etapes
from Data_processing import Image_processing, Scattering_data, Plot_scattering_data

import threading
import multiprocessing

from PIL import Image, ImageTk
import time
import datetime

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
from windows_setup import configure_path

try:
    configure_path()
except ImportError:
    configure_path = None
    
    
class Interface_Instrument:
    def __init__(self,  window):
        '''
        Construction de la fenetre tkinter

        Parameters
        ----------
        window : tk.Tk()
            Fenetre de base qui englobe toutes les autres fenetres.

        '''
        #Définition des variables 
        
        self.var=4  #Variable permettant la sauvegarde des images
        self.var_open = 0   #Permet de savoir si la caméra a été allumée
        self.var_plot=0     #Permet de savoir si une image a été générée
        self.phase_plot=0   #Permet de savoir si la fonction de phase a été générée
        
        ##########################################################
        #Définition de la fenêtre principale
        self.window = window
        
        #Barre menu
        menuBar = tk.Menu(window)
        File_menu = tk.Menu(menuBar, tearoff=0,bg='#EDF2F5')
        File_menu.add_command(label="Exit", command=lambda:[disconnectAll(self),window.quit(),window.destroy()])
        menuBar.add_cascade(label="File", menu=File_menu)
        window.config(menu=menuBar)
        
        #Fermer la fenêtre
        window.protocol("WM_DELETE_WINDOW", lambda:[disconnectAll(self), window.quit(), window.destroy()])
    
        #Création des deux onglets
        tabControl = ttk.Notebook (window)
        tab1 = ttk.Frame (tabControl)
        tab2 = ttk.Frame (tabControl)
        tabControl.add (tab1, text = 'Tests')
        tabControl.add (tab2, text = 'Steps')
        tabControl.pack(expand = 1, fill ="both")
        
        ##########################################################
        #Définition des frames principales des deux onglets
        
        self.frame_up = tk.Frame(tab1,bg='#EDF2F5')
        self.frame_up.grid(row=1,column=0)
        self.frame_up1 = tk.Frame(self.frame_up,bg='#EDF2F5')
        self.frame_up1.grid(row=1,column=0)
        self.frame_up2 = tk.Frame(self.frame_up,bg='#EDF2F5', highlightthickness=3, highlightbackground='black')
        self.frame_up2.grid(row=1,column=1)

        self.frame_down = tk.Frame(tab1,bg='#EDF2F5')
        self.frame_down.grid(row=1,column=1)
    
    ############################################################################################################################################################################
        #ONGLET TEST
        
        #definition des objets de l'application (boites de texte, titres et boutons)
        
        #Nom de l'interface
        self.box_nom = tk.Entry(self.frame_up1)
        self.box_nom.insert(0, "Interface");
        self.label_nom = tk.Label(self.frame_up1, text = 'File name',bg='#EDF2F5')

        #Monochromateur
        self.label_mono = tk.Label(self.frame_up1, text = 'Monochromator',font=("Aharoni", 9,'bold'),bg='#EDF2F5')
        self.box_wl = tk.Entry(self.frame_up1)
        self.box_wl.insert(0,'450')
        self.label_wl = tk.Label(self.frame_up1, text="Wavelength (nm)",bg='#EDF2F5')
        
        #Laser
        self.label_laser = tk.Label(self.frame_up1, text = 'Laser',font=("Aharoni", 9,'bold'),bg='#EDF2F5')
        
        #Platine
        self.label_platine = tk.Label(self.frame_up1, text = 'Translation stage',font=("Aharoni", 9,'bold'),bg='#EDF2F5')
        self.box_stage = tk.Entry(self.frame_up1)
        self.box_stage.insert(0,'8000')
        self.label_stage = tk.Label(self.frame_up1, text="Camera position",bg='#EDF2F5')
        
        #Filtre
        self.label_filtre = tk.Label(self.frame_up1, text = 'Filter',font=("Aharoni", 10,'bold'),bg='#EDF2F5')
        self.choixfiltre = tk.Label(self.frame_up1, text = "Filter choice",bg='#EDF2F5')
        listefiltres = ["1","2","3","4","5","6"]
        self.combofiltres = ttk.Combobox(self.frame_up1, values = listefiltres, state="readonly")
        self.combofiltres.current(0)
        
        #Cameras
        self.choixcam = tk.Label(self.frame_up2, text = "Camera choice",font=("Aharoni", 9,'bold'), bg='#EDF2F5', relief='raised')
        listecam = ["Camera VIS","Camera FLIR", "Camera Hama", "Camera lucid"]
        self.combocam = ttk.Combobox(self.frame_up2, values = listecam, state="readonly")
        self.combocam.current(0)
        
        self.box_frame_number = tk.Entry(self.frame_up2)
        self.box_frame_number.insert(0, "100")
        self.label_frame_number = tk.Label(self.frame_up2, text = 'Frame number',font=("Aharoni", 9),bg='#EDF2F5')
     
        self.box_integration_time = tk.Entry(self.frame_up2)
        self.box_integration_time.insert(0, "10000")
        self.label_integration_time = tk.Label(self.frame_up2, text = 'Integration time (µsec)',font=("Aharoni", 9),bg='#EDF2F5')
        
        self.box_gain = tk.Entry(self.frame_up2)
        self.box_gain.insert(0, "1")
        self.label_gain = tk.Label(self.frame_up2, text = 'Gain',font=("Aharoni", 9),bg='#EDF2F5')
        
        
        #Création d'espaces
        
        self.space2 = tk.Label(self.frame_up1,bg='#EDF2F5') 
        self.space2.grid(row=2,column=0) 
        self.space4 = tk.Label(self.frame_up1,bg='#EDF2F5') 
        self.space4.grid(row=4,column=0) 
        self.space8 = tk.Label(self.frame_up1,bg='#EDF2F5') 
        self.space8.grid(row=8,column=0)
        self.space10 = tk.Label(self.frame_up1,bg='#EDF2F5') 
        self.space10.grid(row=10,column=0)
        self.space12 = tk.Label(self.frame_up1,bg='#EDF2F5') 
        self.space12.grid(row=12,column=0)
        self.space14 = tk.Label(self.frame_up1,bg='#EDF2F5') 
        self.space14.grid(row=14,column=0)
        self.space17 = tk.Label(self.frame_up1,bg='#EDF2F5') 
        self.space17.grid(row=17,column=0)
        self.space19 = tk.Label(self.frame_up1,bg='#EDF2F5') 
        self.space19.grid(row=19,column=0)
        self.spacecol = tk.Label(self.frame_up1,bg='#EDF2F5') 
        self.spacecol.grid(column=3,ipadx=20,ipady=3)

        self.space3 = tk.Label(self.frame_up2,bg='#EDF2F5') 
        self.space3.grid(row=2,column=0) 
        self.space9 = tk.Label(self.frame_up2,bg='#EDF2F5') 
        self.space9.grid(row=3,column=0)
        self.space16 = tk.Label(self.frame_up2,bg='#EDF2F5') 
        self.space16.grid(row=8,column=0)

        ##########################################################
        #APPEL DES DIFFERENTES CLASSES
        
        Monochromator = CM110('COM3')
        #Laser = Laser_515('COM4')
        Stage1 = Stage('COM6')
        #Filter = Wheel('COM5')
        #Camera_VIS = camera.camera_VIS()
        Camera_FLIR = camera.camera_flir()
        Camera_Hama = camera.camera_hama()
        #Camera_Lucid = camera.camera_lucid()
        etp = Etapes(Monochromator, Stage1)
        
        
        ##########################################################
        #FONCTIONS ASSOCIEES AUX BOUTONS
        on = ImageTk.PhotoImage(file = "on1.png") #Image ON pour le bouton de connexion des instruments
        off = ImageTk.PhotoImage(file = "off1.png")  #Image OFF pour le bouton de connexion des instruments
        
        #MONOCHROMATEUR
        
        #Connexion
        self.is_on = True #booleen pour la connexion du mono
        self.connexion = tk.Label(self.frame_up1, text = "Connected", fg = "green", font = ("Helvetica", 8))

        def mono_connect(): 
            '''
            Permet de connecter ou déconnecter le monochromateur en cliquant sur l'image ON/OFF'


            '''
            global is_on   
            
            if (self.is_on): 
                self.on_button.config(image = off) 
                self.connexion.config(text = "Disconnected", fg = "grey", font=("Helvetica", 7)) 
                Monochromator.DISCONNECT()
                self.is_on = False
            else: 
                self.on_button.config(image = on) 
                self.connexion.config(text = "Connecté", fg = "green") 
                
                Monochromator.CONNECT('COM3')
                self.is_on = True
          
        #Bouton connexion monochromateur
        self.on_button = tk.Button(self.frame_up1, image = on, bd = 0, command = mono_connect)
        
        
        def mono_GOTO(self, wl):
            '''
            Bouge le monochromateur à la longueur d'onde entrée par l'utilisateur 
            
            Parameters
            ----------
            wl : Integer
            Longueur d'onde souhaitée par l'utilisateur

            '''
            if Monochromator.Test_WL(wl):
                self.box_wl.config(bg="white")
                Monochromator.GOTO(wl)
               
            else: 
                self.box_wl.delete(0,"end")
                self.box_wl.insert(0,'WL not in [0; 65535]')
                self.box_wl.config(bg="red")
                
        #Bouton Single Wavelength               
        self.singleWL = tk.Button (self.frame_up1, text="Single WL", command=lambda:[mono_GOTO(self,int(self.box_wl.get()))])
        
          
        #PLATINE
        
        #Connexion
        self.st_connexion = tk.Label(self.frame_up1, text = "Connected", fg = "green", font = ("Helvetica", 8)) 
        self.st_is_on = True #booleen pour la connexion de la platine
        
        def stage_connect(): 
            '''
            Permet de connecter ou déconnecter la platine en cliquant sur l'image ON/OFF'

            '''
            global st_is_on
               
            if (self.st_is_on): 
                self.st_on_button.config(image = off) 
                self.st_connexion.config(text = "Disconnected",  fg = "grey", font=("Helvetica", 7)) 
                Stage1.DISCONNECT()
                self.st_is_on = False
            else: 
                self.st_on_button.config(image = on) 
                self.st_connexion.config(text = "Connected", fg = "green") 
                Stage1.CONNECT("COM6")
                self.st_is_on = True
        
        #Bouton connexion platine
        self.st_on_button = tk.Button(self.frame_up1, image = on, bd = 0, command = stage_connect)
        
        
        def stage_Disp(self, pos):
            '''
            Déplace la platine à la position entrée par l'utilisateur

            Parameters
            ----------
            pos : Integer
            Position de la platine souhaitée par l'utilisateur
            '''
            
            if Stage1.Test_displacement(pos):
                self.box_stage.config(bg="white")
                Stage1.pos_translation(int(self.box_stage.get()))     
            else: 
                self.box_stage.delete(0,"end")
                self.box_stage.insert(0,'Position must be < 14000')
                self.box_stage.config(bg="red")
              
        #Boutons pour déplacer et calibrer la platine        
        self.stage = tk.Button (self.frame_up1, text="Platine Displacement", command=lambda:[stage_Disp(self,int(self.box_stage.get()))])
        self.stagecal = tk.Button (self.frame_up1, text="Calibration", command=lambda:[Stage1.cal()])
        
        
        #ROUE
        
        #Connexion
        self.fl_connexion = tk.Label(self.frame_up1, text = "Connected", fg = "green", font = ("Helvetica", 8)) 
        self.fl_is_on = True #booleen pour la connexion du filtre
        
        # def filter_connect(): 
        #     global fl_is_on
               
        #     if (self.fl_is_on): 
        #         self.fl_on_button.config(image = off) 
        #         self.fl_connexion.config(text = "Déconnecté", fg = "grey") 
        #         Filter.DISCONNECT()
        #         self.fl_is_on = False
        #     else: 
        #         self.fl_on_button.config(image = on) 
        #         self.fl_connexion.config(text = "Connecté", fg = "green") 
        #         Filter.CONNECT("COM5")
        #         self.fl_is_on = True
        
        #Bouton connexion filtre
        self.fl_on_button = tk.Button(self.frame_up1, image = on, bd = 0, command = print("Roue déconnectée")) 
        
        #Bouton rotation filtre
        self.filter = tk.Button (self.frame_up1, text="Filter", command=lambda:[print("pas de filtre")])

        
        #LASER
        
        #Boutons radios pour allumer ou éteindre le laser
        value = tk.IntVar()
        value.set(2)

        def laser():
            '''
            Allume ou éteint le laser
            '''
            if (value.get() ==1):
                print("LASER ON")
                #Laser.start()
            elif (value.get() ==2):
                print("LASER OFF")
                #Laser.stop()
                
        self.b1 = tk.Radiobutton(self.frame_up1, text="ON", bg='#EDF2F5', variable=value, value=1, command= laser)
        self.b2 = tk.Radiobutton(self.frame_up1, text="OFF", bg='#EDF2F5', variable=value, value=2, command= laser)
        
        
        #CAMERAS
        
        def camera_On(self):
            '''
            Allume la caméra choisie par l'utilisateur
            '''
            if (self.combocam.current()==0):
               # Camera_VIS.open_cam()
                print("Cam")
            elif (self.combocam.current() == 1):
                Camera_FLIR.open_cam()
            elif (self.combocam.current() == 2):
                Camera_Hama.open_cam()
            elif (self.combocam.current() == 3):
                #self.Camera_Lucid.open_cam()
                print("Cam")
            self.var_open=1
            
        self.cam = tk.Button (self.frame_up2, text="ON", command=lambda:[camera_On(self)]) #bouton allumer camera 
      
        def camera_Off(self):
            '''
            Eteint la caméra choisie par l'utilisateur
            '''
            if (self.combocam.current()==0):
                #Camera_VIS.close_cam()
                print("Cam")
            elif (self.combocam.current() == 1):
                Camera_FLIR.close_cam()
            elif (self.combocam.current() == 2):
                Camera_Hama.close_cam()
            elif (self.combocam.current() == 3):
                #Camera_Lucid.close_cam()
                print("Cam")
                
        self.cam_off = tk.Button (self.frame_up2, text="OFF", command=lambda:[camera_Off(self)]) #bouton éteindre camera 

        
        def Plot_Image(self):
            '''
            Affiche l'image de la caméra sélectionnée
            '''
            self.diameter = 20e-6   #Diamètre de la particule
            self.m = 1.52+0.002j    #Indice optique de la particule
            self.focal_length = 16e-3   #Longueur focale
            self.Lambda = int(self.box_wl.get())    #Longueur d'onde du laser
            self.var_plot =1      
            
            if ((int(self.box_frame_number.get()) > 0) and (int(self.box_integration_time.get()) > 0) and (int(self.box_gain.get()) > 0) ):
                if (self.var_open == 1 ):
                    
                    if (self.combocam.current()==0):
                        self.var=0
                        #mat_VIS, pixel_size = Camera_VIS.Get_multi(int(self.box_frame_number.get()),np.array([int(self.box_integration_time.get())]),int(self.box_gain.get()),dark = False )
                        #self.correction = 255*(mat_VIS-np.min(mat_VIS))/(np.max(mat_VIS)-np.min(mat_VIS)).astype(float)
                        
                    elif (self.combocam.current() == 1):
                        self.var=1
                        mat_FLIR, self.pixel_size = Camera_FLIR.Get_multi(int(self.box_frame_number.get()),np.array([int(self.box_integration_time.get())]),int(self.box_gain.get()),dark = False )
                        self.correction = 255*(mat_FLIR-np.min(mat_FLIR))/(np.max(mat_FLIR)-np.min(mat_FLIR)).astype(float)
                    
                    elif (self.combocam.current() == 2):
                        self.var=2
                        mat_Hama, self.pixel_size = Camera_Hama.Get_multi(int(self.box_frame_number.get()),int(self.box_integration_time.get()),int(self.box_gain.get()),dark = False )
                        self.correction = 255*(mat_Hama-np.min(mat_Hama))/(np.max(mat_Hama)-np.min(mat_Hama)).astype(float)
                    
                    elif (self.combocam.current() == 3):
                        self.var=3
                        #mat_Lucid, pixel_size = Camera_Lucid.Get_multi(int(self.box_frame_number.get()),np.array([int(self.box_integration_time.get())]),int(self.box_gain.get()),dark = False )
                        #self.correction = 255*(mat_Lucid-np.min(mat_Lucid))/(np.max(mat_Lucid)-np.min(mat_Lucid)).astype(float)
                        
                    plt.ioff()
                    self.fig = plt.figure(figsize = (5,5))
                    self.fig.suptitle("Image caméra")
                    plt.axis('off')
                    plt.imshow(self.correction)

                    canvas = FigureCanvasTkAgg(self.fig, master=self.frame_down)
                    canvas.draw()
                    canvas.get_tk_widget().grid(row = 0, column = 0)
                    
                else:
                    print("La caméra n'est pas allumée")
            else:
                 print("Les paramètres rentrés ne sont pas valides")
              
        
        #TEST THREADING
        #t1 = threading.Thread(target=Plot_Image(self)) 
        #self.multi= tk.Button (self.frame_up2, text="Show Image", command=threading.Thread(target=Plot_Image, args=[self]).start) #get multi Camera
        #test = multiprocessing.Process(target=Plot_Image, args=[self])
        #self.multi= tk.Button (self.frame_up2, text="Show Image", command=test.start()) #get multi Camera
        
        #Bouton pour afficher l'image de la caméra
        self.multi= tk.Button (self.frame_up2, text="Show Image", command=lambda:[Plot_Image(self)]) 
             
        
        def Plot_Phase(self):
            '''
            Affiche la fonction de phase de l'image générée par la caméra
            '''
            if (self.var != 4):

                self.phase_plot =1
                self.fig1 = plt.figure(figsize = (5,5))
                self.fig1.suptitle("Fonction de phase")
                canvas1 = FigureCanvasTkAgg(self.fig1, master=self.frame_down)
                canvas1.draw()
                canvas1.get_tk_widget().grid(row = 1, column = 0)
                
                ip = Image_processing(self.correction, self.Lambda, self.pixel_size, self.focal_length)
                data = ip.image_to_datas()
                sd = Scattering_data(data, self.diameter, self.Lambda, self.m, self.focal_length, mode = 2 , backscattering = True)
                teta, final_data, theory_val = sd.data_to_pfunction()
    
                self.subplot1=self.fig1.add_subplot(1,1,1)
                self.subplot1.plot(np.rad2deg(teta), final_data)
                
            else:
                print("Aucune image n'a été générée")
        
        #Bouton pour afficher la fonction de phase
        self.f_phase=tk.Button (self.frame_up2, text="Show Phase fonction", command=lambda:[Plot_Phase(self)])        

        
        def sav_im(self,var):
            '''
            Sauvegarde l'image générée en dernier

            Parameters
            ----------
            var : Integer
                Permet d'identifier le type d'image sauvegardée
            '''
            string_date(self)
            
            #Création du dossier Camera_images permettant de stocker les images sauvegardées 
            if not os.path.exists('Camera_images'):
               os.mkdir('Camera_images/') 

            
            if var ==0 :
                self.inputs = 'Caméra VIS\t\t ' + '\nWavelength [um]\t\t' + str(int(self.box_wl.get())) + '\nFrame number\t\t'+ str(int(self.box_frame_number.get()))+ '\nIntegration time [ms]\t\t' + str(int(self.box_integration_time.get()))+'\nGain\t\t'+ str(int(self.box_gain.get()))
                save_all(self)
                print("Image VIS sauvegardée dans le fichier Camera_images")
            
            elif var ==1 :
                self.inputs = 'Caméra FLIR\t\t ' + '\nWavelength [um]\t\t' + str(int(self.box_wl.get())) + '\nFrame number\t\t'+ str(int(self.box_frame_number.get()))+ '\nIntegration time [ms]\t\t' + str(int(self.box_integration_time.get()))+'\nGain\t\t'+ str(int(self.box_gain.get()))
                save_all(self)
                print("Image FLIR sauvegardée dans le fichier Camera_images")
                
            elif var == 2:
                self.inputs = 'Caméra Hamamatsu\t\t ' + '\nWavelength [um]\t\t' + str(int(self.box_wl.get())) + '\nFrame number\t\t'+ str(int(self.box_frame_number.get()))+ '\nIntegration time [ms]\t\t' + str(int(self.box_integration_time.get()))+'\nGain\t\t'+ str(int(self.box_gain.get()))
                save_all(self)
                print("Image Hamamatsu sauvegardée dans le fichier Camera_images")
                
            elif var ==3:
                self.inputs = 'Caméra Lucid\t\t ' + '\nWavelength [um]\t\t' + str(int(self.box_wl.get())) + '\nFrame number\t\t'+ str(int(self.box_frame_number.get()))+ '\nIntegration time [ms]\t\t' + str(int(self.box_integration_time.get()))+'\nGain\t\t'+ str(int(self.box_gain.get()))
                save_all(self)
                print("Image Lucid sauvegardée dans le fichier Camera_images")
                
            else:
                print("Aucune image n'a été générée")
        
        #Bouton pour sauvegarder l'image et la fonction de phase
        self.save=tk.Button(self.frame_up2, text="Save Image", command=lambda:[sav_im(self, self.var)])
        
        
        def save_all(self):
            '''
            Gère les paramètres de sauvegarde dans un dossier avec un fichier texte contenant les paramètres de l'image

            '''
            string_date(self)
            create_folder(self)
            
            if (self.phase_plot==0):
                #génération de la fonction de phase si celle-ci n'a pas été générée
                self.fig1 = plt.figure(figsize = (5,5))
                self.fig1.suptitle("Fonction de phase")
                ip = Image_processing(self.correction, self.Lambda, self.pixel_size, self.focal_length)
                data = ip.image_to_datas()
                sd = Scattering_data(data, self.diameter, self.Lambda, self.m, self.focal_length, mode = 2 , backscattering = True)
                teta, final_data, theory_val = sd.data_to_pfunction()
                self.subplot1=self.fig1.add_subplot(1,1,1)
                self.subplot1.plot(np.rad2deg(teta), final_data)
            

            np.save(self.adress_file + 'image', self.correction)
            np.save(self.adress_file + 'image', self.subplot1)

            self.fig.savefig(self.adress_file+ 'Camera_Image')
            self.fig1.savefig(self.adress_file+ 'Phase_Fonction')
            
            txt_file = open(self.adress_file+"inputs.txt", "w")
            txt_file.write(self.inputs)
            txt_file.close()
            self.phase_plot=0
        
        
        def string_date(self):
            '''
            Genere un texte comportant la date et l'heure pour le ou les fichiers à enregistrer
            Le début du nom de chaque fichier ce fait avec ce texte de type: jour_mois_année_heure_minute_seconde

            '''
            date = datetime.datetime.now()
            
            year = '{:02d}'.format(date.year)
            month = '{:02d}'.format(date.month)
            day = '{:02d}'.format(date.day)
            hour = '{:02d}'.format(date.hour)
            minute = '{:02d}'.format(date.minute)
            sec = '{:02d}'.format(date.second)
            
            self.str_date = str(year)+"_"+str(month)+"_"+str(day)+"_"+str(hour)+"_"+str(minute)+"_"+str(sec)
            
            return self.str_date
        
        
        def create_folder(self):
            '''
            Cettte fonction crée un dossier permettant d'enregistrer les images'

            '''
            os.mkdir('Camera_images/'+ self.str_date)
            self.adress_file = 'Camera_images/'+ self.str_date+'/'
        
        
        def disconnectAll(self):
            '''
            Déconnecte tous les instruments. Utilisé lors de la fermeture de l'interface.
            '''
            Monochromator.DISCONNECT()
            Stage1.DISCONNECT()
            #Laser.stop()
            #Laser.DISCONNECT()
            #Camera_VIS.close_cam() 
            Camera_FLIR.close_cam() 
            Camera_Hama.close_cam()
            #Camera_Lucid.close_cam()
         
            
        ##########################################################
        #Placement des éléments dans une grille
        
        #TITRE
        self.box_nom.grid(row=0,column=2, sticky='n')   #boîte nom
        self.label_nom.grid(row=0,column=1, sticky='n') #text nom
        
        #ELEMENTS MONOCHROMATEUR 
        self.connexion.grid(row=3, column=2, sticky='e') #affichage connecté/déconnecté
        self.on_button.grid(row=3, column=2, sticky='w') #bouton connexion/déconnexion
        self.label_mono.grid(row=3,column=1, sticky='w') #nom colonne monochromateur
        self.box_wl.grid(row=5,column=2)    #longueur d'onde
        self.label_wl.grid(row=5,column=1, sticky='e')  #longueur d'onde
        self.singleWL.grid(row=7,column=2,sticky='e')  #bouton GOTO
        
        #ELEMENTS LASER
        self.label_laser.grid(row=9,column=1, sticky='w') #nom colonne laser
        self.b1.grid(row=11,column=1)    #allume le laser
        self.b2.grid(row=11,column=2, sticky='w')  #éteint le laser
        
        #ELEMENTS PLATINE
        self.st_connexion.grid(row=13, column=2, sticky='e') #platine connectée/déconnectée
        self.st_on_button.grid(row=13, column=2, sticky='w') #bouton pour connecter/déconnecter platine
        
        self.label_platine.grid(row=13,column=1, sticky='w') #nom colonne platine
        self.box_stage.grid(row=15,column=2)    #stage
        self.label_stage.grid(row=15,column=1, sticky='e')  #position de la platine
        self.stage.grid(row=16,column=2,sticky='e') #declenchement du déplacement
        self.stagecal.grid(row=16, column = 1, sticky='s') #calibration platine
        
        #ELEMENTS FILTRE
        self.fl_connexion.grid(row=18, column=2, sticky='e')    #roue connectée/déconnectée
        self.fl_on_button.grid(row=18, column=2, sticky='w')    #bouton pour connecter/déconnecter roue
        
        self.label_filtre.grid(row=18,column=1, sticky='w') #nom colonne platine
        self.choixfiltre.grid(row=20,column = 1,sticky = 'w')
        self.combofiltres.grid(row=20,column = 2,sticky = 'w')
        self.filter.grid(row=21,column = 2,sticky = 'e') 
        
        #ELEMENTS CAMERA
        
        self.choixcam.grid(row=1,column = 0,sticky = 'w')
        self.combocam.grid(row=1,column = 1,sticky = 'w')
        self.cam.grid(row=1,column=2,sticky = 'e',ipadx=17,ipady=2)   #Bouton allumer 
        self.cam_off.grid(row=2,column=2,sticky = 'e',ipadx=17,ipady=2) #Bouton éteindre
        self.box_frame_number.grid(row=4,column=1, sticky='e')   #frame number
        self.label_frame_number.grid(row=4,column=0, sticky='e') 
        self.box_integration_time.grid(row=5,column=1, sticky='e')  #integration time 
        self.label_integration_time.grid(row=5,column=0, sticky='e')
        self.box_gain.grid(row=6,column=1, sticky='e')  #Gain
        self.label_gain.grid(row=6,column=0, sticky='e')
        self.multi.grid(row=7,column=1,sticky = 'e',ipadx=15.5,ipady=2)   #Bouton afficher image
        self.save.grid(row=8,column=1,sticky = 'e',ipadx=18,ipady=2)    #bouton save
        self.f_phase.grid(row=9,column=1,sticky = 'e',ipadx=18,ipady=2) #Bouton fonction de phase
        
        
  ############################################################################################################################################################################
        #ONGLET ETAPES
        
        #FRAMES 
        self.frame_up20 = tk.Frame(tab2,bg='#EDF2F5')
        self.frame_up20.grid(row=1,column=0)
        self.frame_up21 = tk.Frame(self.frame_up20,bg='#EDF2F5')
        self.frame_up21.grid(row=0,column=0)
        self.frame_up22 = tk.Frame(self.frame_up20,bg='#EDF2F5')
        self.frame_up22.grid(row=0,column=1)
        self.frame_down20 = tk.Frame(tab2,bg='#EDF2F5')
        self.frame_down20.grid(row=1,column=1)
        
        #definition des objets de l'application (boites de texte, titres et boutons)
        
        #Retrodiffusion and Dark
        self.label_retro = tk.Label(self.frame_up21, text ='Retrodiffusion and Dark',font=("Aharoni", 10,'bold'),bg='#EDF2F5')
        
        self.label_gain21 = tk.Label(self.frame_up21, text ='Gain',font=("Aharoni", 10),bg='#EDF2F5')
        self.box_gain21 = tk.Entry(self.frame_up21)
        self.box_gain21.insert(0, "1")
        
        self.label_integration_time21 = tk.Label(self.frame_up21, text ='Integration time (µs)',font=("Aharoni", 10),bg='#EDF2F5')
        self.box_integration_time21 = tk.Entry(self.frame_up21)
        self.box_integration_time21.insert(0, "1000")
        
        self.label_wldark1 = tk.Label(self.frame_up21, text ='Start Wavelength(nm)',font=("Aharoni", 10),bg='#EDF2F5')
        self.box_wldark1 = tk.Entry(self.frame_up21)
        self.box_wldark1.insert(0, "200")
        
        self.label_wldark2 = tk.Label(self.frame_up21, text ='End Wavelength(nm)',font=("Aharoni", 10),bg='#EDF2F5')
        self.box_wldark2 = tk.Entry(self.frame_up21)
        self.box_wldark2.insert(0, "300")
        
        self.label_step = tk.Label(self.frame_up21, text ='Step (nm)',font=("Aharoni", 10),bg='#EDF2F5')
        self.box_step = tk.Entry(self.frame_up21)
        self.box_step.insert(0, "10")
        
        
        #Hologramme and Reference
        self.label_holo = tk.Label(self.frame_up21, text ='Hologramme and Reference',font=("Aharoni", 10,'bold'),bg='#EDF2F5')
        
        self.label_gain22 = tk.Label(self.frame_up21, text ='Gain',font=("Aharoni", 10),bg='#EDF2F5')
        self.box_gain22 = tk.Entry(self.frame_up21)
        self.box_gain22.insert(0, "2")
        
        self.label_integration_time22 = tk.Label(self.frame_up21, text ='Integration time (µs)',font=("Aharoni", 10),bg='#EDF2F5')
        self.box_integration_time22 = tk.Entry(self.frame_up21)
        self.box_integration_time22.insert(0, "2000")
        
        
        #Laser Spot
        self.label_laser_spot = tk.Label(self.frame_up21, text ='Laser Spot',font=("Aharoni", 10,'bold'),bg='#EDF2F5')
        
        self.label_gain23 = tk.Label(self.frame_up21, text ='Gain',font=("Aharoni", 10),bg='#EDF2F5')
        self.box_gain23 = tk.Entry(self.frame_up21)
        self.box_gain23.insert(0, "3")
        
        self.label_integration_time23 = tk.Label(self.frame_up21, text ='Integration time (µs)',font=("Aharoni", 10),bg='#EDF2F5')
        self.box_integration_time23 = tk.Entry(self.frame_up21)
        self.box_integration_time23.insert(0, "3000")

        
        #Création d'espaces Onglet Test
        self.space20 = tk.Label(self.frame_up21,bg='#EDF2F5') 
        self.space20.grid(row=8,column=0)  
        self.space21 = tk.Label(self.frame_up21,bg='#EDF2F5') 
        self.space21.grid(row=14,column=0) 
        self.spacecol1 = tk.Label(self.frame_up21,bg='#EDF2F5') 
        self.spacecol1.grid(column=3,ipadx=20,ipady=3)
        self.space221 = tk.Label(self.frame_up22,bg='#EDF2F5')
        self.space221.grid(row=1,column=0) 
        
        ##########################################################
        #Fonctions liées à l'onglet Etapes
        
        #Initialisation tableau 
        tab_steps = [[int(self.box_gain21.get()),int(self.box_integration_time21.get()), int(self.box_wldark1.get()), int(self.box_wldark2.get()), int(self.box_step.get())], [int(self.box_gain22.get()),int(self.box_integration_time22.get())], [int(self.box_gain22.get()),int(self.box_integration_time22.get())], [int(self.box_gain23.get()),int(self.box_integration_time23.get())], [int(self.box_gain21.get()),int(self.box_integration_time21.get()), int(self.box_wldark1.get()), int(self.box_wldark2.get()), int(self.box_step.get())]]
        #print(tab_steps)
        
        #Liste étapes
        list_steps = tk.Listbox(self.frame_up22, selectmode='single')
        list_steps.insert(0, "Retrodiffusion")
        list_steps.insert(1, "Hologramme")
        list_steps.insert(2, "Ref hologramme")
        list_steps.insert(3, "Spot laser")
        list_steps.insert(4, "Dark")
        list_steps.grid(row=2,column=1,sticky = 'n',)
        
        
        def up(self):
            '''
            Permet de remonter un élément dans la liste d'étapes
            '''
            if (list_steps.curselection()):
                place = list_steps.curselection()[0]
                mot = list_steps.get(list_steps.curselection()[0])
                case = tab_steps[list_steps.curselection()[0]]
                
                list_steps.delete(list_steps.curselection()[0])
                del tab_steps[place]
                list_steps.insert(place-1, mot)
                tab_steps.insert(place-1, case)
                list_steps.selection_set(place-1)
                print(tab_steps)     
            else:
                print("Veuillez sélectionner une étape dans la liste")
        
        self.UP= tk.Button (self.frame_up22, text="↑", command=lambda:[up(self)]) #Bouton pour monter l'étape dans la liste

            
        def down(self):
            '''
            Permet de descendre un élément dans la liste d'étapes

            '''
            if (list_steps.curselection()):
                place = list_steps.curselection()[0]
                mot = list_steps.get(list_steps.curselection()[0])
                case = tab_steps[list_steps.curselection()[0]]
                
                list_steps.delete(list_steps.curselection()[0])
                del tab_steps[place]
                list_steps.insert(place+1, mot)
                tab_steps.insert(place+1, case)
                list_steps.selection_set(place+1)
                print(tab_steps)
                
            else:
                print("Veuillez sélectionner une étape dans la liste")

        self.DOWN= tk.Button (self.frame_up22, text="↓", command=lambda:[down(self)]) #Bouton pour monter l'étape dans la liste


        def addR(self):
            '''
            Ajoute l'étape de rétrodiffusion dans la liste
            '''
            if ((int(self.box_gain21.get()) > 0) & (int(self.box_integration_time21.get())>0) & (int(self.box_wldark1.get())>0) & (int(self.box_wldark2.get())>0) & (int(self.box_step.get())>0)) :
                list_steps.insert('end', "Retrodiffusion")
                tab_steps.append([int(self.box_gain21.get()),int(self.box_integration_time21.get()), int(self.box_wldark1.get()), int(self.box_wldark2.get()), int(self.box_step.get())])
                print(tab_steps)
            else:
                print("Paramètre non valide")
                
        self.add_retro = tk.Button (self.frame_up21, text="✚ retrodiffusion", command=lambda:[addR(self)])  #bouton pour ajouter étape rétrodiff
        
                
        def addD(self):
            '''
            Ajoute l'étape de dark dans la liste
            '''
            if ((int(self.box_gain21.get()) > 0) & (int(self.box_integration_time21.get())>0) & (int(self.box_wldark1.get())>0) & (int(self.box_wldark2.get())>0) & (int(self.box_step.get())>0)) :
                list_steps.insert('end', "Dark")
                tab_steps.append([int(self.box_gain21.get()),int(self.box_integration_time21.get()), int(self.box_wldark1.get()), int(self.box_wldark2.get()), int(self.box_step.get())])
            else:
                print("Paramètre non valide")
                
        self.add_dark = tk.Button (self.frame_up21, text="✚ dark", command=lambda:[addD(self)])     #bouton pour ajouter étape dark


        def addH(self):
            '''
            Ajoute l'étape d'holographie dans la liste
            '''
            if ((int(self.box_gain22.get())>0) & (int(self.box_integration_time22.get())>0)):
                list_steps.insert('end', "Hologramme")
                tab_steps.append([int(self.box_gain22.get()),int(self.box_integration_time22.get())])
            else:
                print("Paramètre non valide")
                
        self.add_holo = tk.Button (self.frame_up21, text="✚ hologramme", command=lambda:[addH(self)])   #bouton pour ajouter étape holographie

                
        def addRef(self):
            '''
            Ajoute l'étape de référence holographie dans la liste
            '''
            if ((int(self.box_gain22.get())>0) & (int(self.box_integration_time22.get())>0)):
                list_steps.insert('end', "Ref hologramme")
                tab_steps.append([int(self.box_gain22.get()),int(self.box_integration_time22.get())])
            else:
                print("Paramètre non valide")
                
        self.add_ref = tk.Button (self.frame_up21, text="✚ reference", command=lambda:[addRef(self)]) #bouton pour ajouter étape référence
                
        
        def addS(self):
            '''
            Ajoute l'étape de spot laser dans la liste
            '''
            if ((int(self.box_gain23.get())>0) & (int(self.box_integration_time23.get())>0)):
                list_steps.insert('end', "Spot laser")
                tab_steps.append([int(self.box_gain23.get()),int(self.box_integration_time23.get())])
            else:
                print("Paramètre non valide")
                
        self.add_spot = tk.Button (self.frame_up21, text="✚ spot laser", command=lambda:[addS(self)]) #bouton pour ajouter étape spot laser


        def modif(self):
            '''
            Permet de modifier les paramètres d'une étape lorsqu'elle est sélectionnée
            '''
            if list_steps.curselection():
                if ((int(self.box_gain21.get()) > 0) & (int(self.box_integration_time21.get())>0) & (int(self.box_wldark1.get())>0) & (int(self.box_wldark2.get())) & (int(self.box_step.get())>0) & (int(self.box_gain22.get())>0) & (int(self.box_integration_time22.get())>0) & (int(self.box_gain23.get())>0) & (int(self.box_integration_time23.get())>0)):
                    if ((list_steps.get(list_steps.curselection()[0]) == "Retrodiffusion") or (list_steps.get(list_steps.curselection()[0]) == "Dark")):  
                        tab_steps[list_steps.curselection()[0]] = [int(self.box_gain21.get()),int(self.box_integration_time21.get()), int(self.box_wldark1.get()), int(self.box_wldark2.get()), int(self.box_step.get())]
                        print(tab_steps)
                    elif ((list_steps.get(list_steps.curselection()[0]) == "Hologramme") or (list_steps.get(list_steps.curselection()[0]) == "Ref hologramme")):
                        tab_steps[list_steps.curselection()[0]] = [int(self.box_gain22.get()),int(self.box_integration_time22.get())]
                        print(tab_steps)
                    elif (list_steps.get(list_steps.curselection()[0]) == "Spot laser"):
                        tab_steps[list_steps.curselection()[0]] = [int(self.box_gain23.get()),int(self.box_integration_time23.get())]
                        print(tab_steps)
                else:
                    print("Paramètre non valide")
            else:
                print("Aucune étape n'est selectionnée")
                
        self.modif= tk.Button (self.frame_up22, text="Modify", command=lambda:[modif(self)]) #Bouton pour modifier l'étape
        
        
        def delete(self):
            '''
            Supprime l'étape sélectionnée de la liste
            '''
            if list_steps.curselection():
                del tab_steps[list_steps.curselection()[0]]
                list_steps.delete(list_steps.curselection()[0])
                print(tab_steps)
            else:
                print("Aucune étape n'est selectionnée")
                
        self.supp= tk.Button (self.frame_up22, text="Delete", command=lambda:[delete(self)]) #Bouton pour supprimer l'étape de la liste

        
        def delete_all(self):
            '''
            Vide la liste d'étapes
            '''
            del tab_steps[:]
            list_steps.delete(0, 'end')
            
        self.del_all= tk.Button (self.frame_up22, text="Delete all", command=lambda:[delete_all(self)]) #Bouton pour supprimer toutes les étapes

            
        def see_param(event):
            '''
            Permet d'afficher les paramètres de l'étape sélectionnée

            Parameters
            ----------
            event : appelée lorsque l'utilisateur clique sur une étape de la liste


            '''
            selection = event.widget.curselection()[0]
            if (list_steps.get(selection) == "Retrodiffusion"):
                self.box_gain21.delete(0,'end')
                self.box_gain21.insert(0, tab_steps[selection][0])
                self.box_integration_time21.delete(0,'end')
                self.box_integration_time21.insert(0, tab_steps[selection][1])
                self.box_wldark1.delete(0,'end')
                self.box_wldark1.insert(0, tab_steps[selection][2])
                self.box_wldark2.delete(0,'end')
                self.box_wldark2.insert(0, tab_steps[selection][3])
                self.box_step.delete(0,'end')
                self.box_step.insert(0, tab_steps[selection][4])
                self.label_retro.configure(relief = 'sunken')
                self.label_retro.configure(bg = '#8CB3CB')
                self.label_holo.configure(relief = 'flat')
                self.label_holo.configure(bg = '#EDF2F5')
                self.label_laser_spot.configure(relief = 'flat')
                self.label_laser_spot.configure(bg = '#EDF2F5')
                
            elif (list_steps.get(selection) == "Dark"):
                self.box_gain21.delete(0,'end')
                self.box_gain21.insert(0, tab_steps[selection][0])
                self.box_integration_time21.delete(0,'end')
                self.box_integration_time21.insert(0, tab_steps[selection][1])
                self.box_wldark1.delete(0,'end')
                self.box_wldark1.insert(0, tab_steps[selection][2])
                self.box_wldark2.delete(0,'end')
                self.box_wldark2.insert(0, tab_steps[selection][3])
                self.box_step.delete(0,'end')
                self.box_step.insert(0, tab_steps[selection][4])
                self.label_retro.configure(relief = 'sunken')
                self.label_retro.configure(bg = '#8CB3CB')
                self.label_holo.configure(relief = 'flat')
                self.label_holo.configure(bg = '#EDF2F5')
                self.label_laser_spot.configure(relief = 'flat')
                self.label_laser_spot.configure(bg = '#EDF2F5')
                
            elif (list_steps.get(selection) == "Hologramme"):
                self.box_gain22.delete(0,'end')
                self.box_gain22.insert(0, tab_steps[selection][0])
                self.box_integration_time22.delete(0,'end')
                self.box_integration_time22.insert(0, tab_steps[selection][1])
                self.label_retro.configure(bg="#EDF2F5")
                self.label_retro.configure(relief = 'flat')
                self.label_holo.configure(relief = 'sunken')
                self.label_holo.configure(bg = '#8CB3CB')
                self.label_laser_spot.configure(relief = 'flat')
                self.label_laser_spot.configure(bg = '#EDF2F5')
                
            elif (list_steps.get(selection) == "Ref hologramme"):
                self.box_gain22.delete(0,'end')
                self.box_gain22.insert(0, tab_steps[selection][0])
                self.box_integration_time22.delete(0,'end')
                self.box_integration_time22.insert(0, tab_steps[selection][1])
                self.label_retro.configure(bg="#EDF2F5")
                self.label_retro.configure(relief = 'flat')
                self.label_holo.configure(relief = 'sunken')
                self.label_holo.configure(bg = '#8CB3CB')
                self.label_laser_spot.configure(relief = 'flat')
                self.label_laser_spot.configure(bg = '#EDF2F5')
            
            elif (list_steps.get(selection) == "Spot laser"):
                self.box_gain23.delete(0,'end')
                self.box_gain23.insert(0, tab_steps[selection][0])
                self.box_integration_time23.delete(0,'end')
                self.box_integration_time23.insert(0, tab_steps[selection][1])
                self.label_retro.configure(relief = 'flat')
                self.label_retro.configure(bg="#EDF2F5")
                self.label_holo.configure(relief = 'flat')
                self.label_holo.configure(bg = '#EDF2F5')
                self.label_laser_spot.configure(relief = 'sunken')
                self.label_laser_spot.configure(bg = '#8CB3CB')
            
                
        list_steps.bind("<<ListboxSelect>>", see_param)
        
        
        
        def start_steps():
            '''
            Lance le début de la succession des étaoes de la liste. Appel de la classe "Fonctions étapes"
            '''
            
            string_date(self)
            create_folder(self)
            i=0
            j=0

            TabWl = np.arange(int(self.box_wldark1.get()),int(self.box_wldark2.get())+1,int(self.box_step.get()))
            if (list_steps.size() > 0):
                while (i < list_steps.size()):
                    list_steps.itemconfig(i, bg = "orange")
                    
                    if ((list_steps.get(i) == "Retrodiffusion") or (list_steps.get(i) == "Dark")):
                        etp.Retrodiff(tab_steps[i][0], tab_steps[i][1])
                        for j in TabWl:
                            time.sleep(2)
                            Monochromator.GOTO(j)
                            time.sleep(2)
                            mat_Hama, self.pixel_size = Camera_Hama.Get_multi(10,tab_steps[i][1],tab_steps[i][0],dark = False )
                            self.correction = 255*(mat_Hama-np.min(mat_Hama))/(np.max(mat_Hama)-np.min(mat_Hama)).astype(float)
                            
                            #Enregistrer l'image
                            plt.ioff()
                            self.fig3 = plt.figure(figsize = (5,5))
                            self.fig3.suptitle("Image caméra Hamamatsu")
                            ax = self.fig3.add_subplot((111))
                            ax.imshow(self.correction)
                            np.save(self.adress_file + 'image', self.correction)
                            self.fig3.savefig(self.adress_file+ 'Camera_Image')
                            
                            
                    else:
                        if ((list_steps.get(i) == "Hologramme") or (list_steps.get(i) == "Ref hologramme")):
                            etp.Hologramme(tab_steps[i][0], tab_steps[i][1])
                            mat_FLIR, self.pixel_size = Camera_FLIR.Get_multi(10,np.array([tab_steps[i][1]]),tab_steps[i][0],dark = False )
                            self.correction = 255*(mat_FLIR-np.min(mat_FLIR))/(np.max(mat_FLIR)-np.min(mat_FLIR)).astype(float)
                        
                        elif (list_steps.get(i) == "Spot laser"):
                            etp.Spot_Laser(self, tab_steps[i][0], tab_steps[i][1])
                            mat_FLIR, self.pixel_size = Camera_FLIR.Get_multi(100,np.array([tab_steps[i][1]]),tab_steps[i][0],dark = False )
                            self.correction = 255*(mat_FLIR-np.min(mat_FLIR))/(np.max(mat_FLIR)-np.min(mat_FLIR)).astype(float)
                        
                        #Enregistrer l'image
                        plt.ioff()
                        fig = plt.figure(figsize = (5,5))
                        fig.suptitle("Image caméra")
                        plt.axis('off')
                        plt.imshow(self.correction)
                        np.save(self.adress_file + 'image', self.correction)
                        fig.savefig(self.adress_file+ 'Camera_Image')
                        
                    list_steps.itemconfig(i, bg = "green")
   
                    i=i+1
                print("Toutes les étapes sont terminées")
            else :
                print("Aucune étape dans la liste")
        

        self.etapes= tk.Button (self.frame_up22, text=" ▷ Start", command = start_steps)  #Bouton pour lancer les étapes
        #self.etapes= tk.Button (self.frame_up22, text=" ▷ Start", command =threading.Thread(target=start_steps).start)  #Bouton pour lancer les étapes
        self.stop= tk.Button (self.frame_up22, text=" STOP", command=lambda:[print("stop")]) #Bouton pour stopper les étapes

     
        #Placement des éléments 
        
        self.label_retro.grid(row= 0, column= 0, sticky = 'e')
        self.label_gain21.grid(row= 1, column= 0, sticky = 'e')
        self.box_gain21.grid(row= 1, column= 1, sticky = 'e')
        self.label_integration_time21.grid(row= 2, column= 0, sticky = 'e')
        self.box_integration_time21.grid(row= 2, column= 1, sticky = 'e')
        self.label_wldark1.grid(row= 3, column= 0, sticky = 'e')
        self.box_wldark1.grid(row= 3, column= 1, sticky = 'e')
        self.label_wldark2.grid(row= 4, column= 0, sticky = 'e')
        self.box_wldark2.grid(row= 4, column= 1, sticky = 'e')
        self.label_step.grid(row= 5, column= 0, sticky = 'e')
        self.box_step.grid(row= 5, column= 1, sticky = 'e')
        self.add_retro.grid(row=6,column=1,sticky = 'n')  
        self.add_dark.grid(row=7,column=1,sticky = 'n')
        
        self.label_holo.grid(row= 9, column= 0, sticky = 'e')
        self.label_gain22.grid(row= 10, column= 0, sticky = 'e')
        self.box_gain22.grid(row= 10, column= 1, sticky = 'e')
        self.label_integration_time22.grid(row= 11, column= 0, sticky = 'e')
        self.box_integration_time22.grid(row= 11, column= 1, sticky = 'e')
        self.add_holo.grid(row=12,column=1,sticky = 'n')  
        self.add_ref.grid(row=13,column=1,sticky = 'n')
        
        self.label_laser_spot.grid(row= 15, column= 0, sticky = 'e')
        self.label_gain23.grid(row= 16, column= 0, sticky = 'e')
        self.box_gain23.grid(row= 16, column= 1, sticky = 'e')
        self.label_integration_time23.grid(row= 17, column= 0, sticky = 'e')
        self.box_integration_time23.grid(row= 17, column= 1, sticky = 'e')
        self.add_spot.grid(row=18,column=1,sticky = 'n')
        
        #Partie droite
       
        self.UP.grid(row=2,column=2,sticky = 'n',ipadx=5,ipady=2)   #Bouton monter une étape dans la liste
        self.DOWN.place(x=192, y=85, width=28, height=30)   #Bouton descendre une étape dans la liste
        self.modif.grid(row=2,column=0,sticky = 'n',ipadx=5,ipady=2)     #Bouton modifier une étape
        self.supp.grid(row=2,column=0,sticky = 'e',ipadx=5,ipady=2)  #Bouton supprimer une étape
        self.del_all.grid(row=2,column=0,sticky = 's',ipadx=5,ipady=2)   #Bouton supprimer toutes les étapes
        
        self.etapes.grid(row=0,column=1,sticky = 'w',ipadx=7,ipady=2)   #Bouton lancement étape
        self.stop.grid(row=0,column=1,sticky = 'e',ipadx=7,ipady=2)   #Bouton pour stopper les etapes
        
    def fenetre(self, window):
        '''
        Regroupe toutes les fonctions liées à la fenêtre tkinter
        '''
        window.title("Instrument Interface")
        window.minsize(520,300)
        window.mainloop()   #afficher
        
    
def main():
    window= tk.Tk()    # créer une première fenêtre
    start = Interface_Instrument(window)
    start.fenetre(window)
        
        
if __name__ == '__main__':
        main()

