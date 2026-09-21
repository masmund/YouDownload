import customtkinter as ctk
from tkinter import filedialog
import yt_dlp
import threading
import os
import time


# 1. Configuration globale
ctk.set_appearance_mode("dark")      
ctk.set_default_color_theme("blue")  

fenetre = ctk.CTk()
fenetre.title("Téléchargeur universel")
fenetre.geometry("900x600")


def choisir_dossier():
    dossier = filedialog.askdirectory()
    if dossier:
        champ_dossier.delete(0, 'end') 
        champ_dossier.insert(0, dossier) 

def hook_progression(d):
    if d['status'] == 'downloading':
        telecharge = d.get('downloaded_bytes', 0)
        total = d.get('total_bytes', 1) 
        pourcentage = telecharge / total
        barre_progression.set(pourcentage)
        
        # On récupère des indices sur ce qui est téléchargé
        # yt-dlp stocke souvent le nom du fichier ou le format en cours
        info = d.get('info_dict', {})
        format_note = info.get('format_note', '').lower()
        filename = d.get('filename', '').lower()
        
        # Petit test intelligent pour deviner s'il s'agit de l'audio ou de la vidéo
        if 'audio' in format_note or 'audio' in filename or 'm4a' in filename or 'webm' in filename:
            label_statut.configure(text="Téléchargement de l'audio en cours...")
        else:
            label_statut.configure(text="Téléchargement de la vidéo en cours...")
            
    elif d['status'] == 'finished':
        label_statut.configure(text="Assemblage et conversion (FFmpeg)...")

def telecharger_en_arriere_plan():
    heure_actuelle = time.strftime("%H%M%S")

    url = champ_url.get()
    print(f"Lancement du téléchargement pour : {url}")
    dossier_choisi = champ_dossier.get()

    choix = menu_format.get()
    print(f"L'utilisateur veut du : {choix}")

    if choix == "Vidéo (MP4)":
        ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'progress_hooks': [hook_progression],
        'outtmpl': os.path.join(dossier_choisi, f'%(title)s_{heure_actuelle}.%(ext)s'),
        'overwrites': True,
        }
    else:
        ydl_opts = {
            'format': 'bestaudio/best', # On demande que le son
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192', # Bonne qualité (192 kbps)
            }],
            'progress_hooks': [hook_progression],
            'outtmpl': os.path.join(dossier_choisi, f'%(title)s_{heure_actuelle}.%(ext)s'),
            'overwrites': True,
        }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("Téléchargement terminé avec succès !")
        label_statut.configure(text="Téléchargement terminé avec succès !", text_color="green")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
        label_statut.configure(text="Une erreur est survenue veuillez réessayez", text_color="red")

def lancer_telechargement():
    # 1. On lit ce que l'utilisateur a tapé
    url_test = champ_url.get()
    dossier_test = champ_dossier.get()
    
    # 2. On vérifie si l'URL est vide
    if url_test == "":
        label_statut.configure(text="Erreur : Veuillez coller un lien !", text_color="red")
        return # Le 'return' arrête la fonction immédiatement
        
    # 3. On vérifie si le dossier est vide
    if dossier_test == "":
        label_statut.configure(text="Erreur : Veuillez choisir un dossier !", text_color="red")
        return
        
    # 4. Si on arrive ici, c'est que tout est rempli ! On peut lancer.
    label_statut.configure(text="Démarrage...", text_color="gray")
    barre_progression.set(0)
    print("Création du thread...")
    nouveau_thread = threading.Thread(target=telecharger_en_arriere_plan)
    nouveau_thread.start()

# ==== WIDGETS ====

# Police personnalisée : type, taille, style
titre = ctk.CTkLabel(fenetre, text="Téléchargeur de vidéo", font=("Helvetica", 24, "bold"))
titre.pack(pady=(20, 5))

sous_titre = ctk.CTkLabel(fenetre, text="Télécharge n'importe quelle vidéo avec un lien!", text_color="gray", font=("Helvetica", 12))
sous_titre.pack(pady=(0, 20))

# champ de l'URL
champ_url = ctk.CTkEntry(fenetre, 
                         width=400, 
                         height=40, # Plus d'espace pour respirer
                         placeholder_text="🔗 Collez l'URL de la vidéo ici",
                         border_color="#2A9D8F", # La même couleur émeraude que le bouton
                         border_width=2,         # Épaisseur de la bordure
                         corner_radius=10,       # Angles arrondis
                         fg_color="#1E2725")     # Un fond très subtilement teinté de vert foncé
champ_url.pack(pady=(30, 10))

# Ligne du dossier (Cadre invisible)
cadre_dossier = ctk.CTkFrame(fenetre, fg_color="transparent")
cadre_dossier.pack(pady=10)

champ_dossier = ctk.CTkEntry(cadre_dossier, 
                             width=250, 
                             height=40,
                             placeholder_text="📁 Dossier d'arrivée",
                             border_color="#2A9D8F",
                             border_width=2,
                             corner_radius=10,
                             fg_color="#1E2725")
champ_dossier.pack(side="left", padx=5)

# format du téléchargement
menu_format = ctk.CTkOptionMenu(fenetre, 
                                values=["🎬 Vidéo (MP4)", "🎵 Audio (MP3)"],
                                width=200,
                                height=40,
                                corner_radius=10,
                                fg_color="#3d5a55",             # Couleur du fond principal
                                button_color="#2A9D8F",         # Couleur du carré avec la flèche
                                button_hover_color="#21867a",   # Flèche au survol
                                dropdown_fg_color="#1E2725",    # Fond du menu déroulé
                                dropdown_hover_color="#2A9D8F") # Surlignage au passage de la souris
menu_format.pack(pady=10)

bouton_parcourir = ctk.CTkButton(cadre_dossier, 
                                 text="Parcourir...", 
                                 command=choisir_dossier, 
                                 width=100,
                                 height=40,
                                 corner_radius=10,
                                 fg_color="#3d5a55",    # Un vert-gris secondaire plus discret
                                 hover_color="#2A9D8F")
bouton_parcourir.pack(side="left", padx=5)

# Bouton Télécharger
bouton = ctk.CTkButton(fenetre, 
                       text="Télécharger", 
                       command=lancer_telechargement, 
                       font=("Helvetica", 14, "bold"),
                       fg_color="#2A9D8F",       # Un vert émeraude doux
                       hover_color="#21867a",    # Un vert légèrement plus foncé au survol
                       corner_radius=20,         # Des bords très arrondis
                       height=40)                # Un bouton un peu plus épais
bouton.pack(pady=20)

# Barre de progression
barre_progression = ctk.CTkProgressBar(fenetre, 
                                       width=400,
                                       height=12,               # Barre un peu plus épaisse
                                       corner_radius=10,        # Bords bien ronds
                                       progress_color="#2A9D8F",# Le vert émeraude qui avance
                                       fg_color="#1E2725")      # La piste sombre en arrière-plan
barre_progression.set(0) 
barre_progression.pack(pady=15)

# Statut du téléchargement   
label_statut = ctk.CTkLabel(fenetre, text="Prêt", text_color="gray")
label_statut.pack(pady=5)

fenetre.mainloop()