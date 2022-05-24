# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 14:00:55 2021

@author: Mattéo Labrousse
"""

import tkinter as tk
import os

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from simulation_NEW import Scattering_sim


class Interface_Simu:
    def __init__(self,  window):
        '''
        Construction de la fenetre tkinter

        Parameters
        ----------
        window : tk.Tk()
            Fenetre de base qui englobe toutes les autres fenetres.

        '''
        ini = Scattering_sim(shape=(1,1), Lambda=0.6, pixel_size=2.4, focal_length=16)
        self.var = 3
        #definition des différentes fenêtres de l'application
        self.window = window
        self.frame_up = tk.Frame(window)
        self.frame_down = tk.Frame(window,bg='#EADF8E')
        self.frame_up.grid(row=1,column=1)
        self.frame_down.grid(row=1,column=2)
        self.window.columnconfigure(index=3, weight=2)

         #definition des objets de l'application boite de texte, titre et boutons
        self.box_nom = tk.Entry(self.frame_up)
        self.box_nom.insert(0, ini.string_date())
        self.label_nom = tk.Label(self.frame_up, text = 'File name')
        
        self.box_wl = tk.Entry(self.frame_up)
        self.box_wl.insert(0,'0.5')
        self.label_wl = tk.Label(self.frame_up, text="Wavelength (um)")
        
        self.box_diam = tk.Entry(self.frame_up)
        self.box_diam.insert(0,'20')
        self.label_diameter = tk.Label(self.frame_up, text='Diameter (um)')
        
        self.label_indice = tk.Label(self.frame_up, text='Optical Index')
        
        self.box_ind =tk.Entry(self.frame_up)
        self.box_ind.insert(0,'1')
        self.label_indiceRe = tk.Label(self.frame_up, text='Real Part')
        
        self.box_indim=tk.Entry(self.frame_up)
        self.box_indim.insert(0,'0.01')
        self.label_indiceIm = tk.Label(self.frame_up, text='Imaginary Part')
        
        self.label_shape = tk.Label(self.frame_up, text ='Shape (pixels)')
        
        self.shapex = tk.Entry(self.frame_up)
        self.shapex.insert(0,'1000')
        self.label_shapex = tk.Label(self.frame_up, text='')
        
        self.shapey = tk.Entry(self.frame_up)
        self.shapey.insert(0,'1000')
        self.label_shapey = tk.Label(self.frame_up, text='')
        
        self.pix_size = tk.Entry(self.frame_up)
        self.pix_size.insert(0,'2.4')
        self.label_pix_size = tk.Label(self.frame_up,text = 'Pixel size (um)')
        
        self.focal_length = tk.Entry(self.frame_up)
        self.focal_length.insert(0,'35')
        self.label_focal_length = tk.Label(self.frame_up, text='Focal length')
        
        self.particle = tk.Entry(self.frame_up)
        self.particle.insert(0,'1')
        self.label_particle = tk.Label(self.frame_up, text='Particle ratio')
        
        #Création d'espaces
        
        self.space4 = tk.Label(self.frame_up) 
        self.space4.grid(row=4,column=1) 
        self.space8 = tk.Label(self.frame_up) 
        self.space8.grid(row=8,column=1)
        self.space12 = tk.Label(self.frame_up) 
        self.space12.grid(row=12,column=1)
        self.space16 = tk.Label(self.frame_up) 
        self.space16.grid(row=16,column=1)
        self.space19 = tk.Label(self.frame_up) 
        self.space19.grid(row=19,column=1)
        
        
        def mie(self):
            '''
            Fonctions associées au bouton "plot Mie", composé de image_mie et plot_polar

            '''
            self.im0 = Scattering_sim(shape=(int(self.shapex.get()),int(self.shapey.get())), Lambda=float(self.box_wl.get()), pixel_size=float(self.pix_size.get()), focal_length=float(self.focal_length.get()))
            self.im0.image_mie(float(self.box_diam.get()), complex(float(self.box_ind.get()),float(self.box_indim.get())))
            self.im0.plot_polar()
            canvas = FigureCanvasTkAgg(self.im0.fig, master=self.frame_down)
            canvas.get_tk_widget().grid(row = 1, column = 1)
            canvas.draw()
            self.var=0
            
        
        def airy(self):
            '''
            Fonctions associées au bouton "plot Airy", composé de image_airy et plot_polar

            '''
            self.im1 = Scattering_sim(shape=(int(self.shapex.get()),int(self.shapey.get())), Lambda=float(self.box_wl.get()), pixel_size=float(self.pix_size.get()), focal_length=float(self.focal_length.get()))
            self.im1.image_airy(float(self.box_diam.get()))
            self.im1.plot_polar()
            canvas = FigureCanvasTkAgg(self.im1.fig, master=self.frame_down)
            canvas.get_tk_widget().grid(row = 1, column = 1)
            canvas.draw()
            #im.save_all()
            self.var=1
        
        def t_mat(self):
            '''
            Fonctions associées au bouton "plot T_Matrix", composé de image_tmat et plot_polar

            '''
            self.im2 = Scattering_sim(shape=(int(self.shapex.get()),int(self.shapey.get())), Lambda=float(self.box_wl.get()), pixel_size=float(self.pix_size.get()), focal_length=float(self.focal_length.get()))
            self.im2.image_tmat(float(self.box_diam.get()),complex(float(self.box_ind.get()),float(self.box_indim.get())),float(self.particle.get()))
            self.im2.plot_polar()
            canvas = FigureCanvasTkAgg(self.im2.fig, master=self.frame_down)
            canvas.get_tk_widget().grid(row = 1, column = 1)
            canvas.draw()
            self.var=2
        
        
        def sav_im(self,var):
            '''
            Sauvegarde l'image générée en dernier

            Parameters
            ----------
            var : TYPE int
                Permet d'identifier le type d'image sauvegardée

            '''
            #Création du dossier OUTPUT permettant de stocker les images sauvegardées
            
            if not os.path.exists('OUTPUT'):
               os.mkdir('OUTPUT/') 

            
            if var ==1 :
                self.im1.save_all()
                print("Image airy sauvegardée dans le fichier OUTPUT")
            
            elif var ==0 :
                self.im0.save_all()
                print("Image mie sauvegardée dans le fichier OUTPUT")
            elif var==2 :
                self.im2.save_all()
                print("Image airy_matrix sauvegardée dans le fichier OUTPUT")
            else:
                print("Aucune image n'a été générée")
                
        
        #fonctions associées aux boutons

        self.button1 = tk.Button (self.frame_up, text="plot Mie", command=lambda:[mie(self)])
        
        self.button2 = tk.Button (self.frame_up, text="plot Airy", command=lambda:[airy(self)])
        
        self.button3 = tk.Button (self.frame_up, text="plot T_Matrix", command=lambda:[t_mat(self)])
        
        self.button4 = tk.Button(self.frame_up, text="save", command=lambda:[sav_im(self,self.var)])
        
        self.button_exit = tk.Button(self.frame_up, text="Quit", command=lambda:[window.quit(),plt.close('all'),window.destroy()])
        
        
        #placement des éléments dans une grille
        self.box_nom.grid(row=1,column=2)   #nom
        self.label_nom.grid(row=1,column=1, sticky='e') #text nom
        
        self.box_wl.grid(row=2,column=2)    #longueur d'onde
        self.label_wl.grid(row=2,column=1, sticky='e')  #longueur d'onde
        
        self.box_diam.grid(row=3,column=2)  #diamètre
        self.label_diameter.grid(row=3,column=1, sticky='e')    #text diamètre
        
        
        self.label_indice.grid(row=5,column=2, sticky='w') #text indice
        
        self.box_ind.grid(row=6,column=2)   #partie réelle
        self.label_indiceRe.grid(row=6,column=1, sticky='e')    #text partie réelle
        self.box_indim.grid(row=7,column=2) #partie imaginaire
        self.label_indiceIm.grid(row=7,column=1, sticky='e')    #text partie imaginaire
        
        self.label_shape.grid(row=9,column=2,sticky='w')    
        self.shapex.grid(row=10,column=2)   #taille image en x
        self.label_shapex.grid(row=10,column=1, sticky='e')
        self.shapey.grid(row=11,column=2)   #taille image en y
        self.label_shapey.grid(row=11,column=1, sticky='e')
        
        self.pix_size.grid(row=13,column=2,sticky='e')
        self.label_pix_size.grid(row=13,column=1,sticky='e')
       
        self.focal_length.grid(row=14,column=2,sticky='e')
        self.label_focal_length.grid(row=14,column=1,sticky='e')
        
        self.particle.grid(row=15,column=2,sticky='e')
        self.label_particle.grid(row=15,column=1,sticky='e')
        
        self.button1.grid(row=17,column=1,sticky='e')  #bouton plot
        self.button2.grid(row=17,column=2,sticky='s')  #bouton plot Airy
        self.button3.grid(row=17,column=3,sticky='w')  #bouton plot Tmat
        self.button4.grid(row=20,column=2,sticky='w')  #bouton save
        self.button_exit.grid(row=20,column=3,sticky='w')   #bouton quit
         
        #Valeurs tampons pour ce déplacer dans l'image
        self.handlex = 0
        self.handley = 0
        
    
    def fenetre(self, window):
        '''
        Regroupe toutes les fonctions liées à la fenêtre tkinter

        '''
        window.title("Scattering simulation")
        window.minsize(480,260)
        window.mainloop()   #afficher
        
    
        
def main():
    window= tk.Tk()    # créer une première fenêtre
    global var
    start = Interface_Simu(window)
    start.fenetre(window)
    
    
if __name__ == '__main__':
    main()

