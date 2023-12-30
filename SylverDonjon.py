
import random
import pygame
import os
import dotenv

import json
import cryptography.fernet
import sys
import smtplib, ssl
from email.message import EmailMessage

env = dotenv.dotenv_values()
pygame.init()
pygame.mixer.init()
pygame.display.init()
pygame.font.init()
pygame.key.set_repeat(200,200)
music_played_all_time = []
music_already_played = ["the_dying_main.ogg","boss_assassin_main.ogg","game_over_main.ogg","boss_mage_main.ogg","boss_chevalier_main.ogg"]
volume = 0.75
def get_volume(id_ = 0):
    """
        fonction permettant de regler le volume de la music
        :param 1: indice pour verifier l'action a appliquer sur le volume
    """
    global volume
    if id_ == 1:
        volume += 0.1
    elif id_ == -1:
        volume -= 0.1
    return volume
    
global pause
pause = False

def make_music(dossier_music = os.listdir('playlist_music'), id_ = 0):
    """
        fonction permettant de jouer une music et qui change de music quand aucune n'est joué
        :param 1: fichier dans lequel sont stocker les musics
        :param 2: indice pour verifier si on a un changement de musics forcer
        
    """
    global music_already_played
    global music_played_all_time
    global volume
    global pause
    pygame.mixer.music.set_volume(volume)
    if (not pygame.mixer.music.get_busy() or id_ == "switch") and not pause:
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.unload()
        if len(music_already_played) >= len(dossier_music):
            music_already_played = ["the_dying_main.ogg","boss_assassin_main.ogg","game_over_main.ogg","boss_mage_main.ogg","boss_chevalier_main.ogg"]
        random_music = random.randint(0,len(dossier_music)-1)
        erreur = False
        for i in music_already_played:
            if dossier_music[random_music] == i:
                erreur = True
                break
            else:
                erreur = False 
        
        while erreur:
            random_music = random.randint(0,len(dossier_music)-1)
            erreur = False
            for i in music_already_played:
                if dossier_music[random_music] == i:
                    erreur = True
        music_already_played.append(dossier_music[random_music])
        music_played_all_time.append(dossier_music[random_music])
        chemin = f'playlist_music/{dossier_music[random_music]}'
        var_music = pygame.mixer.music.load(chemin)
        pygame.mixer.music.play(0,0,1000)

file_extension = []
file_name = []
global file_full
file_full = ""
for file in os.listdir("file"):
    split_tup = os.path.splitext(file)
    # extract the file name and extension
    if split_tup[1] == ".txt":
        file_name.append(split_tup[0])
        file_extension.append(split_tup[1])

move_left,move_right,move_up,move_down = False,False,False,False
group_using = None

def animate(current_sprite,sprite_group,frame_per):
    """
        fonction qui fait le lien pour animer le personnage
        :param 1: rang de l'image du sprite
        :param 2: liste des images du sprite
        :param 3: vitesse de changement de l'image
        :CU: arg 1 est un int, arg 2 est une liste d'image, arg 3 est un int ou un float
        :return: return le sprite du joueur avec son rang
    """
    global anim
    anim = True
    joueur_sprite, current_sprite = uptade_sprite(sprite_group,frame_per)
    return joueur_sprite,current_sprite

def uptade_sprite(sprite_group=0, frame_per = 0.2):
    """
        fonction qui anime le sprite du joueur
        :param 1: ensemble d'image composant l'animation
        :param 2: vitesse de changement des image
        :CU: arg 1 est une liste et arg 2 est un int ou un float
        :return: return l'image du sprite et son rang
    """
    global current_sprite
    global anim
    if anim:
        current_sprite += frame_per
        if current_sprite >= len(sprite_group):
            current_sprite = 0
        return sprite_group[int(current_sprite)],current_sprite

direction = pygame.math.Vector2(0, 0)
acceleration = 0.35
current_speed = 0

def move(player_pos_x,player_pos_y,sprite_group_right=0,sprite_group_left=0):
    """
        fonction qui permet a l'utilisateur de bouger
        :param 1: position en x du player
        :param 2: position en y du player
        :param 3:
        :param 4:
        :return: les nouvelles positions x et y du player
    """
    
    global vel
    global reducer
    global move_left
    global move_down
    global move_up
    global move_right
    global joueur_sprite
    global current_sprite
    global group_using
    global direction
    global current_speed
    global current_sprite
    keys = pygame.key.get_pressed()
    frame_per = 0.25
    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
        max_vel = 5
    else:
        max_vel = 2.5
    direction.x = 0
    direction.y = 0
    if keys[pygame.K_UP] or keys[pygame.K_z]:
        direction.y -=1
        move_up = True
    else:
        move_up = False
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        direction.y += 1
        move_down = True
    else:
        move_down = False
    if keys[pygame.K_LEFT] or keys[pygame.K_q]:
        direction.x -= 1
        group_using = sprite_group_left
        move_left = True
    else:
        move_left = False
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        direction.x+= 1
        group_using = sprite_group_right
        move_right = True
    else:
        move_right = False
    if not move_right and not move_left and not move_up and not move_down:
        global anim
        anim = False
        current_speed = 0
    current_speed += acceleration
    if abs(current_speed) > max_vel:
        current_speed = max_vel 
    if direction.length() > 0:
        direction.normalize()
    player_pos_x += direction.x * abs(current_speed)
    player_pos_y += direction.y * abs(current_speed)    
    if sprite_group_left != 0:
        if group_using == sprite_group_left:
            joueur_sprite, current_sprite = animate(current_sprite, sprite_group_left, frame_per)
        else:
            joueur_sprite, current_sprite = animate(current_sprite, sprite_group_right, frame_per)
    return player_pos_x, player_pos_y,move_left,move_right,move_down,move_up,joueur_sprite,group_using

def sortir_combat(element,pos_img1,collision_tolerance = 10, v  = 0.1):
    """
        fonction permettant de gerer les collisions obtacles
        :param 1: le Rect de l'element collisionner
        :param 2: le rect du joueur
        :param 3: limite a laquelle une collision est considéré (defaut = 10)
        :CU: arg 1 et 2 sont des rects arg 3 est un int
    """
    if abs(element.right - pos_img1.left) < collision_tolerance:
        while abs(element.right - pos_img1.left) < collision_tolerance:
            pos_img1.x = pos_img1.x +1
    elif abs(element.left - pos_img1.right) < collision_tolerance:
        while abs(element.left - pos_img1.right) < collision_tolerance:
            pos_img1.x = pos_img1.x -1
    elif abs(element.top - pos_img1.bottom) < collision_tolerance:
        while abs(element.top - pos_img1.bottom) < collision_tolerance:
            pos_img1.y = pos_img1.y -1
    elif abs(element.bottom - pos_img1.top) < collision_tolerance:
        while abs(element.bottom - pos_img1.top) < collision_tolerance:
            pos_img1.y = pos_img1.y +1
    return pos_img1
        
def collision_test(element,pos_img1,collision_tolerance = 10, v  = False):
    """
        fonction permettant de gerer les collisions obtacles
        :param 1: le Rect de l'element collisionner
        :param 2: le rect du joueur
        :param 3: limite a laquelle une collision est considéré (defaut = 10)
        :CU: arg 1 et 2 sont des rects arg 3 est un int
    """
    if abs(element.right - pos_img1.left) < collision_tolerance:
        pos_img1.left = element.right
        #la position du joueur est alors fixé a l'obstacle
    elif abs(element.left - pos_img1.right) < collision_tolerance:
        pos_img1.right = element.left
    elif abs(element.top - pos_img1.bottom) < collision_tolerance:
        pos_img1.bottom = element.top
    elif abs(element.bottom - pos_img1.top) < collision_tolerance:
        pos_img1.top = element.bottom

def collision_screen(pos_img1, rect_screen):
    """
    fonction permettant de detecter les collisions avec le screen
    :param 1: rect du joueur
    :param 2: rect de l'ecran
    :CU: arg 1 et 2 sont des rects
    """
    if pos_img1.top < 0:
        pos_img1.top = rect_screen.top
    if pos_img1.bottom > rect_screen.h:
        pos_img1.bottom = rect_screen.bottom
    if pos_img1.left <= 0:
        pos_img1.left = rect_screen.left
    if pos_img1.right >= rect_screen.w:
        pos_img1.right =rect_screen.right


def py_start():
    global file_full
    global pause
    origine_screen = pygame.display.Info()
    screen = pygame.display.set_mode((origine_screen.current_w - origine_screen.current_h/2,origine_screen.current_h - 68))
    global rect_screen
    rect_screen = screen.get_rect()
    pygame.display.set_caption("SylverDonjon")
    running = True
    default_size = (50,50)
    big_size = (200,200)
    sprite_ogre = pygame.image.load("image_site/image_ogre.png").convert_alpha()
    sprite_ogre_str = "image_site/image_ogre.png"
    sprite_mort_vivant = pygame.image.load("image_site/image_mort_vivant.png").convert_alpha()
    sprite_mort_vivant_str = "image_site/image_mort_vivant.png"
    sprite_tueur_a_gage = pygame.image.load("image_site/image_tueur_a_gage.png").convert_alpha()
    sprite_tueur_a_gage_str = "image_site/image_tueur_a_gage.png"
    sprite_healeur = pygame.image.load("image_site/image_healeur.png").convert_alpha()
    sprite_healeur_str = "image_site/image_healeur.png"
    sprite_ogre = pygame.transform.scale(sprite_ogre,big_size)
    sprite_mort_vivant = pygame.transform.scale(sprite_mort_vivant,big_size)
    sprite_tueur_a_gage = pygame.transform.scale(sprite_tueur_a_gage,big_size)
    sprite_healeur = pygame.transform.scale(sprite_healeur,big_size)
    btn_retour =  pygame.image.load("image_site/return.png")
    contener = pygame.image.load("image_site/fond_contener.png").convert_alpha()
    longueur_barre,hauteur_barre = 100,10
    couleur_barre_vie = (0,100,0)
    couleur_vie_restante = (0,255,0)
    couleur_barre_energie = (0,0,100)
    couleur_energie_restante=(0,0,255)
    surface_barre_vie = pygame.Surface((longueur_barre,hauteur_barre))
    contener_dimension = contener.get_rect()
    contener_ = pygame.Rect(rect_screen.w/8,rect_screen.h/2,contener_dimension[2],contener_dimension[3])
    contener_btn = pygame.image.load("image_site/contener_btn.png").convert_alpha()
    contener_btn_dimension = contener_btn.get_rect()
    ligne = pygame.image.load("image_site/ligne.png")
    clavier = pygame.image.load("image_site/tuto_touche_img.jpg").convert_alpha()
    clavier = pygame.transform.scale(clavier,(510,400))
    clavier_rect = clavier.get_rect()
    clavier_rect.x = rect_screen.center[0] - clavier_rect.w/2
    clavier_rect.y = rect_screen.center[1] - clavier_rect.h/2    
    x_btn = contener_[0]
    y_btn = contener_[1]
    marge_btn = 145
    contener_btn_pos = [(pygame.Rect((x_btn+9),(y_btn+8),contener_btn_dimension[2],contener_btn_dimension[3])),(pygame.Rect((x_btn+9),(y_btn+8 + marge_btn),contener_btn_dimension[2],contener_btn_dimension[3])), (pygame.Rect((x_btn+9),(y_btn+8 + marge_btn*2),contener_btn_dimension[2],contener_btn_dimension[3])) ]
    ligne = pygame.transform.scale(ligne, (10,contener_.h))
    contener_btn_pos_ = [{"nom" : "item", "rect" : contener_btn_pos[0]},{"nom" : "atk", "rect" : contener_btn_pos[1]},{"nom" : "info", "rect" : contener_btn_pos[2]}]
    default_size = (50,50)
    big_size = (100,100)
    btn_retour = pygame.transform.scale(btn_retour, default_size)
    pos_btn_retour = btn_retour.get_rect()
    pos_btn_retour.x = 0
    pos_btn_retour.y = 0
    global width
    global height
    width = rect_screen.w - 2 * rect_screen.w/6
    height = rect_screen.h - 2 * rect_screen.h/4
    pop_up = pygame.Rect(rect_screen.w/2 - width/2 , rect_screen.h/2-height/2, width,height)
    #allcolor
    gris = (100,100,100)
    pos_img2 = sprite_ogre.get_rect()
    pos_img3 = sprite_ogre.get_rect()
    pos_img2.x += 250
    pos_img2.y = 100
    pos_img3.x += 500
    pos_img3.y = 100
    rect_ennemie_easy3 =  sprite_ogre.get_rect()
    rect_ennemie_moyen3 = sprite_mort_vivant.get_rect()
    rect_ennemie_moyen4 = sprite_mort_vivant.get_rect()
    rect_ennemie_dur3 = sprite_tueur_a_gage.get_rect()
    rect_ennemie_dur4 = sprite_tueur_a_gage.get_rect()
    rect_ennemie_dur5 = sprite_tueur_a_gage.get_rect()
    del sprite_ogre
    del sprite_mort_vivant
    del sprite_tueur_a_gage
    rect_ennemie_easy3.x,rect_ennemie_easy3.y = 250,300
    rect_ennemie_moyen3.x,rect_ennemie_moyen3.y = 500,500
    rect_ennemie_moyen4.x,rect_ennemie_moyen4.y = 200,500
    rect_ennemie_dur3.x,rect_ennemie_dur3.y = 100,500
    rect_ennemie_dur4.x,rect_ennemie_dur4.y = 300,500
    rect_ennemie_dur5.x,rect_ennemie_dur5.y = 500,500
    #collision = [pos_img2,obstacle,obstacle1,obstacle2]
    def toTuple(elt):
        """
            faciliter la convertion en json
            :param1: liste a transformer en json_readable
        """
        return elt[0],elt[1],elt[2],elt[3]
    desc1 = "Un Item de base donnant de la force ? mon  premier petit stéroide ! Prenons le !"
    desc2 = "Une petite potion pour me soigner, ça pourrait m'etre très utile."
    desc3 = "Un item pour le cardio ? incroyable ! je ferais mieux de bien m'en servir"
    desc4 = "Il est dit que c'est le grand Thorkell qui a créé cette potion. Je me demande si je deviendrais aussi fort que lui."
    desc5 = "Cette elixir me donne de nombreux bonus ! Dans les situations critique ce sera très utile !"
    
    
    item_holder = {
                   "potion_force_base" : {"nom_variable" : "potion_force_base","nom" : "M-Extra", "bonus_endurance" : 0, "bonus_defence" : 0, "bonus_attaque" : 0.05, "fonction" : "attaque", "img" : ("image_site/force_potion_rpg.png"),"description" : desc1},
                   "potion_defence_base" : {"nom_variable" : "potion_defence_base","nom" : "Poudre de coca", "bonus_endurance" : 0, "bonus_defence" : 0.05, "bonus_attaque" : 0, "fonction" : "defence", "img" : ("image_site/health_potion_rpg.png"), "description" : desc2},
                   "potion_endurance_base" : {"nom_variable" : "potion_endurance_base","nom" : "C-synthétique", "bonus_endurance" : 0.05, "bonus_defence" : 0, "bonus_attaque" : 0, "fonction" : "endurance", "img" : ("image_site/stamina_potion_rpg.png"),"description" : desc3},
                   "poudre Thorkellique" : {"nom_variable" : "poudre Thorkellique","nom" : "Thorkellite", "bonus_endurance" : 0, "bonus_defence" : 0, "bonus_attaque" : 0.50, "fonction" : "attaque", "img" : ("image_site/thorkellite_potion_rpg.png"), "description" : desc4},
                   "elixir De jouvence" : {"nom_variable" : "elixir De jouvence","nom" : "Elixir de Jouvence", "bonus_endurance" : 0.1, "bonus_defence" : 0.2, "bonus_attaque" : 0, "fonction" : "endurance / defence", "img" :("image_site/elexir_de_jouvence_potion_rpg.png"),"description" : desc5}
                   }
    
    
        
    attaque_holder = {
                      "coup rapide" : {"nom" : "Coup rapide", "degat" :  10,  "coup_en_energie" : 5, "vitesse" : 12, "damage_reduction" : 0, "ulti" : False, "turn_to_work" : None, "atk_type": "force"}
                      , "slash" : {"nom" : "slash", "degat" :  12,  "coup_en_energie" : 5, "vitesse" : 9, "damage_reduction" : 0, "ulti" : False, "turn_to_work" : None, "atk_type": "force"},
                      "boule de feu" : {"nom" : "boule de feu","degat" : 12,  "coup_en_energie" : 5, "vitesse" : 10, "damage_reduction" : 0, "ulti" : False, "turn_to_work" : None, "atk_type": "magie"},
                      "mise a mort" : {"nom" : "Mise a mort", "degat" : 50,  "coup_en_energie" : 14, "vitesse" : 30, "damage_reduction" : 0, "ulti" : True, "turn_to_work" : 4, "atk_type": "force"},
                      "combo barbare" : {"nom" : "Combo Barbare", "degat" : 50,  "coup_en_energie" : 15, "vitesse" : 25, "damage_reduction" : 0, "ulti" : True, "turn_to_work" : 4, "atk_type": "force"},
                      "mur de mana" : {"nom" : "Mur de Mana", "degat" :  3,  "coup_en_energie" : 11, "vitesse" : 100, "damage_reduction" : 50, "ulti" : False, "turn_to_work" : None, "atk_type": "aucun","tour_effect" : 2, "defence_reduction" : 2},
                      "invisibilité" : {"nom" : "Invisibilité", "degat" : 1,  "coup_en_energie" : 5, "vitesse" : 100, "damage_reduction" : 50, "ulti" : False, "turn_to_work" : None, "atk_type": "aucun", "tour_effect" : 2},
                      "void hole" : {"nom" : "Void Hole", "degat" : 50,  "coup_en_energie" : 20, "vitesse" : 30, "damage_reduction" : 0, "ulti" : True, "turn_to_work" : 4, "atk_type": "magie"},
                      "garde du chevalier" : {"nom" : "Garde du chevalier", "degat" : 1,  "coup_en_energie" : 10, "vitesse" : 100, "damage_reduction" : 50, "ulti" : False, "turn_to_work" : None, "atk_type": "aucun", "tour_effect" : 2, "defence_reduction" : 2},
                      "coup de poing" : {"nom" : "coup de poing","degat" : 6,  "coup_en_energie" : 0, "vitesse" : 5, "damage_reduction" : 0, "ulti" : False, "turn_to_work" : None, "atk_type": "force"},
                      }

    pos_img2_ = {"categorie" : "ogre","type" : "ennemie", "rect" : (pos_img2[0],pos_img2[1],pos_img2[2],pos_img2[3]), "img" : sprite_ogre_str, "data_ennemie" : {"reflexe" : 5,"id" : 1, "nom" : "Kurdash", "vie" : 60, "vie_max" : 60, "force" : 2, "agilite" : 2, "vol de vie" : 0, "magie" : 0, "vitesse" : 2, "energie_max" : 30, "energie" : 30, "level" : 1, "loot" : {"gold_drop" : 20, "xp_drop" : 500, "item_drop" : item_holder["poudre Thorkellique"], "chance_drop" : 45}, "abilite" : [{"nom" : "morsure", "degat" :  8, "cout" : 0, "vitesse" : 9, "damage_reduction" : 0, "ulti" : False, "type" : "force"},{"nom" : "Grosse morsure", "degat" :  14, "cout" : 5, "vitesse" : 8, "damage_reduction" : 0, "ulti" : False, "type" : "force"}]}, "etat" : "vivant", "mort_def" : False}
    pos_img3_ = {"categorie" : "ogre","type" : "ennemie", "rect" : (pos_img3[0],pos_img3[1],pos_img3[2],pos_img3[3]), "img" : sprite_ogre_str, "data_ennemie" : {"reflexe" : 5,"id" : 2, "nom" : "Maklúk", "vie" : 60, "vie_max" : 60, "force" : 2, "agilite" : 2, "vol de vie" : 0, "magie" : 0, "vitesse" : 2, "energie_max" : 30, "energie" : 30, "level" : 1, "loot" : {"gold_drop" : 20, "xp_drop" : 500, "item_drop" : item_holder["elixir De jouvence"], "chance_drop" : 45}, "abilite" : [{"nom" : "Coup de masse", "degat" :  15, "cout" : 0, "vitesse" : 9, "damage_reduction" : 0, "ulti" : False, "type" : "force"},{"nom" : "droite chantante", "degat" :  13, "cout" : 5, "vitesse" : 8, "damage_reduction" : 0, "ulti" : False, "type" : "force"}]}, "etat" : "vivant", "mort_def" : False}#Obstacle("ennemie", pos_img3, mechant_sprite2,Enemy(2,"shai testeur",40,25,1,1,0,0,0.9,30,30,1,Loot(10,25,Ability_holder.coup_rapide,45)), "vivant", False)
    ennemie_easy_3 = {"categorie" : "ogre","type" : "ennemie", "rect" : (rect_ennemie_easy3[0],rect_ennemie_easy3[1],rect_ennemie_easy3[2],rect_ennemie_easy3[3]), "img" : sprite_ogre_str, "data_ennemie" : {"reflexe" : 5,"id" : 2, "nom" : "Vassily", "vie" : 80, "vie_max" : 80, "force" : 2, "agilite" : 2, "vol de vie" : 0, "magie" : 0, "vitesse" : 2, "energie_max" : 30, "energie" : 30, "level" : 1, "loot" : {"gold_drop" : 10, "xp_drop" : 100, "item_drop" : item_holder["poudre Thorkellique"], "chance_drop" : 45}, "abilite" : [{"nom" : "Masse volante", "degat" :  10, "cout" : 0, "vitesse" : 9, "damage_reduction" : 0, "ulti" : False, "type" : "force"},{"nom" : "droite chantante", "degat" :  15, "cout" : 5, "vitesse" : 8, "damage_reduction" : 0, "ulti" : False, "type" : "force"}]}, "etat" : "vivant", "mort_def" : False}#Obstacle("ennemie", pos_img3, mechant_sprite2,Enemy(2,"shai testeur",40,25,1,1,0,0,0.9,30,30,1,Loot(10,25,Ability_holder.coup_rapide,45)), "vivant", False)
    ennemie_moyen_3 = {"categorie" : "Mort Vivant","type" : "ennemie", "rect" : (toTuple(rect_ennemie_moyen3)), "img" : sprite_mort_vivant_str, "data_ennemie" : {"reflexe" : 8,"id" : 2, "nom" : "Eniola Tionge", "vie" : 80, "vie_max" : 80, "force" : 5, "agilite" : 5, "vol de vie" : 0, "magie" : 0, "vitesse" : 6, "energie_max" : 30, "energie" : 30, "level" : 2, "loot" : {"gold_drop" : 50, "xp_drop" : 600, "item_drop" : item_holder["elixir De jouvence"], "chance_drop" : 45}, "abilite" : [{"nom" : "Coup de squellette", "degat" :  15, "cout" : 0, "vitesse" : 9, "damage_reduction" : 0, "ulti" : False, "type" : "force"},{"nom" : "assaut de poussiere", "degat" :  8, "cout" : 5, "vitesse" : 14, "damage_reduction" : 0, "ulti" : False, "type" : "force"}]}, "etat" : "vivant", "mort_def" : False}#Obstacle("ennemie", pos_img3, mechant_sprite2,Enemy(2,"shai testeur",40,25,1,1,0,0,0.9,30,30,1,Loot(10,25,Ability_holder.coup_rapide,45)), "vivant", False)
    ennemie_moyen_4 = {"categorie" : "Mort Vivant","type" : "ennemie", "rect" : toTuple(rect_ennemie_moyen4), "img" : sprite_mort_vivant_str, "data_ennemie" : {"reflexe" : 8,"id" : 2, "nom" : "Mihalis", "vie" : 80, "vie_max" : 80, "force" : 7, "agilite" : 7, "vol de vie" : 0, "magie" : 0, "vitesse" : 8, "energie_max" : 30, "energie" : 30, "level" : 2, "loot" : {"gold_drop" : 50, "xp_drop" : 600, "item_drop" : item_holder["poudre Thorkellique"], "chance_drop" : 45}, "abilite" : [{"nom" : "Squellete shoot", "degat" :  15, "cout" : 0, "vitesse" : 9, "damage_reduction" : 0, "ulti" : False, "type" : "force"},{"nom" : "Lance poussiere", "degat" :  8, "cout" : 5, "vitesse" : 14, "damage_reduction" : 0, "ulti" : False, "type" : "force"}]}, "etat" : "vivant", "mort_def" : False}#Obstacle("ennemie", pos_img3, mechant_sprite2,Enemy(2,"shai testeur",40,25,1,1,0,0,0.9,30,30,1,Loot(10,25,Ability_holder.coup_rapide,45)), "vivant", False)
    ennemie_dur_3 = {"categorie" : "Tueur a Gage","type" : "ennemie", "rect" : toTuple(rect_ennemie_dur3), "img" : sprite_tueur_a_gage_str, "data_ennemie" : {"reflexe" : 11,"id" : 2, "nom" : "JOhN Wish", "vie" : 120, "vie_max" : 120, "force" : 7, "agilite" : 10, "vol de vie" : 0, "magie" : 0, "vitesse" : 11, "energie_max" : 30, "energie" : 30, "level" : 3, "loot" : {"gold_drop" : 100, "xp_drop" : 600, "item_drop" : item_holder["poudre Thorkellique"], "chance_drop" : 45}, "abilite" : [{"nom" : "Slash surprise", "degat" :  15, "cout" : 0, "vitesse" : 9, "damage_reduction" : 0, "ulti" : False, "type" : "force"},{"nom" : "Main de l'assassin", "degat" :  14, "cout" : 5, "vitesse" : 15, "damage_reduction" : 0, "ulti" : False, "type" : "force"}]}, "etat" : "vivant", "mort_def" : False}#Obstacle("ennemie", pos_img3, mechant_sprite2,Enemy(2,"shai testeur",40,25,1,1,0,0,0.9,30,30,1,Loot(10,25,Ability_holder.coup_rapide,45)), "vivant", False)
    ennemie_dur_4 = {"categorie" : "Tueur a Gage","type": "ennemie","rect": toTuple(rect_ennemie_dur4), "img": sprite_tueur_a_gage_str,
                     "data_ennemie": {"reflexe" : 11,"id": 2, "nom": "HitWomEn", "vie": 120, "vie_max": 150, "force": 8, "agilite": 12,
                                      "vol de vie": 0, "magie": 0, "vitesse": 11, "energie_max": 30, "energie": 30,
                                      "level": 3, "loot": {"gold_drop": 100, "xp_drop": 600,
                                                           "item_drop": item_holder["poudre Thorkellique"],
                                                           "chance_drop": 45}, "abilite": [
                             {"nom": "Shoot gun", "degat": 16, "cout": 0, "vitesse": 9, "damage_reduction": 0,
                              "ulti": False, "type": "force"},
                             {"nom": "Charge mortel", "degat": 18, "cout": 5, "vitesse": 12, "damage_reduction": 0,
                              "ulti": False, "type": "force"}]}, "etat": "vivant",
                     "mort_def": False}  # Obstacle("ennemie", pos_img3, mechant_sprite2,Enemy(2,"shai testeur",40,25,1,1,0,0,0.9,30,30,1,Loot(10,25,Ability_holder.coup_rapide,45)), "vivant", False)
    ennemie_dur_5 = {"categorie" : "Tueur a gage frustre", "type" : "ennemie", "rect" : toTuple(rect_ennemie_dur5), "img" : sprite_tueur_a_gage_str, "data_ennemie" : {"reflexe" : 11,"id" : 2, "nom" : "William", "vie" : 150, "vie_max" : 150, "force" : 9, "agilite" : 17, "vol de vie" : 0, "magie" : 0, "vitesse" : 9, "energie_max" : 30, "energie" : 30, "level" : 4, "loot" : {"gold_drop" : 200, "xp_drop" : 600, "item_drop" : item_holder["elixir De jouvence"], "chance_drop" : 45}, "abilite" : [{"nom" : "Bdg originel", "degat" :  25, "cout" : 0, "vitesse" : 9, "damage_reduction" : 0, "ulti" : False, "type" : "force"},{"nom" : "Calvitie sacré", "degat" :  15, "cout" : 5, "vitesse" : 20, "damage_reduction" : 0, "ulti" : False, "type" : "force"}]}, "etat" : "vivant", "mort_def" : False}#Obstacle("ennemie", pos_img3, mechant_sprite2,Enemy(2,"shai testeur",40,25,1,1,0,0,0.9,30,30,1,Loot(10,25,Ability_holder.coup_rapide,45)), "vivant", False)
    boss_ennemie_assassin = {"categorie" : "Maitre du monde (Boss)","type": "ennemie", "rect": toTuple(rect_ennemie_dur4), "img": sprite_tueur_a_gage_str,
                     "data_ennemie": {"boss" : True, "reflexe" : 20, "id": 2, "nom": "StAn", "vie": 220, "vie_max": 220, "force": 13, "agilite": 17,
                                      "vol de vie": 0, "magie": 0, "vitesse": 18, "energie_max": 100, "energie": 100,
                                      "level": 20, "loot": {"gold_drop": 10000, "xp_drop": 100000000,
                                                           "item_drop": item_holder["poudre Thorkellique"],
                                                           "chance_drop": 55}, "abilite": [
                             {"nom": "cOUPURE DE couraNT", "degat": 25, "cout": 0, "vitesse": 20, "damage_reduction": 0,
                              "ulti": False, "type": "force"},
                             {"nom": "Baisse la moyenne", "degat": 18, "cout": 0, "vitesse": 31, "damage_reduction": 0,
                              "ulti": False, "type": "force"}]}, "etat": "vivant",
                     "mort_def": False}
    
    boss_ennemie_guerrier = {"categorie" : "William Originel (boss)","type": "ennemie", "rect": toTuple(rect_ennemie_dur4), "img": sprite_tueur_a_gage_str,
                     "data_ennemie": {"boss" : True, "reflexe" : 20, "id": 2, "nom": "William Prime", "vie": 160, "vie_max": 160, "force": 13, "agilite": 17,
                                      "vol de vie": 0, "magie": 0, "vitesse": 18, "energie_max": 100, "energie": 100,
                                      "level": 20, "loot": {"gold_drop": 10000, "xp_drop": 100000000,
                                                           "item_drop": item_holder["poudre Thorkellique"],
                                                           "chance_drop": 55}, "abilite": [
                             {"nom": "Diamond Smash", "degat": 25, "cout": 0, "vitesse": 20, "damage_reduction": 0,
                              "ulti": False, "type": "force"},
                             {"nom": "Rocket God", "degat": 18, "cout": 0, "vitesse": 31, "damage_reduction": 0,
                              "ulti": False, "type": "force"}]}, "etat": "vivant",
                     "mort_def": False}
    
    boss_ennemie_mage = {"categorie" : "Le Dieu Mage","type": "ennemie", "rect": toTuple(rect_ennemie_dur4), "img": sprite_tueur_a_gage_str,
                     "data_ennemie": {"boss" : True, "reflexe" : 20, "id": 2, "nom": "Heirzir", "vie": 140, "vie_max": 140, "force": 13, "agilite": 17,
                                      "vol de vie": 0, "magie": 20, "vitesse": 18, "energie_max": 100, "energie": 100,
                                      "level": 20, "loot": {"gold_drop": 10000, "xp_drop": 100000000,
                                                           "item_drop": item_holder["poudre Thorkellique"],
                                                           "chance_drop": 55}, "abilite": [
                             {"nom": "Mode Cremation", "degat": 25, "cout": 0, "vitesse": 20, "damage_reduction": 0,
                              "ulti": False, "type": "magie"},
                             {"nom": "Boule de Zar", "degat": 18, "cout": 0, "vitesse": 31, "damage_reduction": 0,
                              "ulti": False, "type": "magie"}]}, "etat": "vivant",
                     "mort_def": False}
    #les sprites des boss ne sont pas a jour
    global png_heal_room
    png_heal_room = {"type" : "png", "rect" : toTuple(pos_img3), "img" : sprite_healeur_str, "data_ennemie" : None,"etat" : "mort", "boss" : None, "fonction" : "healeur"}
    pos_btn_retour_ = {"nom" : "retour", "rect" : pos_btn_retour}#Bouton("retour", pos_btn_retour)
    global collision
    global collision_
    collision = [] #collision comportant le nom, l'element, l'image, et les donneés ennemie
    collision_ = [] #collision avec seulemeent les rects
    global btn
    btn = []
    btn.append(pos_btn_retour_)
    clock = pygame.time.Clock()
    collision_tolerance = 10
    has_hit = False
    background = (100,100,100)
    global combat
    combat = False
    color_text = (255,255,255) #blancp    
    #police
    csm = 'Comic Sans Ms'
    cambria = 'Cambria'
    arial = 'Arial'
    global sinistre
    sinistre = "dossier_police/Sinistre.otf"
    minecraft_factory = "dossier_police/minecrafFactory.ttf"
    agero = "dossier_police/agero.ttf"
    Arial = pygame.font.SysFont(arial,20)
    comic_sans_ms = pygame.font.SysFont(csm, 20)
    global text_
    text_ = ""
    fond_contener = (200,200,200)
    background_pop_up = (80,80,80)
    bonus_enchainement_combat = 0
    combat_enchainé = 0
    #color_here

    color_pick = {"bordeaux_f" : (153,0,0),"orange" : (255,102,0),"rose" : (255,51,153), "marron" : (102,51,0),"mauve" : (153,0,204),"vert_f": (51,153,0),"bleu_f" : (51,51,153), "bordeaux" : (153,0,0), "cyan" : (0,204,204), "cyan_f" :(0,153,153), "noir" : (0,0,0), "blanc" : (255,255,255), "violet_rouge" : (159,0,76), "vert_bleu" : (0,102,102), "gris" : (100,100,100), 'gris_f' : (80,80,80), "jaune" : (255,255,0), "rouge" : (255,0,0), "bleu" : (0,0,255), 'vert' : (0,255,0)}
    
    def get_dimension(text, font,size, pos = False, font_import = False):
        if pos == False:
            """  
                obtenir la dimension d'un text tout simplement/ou sa position
                :param 1: text qu'on veut obtenir la dimension
                :param 2: font que le text utilise
                :param 3: booléen si on veut la pos ou pas (fonctionne pas, mettre False)
                :param 4: determiner si la font est une font import (booléen)
                :return: la width du texte et sa height
                :CU: arg 1 est un str, arg 2 est de type font.FONT ou font.SysFont, arg 3 est un int, arg 3 et 4 est un booléen
            """
            if not font_import:
                font_ = pygame.font.SysFont(font, size)
            else:
                font_ = pygame.font.Font(font, size)
            text_ = font_.render(text,True,(0,0,0))
            return text_.get_rect()[2], text_.get_rect()[3]
        else:
            font_ = pygame.font.SysFont(font, size)
            text_ = font_.render(text,True,(0,0,0))
            return text_.get_rect()[0], text_.get_rect()[1]
        
    def appear_tuto_touche():
        """
            Faire apparaitre l'image du tuto des commandes
        """
        make_music(os.listdir("playlist_music"))
        image_delete = pygame.transform.scale(pygame.image.load("image_site/image_delete.png"),(40,40))
        mettre_fond_transparent((rect_screen.w,rect_screen.h),50,(200,200,200))
        pygame.draw.rect(screen,(0,0,0,128), (clavier_rect.x -50,clavier_rect.y - 50,clavier_rect.w+100,clavier_rect.h+100),2)
        draw_in("Appuie sur Entrer pour fermer",0,clavier_rect,20,(0,0,0),minecraft_factory,clavier_rect.w/2 -
                get_dimension("Appuie sur Entrer pour fermer",minecraft_factory,20,False,True)[0]/2,-45,False,True)
        screen.blit(clavier, clavier_rect)
        quitter = False
        rect_del = pygame.Rect(clavier_rect.x -45,clavier_rect.y-45,40,40)
        while True:
            mouse = pygame.mouse.get_pos()
            for event in [pygame.event.poll()]:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        quitter = True
                        break
                collide = False
                if rect_del.collidepoint(mouse):
                    collide = True
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        quitter = True
                        break
                screen.blit(change_color_img(image_delete,(0,0,0)),(clavier_rect.x -45,clavier_rect.y-45)) if not collide\
                else screen.blit(change_color_img(image_delete,(255,0,0)),(clavier_rect.x -45,clavier_rect.y-45))                                                                  
            if quitter:
                break
            pygame.display.flip()
            
    def left_combat(name, pos_img1, collisionneur, collision_tolerance):
        """
            fonction permettant de quitter le combat
            :param 1: type de l'utilisation
            :param 2: rect du jour
            :param 3: rect de l'element collisionner
            :param 4: limite a laquelle une collision est considéré
            :CU: arg 1 est un str, arg 2 et 3 est un rect, arg 4 est un int
        """
        global combat
        global degat_encaissé
        global energie_cost
        global degat_ennemie
        global mort
        if name == "retour":
            del degat_encaissé[:]
            del degat_ennemie[:]
            del energy_cost[:]
            indice_combat = 0
            mort = False
            combat = False
            sortir_combat(collisionneur, pos_img1, collision_tolerance)
            return combat, mort

    def make_hit(sprite, temp=100, x= contener_.x + 70, y=contener_.y -150, grosx = 200, grosy = 200):
        """
            fonction permettant de faire une hit frame
            :param 1: l'image pour faire le hit
            :param 2: le temps que prend la hit frame (ms)
            :param 3: coordonne x de l'image
            :param 4: coordonne y de l'image
            :param 5: grossissement de l'image en longueur
            :param 6: grossissement de l'image en largueur
            :CU: arg 1 est une image, arg 2,3,4,5 et 6  sont des int
        """
        sprite = pygame.transform.scale(sprite, (grosx, grosy))
        hit = hit_frame(sprite, (x, y))
        screen.blit(hit, (x, y))
        appear_contener()
        pygame.display.flip()
        pygame.time.delay(temp)
        screen.blit(sprite, (x, y))
        appear_contener()

    def hit_frame(image, pos):
        """
            fonction permettant de faire apparaitre l'image du hit en rouge
            :param 1: c'est une image
            :param 2: position de l'image
            :return: l'image en rouge est return
        """
        hit_image = pygame.Surface(image.get_size()).convert_alpha()
        color = pygame.Color(0)
        color.hsla = (1, 100,50,100)
        hit_image.fill(color)
        finalImage = image.copy()
        finalImage.blit(hit_image, (0, 0), special_flags=pygame.BLEND_MULT)
        return finalImage
    
    def change_color_img(image,color):
        """
            permet de changer la couleur d'une image, version simplifier de hit_frame
            :param1: l'image
            :param2: la couleur
        """
        s = pygame.Surface(image.get_size()).convert_alpha()
        s.fill(color)
        image_final = image.copy()
        image_final.blit(s,(0,0),special_flags=pygame.BLEND_MULT)
        return image_final
    
    def appear_pop_up(id_ = 0):
        """
            fonction faisant apparaitre un pop_up au millieu de l'ecran
        """
        
        if id_ == 0:
            pop_up = pygame.Rect(rect_screen.w / 2 - 500 / 2, rect_screen.h / 2 - 300 / 2, 500, 300)
        else:
            pop_up = pygame.Rect(rect_screen.w/2 - width/2 , rect_screen.h/2-height/2, width,height)
        screen.fill((80,80,80), pop_up)
        pygame.draw.rect(screen,(0,5,0), pop_up, 4)
        return pop_up
    
    def check_size_opti(text,font,font_import,comparaison):        
            taille = 1
            while True:
                if font_import :
                    font_ = pygame.font.Font(font,taille)                        
                else:
                    font_ = pygame.font.SysFont(font,taille)
                size = font_.size(text)[0]
                if size < comparaison:
                    taille += 1
                else:
                    break
            taille -= 1
            return taille
        
    global dict_data
    dict_data_item = {}
    #chargement donnée inventaire rect et line coupage
    part_item = pygame.Rect(rect_screen.w/2 - (width)/2 , rect_screen.h/2-height/2,
                                     width - width/3, height - height/3)
    part_info = pygame.Rect(part_item.x + part_item.w + 20, part_item.y, width/3 - 20, height-height/3)
    part_choose = pygame.Rect(part_item.x, part_item.y + part_item.h + 20, width,height/3)
    rect_quitter = pygame.Rect(part_item.x - 50, part_item.y - 50, 40,40)
    text = "Voici vos items"
    taille1 = check_size_opti(text,sinistre,True,part_item.w/3)
    text = "Description"
    taille2_ = check_size_opti(text,sinistre,True,part_info.w - 100)
    text = "Voici vos items actif"
    taille3 = check_size_opti(text,sinistre,True,part_choose.w/3)
    text_consigne = "APPUYER SUR UN ELEMENT NON EQUIPER (click millieu) AFIN DE LE SELECTIONNER"
    taille4 = check_size_opti(text_consigne,sinistre,True, part_choose.w - 50)
    dict_data_item["taille1"] = taille1
    dict_data_item["taille2_"] = taille2_
    dict_data_item["taille3"] = taille3
    dict_data_item["taille4"] = taille4
    
    
    def calcul_line(elt,font = csm, taille = 15, comparaison = part_info.w -10, pos = False, import_ = False):       
        new_desc = elt        
        line = 1  
        i = 0
        start = 0
        coupage = [0]                    
        while i < len(elt):
            if (get_dimension(new_desc[start:i],font,taille,pos,import_)[0] > comparaison):
                w = -1                                                   
                while new_desc[start:i][w] != " ":
                    w -= 1
                i += w
                start = i
                coupage.append(start)                  
                line +=1             
            i+=1
        dimension = 0
        for i in range(line):
            dimension = get_dimension(new_desc,csm,15)[1] + 20 + 20*i
        dimension -= 10
        return line,coupage,dimension
    
    for key,value in item_holder.items():
        desc = value["description"]
        line,coupage,dimension = calcul_line(desc,font = csm,taille = 15, comparaison = part_info.w - 15)
        value["id"] = {"line" : line, "coupage" : coupage,"height" : dimension}
    
    def encadrer_text(x = 5,y = 5,color_text = (0,0,0),lenght = 200,height = 200,text = "LOREM IPSUM",coupage = [0],line = 1,color_fond = (255,255,255),color_bord = (0,0,0),font = csm,size = 15, border = 1):
        surface_lenght = lenght
        surface_desc = pygame.Surface((surface_lenght, height))
        surface_desc.fill((color_fond))
        fake_rect = pygame.Rect(0,0,0,0)                        
        for i in range(line):
            start = coupage[i]
            try:
                limite = coupage[i+1]
            except:
                limite = len(text)
            desc = text[start:limite].strip()
            draw_in(desc,"",fake_rect,size,color_text,font, surface_lenght/2 - get_dimension(desc,font,size)[0]/2,
                    5+ 20*i, surface = surface_desc)
        pygame.draw.rect(surface_desc,color_bord,(0,0,lenght,height),border)
        screen.blit(surface_desc,(x, y))
        
    def inventaire_item():
        global pause
        """
            fonction permettant de faire apparaitre l'inventaire de jeux !
            
        """
        
        global dict_data
        make_music(os.listdir("playlist_music"))        
        image_delete = pygame.transform.scale(pygame.image.load("image_site/image_delete.png"),(40,40))
        """
        if len(dict_data_item) == 0:
            text = "Voici vos items"
            taille1 = check_size_opti(text,sinistre,True,part_item.w/3)
            text = "Description"
            taille2_ = check_size_opti(text,sinistre,True,part_info.w - 100)
            text = "Voici vos items actif"
            taille3 = check_size_opti(text,sinistre,True,part_choose.w/3)
            text_consigne = "APPUYER SUR UN ELEMENT NON EQUIPER (click millieu) AFIN DE LE SELECTIONNER"
            taille4 = check_size_opti(text_consigne,sinistre,True, part_choose.w - 50)
            dict_data_item["taille1"] = taille1
            dict_data_item["taille2_"] = taille2_
            dict_data_item["taille3"] = taille3
            dict_data_item["taille4"] = taille4
        """
        
        taille1 = dict_data_item["taille1"]
        taille2_ = dict_data_item["taille2_"]
        taille3 = dict_data_item["taille3"]
        taille4 = dict_data_item["taille4"]
        text_consigne = "APPUYER SUR UN ELEMENT NON EQUIPER (click millieu) AFIN DE LE SELECTIONNER"
        global joueur
        marge_x = [part_item.x + 50, part_item.x + part_item.w/2, part_item.x + part_item.w - 50] * 3
        marge_x2 = [part_choose.x + 50, part_choose.x + part_choose.w/2, part_choose.x + part_choose.w - 50] 
        write = False
        marge_y_bonus = [30,110,180]
        mode_change = False
        item_choose = None
        can_left = False
        default_size = 75,75
        time = []
        global can_draw
        can_draw = [False]
        start_time =[]
        text_healz = "Appuyer sur o pour fermer l'inventaire !"
        mettre_fond_transparent((rect_screen.w,rect_screen.h),50,(200,200,200))
        draw_text(text_healz, pygame.font.SysFont(arial,40),(0,0,0),rect_screen.x + rect_screen.w/2 - get_dimension(text_healz, arial,40)[0]/2, rect_screen.h - 150)
        sauvegarde_rapide = False
        wait = False
        elt2,elt1 = None,None
            
        while True:
            for event in [pygame.event.poll()]:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        pause = True
                        pygame.mixer.music.pause()
                    elif event.key == pygame.K_u:
                        pause = False
                        pygame.mixer.music.unpause()
                    elif event.key == pygame.K_SPACE:
                        pygame.mixer.music.fadeout(1000)
                        make_music(os.listdir("playlist_music"), "switch")
                    elif event.key == pygame.K_r:
                        pygame.mixer.music.rewind()
                    elif event.key == pygame.K_KP6:
                        volume = get_volume(1)
                    elif event.key == pygame.K_KP4:
                        volume = get_volume(-1)
                    elif event.key == pygame.K_y:
                        make_sauvegarde(file_full,Ingame = True,cryptage = False)
                        sauvegarde_rapide = True
                if sauvegarde_rapide:
                    if not wait:
                        time_start = pygame.time.get_ticks()
                        time_elapsed= 0
                        wait = True
                    time_elapsed = pygame.time.get_ticks() - time_start
                    screen.fill((100,100,100),(rect_screen.w/2 - get_dimension("Sauvegarde effectuée", csm, 20)[0]/2, 20, get_dimension("Sauvegarde effectuée", csm, 20)[0],get_dimension("Sauvegarde effectuée", csm, 20)[1] ))
                    center_screen("Sauvegarde effectuée", comic_sans_ms, get_dimension("Sauvegarde effectuée", csm, 20), 20, False)
                    if time_elapsed >= 1000:
                        screen.fill((100,100,100),(rect_screen.w/2 - get_dimension("Sauvegarde effectuée", csm, 20)[0]/2, 20, get_dimension("Sauvegarde effectuée", csm, 20)[0],get_dimension("Sauvegarde effectuée", csm, 20)[1] ))
                        sauvegarde_rapide = False
                        wait = False
                        del time_elapsed
                        del time_start
                if event.type == pygame.QUIT:
                     running = left_game()
                mouse = pygame.mouse.get_pos()
                all_touch_item = []
                all_rect_item_choose = []
                screen.fill((200,200,200), part_item)
                screen.fill((200,200,200), part_info)
                screen.fill((200,200,200), part_choose)
                draw_in(text_consigne,'',part_choose,taille4,color_pick["bordeaux"],sinistre,25, part_choose.h - get_dimension(text_consigne,sinistre,taille4,False,True)[1] ,False,True)
                pygame.draw.rect(screen,(12,56,100), part_item, 2)
                pygame.draw.rect(screen,(12,56,100), part_info, 2)
                pygame.draw.rect(screen,(12,56,100), part_choose, 2)
                color_quit = (0,0,0) if not rect_quitter.collidepoint(mouse) else (200,0,0)
                screen.blit(change_color_img(image_delete,color_quit),rect_quitter)
                if color_quit == (200,0,0):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        can_left = True
                        break
                text = "VOICI VOS ITEMS DU SAC"     
                draw_in(text,"",part_item,taille1,(0,0,0),sinistre,part_item.w/2 - get_dimension(text,sinistre,taille1,False,True)[0]/2,10,False,True)
                text = "VOICI VOS ITEMS ACTIF"
                draw_in(text,"",part_choose,taille2_,(0,0,0),sinistre,part_choose.w/2 - get_dimension(text,sinistre,taille2_,False,True)[0]/2,10,False,True)
                text = "DESCRIPTION"
                draw_in(text,"",part_info,taille3,(0,0,0),sinistre,part_info.w/2 - get_dimension(text,sinistre,taille3,False,True)[0]/2,10,False,True)
                i = 0          
                for item in joueur["item_bag"]:
                    bonus = []
                    nom_bonus = []
                    if i <= 2:
                        marge_y = 50
                    elif i > 2 and i <=5:
                        marge_y = 120
                    else:
                        marge_y = 180
                    img = pygame.image.load(item["img"])
                    img = pygame.transform.scale(img, default_size)
                    if "defence" in item["fonction"]:
                        bonus.append(item["bonus_defence"])
                        nom_bonus.append("defence")
                    if "attaque" in item["fonction"]:
                        bonus.append(item["bonus_attaque"])
                        nom_bonus.append("attaque")
                    if "endurance" in item["fonction"]:
                        bonus.append(item["bonus_endurance"])
                        nom_bonus.append("endurance")
                                    
                    position = pygame.Rect(marge_x[i] - img.get_rect()[2]/2, part_item.y + marge_y,img.get_rect()[2],img.get_rect()[3])                
                    screen.blit(img, position)
                    touche_item = {"rect_case" : position, "nom" : item["nom"], "bonus" : bonus,"img" : img, "fonction" : item["fonction"],"nom_bonus" : nom_bonus,
                                   "item" : item, "description" : item["description"], "id" : item["id"]}
                    i+=1
                    all_touch_item.append(touche_item)              
                
                for elt in all_touch_item:
                    if elt["rect_case"].collidepoint(mouse):
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:                          
                            item_choose = elt["item"]
                            if item_choose in joueur["stat_joueur"]["item"]:
                                mode_change = False
                                text1 = "Cette element est deja a votre actif !"
                                time_start = pygame.time.get_ticks() # On enregistre le temps de début
                                time_elapsed = 0
                                while time_elapsed <= 1000:
                                    screen.fill((200,200,200),(part_item.x+part_item.w/2 - get_dimension(text1,sinistre,20,False,True)[0]/2,
                                                           part_item.y + part_item.h - get_dimension(text1,sinistre,20,False,True)[1],
                                                           get_dimension(text1,sinistre,20,False,True)[0],
                                                           get_dimension(text1,sinistre,20,False,True)[1] - 2))
                                    draw_in(text1,0,part_item,20,color_pick["bordeaux"],sinistre,part_item.w/2 - get_dimension(text1,sinistre,20,False,True)[0]/2,
                                            part_item.h - get_dimension(text1,sinistre,20,False,True)[1],False,True)
                                    i = 0
                                    for item in joueur["stat_joueur"]["item"]:
                                        img = pygame.image.load(item["img"])
                                        img = pygame.transform.scale(img,default_size)
                                        position = pygame.Rect(marge_x2[i] - img.get_rect()[2]/2, part_choose.y + 60,img.get_rect()[2],img.get_rect()[3])
                                        rect_item_choose = {"rect" : position, "item" : item}
                                        all_rect_item_choose.append(rect_item_choose)
                                        screen.blit(img, position)
                                        i+=1
                                    pygame.display.flip()
                                    time_elapsed = pygame.time.get_ticks() - time_start
                                screen.fill((200,200,200),(part_item.x+part_item.w/2 - get_dimension(text1,sinistre,20,False,True)[0]/2,
                                                           part_item.y + part_item.h - get_dimension(text1,sinistre,20,False,True)[1],
                                                           get_dimension(text1,sinistre,20,False,True)[0],
                                                           get_dimension(text1,sinistre,20,False,True)[1] -2))
                            else:
                                text_consigne = "MAINTENANT CLICK SUR UN ELEMENT DANS LES ITEMS ACTIFS POUR LE REMPLACER"
                                taille4 = check_size_opti(text_consigne,sinistre,True,part_choose.w - 50)
                                mode_change = True                          
                        
                        if (event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP) and event.button == 1:
                            pygame.event.clear()
                            taille2 = []
                            all_phrase_bonus = []
                            write = False
                            elt1,elt2 = elt["img"],pygame.Rect(part_info.x + part_info.w/2 - elt["rect_case"].w/2, part_info.y + 50,elt["img"].get_rect()[2],elt["img"].get_rect()[3])
                            phrase_nom = f"{elt['nom']}"
                            line = elt["id"]["line"]
                            coupage = elt["id"]["coupage"]
                            height_desc = elt["id"]["height"]
                            desc = elt["description"]
                            i = 0                        
                            for bonus in elt["bonus"]:
                                phrase_bonus = f"{bonus * 100}% de bonus {elt['nom_bonus'][i]}"
                                i+=1
                                all_phrase_bonus.append(phrase_bonus)
                i = 0
                for item in joueur["stat_joueur"]["item"]:
                    img = pygame.image.load(item["img"])
                    img = pygame.transform.scale(img,default_size)
                    position = pygame.Rect(marge_x2[i] - img.get_rect()[2]/2, part_choose.y + 60,img.get_rect()[2],img.get_rect()[3])
                    rect_item_choose = {"rect" : position, "item" : item}
                    all_rect_item_choose.append(rect_item_choose)
                    screen.blit(img, position)
                    i+=1
                z = 0
                for rect in all_rect_item_choose:
                    if rect["rect"].collidepoint(mouse):
                        if (pygame.mouse.get_pressed()[1] or pygame.mouse.get_pressed()[2] or pygame.mouse.get_pressed()[0]) and mode_change:
                            valeur_item = all_rect_item_choose[z]["item"]
                            text_consigne = "APPUYER SUR UN ELEMENT NON EQUIPER (click millieu) AFIN DE LE SELECTIONNER"
                            if mode_change:
                                i = 0                          
                                for item in joueur["stat_joueur"]["item"]:
                                    if item == valeur_item:                             
                                        joueur["stat_joueur"]["item"][i] = item_choose
                                        break
                                    i+=1
                    z+=1
                try:
                    screen.blit(elt1,elt2)
                    retour_ligne = elt2.x - part_info.x
                    draw_in("Nom : ","",elt2,18,(0,0,0),sinistre,-retour_ligne + 5,elt2.h - 10,False,True)
                    draw_in(phrase_nom,"",elt2,18,(0,0,0),sinistre,-retour_ligne + 5 + get_dimension("Nom : ", sinistre, 18, False,True)[0],elt2.h -10,False,True)
                    count_h = 0
                    for i in range(len(all_phrase_bonus)):                    
                        draw_in(all_phrase_bonus[i].upper(),"",elt2,13,(0,0,0),sinistre,-retour_ligne + 5
                                ,elt2.h -10 + get_dimension(phrase_nom,sinistre,20,False,True)[1] + (get_dimension(phrase_nom,sinistre,15,False,True)[1]*i),False,True)
                        count_h = elt2.h -10+ get_dimension(phrase_nom,sinistre,20,False,True)[1] + (get_dimension(phrase_nom,sinistre,15,False,True)[1]*i)
                    encadrer_text(part_info.x+5,elt2.y + count_h+20,(0,0,0),part_info.w - 10,height_desc, desc,coupage,line,(255,255,255),(0,50,50))
                    pygame.display.update(part_info)  
                except:
                    pass

                key = pygame.key.get_pressed()
                if key[pygame.K_o] or event.type == pygame.KEYDOWN and event.key == pygame.K_o:
                    can_left = True
                    break
                make_music()
                pygame.display.flip()
            if can_left:
                break
            
                
        
    
    def draw_text(text, font = comic_sans_ms, color = (0,0,0), x = 0, y = 0):
        """
            dessiner un texte a une position donné
            :param 1: text qu'on veut dessiner
            :param 2: font qu'utilise le texte
            :param 3: couleur du texte
            :param 4: coordonne x ou le dessiner
            :param 5: coordonne y ou le dessiner
            :CU: arg 1 est un str, arg 2 est de type font.FONT ou font.SysFont, arg 3 est un rbg, arg 4 et 5 sont des int
        """
        global text_
        text_ = font.render(text, True, color)
        screen.blit(text_, (x,y))
        
    def draw_in(text, location,location_pos,size,color,font_choose,margex,margey, center = False, font_import = False, transparancy = None,surface = screen):
        """
            fonction pour dessiner un text dans un element precis avec une marge x et y
            :param 1: le text qu'on veut dessiner
            :param 2: erreur de code (rentrer n'importe quoi)
            :param 3: rect de l'element viser
            :param 4: size du text
            :param 5: couleur du text
            :param 6: font du texte
            :param 7: booléen pour centrer le texte ou non
            :param 8: booléen pour savoir si la font est importé
        """
        global text_
        if not font_import:
            font = pygame.font.SysFont(font_choose, size)
        else:
            font = pygame.font.Font(font_choose,size)
        text_ = font.render(text, True, color)
        if transparancy != None:
            text_.set_alpha(127)
        text_rect = text_.get_rect()
        if center == False and surface == screen:
            surface.blit(text_, (location_pos.x + margex, location_pos.y + margey))
        elif center == True and surface == screen:
            surface.blit(text_, (location_pos.x + location_pos.w/2 - get_dimension(text, font_choose,size)[0]/2, location_pos.y + location_pos.h/2 - get_dimension(text, font_choose,size)[1]/2))
        if surface != screen:
            surface.blit(text_,(margex,margey))
            
    def center_screen(text,font,dimension,y, center_y, margex = 0, margey = 0):
        """
            permet de center un "text" avec une "font" a un niveau "y" ou de centrer un text au millieu de l'ecran si
            center_y = True
        """
        if center_y == False:
            draw_text(text, font,(0,0,0), rect_screen.w/2 - dimension[0]/2 + margex, y + margey)
        else:
            draw_text(text, font,(0,0,0), rect_screen.w/2 - dimension[0]/2, rect_screen.h/2 - dimension[1]/2)

    def arrondir(value):
        """
            permet d'arrondir un chiffre, la fonction round existe mais pour 0.5 elle arrondie aux chiffre inferieur et pas au superieur
        """
        if value - 0.5 < int(value):
            return round(value)
        else:
            return int(value) + 1
                       
    global input_nom
    input_nom = pygame.font.Font(None,25)
    global input_user
    input_user = ''
    global degat_encaissé
    degat_encaissé = []
    global degat_ennemie
    degat_ennemie = []
    global energy_cost
    energy_cost = []
    indice_combat = 0
    mort = False
    can_attack = True
    debut_combat = False
    click = 0
    tour_effect = 0
    log = False
    limite_fichier = 10
    global new_data
    new_data = False
    max_sauvegarde = 0
    global click_log
    click_log = 0
    global getting
    getting = False
    tour_sans_utilise = 0
    tour_sans_utilise_ennemie = 0
    global attaque_in_effect
    attaque_in_effect = None
    global text_appear
    text_appear = False
    global cooldown
    cooldown = 0
    global reduction_attque
    reduction_attaque = 0
    combat = False
    numero = ""
    in_log = False
    global end_game
    end_game = False
    def do_input():
        """
            fonction pour generaliser la creation d'input mais jamais faite.. a faire
        """
        pass

    def adjust_all_stat(joueur : dict, level_gagner : int):
        """
            Fonction pour ajuster les stats du joueur en fonction des niveaux gagner
            :param 1: joueur est un dictionnaire contenant toute les informations du joueur
            :param 2: level_gagner est un int qui indique le nombre de level gagner
            :Cu: param 1 est dict et param 2 est un int
        """
        amount = 0.5
        if joueur["class"] == "Guerrier":
            joueur["stat_joueur"]["force"] = joueur["stat_joueur"]["force"] + amount * level_gagner if joueur["stat_joueur"]["force"] + amount*level_gagner <= 20 else 20
            joueur["stat_joueur"]["agilite"] = joueur["stat_joueur"]["agilite"] +  amount * level_gagner if joueur["stat_joueur"]["agilite"] + amount*level_gagner <= 20 else 20
            joueur["stat_joueur"]["vitesse"] = joueur["stat_joueur"]["vitesse"]  +amount * level_gagner if joueur["stat_joueur"]["vitesse"] + amount*level_gagner <=20 else 20
            joueur["stat_joueur"]["vie"] = joueur["stat_joueur"]["vie"] + amount * level_gagner if joueur["stat_joueur"]["vie"] + amount*level_gagner <=280 else 280
            joueur["stat_joueur"]["vie_max"] = joueur["stat_joueur"]["vie_max"]+amount * level_gagner if joueur["stat_joueur"]["vie_max"] + amount*level_gagner <=280 else  280
            joueur["stat_joueur"]["energie"] = joueur["stat_joueur"]["energie"]+amount* level_gagner if joueur["stat_joueur"]["energie"] + amount*level_gagner <=150 else 150
            joueur["stat_joueur"]["energie_max"] = joueur["stat_joueur"]["energie_max"]+amount* level_gagner if joueur["stat_joueur"]["energie_max"] + amount*level_gagner <=150 else 150
            joueur["stat_joueur"]["reflexe"] = joueur["stat_joueur"]["reflexe"]+amount * level_gagner if joueur["stat_joueur"]["reflexe"] + amount*level_gagner <=20 else 20
        
        elif joueur["class"] == "Assassin":
            joueur["stat_joueur"]["force"] = joueur["stat_joueur"]["force"] + amount * level_gagner if joueur["stat_joueur"]["force"] + amount*level_gagner <= 20 else 20
            joueur["stat_joueur"]["agilite"] = joueur["stat_joueur"]["agilite"] +  amount * level_gagner if joueur["stat_joueur"]["agilite"] + amount*level_gagner <= 20 else 20
            joueur["stat_joueur"]["vitesse"] = joueur["stat_joueur"]["vitesse"]  + amount * level_gagner if joueur["stat_joueur"]["vitesse"] + amount*level_gagner <=20 else 20
            joueur["stat_joueur"]["vie"] = joueur["stat_joueur"]["vie"] + amount * level_gagner if joueur["stat_joueur"]["vie"] + amount*level_gagner <=200 else 200
            joueur["stat_joueur"]["vie_max"] = joueur["stat_joueur"]["vie_max"]+amount * level_gagner if joueur["stat_joueur"]["vie_max"] + amount*level_gagner <=200 else  200
            joueur["stat_joueur"]["energie"] = joueur["stat_joueur"]["energie"]+amount* level_gagner if joueur["stat_joueur"]["energie"] + amount*level_gagner <=200 else 200
            joueur["stat_joueur"]["energie_max"] = joueur["stat_joueur"]["energie_max"]+amount* level_gagner if joueur["stat_joueur"]["energie_max"] + amount*level_gagner <=200 else 200
            joueur["stat_joueur"]["reflexe"] = joueur["stat_joueur"]["reflexe"]+amount * level_gagner if joueur["stat_joueur"]["reflexe"] + amount*level_gagner <=20 else 20
        else:
            joueur["stat_joueur"]["magie"] = joueur["stat_joueur"]["magie"] + amount * level_gagner if joueur["stat_joueur"]["magie"] + amount*level_gagner <= 20 else 20
            joueur["stat_joueur"]["agilite"] = joueur["stat_joueur"]["agilite"] +  amount * level_gagner if joueur["stat_joueur"]["agilite"] + amount*level_gagner <= 20 else 20
            joueur["stat_joueur"]["vitesse"] = joueur["stat_joueur"]["vitesse"]  +amount * level_gagner if joueur["stat_joueur"]["vitesse"] + amount*level_gagner <=20 else 20
            joueur["stat_joueur"]["vie"] = joueur["stat_joueur"]["vie"] + amount * level_gagner if joueur["stat_joueur"]["vie"] + amount*level_gagner <=280 else 280
            joueur["stat_joueur"]["vie_max"] = joueur["stat_joueur"]["vie_max"]+amount * level_gagner if joueur["stat_joueur"]["vie_max"] + amount*level_gagner <=180 else  180
            joueur["stat_joueur"]["energie"] = joueur["stat_joueur"]["energie"]+amount* level_gagner if joueur["stat_joueur"]["energie"] + amount*level_gagner <=250 else 250
            joueur["stat_joueur"]["energie_max"] = joueur["stat_joueur"]["energie_max"]+amount* level_gagner if joueur["stat_joueur"]["energie_max"] + amount*level_gagner <=250 else 250
            joueur["stat_joueur"]["reflexe"] = joueur["stat_joueur"]["reflexe"]+amount * level_gagner if joueur["stat_joueur"]["reflexe"] + amount*level_gagner <=20 else 20


    def change_text(locationx, locationy, width, heigh, color):
        """
            fonction pour remplir la zone avec un rect definit;
            :param1: position en x de la barre
            :param2: position en y de la barre
            :param3: longueur de la barre
            :param4: largeur de la barre
        """
        screen.fill(color, (locationx, locationy, width, heigh))

    def write2(file=file_full, save_number=0):
        """
            fonction ecrivant le numero sauvegarde du fichier dit file
            :param1: chemin d'acces au fichier
            :param2: numero de save
        """
        with open(file, "a") as fichier:
            fichier.write(f"\nsave : {save_number}\n")

    def check_size(taille, case, text1, text2=None, font=sinistre):
        """
            fonction pour modifier la taille d'un text part rapport a une case (fonction exclusive au log
            donc la comparaison est deja defini)
            :param1: taille de du text
            :param2: rect de la case
            :param3: premier text
            :param4: suivi du deuxieme si y'a
            :param5: font du texte
        """
        try:
            font_object = pygame.font.Font(font, taille)
        except:
            font_object = pygame.font.SysFont(font, taille)
        text1_width, text1_height = font_object.size(text1)
        total_width = text1_width
        if text2 is not None:
            text2_width, text2_height = font_object.size(text2)
            total_width += text2_width
            if total_width <= case.w:
                while total_width <= case.w - 20:
                    taille += 2
                    try:
                        font_object = pygame.font.Font(font, taille)
                    except:
                        font_object = pygame.font.SysFont(font, taille)
                    text1_width, text1_height = font_object.size(text1)
                    text2_width, text2_height = font_object.size(text2)
                    total_width = text1_width + text2_width
                    if taille > 35:
                        break
            else:                
                while total_width > case.w:
                    taille -= 2
                    try:
                        font_object = pygame.font.Font(font, taille)
                    except:
                        font_object = pygame.font.SysFont(font, taille)
                    text1_width, text1_height = font_object.size(text1)
                    total_width = text1_width
                    if taille > 35:
                        break
            taille -= 1
        else:
            while total_width <= case.w / 2 + 20:
                taille += 2
                try:
                    font_object = pygame.font.Font(font, taille)
                except:
                    font_object = pygame.font.SysFont(font, taille)
                text1_width, text1_height = font_object.size(text1)
                total_width = text1_width
                if taille > 35:
                    break
            while total_width > case.w/2 +20:
                taille -= 2
                try:
                    font_object = pygame.font.Font(font, taille)
                except:
                    font_object = pygame.font.SysFont(font, taille)
                text1_width, text1_height = font_object.size(text1)
                total_width = text1_width
                if taille > 35:
                    break
        return taille
    
    global delete
    delete = False
    global first_data
    first_data = False
    etat_tuto = 'not achieve'
    global spawn_joueur
    spanw_joueur = None    
    global spawn_equivalent_rect
    spawn_equivalent_rect = {"haut" : [rect_screen.w/2,0], "bas" : [rect_screen.w/2, rect_screen.h], "droit" : [rect_screen.w, rect_screen.h/2], "gauche" : [0,rect_screen.h/2]}
    global equivalent
    equivalent = {"haut" : "bas","bas":"haut","gauche":"droit","droit":"gauche"}
    
    def make_sauvegarde(file = file_full,Ingame = True,cryptage = True):
        """
            fonction permettant de sauvegarder les données users
        """
        global save
        global nom
        global class_
        global etat_tuto
        global going_back
        global went_back
        global joueur
        global nb_room
        global mot_de_passe_user
        global data_secu
        global repos_left
        with open(file, "r") as f:
            fichier_recup = f.readlines()
        try:
            with open(file, "w") as fichier:
                attribut = ["nom\n",f"{nom}\n","class\n",f"{class_}\n","exp\n",f"{joueur['stat_joueur']['exp']}\n","gold\n",
                            f"{joueur['stat_joueur']['or']}\n","exp_need\n",f"{joueur['stat_joueur']['exp_needed']}\n","level\n",
                            f"{joueur['level']}\n","repos_left\n",f"{repos_left}\n"]
                fichier.write(f"{save}\n")
                if data_secu:
                    fichier.write("mdp\n")
                    fichier.write(f"{mot_de_passe_user}\n")
                for i in attribut:
                    fichier.write(i)
                attribut = ["force",f"{joueur['stat_joueur']['force']}","vol de vie",f"{joueur['stat_joueur']['vol_de_vie']}",
                            "vie",f"{joueur['stat_joueur']['vie']}","reflexe",f"{joueur['stat_joueur']['reflexe']}"
                            ,"energie",f"{joueur['stat_joueur']['energie']}","magie",f"{joueur['stat_joueur']['magie']}",
                            "vitesse",f"{joueur['stat_joueur']['vitesse']}","agilite",f"{joueur['stat_joueur']['agilite']}","item1",f"{joueur['stat_joueur']['item'][0]['nom_variable']}", "item2",
                            f"{joueur['stat_joueur']['item'][1]['nom_variable']}","item3", f"{joueur['stat_joueur']['item'][2]['nom_variable']}"]
                for i in range(len(attribut)):
                    fichier.write(f"{attribut[i]}\n")
                fichier.write("max vie\n")
                fichier.write(f"{joueur['stat_joueur']['vie_max']}\n")
                fichier.write("max energie\n")
                fichier.write(f"{joueur['stat_joueur']['energie_max']}\n")
                fichier.write("died_in_game\n")
                fichier.write(f"{died_in_game}\n")
                fichier.write("end_game\n")
                fichier.write(f"{end_game}\n")
                list_item = [element["nom_variable"] for element in joueur['item_bag']]
                fichier.write("item_bag\n")
                json.dump(list_item,fichier)
                fichier.write("\n")
                fichier.write("TUTO_ACHIEVE\n")
                if Ingame:
                    fichier.write("room_already_logged\n")
                    attribut = ["heal_room",f"{heal_room}","room_passed",f"{room_passed}","current_room",f"{current_room}","switch_collision",f"{switch_collision}","stage",f"{stage}","boss_room",f"{boss_room}",
                                "nb_room", f"{nb_room}","room_exist", f"{room_exist}","room_visited",f"{room_visited}","room_actu",f"{room_actu}","can_switch",f"{can_switch}","going_back",f"{going_back}","cooldown",f"{cooldown_heal_room}","have_heal",f"{have_heal_room}"]
                    for i in attribut:
                        fichier.write(f"{i}\n")
                    fichier.write("rooms\n")
                    json.dump(rooms,fichier)
                    fichier.write("\n")
                    fichier.write("collision1\n")
                    json.dump(collision,fichier)
                    fichier.write("\n")
                    fichier.write("collision2\n")
                    json.dump(collision_,fichier)
                    fichier.write("\n")
                    fichier.write("heal_log\n")
                    json.dump(heal_rooms,fichier)
                    fichier.write("\n")
                    fichier.write("recup_switch\n")
                    json.dump(switch_collisions,fichier)
                    fichier.write("\n")
                    fichier.write("recup_stagz\n")
                    json.dump(stages,fichier)
                    fichier.write("\n")
                    fichier.write("went_back\n")
                    fichier.write(f"{went_back}\n")
                    fichier.write("mask_ennemie\n")
                    json.dump(mask_ennemie,fichier)
                    fichier.write("\n")
        except:
            with open(file, "w") as fichier:
                for i, line in enumerate(fichier_recup,1):
                    fichier.writelines(line)
                fichier.write("votre dossier a été récupéré apres un bug, les données n'on pas été sauvegarder")
                fichier.write("signalez le bug a l'addresse suivante : sylvio0801@gmail.com. Désolé !")
        
        def crypt(file_key,file):
            """
                fonction permettant de cripter les fichiers a la sortie du jeux.
                :param1: chemin d'accès de ma key
                :param2: chemin d'accès du fichier
            """
            with open(file_key, 'rb') as filekey:
               key = filekey.read()
            with open(file,"rb") as filee:
                original = filee.read()
            fernet = cryptography.fernet.Fernet(key)
            encrypt = fernet.encrypt(original)
            with open(file,"wb") as filee:
                filee.write(encrypt)
        
        if cryptage:
            for i in range(len(file_name)):
                text = f"key/{file_name[i]}.key"
                text_full = f"file/{file_name[i]}.txt"
                try:
                    crypt(text,text_full)
                except:
                    pass
                
        
    
    def left_game(id = 0,Ingame = True, restart_game = False):
        """
            fonction pour demarrer le process quand on quitte la game
        """
        if id ==0:
            make_sauvegarde(file_full,Ingame)
        pygame.quit()
        sys.exit()

    def text_ephemere(text, font, size, temps, posx, posy, font_import, background, color = (0,0,0), surface = contener_):
        """
            Fonction permettant de faire apparaitre un text pendant un labs de temps, apres celui-ci sera effacé
            :param1: text qu'on souhaite ecrire
            :param2: font du texte
            :param3: size du text
            :param4: temps de l'apparition
            :param5: ajout en x de la position celon la surface (ex, surface.x + posx)
            :param6: ajout en y
            :param7: informer si la police est importer ou non
            :param8: le fond de la surface
            :param9: color du texte
            :param10: surface référence
        """
        draw_in(text, "useless", surface, size, color, font,posx,posy, False, font_import)
        pygame.display.flip()
        pygame.time.delay(temps)
        change_text(surface.x+posx,surface.y+posy, get_dimension(text, font, size, False, font_import)[0],get_dimension(text, font, size, False, font_import)[1], background)
        pygame.display.flip()

    def uptade_data(bonus_enchainement_combat,id=0,bonus=0):
        """
            fonction permettant de recompencer le joueur et de sauvegarder les degats qu'il a prit
            :param1: bonus de récompense si on enchaine les combats
        """
        if id == 0:
            joueur['stat_joueur']['or'] += ennemie["loot"]["gold_drop"]
            joueur['stat_joueur']['exp'] += ennemie["loot"]["xp_drop"] + ennemie["loot"]["xp_drop"] * bonus_enchainement_combat
            somme = 0
            for i in degat_ennemie:
                somme += i
            joueur["stat_joueur"]["vie"] =  joueur["stat_joueur"]["vie"] * (1+bonus["defence"]) - somme
            joueur["stat_joueur"]["vie"] = joueur["stat_joueur"]["vie_max"] if joueur["stat_joueur"]["vie"] > joueur["stat_joueur"]["vie_max"] else joueur["stat_joueur"]["vie"]

            somme = 0
            for i in energy_cost:
                somme += i
            joueur["stat_joueur"]["energie"] = joueur["stat_joueur"]["energie"] * (1+bonus["endurance"]) - somme
            joueur["stat_joueur"]["energie"] = joueur["stat_joueur"]["energie_max"] if joueur["stat_joueur"]["energie"] > joueur["stat_joueur"]["energie_max"] else joueur["stat_joueur"]["energie"]
            level_gagner = 0
            while joueur['stat_joueur']['exp'] > joueur['stat_joueur']['exp_needed']:
                joueur['stat_joueur']['exp'] -= joueur['stat_joueur']['exp_needed']
                joueur['stat_joueur']['exp_needed'] = joueur['stat_joueur']['exp_needed'] * 3
                level_gagner += 1
            return joueur,level_gagner
    
    def mettre_fond_transparent(taille : tuple, transparence : int, couleur : tuple, pos = (0,0)):
        """
            fonction permettant de mettre un fond transparent a l'aide d'une surface
            :param1: la taille de la surface (dimension w;h)
            :param2: la transparence en pourcentage
            :param3: la couleur de la transparence
            :param4: la position ou dessiner la surfacee
        """
        s = pygame.Surface((taille), pygame.SRCALPHA)
        pygame.draw.rect(s, (couleur[0],couleur[1],couleur[2],254*(50/100)), s.get_rect())                      
        screen.blit(s,pos)
    
    def decrypt_file(filename,nom):
        """
            fonction permettant de decrypter un fichier si celui est crypter
            :param1: chemin d'acces au fichier .txt
            :param2: nom du fichier .txt
        """
        with open(f"key/{nom}.key", "rb") as f:
            key = f.read()
        fernet = cryptography.fernet.Fernet(key)
        with open(filename, "rb") as f:
            encrypted_data = f.read()
        decrypted_data = fernet.decrypt(encrypted_data)
        with open(filename, "wb") as f:
            f.write(decrypted_data)
    global data_save
    data_save = []
    
    def contact():
        global input_nom
        dict_active = {"active_name" : {"active" : False,"valid" : False,"input" : "Nom","research": "Nom", "max" : 20}, "active_object" : {"active" : False,"valid" : False,"input" : "Objet","research" : "Objet", "max" : 30}, "active_desc" : {"active" : False,"valid" : False,"input" : "Message","research" : "Message", "max" : 769},
                       "active_adresse" : {"active" : False,"valid" : False,"input" : "votre Email (non obligatoire)","research" : "votre Email (non obligatoire)", "max" : 40}}
        key_dict = [key for key in dict_active.keys()]
        input_name = 'Nom'
        input_objet = 'Objet'
        input_desc = 'Message'
        input_adresse = 'votre Email (non obligatoire)'
        adresse = "sylvio0801@gmail.com"
        render_y = 5
        w = 150
        h= 50
        width__ = 150
        height__ = 50
        def verif_dict(dict_):
            if "name" in dict_:
                return input_name
            elif "object" in dict_:
                return input_objet
            elif "desc" in dict_:
                return input_desc
            elif "adresse" in dict_:
                return input_adresse
    
        def look_valid(dict_ = dict_active):
            for key,values in dict_active.items():
                if values["input"] == values["research"] and key != "active_adresse":
                    return False
            return True
        coupage = [0]
        line = 1
        c_ = (0,100,100)
        coup_d = 0
        finish = False
        wait = False
        max_object = 30
        next_time = 0
        global actual_line
        actual_line = 0
        while 1:
            current_time = pygame.time.get_ticks()
            mouse = pygame.mouse.get_pos()
            screen.fill((255,255,255))
            if finish:
                center_screen("Envoyer avec succès !", comic_sans_ms, get_dimension("Envoyer avec succès !", csm, 20), 0, False)
                if not wait:
                    time_start = pygame.time.get_ticks()
                    time_elapsed= 0
                    wait = True
                time_elapsed = pygame.time.get_ticks() - time_start
                if time_elapsed >= 1000:
                    finish = False
                    wait = False
                    del time_elapsed
                    del time_start
                    return contact()

            rect_barre = pygame.Surface((1,20))
            rect_barre.fill((0,0,0))
            case_contact = pygame.Rect(rect_screen.w- 200,30, 150,50)
            pygame.draw.rect(screen,(0,0,0),case_contact,2)
            draw_in("RETOUR", "", case_contact,30,(0,0,0),arial,5,10)
            send = pygame.Rect(rect_screen.w/2 -width__/2 ,rect_screen.h - 100,width__,height__)
            if send.collidepoint(mouse):
                width__ += 20
                width__ = 200 if width__ >= 200 else width__
            else:
                width__ -= 20
                width__ = 150 if width__ <= 150 else width__
            pygame.draw.rect(screen,c_,send)
            size_text = get_dimension("ENVOYER",arial,30)
            draw_in("ENVOYER", "", send,30,(255,255,255),arial,send.w/2 - size_text[0]/2,10)
            
            #name
            active_dict = dict_active["active_name"]
            surface_name = pygame.Surface((rect_screen.w/2 - 120, 50))
            surface_name.fill((background))
            rect_name = pygame.Rect(100,100,rect_screen.w/2-120,50)
            pygame.draw.rect(surface_name,(0,0,0),(0,0,rect_screen.w/2 - 120,50),2) 
            input_nom_r = input_nom.render(active_dict["input"],True,(255,255,255))
            surface_name.blit(input_nom_r,(5,5))
            if active_dict['active']:
                surface_name.blit(rect_barre,(5 + input_nom.size(active_dict["input"])[0],5))
            screen.blit(surface_name,(100,100))
            
            #email
            active_dict = dict_active["active_adresse"]
            surface_email = pygame.Surface((rect_screen.w/2 - 120, 50))
            surface_email.fill((background))
            rect_email = pygame.Rect(100+ rect_screen.w/2 -120 + 50,100,rect_screen.w/2-120,50)
            pygame.draw.rect(surface_email,(0,0,0),(0,0,rect_screen.w/2 - 120,50),2) 
            input_nom_r = input_nom.render(active_dict["input"],True,(255,255,255))
            surface_email.blit(input_nom_r,(5,5))
            if active_dict['active']:
                surface_email.blit(rect_barre,(5 + input_nom.size(active_dict["input"])[0],5))
            screen.blit(surface_email,(100 + rect_screen.w/2 -120 + 50,100))
            
            #object
            active_dict = dict_active["active_object"]
            surface_object = pygame.Surface((300,50))
            surface_object.fill((background))
            rect_object = pygame.Rect(100,180,300,50)
            pygame.draw.rect(surface_object,(0,0,0),(0,0,300,50),2)
            caractere = len(active_dict["input"])
            #ameliorer les input encore. 25/04/2023
            if input_nom.size(active_dict["input"])[0] >= rect_object.w - 20:
                coupagedebut = True
            else:
                coupagedebut = False
            input_nom_r = input_nom.render(active_dict["input"][coup_d:],True,(255,255,255))
            surface_object.blit(input_nom_r,(5,5))
            if active_dict['active']:
                surface_object.blit(rect_barre,(5 + input_nom.size(active_dict["input"][coup_d:])[0],5))
            screen.blit(surface_object,(100,180))
            
            #desc
            active_dict = dict_active["active_desc"]
            surface_desc = pygame.Surface((rect_screen.w - 200,rect_screen.h - 400))
            surface_desc.fill((background))
            rect_desc = pygame.Rect(100,250,rect_screen.w-200,rect_screen.h-400)
            pygame.draw.rect(surface_desc,(0,0,0),(0,0,rect_screen.w-200,rect_screen.h-400),2) 
            
            def look_number_line(text = input_nom_r, rect = rect_desc,line = line,coupage = coupage):
                global actual_line
                size = input_nom.size(active_dict["input"][coupage[-1]:])
                real_size = size[0]
                size_ = size[0]
                caractere = len(active_dict["input"])
                if size_ > (rect.w - 30):
                    size_ -= rect.w
                    line += 1
                    actual_line += 1
                    coupage.append(caractere)
                return size,line,coupage
            
            size,line,coupage = look_number_line()
            render_y = [10 + line*30 for line in range(line)]
            for lin in range(line):
                coupagee = coupage[lin]
                try:
                    limite = coupage[lin+1]
                except:
                    limite = len(active_dict["input"])
                input_nom_r = input_nom.render(active_dict["input"][int(coupagee):int(limite)],True,(255,255,255))
                surface_desc.blit(input_nom_r,(5,render_y[lin]))
            if active_dict["active"]:
                surface_desc.blit(rect_barre,(5 + input_nom.size(active_dict["input"][int(coupagee):int(limite)])[0],render_y[lin]))
            screen.blit(surface_desc,(100,250))
            all_rect = [rect_name,rect_object,rect_desc,rect_email]
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if case_contact.collidepoint(mouse):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        return log_host()
                if event.type == pygame.KEYDOWN and (event.key == pygame.K_RSHIFT or event.key == pygame.K_LSHIFT):
                    maj = True
                else:
                    maj = False
                i = 0
                for rect in all_rect:
                    if rect.collidepoint(mouse) and event.type == pygame.MOUSEBUTTONDOWN:
                        dict_active[key_dict[i]]["active"] = not dict_active[key_dict[i]]["active"]
                        name = dict_active[key_dict[i]]["research"]
                        name_base = dict_active[key_dict[i]]["input"]
                        input_ = verif_dict(key_dict[i])
                        if dict_active[key_dict[i]]["active"]:
                            if name_base == input_:
                                dict_active[key_dict[i]]["input"] = ""
                                name_base = ""
                            for key,active in dict_active.items():
                                if not key_dict[i][7:] in key:
                                    active["active"] = False
                                    active["input"] = active["research"] if active["input"] == "" else active["input"]
                    i += 1
                for key,elt in dict_active.items():
                    if elt["active"]:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_BACKSPACE:
                                elt["input"] = elt["input"][:-1]
                                if key == "active_object":
                                    if coupagedebut:
                                        coup_d +=1
                                if key == "active_desc":
                                    if len(elt["input"][coupage[actual_line]:]) <= 0:
                                        line -= 1
                                        actual_line -= 1
                                        line = 1 if line <= 1 else line
                                        render_y.remove(render_y[-1])
                                        coupage.remove(coupage[-1])
                                        actual_line = 0 if actual_line <= 0 else actual_line
                                break
                            elif event.key == pygame.K_SPACE:
                                elt["input"] = elt["input"]+ " "
                                if coupagedebut:
                                    coup_d = coup_d + 1
                                break
                            elif event.key == pygame.K_RETURN:
                                if key == "active_desc":
                                    caractere = len(elt["input"])
                                    line += 1
                                    actual_line += 1
                                    coupage.append(caractere)
                                break
                            else:
                                if elt["max"] > len(elt["input"]):
                                    if key == "active_object":
                                        if coupagedebut:
                                            coup_d = coup_d + 1
                                    text =  f"{event.unicode.upper()}" if maj else f"{event.unicode}"     
                                    elt["input"] += text
                                    next_time = current_time + 200
                                    break
            mouse_click = pygame.mouse.get_pressed()
            mods = pygame.key.get_mods()
            if mods & pygame.KMOD_CAPS:
                maj = True
            else:
                maj = False
            if send.collidepoint(mouse):
                is_valid = look_valid()
                if mouse_click[0] and is_valid:
                    center_screen("Chargement...", comic_sans_ms, get_dimension("Chargement...", csm, 20), 0, False)
                    pygame.display.flip()
                    msg = EmailMessage()
                    msg["From"] = "sylvio0801@gmail.com"
                    dict_active['active_adresse']['input'] = "" if dict_active['active_adresse']['input'] == "votre Email (non obligatoire)" else dict_active['active_adresse']['input']  
                    msg.set_content(f" message de {dict_active['active_name']['input']} - {dict_active['active_adresse']['input']}\n {dict_active['active_desc']['input']}")
                    msg["Subject"] = dict_active["active_object"]["input"]
                    msg["To"] = "sylvio0801@gmail.com"
                    context=ssl.create_default_context()
                    with smtplib.SMTP('smtp.gmail.com', port=587) as smtp:
                        smtp.starttls(context=context)
                        #Clé smtp
                        smtp.login(msg["To"] ,env.get("MDP_EMAIL"))
                        smtp.send_message(msg)
                        finish = True
                if mouse_click[0] and not is_valid:
                    center_screen("Champs invalide", comic_sans_ms, get_dimension("Champs invalide", csm, 20), 0, False)
                    pygame.display.flip()
                    pygame.time.delay(1000)                        
            pygame.display.flip()
            
    def make_suivant_button(mouse,text = "SUIVANT", color = ((0,0,0),(0,100,100)), pos = ((pop_up.x+pop_up.w/2-150/2),(pop_up.y+pop_up.h+50)), longueur = 150, largeur = 30,pop_up = pop_up):
        rect_start = pygame.Rect(pos[0],pos[1],longueur,largeur)
        color_start = color[0] if not rect_start.collidepoint(mouse) else color[1]
        pygame.draw.rect(screen,color_start,rect_start)
        draw_in(text,0,rect_start,25,(255,255,255),arial,rect_start.w/2 - get_dimension(text,arial,25)[0]/2,rect_start.h/2 - get_dimension(text,arial,25)[1]/2)       
        pygame.display.update(rect_start)
        return rect_start
    
    def input_for_mdp(all_case_data,code_mdp):
        active = False
        input_user = ""
        valid = None
        quitter = False
        one_time = False
        input_visu = ""
        voir = False
        image_voir = pygame.transform.scale(pygame.image.load("image_site/oeil_mdp.png"),(40,20))
        image_delete = pygame.transform.scale(pygame.image.load("image_site/image_delete.png"),(40,40))
        coup_d1 = 0
        coup_d2 = 0
        coupagedebut = False
        max_letter = 20
        maj = False
        while True:
            def check_input(input_):
                valid = False                
                if input_user == code_mdp:
                    valid = True
                return valid
            if one_time == False:
                mettre_fond_transparent((rect_screen.w,rect_screen.h),50,(200,200,200))
            pop_up = appear_pop_up()
            if not one_time:
                draw_in("Entrez le mot de passe !", 0, pop_up, 35,color_pick["bordeaux"], csm, pop_up.w/2 - get_dimension("Entrez le mot de passe !",csm,35)[0]/2,-60)
                one_time = True
            mouse = pygame.mouse.get_pos()
            input_place = input_nom.render(input_visu[coup_d2:],True,(255,255,255)) if not voir else input_nom.render(input_user[coup_d1:],True,(255,255,255))
            text_rect = input_visu if not voir else input_user
            box_input = pygame.Rect(pop_up.x + pop_up.w/2 - 140/2,pop_up.y +
                                    pop_up.h/2-32/2,140,32)
            coupagedebut = False
            if input_nom.size(text_rect)[0] > 130:
                coupagedebut = True
            coup_d = coup_d2 if not voir else coup_d1
            screen.blit(input_place, (box_input.x + 5, box_input.y + box_input.h/2 - get_dimension(text_rect[coup_d:],csm,25)[1]/4))
            color = (200,0,0) if not active else (0,200,0)
            pygame.draw.rect(screen,color,box_input,1)
            text_active = "Activer" if active else "Désactiver"
            barre_type = pygame.Surface((1,20))
            barre_type.fill((0,0,0))
            if active:
                input_ = input_visu if not voir else input_user
                screen.blit(barre_type,(box_input.x+5 + input_nom.size(input_[coup_d:])[0],box_input.y + box_input.h/2 - get_dimension(text_rect[coup_d:],csm,25)[1]/4))
            draw_in(text_active,0,box_input,20,(255,255,255),csm,box_input.w/2 - get_dimension(text_active,csm,20)[0]/2,box_input.h)
            rect_quit = pygame.Rect(pop_up.x + 10,pop_up.y+5,40,40)
            rect_voir = pygame.Rect(box_input.x + box_input.w + 10, box_input.y + box_input.h/2 - image_voir.get_rect().h/2, image_voir.get_rect().w,image_voir.get_rect().h)
            text =  "Appuyer pour voir" if not voir  else "vision activer"
            screen.blit(change_color_img(image_voir,(0,0,0)),rect_voir) if not voir else screen.blit(change_color_img(image_voir,(255,0,0)),rect_voir)
            draw_in(text,0,rect_voir,13,(255,255,200),csm,rect_voir.w +10, rect_voir.h/2 - get_dimension(text,csm,13)[1]/2)
            color_quit = (0,0,0) if not rect_quit.collidepoint(mouse) else (100,0,100)
            bord = 1 if not rect_quit.collidepoint(mouse) else 0
            screen.blit(change_color_img(image_delete,(0,0,0)),rect_quit) if bord ==1 else screen.blit(change_color_img(image_delete,(255,0,0)),rect_quit)
            text_ = "Clickez sur l'input" if not active else "Reclick pour désactiver"
            draw_in(text_,0,pop_up,25,(255,255,255),csm,pop_up.w/2 - get_dimension(text_,csm,25)[0]/2,pop_up.h - get_dimension(text_,csm,25)[1])
            pygame.display.flip()
            mods = pygame.key.get_mods()
            # vérifier si la touche Verr Maj est enfoncée
            if mods & pygame.KMOD_CAPS:
                maj = True
            else:
                maj = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RSHIFT] or keys[pygame.K_LSHIFT]:
                maj = True
            else:
                if maj != True:
                    maj = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = left_game(1)                
                if box_input.collidepoint(mouse):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        active = not active
                if rect_quit.collidepoint(mouse):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        quitter = True
                        return log_host(all_case_data)
                if rect_voir.collidepoint(mouse):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        voir = not voir                  
                    
                if event.type == pygame.KEYDOWN and active:
                    if event.key == pygame.K_BACKSPACE:
                        input_user = input_user[:-1]
                        input_visu = input_visu[:-1]
                        coup_d1 = coup_d1 -  1 if coupagedebut else coup_d1
                        coup_d2 = coup_d2 -  1 if coupagedebut else coup_d2
                        coup_d1 = 0 if coup_d1 <= 0 else coup_d1
                        coup_d2 = 0 if coup_d2 <= 0 else coup_d2
                    elif event.key == pygame.K_SPACE and max_letter > len(input_user):
                        input_user = input_user + " "
                        input_visu += "*"
                        coup_d1 = coup_d1 +  1 if coupagedebut else coup_d1
                        coup_d2 = coup_d2 +  1 if coupagedebut else coup_d2
                    elif event.key == pygame.K_RETURN:
                        active = False
                        valid = check_input(input_user)
                        if not valid:
                            draw_in("mauvais mot de passe", 0,pop_up,20,(0,0,0),csm,pop_up.w/2 - get_dimension(
                                "mauvais mot de passe", csm,20)[0]/2, pop_up.h - pop_up.h/4 - get_dimension(
                                "mauvais mot de passe", csm,20)[1]/2)
                            pygame.display.flip()
                            pygame.time.delay(1000)
                        input_user = ""
                        input_visu = ""
                    else:
                        if max_letter > len(input_user):
                            input_user += event.unicode if not maj else event.unicode.upper()
                            input_visu += "*"
                            if coupagedebut:
                                coup_d1 = coup_d1 + 3
                                coup_d2 = coup_d2 + 3
            if valid or quitter:
                break
        return valid
    
    def input_for_login(titre,mode = 1):
        global file_name
        defaul_setting_user = f"sauv{len(file_extension)+1}"
        input_user = f"sauv{len(file_extension)+1}"
        click_mdp = False
        active_mdp = False
        default_setting_mdp = "motdepasse"
        input_mdp = "motdepasse"
        active = False
        valid = False
        input_mdp_visu = ""
        voir = False
        image_voir = pygame.transform.scale(pygame.image.load("image_site/oeil_mdp.png"),(40,20))
        image_cadena = pygame.transform.scale(pygame.image.load("image_site/cadenas.png"),(25,40))
        coup_d1_mdp = 0
        coup_d2_mdp = 0
        coup_d_user = 0
        can_go_out = False                        
        max_letter = 20
        maj = False                        
        file_full = ""
        nom_fichier = ""
        delete = False
        new_data = False
        while 1:
            current_time = pygame.time.get_ticks()
            mouse = pygame.mouse.get_pos()
            screen.fill((200,200,200))
            pop_up = appear_pop_up()
            barre_type = pygame.Surface((1,20))
            barre_type.fill((255,255,255))                        
            rect_start = make_suivant_button(mouse = mouse)            
            case_new = pygame.Rect(pop_up.x - 100, pop_up.y - 100, 100, 50)
            if mode == 1:    
                pygame.draw.rect(screen, (0, 0, 0), case_new, 2)
                draw_in("Log", "", case_new, 30, (0, 0, 0), arial, 5, 10)
            box_input = pygame.Rect(pop_up.x + (pop_up.w / 2 - 140 / 2), pop_up.y + pop_up.h / 2 - 32 / 2, 140,
                                    32)
            letter = len(input_user)
            draw_in(f"{letter}/{max_letter}","",box_input,20,(255,255,255),arial,box_input.w/2 - get_dimension(f"{letter}/{max_letter}",arial,20)[0]/2,box_input.h + 10)
            surface_box = pygame.Surface((140,32))
            color_box = (0, 255, 0)
            color_passive = (255, 0, 0)
            input_place = input_nom.render(input_user[coup_d_user:], True, (255, 255, 255))
            surface_box.blit(input_place,(5,box_input.h / 4))
            
            text = titre
            draw_in(text, 0, pop_up, 25, (0, 0, 0), minecraft_factory,
                    pop_up.w / 2 - get_dimension(text, minecraft_factory, 25, False, True)[0] / 2, -50, False,
                    True)
            coupagedebut = False
            if input_nom.size(input_user)[0] > 130:
                coupagedebut = True
            else:
                coup_d_user = 0
            if active:
                surface_box.blit(barre_type,(5 + input_nom.size(input_user[coup_d_user:])[0],box_input.h / 4))
            screen.blit(surface_box,box_input)
            pygame.draw.rect(screen, color_box, box_input, 2) if active else pygame.draw.rect(screen, color_passive, box_input, 2)

            if not active:
                text = "clickez sur l'input pour activer/desactiver"
            else:
                text = "bien joué"
            draw_in(text, 0, pop_up, 25, (0, 0, 0), sinistre,
                    pop_up.w / 2 - get_dimension(text, sinistre, 25, False, True)[0] / 2, pop_up.h, False, True)
            rect_mdp = pygame.Rect(pop_up.x + pop_up.w/2 - (12 + get_dimension("securiser sauvegarde (non obligatoire)",csm,20)[0]/2),pop_up.y + pop_up.h - pop_up.h/4,image_cadena.get_rect().w,image_cadena.get_rect().h)
            if not click_mdp:
                draw_text("securiser sauvegarde (non obligatoire)",comic_sans_ms,(255,255,255),pop_up.x + pop_up.w/2 - get_dimension("securiser sauvegarde (non obligatoire)",csm,20)[0]/2 + 20,pop_up.y + pop_up.h - pop_up.h/4 - get_dimension("securiser sauvegarde (non obligatoire)",csm,20)[1]/2 +6)
            color_mdp = (0,200,0) if click_mdp else (0,0,0)
            screen.blit(image_cadena,rect_mdp)
            input_box_mdp = pygame.Rect(rect_mdp.x + 50,rect_mdp.y - 32/4,140,32)
            text_mdp = "donner non proteger par mot de passe"
            if click_mdp:
                screen.blit(change_color_img(image_voir,(0,0,0)),rect_voir) if not voir else screen.blit(change_color_img(image_voir,(255,0,0)),rect_voir)
                color_box2 = (0,200,0) if active_mdp else (0,0,0)
                input2 = input_nom.render(input_mdp_visu[coup_d2_mdp:], True, (255, 255, 255)) if not voir  else input_nom.render(input_mdp[coup_d1_mdp:], True, (255, 255, 255))
                rect_text = input_mdp_visu if not voir else input_mdp
                coupagedebutmdp = False
                if input_nom.size(rect_text)[0] > 130:
                    coupagedebutmdp = True
                pygame.draw.rect(screen,color_box2,input_box_mdp,2)
                screen.blit(input2,(input_box_mdp.x + 5,input_box_mdp.y + input_box_mdp.h/2 - get_dimension(rect_text,csm,25)[1]/4))
                if active_mdp:
                    coup_d_mdp = coup_d2_mdp if not voir else coup_d1_mdp
                    input_ = input_mdp_visu if not voir else input_mdp
                    screen.blit(barre_type,(input_box_mdp.x + 5 + input_nom.size(input_[coup_d_mdp:])[0],input_box_mdp.y + input_box_mdp.h/2 - get_dimension(rect_text[coup_d_mdp:],csm,25)[1]/4))
                text_mdp = "Le mot de passe est sauvegarder" if valid else "Valider votre mot de passe ! (Entrez)"
                text =  "Appuyer pour voir" if not voir  else "vision activer"
                draw_in(text,0,rect_voir,20,(255,255,200),csm,rect_voir.w +10, rect_voir.h/2 - get_dimension(text,csm,20)[1]/2)
            draw_in(text_mdp,0,pop_up,25,(255,255,255),csm,pop_up.w/2 - get_dimension(text_mdp,csm,25)[0]/2,
                        pop_up.h - get_dimension(text_mdp,csm,25)[1] -10)
            rect_voir = pygame.Rect(input_box_mdp.x + input_box_mdp.w + 10, input_box_mdp.y + input_box_mdp.h/2 - image_voir.get_rect().h/2, image_voir.get_rect().w,image_voir.get_rect().h)
            pygame.display.flip()
            mods = pygame.key.get_mods()
            # vérifier si la touche Verr Maj est enfoncée
            if mods & pygame.KMOD_CAPS:
                maj = True
            else:
                maj = False
            key = pygame.key.get_pressed()
            mouse_click = pygame.mouse.get_pressed()
            if case_new.collidepoint(mouse) and mode == 1:
                if mouse_click[0]:
                    new_data = False
                    delete = False
                    can_go_out = True
                    break
            if key[pygame.K_RSHIFT] or key[pygame.K_LSHIFT]:
                maj = True
            else:
                if maj != True:
                    maj = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = left_game(1)
                if box_input.collidepoint(mouse):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        active = not active
                        active_mdp = False
                        if input_user == defaul_setting_user:
                            input_user = ""
                if rect_voir.collidepoint(mouse):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        voir = not voir
                if rect_mdp.collidepoint(mouse):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        click_mdp = not click_mdp
                        valid = False
                if click_mdp:
                    if input_box_mdp.collidepoint(mouse):
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            active_mdp = not active_mdp
                            active = False
                if active and event.type == pygame.KEYDOWN:
                    active_mdp = False                             
                    if event.key == pygame.K_BACKSPACE:
                        input_user = input_user[:-1]
                        coup_d_user -= 3
                        coup_d_user = 0 if coup_d_user <= 0 else coup_d_user
                        next_time = current_time + 100
                    elif event.key == pygame.K_SPACE and len(input_user) < max_letter:
                        input_user = input_user + " "
                        if coupagedebut:
                            coup_d_user += 3
                    elif event.key == pygame.K_RETURN:
                        if input_user != "":
                            file_name.append(input_user)
                            file_extension.append(".txt")
                            file_full = input_user + ".txt"
                            nom_fichier = input_user
                            if file_full in os.listdir("file"):
                                sup = os.listdir("file").count(file_full)
                                file_full = file_full[:-4]
                                file_full += f"({sup+1}).txt"
                                input_user += f"({sup+1})"
                            key = cryptography.fernet.Fernet.generate_key()
                            with open(f'key/{input_user}.key', 'wb') as filekey:
                                filekey.write(key)
                            a = open(f"file/{input_user}.txt", "w")
                            a.close()
                            input_user = ""
                            active = False
                            can_go_out = True
                            new_data = False
                            file_full = f"file/{file_full}"
                            break
                        else:
                            text = "Input non valide"
                            center_screen(text, comic_sans_ms, get_dimension(text, csm,20),0,False)
                            pygame.display.flip()
                            pygame.time.delay(500)
                    else:
                        if len(input_user) < max_letter:
                            input_user += event.unicode if not maj else event.unicode.upper()
                            if coupagedebut:
                                coup_d_user += 3
                                
                elif input_user == defaul_setting_user and active_mdp is False:
                    if (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN) and input_user != "":
                        file_name.append(input_user)
                        file_extension.append(".txt")
                        nom_fichier = input_user
                        file_full = input_user + ".txt"
                        if file_full in os.listdir("file"):
                            sup = os.listdir("file").count(file_full)
                            file_full = file_full[:-4]
                            file_full += f"({sup+1}).txt"
                            input_user += f"({sup+1})"
                        key = cryptography.fernet.Fernet.generate_key()
                        with open(f'key/{input_user}.key', 'wb') as filekey:
                            filekey.write(key)
                        a = open(f"file/{input_user}.txt", "w")
                        a.close()
                        active = False
                        can_go_out = True
                        new_data = False
                        file_full = f"file/{file_full}"
                        break
                if active_mdp and event.type == pygame.KEYDOWN:
                    active = False
                    if input_mdp == default_setting_mdp:
                        input_mdp = ""
                    if event.key == pygame.K_BACKSPACE:
                        input_mdp = input_mdp[:-1]
                        input_mdp_visu = input_mdp_visu[:-1]
                        if coupagedebutmdp:
                            coup_d1_mdp = coup_d1_mdp - 1
                            coup_d2_mdp = coup_d2_mdp - 1
                            coup_d1_mdp = 0 if coup_d1_mdp <= 0 else coup_d1_mdp
                            coup_d2_mdp = 0 if coup_d2_mdp <= 0 else coup_d2_mdp                                        
                    elif event.key == pygame.K_SPACE:
                        input_mdp = input_mdp + " "
                        input_mdp_visu += " "
                        if coupagedebutmdp:
                            coup_d1_mdp = coup_d1_mdp + 3                                    
                            coup_d2_mdp = coup_d2_mdp + 3                                        
                    elif event.key == pygame.K_RETURN:
                        if input_mdp != "":
                            active_mdp = False
                            mot_de_passe_user = input_mdp
                            valid = True
                        else:
                            text = "Input non valide"
                            center_screen(text, comic_sans_ms, get_dimension(text, csm,20),0,False)
                            pygame.display.flip()
                            pygame.time.delay(500)
                    else:
                        input_mdp += event.unicode if not maj else event.unicode.upper()
                        input_mdp_visu += "*"
                        if coupagedebutmdp:
                            coup_d1_mdp = coup_d1_mdp + 3
                            coup_d2_mdp = coup_d2_mdp + 3                   
            
            if rect_start.collidepoint(mouse):
                if mouse_click[0] and input_user != "":
                    file_full = input_user + ".txt"
                    nom_fichier = input_user
                    file_name.append(nom_fichier)
                    file_extension.append(".txt")
                    if file_full in os.listdir("file"):
                        sup = os.listdir("file").count(file_full)
                        file_full = file_full[:-4]
                        file_full += f"({sup+1}).txt"
                        input_user += f"({sup+1})"
                    key = cryptography.fernet.Fernet.generate_key()
                    with open(f'key/{input_user}.key', 'wb') as filekey:
                        filekey.write(key)
                    a = open(f"file/{input_user}.txt", "w")
                    a.close()
                    active = False
                    can_go_out = True
                    new_data = False
                    file_full = f"file/{file_full}"
                    break
                    
                if mouse_click[0] and input_user == "":
                    text = "Input non valide"
                    center_screen(text, comic_sans_ms, get_dimension(text, csm,20),0,False)
                    pygame.display.flip()
                    pygame.time.delay(500)
            if can_go_out:
                break
        if mode == 1:
            return file_full,valid,nom_fichier,new_data,delete,input_mdp
        return file_full,valid,nom_fichier
    
    def log_host(all_case_data = []):
        """
            fonction gérant l'arriver du joueur
            :param1: booléen du mode creation d'une nouvelle sauvegarde
            :param2: booléen du mode delete sauvegarde
        """
        global max_sauvegarde
        max_sauvegarde = 0
        global file_full
        global file_name
        global sinistre
        global volume
        global file_extension
        global click_log
        global numero
        global new_data
        global delete
        global data_secu
        global mot_de_passe_user
        for i in range(len(file_name)):
            text = file_name[i] + file_extension[i]
            text_full = f"file/{text}"
            try:
                decrypt_file(text_full,file_name[i])
            except:
                pass
        cadena = pygame.transform.scale(pygame.image.load("image_site/oeil_mdp.png"),(40,25))
        global data_save
        if delete:
            data_save = []
        while True:
            if (len(file_extension) > 0):
                if not new_data:
                    all_case_data = []
                    screen.fill((200,200,200))
                    pop_up = appear_pop_up(1)
                    if not delete:
                        text = f"vous possedez {len(file_extension)} sauvegarde(s)"
                        draw_in(text, "u", pop_up, 25, color_pick["violet_rouge"], agero,
                                pop_up.w / 2 - get_dimension(text, agero, 25, False, True)[0] / 2, -40, False, True)
                        text = f"Clickez sur l'une d'elles pour débuter"
                        draw_in(text, "u", pop_up, 25, color_pick["violet_rouge"], agero,
                                pop_up.w / 2 - get_dimension(text, agero, 25, False, True)[0] / 2, pop_up.h + 10, False, True)
                        text = f"Click droit sur un fichier pour activé la suppression"
                        draw_in(text, "u", pop_up, 15, color_pick["bleu"], sinistre,
                                pop_up.w / 2 - get_dimension(text, agero, 25, False, True)[0] / 2, pop_up.h + 50, False, True)
                    else:
                        text = f"CLICKEZ sur une sauvegarde pour la supprimer"
                        draw_in(text, "u", pop_up, 25, color_pick["violet_rouge"], agero,
                                pop_up.w / 2 - get_dimension(text, agero, 25, False, True)[0] / 2, -40, False, True)
                        text = f"Click MOLETTE pour desactiver le mode delete"
                        draw_in(text, "u", pop_up, 25, color_pick["bleu_f"], agero,
                                pop_up.w / 2 - get_dimension(text, agero, 25, False, True)[0] / 2, pop_up.h + 10, False, True)
                    case_log = pygame.Rect(pop_up.x + 20, pop_up.y + 50, pop_up.w/2 - 100, pop_up.h/7)
                    marge_casey = [20, pop_up.h/2 - case_log.h, pop_up.h - (pop_up.h/7) - (pop_up.h/7)/2 - 50, 20,pop_up.h/2 - case_log.h , pop_up.h - (pop_up.h/7) - (pop_up.h/7)/2 - 50, 20]
                    case_new = pygame.Rect(pop_up.x - 100, pop_up.y - 100, 100, 50)
                    case_contact = pygame.Rect(pop_up.x+pop_up.w,pop_up.y - 100, 150,50)
                    pygame.draw.rect(screen,(0,0,0),case_contact,2)
                    draw_in("Contact", "", case_contact,30,(0,0,0),arial,5,10)
                    pygame.draw.rect(screen, (0, 0, 0), case_new, 2)
                    draw_in("New", "", case_new, 30, (0, 0, 0), arial, 5, 10)
                    pygame.display.flip()
                    indice = 0
                    for i in range(len(file_extension)):
                        text = file_name[i] + file_extension[i]
                        text2 = file_name[i]
                        text_ = f"file/{text}"
                        have_mdp = False

                        with open(text_, "r") as fichier:
                            li = fichier.read().splitlines()
                            nom_info,class_info = "No name","No class"
                            mdp = False
                            code = None
                            recup_nom = False
                            for z in range(len(li)):
                                if li[z] == "nom" and recup_nom == False:
                                    nom_info = li[z+1]
                                    recup_nom = True
                                if li[z] == "class":
                                    class_info = li[z+1]
                                if li[z] == "mdp" and not have_mdp:
                                    mdp = True
                                    code = li[z+1]
                                    have_mdp = True
                        if indice <= 2:
                            case = pygame.draw.rect(screen, (0, 0, 0),
                                                    (case_log.x, case_log.y + marge_casey[indice], case_log.w, case_log.h))
                            surface = pygame.Surface((case_log.w, case_log.h))
                            taille = check_size(1,case,text,None,csm)
                            draw_in(text2, "", case, taille, (255, 255, 255), csm, 5,-5,surface = surface)
                            taille = check_size(10, case, f"# {(nom_info).upper()} #", f"# {(class_info).upper()} #")
                            draw_in(f"# {(nom_info).upper()} #", "", case, taille, color_pick["rouge"], sinistre, 5,case_log.h -
                                    get_dimension(f"#{(nom_info).upper()}#",sinistre, taille, False, True)[1],
                                    False, True, surface = surface)
                            if mdp:
                                surface.blit(change_color_img(cadena,(255,255,255)), (case_log.w - 45, 5))
                            draw_in(f"# {(class_info).upper()} #", "", case, taille, color_pick["cyan"], sinistre, get_dimension(f"#{(nom_info).upper()}#",sinistre, taille, False, True)[0] + 20, case_log.h - get_dimension(f"# {(class_info).upper()} #", sinistre,taille,False,True)[1],
                                    False, True,surface = surface)
                            screen.blit(surface,case)

                        else:
                            case1 = pygame.draw.rect(screen, (0, 0, 0),
                                                    (case_log.x + pop_up.w - case_log.w - 50, case_log.y + marge_casey[indice], case_log.w, case_log.h))
                            surface = pygame.Surface((case_log.w, case_log.h))
                            taille = check_size(1,case1,text,None,csm)
                            draw_in(text2, "", case1, taille, (255, 255, 255), csm, 5,-5,surface = surface)
                            taille = check_size(10, case1, f"# {(nom_info).upper()} #", f"# {(class_info).upper()} #")
                            draw_in(f"# {(nom_info).upper()} #", "", case, taille, color_pick["rouge"], sinistre, 5,case_log.h -
                                    get_dimension(f"#{(nom_info).upper()}#",sinistre, taille, False, True)[1],
                                    False, True, surface = surface)
                            if mdp:
                                surface.blit(change_color_img(cadena,(255,255,255)), (case_log.w - 45, 5))
                            draw_in(f"# {(class_info).upper()} #", "", case1, taille, color_pick["cyan"], sinistre, get_dimension(f"#{(nom_info).upper()}#",sinistre, taille, False, True)[0] + 20, case_log.h - get_dimension(f"# {(class_info).upper()} #", sinistre,taille,False,True)[1],
                                    False, True,surface = surface)
                            screen.blit(surface,case1)
                        if i > 2:
                            case=case1
                        case_data = {"nom": text, "numero": i + 1, "nom_perso": nom_info, "nom_class": class_info,"rect": case, "file" : file_name[i], "securiser" : (mdp,code)}
                        all_case_data.append(case_data)
                        pygame.display.flip()
                        indice+=1
                        max_sauvegarde += 1
                    if len(data_save) == 0:
                        data_save.append(all_case_data)
                if not new_data and not delete:
                    while True:
                        log = False
                        mouse = pygame.mouse.get_pos()
                        pygame.event.clear()
                        for event in [pygame.event.wait()]:
                            #32787 = fermer la fenetre avec la croix, y'avait un bug ou pygame.QUIT fonctionnait pas
                            if event.type == 32787:
                                running = left_game(1)
                            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                                if event.key == pygame.K_ESCAPE:
                                    running = left_game(1)
                                elif event.key == pygame.K_p:
                                    pygame.mixer.music.pause()
                                elif event.key == pygame.K_u:
                                    pygame.mixer.music.unpause()
                                elif event.key == pygame.K_KP6:
                                    volume = get_volume(1)
                                elif event.key == pygame.K_KP4:
                                    volume = get_volume(-1)
                            pygame.mixer.music.set_volume(volume)
                            collide = False
                            
                            for data_check in range(len(all_case_data)):
                                if all_case_data[data_check]["rect"].collidepoint(mouse):
                                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 3):
                                        delete = True
                                        new_data = False
                                        break
                                    elif (event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP) and event.button != 3:
                                        if not all_case_data[data_check]["securiser"][0]:
                                            log = True
                                            data_secu,mot_de_passe_user = all_case_data[data_check]["securiser"][0],all_case_data[data_check]["securiser"][1]
                                            file_full = f'file/{all_case_data[data_check]["nom"]}'
                                            numero = all_case_data[data_check]["numero"]                                    
                                            break
                                        else:
                                            valid = input_for_mdp(all_case_data,all_case_data[data_check]["securiser"][1])                                            
                                            if valid:
                                                log = True
                                                data_secu,mot_de_passe_user = all_case_data[data_check]["securiser"][0],all_case_data[data_check]["securiser"][1]
                                                file_full = f'file/{all_case_data[data_check]["nom"]}'
                                                numero = all_case_data[data_check]["numero"]                                    
                                                break
                                            else:
                                                pygame.event.clear()
                                                return log_host(all_case_data)
                                            
                            if case_new.collidepoint(mouse):
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    if max_sauvegarde <= 5:
                                        click_log += 1
                                        new_data = True
                                        break
                                    else:
                                        center_screen("trop de sauvegardes", comic_sans_ms, get_dimension("trop de sauvegardes", csm, 20), 0, False)
                                        pygame.display.flip()
                                        pygame.time.delay(1000)
                                        change_text(rect_screen.w/2 - get_dimension("trop de sauvegardes", csm, 20)[0]/2 , 2, get_dimension("trop de sauvegardes", csm, 20)[0], get_dimension("trop de sauvegardes", csm, 20)[1], (200,200,200))
                                        pygame.display.flip()
                            if case_contact.collidepoint(mouse):
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    return contact()
                        if log or delete or new_data:
                            break
                    if log or delete or new_data:
                        break
                if new_data and delete is False:                  
                    file_full,valid,nom_fichier,new_data,delete,input_mdp = input_for_login("Entrez le nom de votre sauvegarde")
                if file_full != "":
                    num = 0
                    data_secu = bool(valid)
                    for file in file_name:
                        with open(f"file/{file}.txt", "r") as fichier:
                            get_all = fichier.readlines()
                        with open(f"file/{file}.txt",'w') as f:
                            for i,line in enumerate(get_all,1):         
                                if i == 1:
                                    try:
                                        f.writelines(f"save : {data_save[0][num]['numero']}\n")
                                    except:
                                        f.writelines(f"save : {len(file_name) + 1}\n") 
                                else:
                                    f.writelines(line)
                        num += 1
                    if data_secu:
                        with open(file_full, "a") as fichier:
                            fichier.write("mdp\n")
                            fichier.write(f"{input_mdp}\n")
                    numero = len(file_extension) + 1 
                    with open(file_full, "r+") as fichier:
                        li = fichier.read().splitlines()
                        i = 0
                        have_save = False
                        for host_log in li:
                            if host_log == f"save : {numero}":
                                have_save = True
                            i+=1
                        if not have_save:
                            write2(file_full, len(file_extension)+1)
                    break
                if delete != False and new_data is False:
                    quiT = False
                    while True:
                        mouse = pygame.mouse.get_pos()
                        event = pygame.event.poll()
                        if event.type == pygame.QUIT:
                            running = left_game(1)
                        collide = False
                        for i in range(len(all_case_data)):
                            if all_case_data[i]["rect"].collidepoint(mouse):
                                collide = True
                            if (event.type == pygame.MOUSEBUTTONDOWN and collide) and event.button != 2:
                                if f'{all_case_data[i]["nom"]}' in os.listdir("file") and all_case_data[i]["securiser"][0] == False:
                                    os.remove(f'file/{all_case_data[i]["nom"]}')
                                    os.remove(f'key/{all_case_data[i]["nom"][:-4]}.key')
                                    file_name.remove(f'{all_case_data[i]["file"]}')
                                    file_extension.remove(".txt")
                                    new_data = False
                                    delete = True
                                    quiT = True
                                    max_sauvegarde -= 1
                                    break
                                elif f'{all_case_data[i]["nom"]}' in os.listdir("file") and all_case_data[i]["securiser"][0] == True:

                                    valid = input_for_mdp(all_case_data,all_case_data[i]["securiser"][1])
                                    if valid:
                                        os.remove(f'file/{all_case_data[i]["nom"]}')
                                        os.remove(f'key/{all_case_data[i]["nom"][:-4]}.key')
                                        file_name.remove(f'{all_case_data[i]["file"]}')
                                        file_extension.remove(".txt")
                                        new_data = False
                                        delete = True
                                        quiT = True
                                        max_sauvegarde -= 1
                                        break
                                    else:
                                        pass
                            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                                delete = False
                                new_data = False
                                quiT = True
                                return log_host()
                            if case_new.collidepoint(mouse):
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    if max_sauvegarde <= 5:
                                        click_log += 1
                                        new_data = True
                                        quiT = True
                                        delete = False
                                        return log_host()
                                    else:
                                        center_screen("trop de sauvegardes", comic_sans_ms, get_dimension("trop de sauvegardes", csm, 20), 0, False)
                                        pygame.display.flip()
                                        pygame.time.delay(1000)
                                        change_text(rect_screen.w/2 - get_dimension("trop de sauvegardes", csm, 20)[0]/2 , 2, get_dimension("trop de sauvegardes", csm, 20)[0], get_dimension("trop de sauvegardes", csm, 20)[1], (200,200,200))
                                        pygame.display.flip()
                        if quiT:
                            break
            else:
                file_full,valid,nom_fichier = input_for_login("Votre première sauvegarde !", mode = 0)
                mot_de_passe_user = None if not valid else mot_de_passe_user
                data_secu = True if valid else False
                write2(file_full, len(file_extension) + 1)
                file_extension.append(".txt")
                file_name.append(nom_fichier)
                global first_data
                first_data = True
                break
                
    
    def log_nom_user(nom, file=file_full):
        """
            fonction permettant d'ecrire le nom de l'user dans son fichier
            :param1: nom de l'user
            :param2: fichier dans lequel ecrire
        """
        with open(file, "a") as fichier:
            fichier.write(f"nom\n")
            fichier.write(f"{nom}\n")

    def test_nom_user(file=file_full):
        """
            fonction permettant de verifier que l'user a un nom
            :param1: fichier dans lequel faut écrire (option)
        """
        recup_nom = False
        with open(file_full, "r") as fichier:
            li = fichier.read().splitlines()
            nom = ""
            for i in range(len(li)):
                if li[i] == "nom" and recup_nom == False:
                    nom = li[i+1]
                    recup_nom = True
            return nom

    def test_class_user(file=file_full):
        """
            fonction permettant de verifer si l'user a une class
            :param1: fichier dans lequel faut écrire (option)
        """
        with open(file, "r") as fichier:
            li = fichier.read().splitlines()
            class_ = ""
            for i in range(len(li)):
                if li[i] == "class":
                    class_ = li[i+1]
            return class_

    def log_class_user(class_, file=file_full):
        """
            fonction permettant d'ecrire la class de l'user
            :param1: class de l'user
            :param2: fichier dans lequel faut ecrire
        """
        with open(file, "a") as fichier:
            fichier.write(f"class\n")
            fichier.write(f"{class_}\n")

    def presentation(id_=0, file=file_full):
        """
            fonction permettant de prendre les stats des users
        """
        # fonction a testez, effacer data_user avant
        dictt = []
        tuto_list = []
        with open(file, "r") as fichier:
            global class_
            global default_stat
            global nom
            li = fichier.read().splitlines()
            can_log_item = False
            tuto_list = True
            item_bag = None
            nom_recup = False
            for i in range(len(li)):
                if "TUTO_ACHIEVE" in li[i]:
                    tuto_list = False
                if "room_already_logged" in li[i]:
                    can_log_item = True
                if li[i] == "nom" and not nom_recup:
                    nom = li[i + 1]
                    nom_recup = True
                if li[i] == "class":
                    class_ = li[i + 1]
                try:
                    dictt.append((type(class_)))
                    new_data_ = False
                except:
                    new_data_ = True
                if li[i] == "level":
                    level = float(li[i + 1])
                if li[i] == "gold":
                    gold = float(li[i + 1])
                if li[i] == "exp":
                    xp = float(li[i + 1])
                if li[i] == "exp_need":
                    xp_need = float(li[i + 1])
                try:
                    dictt.append(type(xp_need))
                    m = True
                except:
                    level = 1
                    gold = 0
                    xp = 0
                    xp_need = 69
                    m = False
                    
                if li[i] == "force":
                    force = float(li[i+1])
                if li[i] == "agilite":
                    agilite = float(li[i+1])
                if li[i] == "vol de vie":
                    vol_de_vie = float(li[i+1])
                if li[i] == "reflexe":
                    reflexe = float(li[i+1])
                if li[i] == "vitesse":
                    vitesse = float(li[i+1])
                if li[i] == "vie":
                    vie = float(li[i+1])
                if li[i] == "energie":
                    energie = float(li[i+1])
                if li[i] == "magie":
                    magie = float(li[i+1])
                if li[i] == "max energie":
                    max_energie = float(li[i+1])
                if li[i] == "max vie":
                    max_vie = float(li[i+1])
                try:
                    dictt.append((type(max_vie)))
                    default_stat = False
                except:                    
                    default_stat = True
                if li[i] == "item1":
                    item1 = item_holder[li[i+1]]
                if li[i] == "item2":
                    item2 = item_holder[li[i+1]]
                if li[i] == "item3":
                    item3 = item_holder[li[i+1]]
                if li[i] == "item_bag":
                    list_item = json.loads(li[i+1])
                    item_bag = [item_holder[element] for element in list_item]
                try:
                    dictt.append((type(item3)))
                    recup_item = True
                except:
                    recup_item = False

            """
                faire pareil pour les autres + ajouté attaque + attaque_holder
            """
            global joueur
            # documentation utiliser les ulti, definir si ulti = 1 ou 0, si ulti = 1 alors cooldown = ulti, puis on fait que temp_sans_ulti = 0 puis += 1 si il est inferieur a cooldwown, puis quand on utilise l'attaque on le met a
            if not new_data_:
                global joueur_sprite
                global sprite_group_right
                global sprite_group_left
                global image_stand
                if default_stat is True:
                    if class_ == "Guerrier":
                        joueur = {"class" : "Guerrier", "nom" : nom, "level" : level, "stat_joueur" : {"reflexe" : 4,"force" : 5, "vitesse" : 4, "agilite" : 4, "magie" : 0, "vie" : 150, "vie_max" : 150,"vol_de_vie" : 0, "energie" : 150, "energie_max" : 150, "item" : [item_holder["potion_force_base"], item_holder["potion_defence_base"], item_holder["potion_endurance_base"]], "abilite" : [attaque_holder["coup de poing"], attaque_holder["slash"],attaque_holder["combo barbare"], attaque_holder["garde du chevalier"]],"exp" : xp, "exp_needed" : xp_need,"or" : gold}, "item_bag" : [None]}
                        joueur_sprite = pygame.image.load("image_site/sprite_chevalier_stand.png").convert_alpha()
                        sprite_group_right = [pygame.image.load("image_site/sprite_chevalier_stand.png").convert_alpha(),pygame.image.load("image_site/knigh_1.png").convert_alpha(),pygame.image.load("image_site/knigh_2.png").convert_alpha()]
                        sprite_group_left = sprite_group_right
                        image_stand = joueur_sprite
                    elif class_ == "Assassin":
                        joueur = {"class" : "Assassin", "nom" : nom, "level" : level, "stat_joueur" : {"reflexe" : 5,"force" : 2, "vitesse" : 5, "agilite" : 5, "magie" : 0, "vie" : 110,"vie_max" : 110, "vol_de_vie" : 0, "energie" : 150, "energie_max" : 150, "item" : [item_holder["potion_force_base"], item_holder["potion_defence_base"], item_holder["potion_endurance_base"]], "abilite" : [attaque_holder["coup de poing"], attaque_holder["coup rapide"], attaque_holder["mise a mort"], attaque_holder["invisibilité"]],"exp" : xp, "exp_needed" : xp_need,"or" : gold}, "item_bag" : [None]}
                        joueur_sprite = pygame.image.load("image_site/sprite_assasin_stand.png").convert_alpha()
                        sprite_group_right = [pygame.image.load("image_site/sprite_assassin_right_1.png").convert_alpha(),pygame.image.load("image_site/sprite_assassin_right_2.png").convert_alpha(),pygame.image.load("image_site/sprite_assassin_right_3.png").convert_alpha()]
                        sprite_group_left = [pygame.image.load("image_site/sprite_assassin_left_1.png").convert_alpha(),pygame.image.load("image_site/sprite_assassin_left_2.png").convert_alpha(),pygame.image.load("image_site/sprite_assassin_left_3.png").convert_alpha()]
                        image_stand =  joueur_sprite
                    else:
                        joueur = {"class" : "Mage", "nom" : nom, "level" : level, "stat_joueur" : {"reflexe" : 3,"force" : 2, "vitesse" : 3, "agilite" : 4, "magie" : 8, "vie" : 120, "vie_max" : 120,"vol_de_vie" : 0, "energie" : 200, "energie_max" : 200, "item" : [item_holder["potion_force_base"], item_holder["potion_defence_base"], item_holder["potion_endurance_base"]], "abilite" : [attaque_holder["boule de feu"],  attaque_holder["mur de mana"],attaque_holder["void hole"],  attaque_holder["coup de poing"]],"exp" : xp, "exp_needed" : xp_need,"or" : gold}, "item_bag" : [None]}
                        joueur_sprite = pygame.image.load("image_site/sprite_mage_stand.png").convert_alpha()
                        sprite_group_right,sprite_group_left = 0,0
                        image_stand = joueur_sprite
                else:
                    if not recup_item or not can_log_item:
                        item1 = item_holder["potion_force_base"]
                        item2 = item_holder["potion_defence_base"]
                        item3 = item_holder["potion_endurance_base"]
                   
                    if class_ == "Guerrier":
                        joueur = {"class" : "Guerrier", "nom" : nom, "level" : level, "stat_joueur" : {"reflexe" : reflexe ,"force" : force, "vitesse" : vitesse, "agilite" : agilite, "magie" : magie, "vie" : vie,"vie_max" : max_vie, "vol_de_vie" : vol_de_vie, "energie" : energie, "energie_max" : max_energie, "item" : [item1, item3, item2], "abilite" : [{"nom" : "coup de poing","degat" : 5,  "coup_en_energie" : 0, "vitesse" : 5, "damage_reduction" : 0, "ulti" : False, "turn_to_work" : None, "atk_type": "force"}, {"nom" : "slash", "degat" :  10,  "coup_en_energie" : 5, "vitesse" : 9, "damage_reduction" : 0, "ulti" : False, "turn_to_work" : None, "atk_type": "force"},{"nom" : "Combo Barbare", "degat" : 50,  "coup_en_energie" : 15, "vitesse" : 25, "damage_reduction" : 0, "ulti" : True, "turn_to_work" : 4, "atk_type": "force"}, {"nom" : "Garde du chevalier", "degat" : 0,  "coup_en_energie" : 10, "vitesse" : 2, "damage_reduction" : 25, "ulti" : False, "turn_to_work" : None, "atk_type": "aucun", "tour_effect" : 2, "defence_reduction" : 2}],"exp" : xp, "exp_needed" : xp_need,"or" : gold}, "item_bag" : item_bag}
                        joueur_sprite = pygame.image.load("image_site/sprite_chevalier_stand.png").convert_alpha()
                        sprite_group_right = [pygame.image.load("image_site/sprite_chevalier_stand.png").convert_alpha(),pygame.image.load("image_site/knigh_1.png").convert_alpha(),pygame.image.load("image_site/knigh_2.png").convert_alpha()]
                        sprite_group_left = sprite_group_right
                        image_stand = joueur_sprite
                    elif class_ == "Assassin":
                        joueur = {"class" : "Assassin", "nom" : nom, "level" : level, "stat_joueur" : {"reflexe" : reflexe,"force" : force, "vitesse" : vitesse, "agilite" : agilite, "magie" : magie, "vie" : vie,"vie_max" : max_vie, "vol_de_vie" : vol_de_vie, "energie" : energie, "energie_max" : max_energie, "item" : [item1, item3, item2], "abilite" : [{"nom" : "coup de poing","degat" : 5,  "coup_en_energie" : 0, "vitesse" : 5, "damage_reduction" : 0, "ulti" : False, "turn_to_work" : None, "atk_type": "force"}, {"nom" : "Coup rapide", "degat" :  13,  "coup_en_energie" : 15, "vitesse" : 12, "damage_reduction" : 0, "ulti" : False, "turn_to_work" : None, "atk_type": "force"},{"nom" : "Mise a mort", "degat" : 50,  "coup_en_energie" : 15, "vitesse" : 30, "damage_reduction" : 0, "ulti" : True, "turn_to_work" : 4, "atk_type": "force"}, {"nom" : "Invisibilité", "degat" : 0,  "coup_en_energie" : 5, "vitesse" : 100, "damage_reduction" : 100, "ulti" : False, "turn_to_work" : None, "atk_type": "aucun", "tour_effect" : 2}],"exp" : xp, "exp_needed" : xp_need,"or" : gold}, "item_bag" : item_bag}
                        joueur_sprite = pygame.image.load("image_site/sprite_assasin_stand.png").convert_alpha()
                        sprite_group_right = [pygame.image.load("image_site/sprite_assassin_right_1.png").convert_alpha(),pygame.image.load("image_site/sprite_assassin_right_2.png").convert_alpha(),pygame.image.load("image_site/sprite_assassin_right_3.png").convert_alpha()]
                        sprite_group_left = [pygame.image.load("image_site/sprite_assassin_left_1.png").convert_alpha(),pygame.image.load("image_site/sprite_assassin_left_2.png").convert_alpha(),pygame.image.load("image_site/sprite_assassin_left_3.png").convert_alpha()]
                        image_stand =  joueur_sprite
                    else:
                        joueur = {"class" : "Mage", "nom" : nom, "level" : level, "stat_joueur" : {"reflexe" : reflexe,"force" : force, "vitesse" : vitesse, "agilite" : agilite, "magie" : magie, "vie" : vie,"vie_max" : max_vie, "vol_de_vie" : vol_de_vie, "energie" : energie, "energie_max" : max_energie, "item" : [item1, item3, item2], "abilite" : [{"nom" : "boule de feu","degat" : 15,  "coup_en_energie" : 7, "vitesse" : 20, "damage_reduction" : 0, "ulti" : False, "turn_to_work" : None, "atk_type": "magie"}, {"nom" : "Mur de Mana", "degat" :  1,  "coup_en_energie" : 20, "vitesse" : 25, "damage_reduction" : 35, "ulti" : False, "turn_to_work" : None, "atk_type": "magie","tour_effect" : 2, "defence_reduction" : 2},{"nom" : "Void Hole", "degat" : 50,  "coup_en_energie" : 15, "vitesse" : 30, "damage_reduction" : 0, "ulti" : True, "turn_to_work" : 4, "atk_type": "force"}, {"nom" : "coup de poing","degat" : 5,  "coup_en_energie" : 0, "vitesse" : 5, "damage_reduction" : 0, "ulti" : False, "turn_to_work" : None, "atk_type": "force"}],"exp" : xp, "exp_needed" : xp_need,"or" : gold}, "item_bag" : item_bag}
                        joueur_sprite = pygame.image.load("image_site/sprite_mage_stand.png").convert_alpha()
                        sprite_group_right,sprite_group_left = 0,0
                        image_stand = joueur_sprite
                if joueur["item_bag"] == [] or joueur["item_bag"] == [None]:
                    joueur["item_bag"] = [item for item in joueur["stat_joueur"]["item"]]
                joueur_sprite = pygame.transform.scale(joueur_sprite, default_size)
            if id_ == 0:
                if new_data_ is False:
                    screen.fill((200, 200, 200))
                    appear_pop_up()
                    draw_in(f"Bienvenue fière {joueur['class']} {joueur['nom']} :)", 0, pop_up, 25, (0, 0, 0), csm,pop_up.w / 2 - get_dimension(f"Bienvenue fière {class_} {nom} :)", csm, 25)[0] / 2,pop_up.h / 2 - get_dimension(f"Bienvenue fière {class_} {nom} :)", csm, 25)[1] / 2)
                    pygame.display.flip()
                    pygame.time.delay(1000)
                    draw_in("Appuyer sur une touche pour entrer dans le donjon ! ", 0, pop_up, 36, color_pick["bordeaux"], sinistre,pop_up.w / 2 - get_dimension("Appuyer sur une touche pour entrer dans le donjon ! ", sinistre, 36, False,True)[0] / 2,pop_up.h / 2 - get_dimension("Appuyer sur une touche pour entrer dans le donjon ! ", sinistre, 36, False, True)[1] / 2 + 200, False, True)
                    pygame.display.flip()
                    pygame.event.clear()
                    can_quit = False
                    rect_start = pygame.Rect(pop_up.x+pop_up.w/2-150/2,pop_up.y+pop_up.h+90,150,30)
                    while True:
                        mouse = pygame.mouse.get_pos()
                        make_music(os.listdir("playlist_music"))
                        color_start = (0,0,0) if not rect_start.collidepoint(mouse) else (0,100,100)
                        screen.fill((200,200,200),rect_start)
                        pygame.draw.rect(screen,color_start,rect_start)
                        draw_in("SUIVANT",0,rect_start,25,(255,255,255),arial,rect_start.w/2 - get_dimension("SUIVANT",arial,25)[0]/2,rect_start.h/2 - get_dimension("SUIVANT",arial,25)[1]/2)
                        pygame.display.update(rect_start)
                        for event in pygame.event.get():
                            if event.type == pygame.KEYDOWN:                                                           
                                can_quit = True
                                if not tuto_list:
                                    pygame.mixer.music.fadeout(2000)
                                break
                            if rect_start.collidepoint(mouse):
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    can_quit = True
                                    if not tuto_list:
                                        pygame.mixer.music.fadeout(2000)
                                    break
                            pygame.event.clear()
                        if can_quit:
                            break
                    
                    if tuto_list:
                        with open(file, "a") as fichier:
                            fichier.write("\nTUTO_ACHIEVE")
                        screen.fill((200,200,200))
                        draw_in("Appuyer sur une touche pour entrer dans le donjon ! ", 0, clavier_rect, 36, color_pick["bordeaux"],
                                sinistre, clavier_rect.w / 2 -
                                get_dimension("Appuyer sur une touche pour entrer dans le donjon ! ", sinistre, 36, False, True)[
                                    0] / 2, clavier_rect.h + 20, False, True)
                        draw_in("Regarder attentivement ! Merci :)", 0, clavier_rect, 40, color_pick["vert_bleu"],
                                sinistre, clavier_rect.w / 2 -
                                get_dimension("Regarder attentivement ! Merci :)", sinistre, 40, False, True)[
                                    0] / 2,-60, False, True)
                        screen.blit(clavier,clavier_rect)
                        pygame.display.flip()
                        pygame.event.clear()
                        can_quit = False
                        rect_start = pygame.Rect(pop_up.x+pop_up.w/2-150/2,pop_up.y+pop_up.h+130,150,30)
                        while True:
                            mouse = pygame.mouse.get_pos()
                            color_start = (0,0,0) if not rect_start.collidepoint(mouse) else (0,100,100)
                            screen.fill((200,200,200),rect_start)
                            pygame.draw.rect(screen,color_start,rect_start)
                            draw_in("SUIVANT",0,rect_start,25,(255,255,255),arial,rect_start.w/2 - get_dimension("SUIVANT",arial,25)[0]/2,rect_start.h/2 - get_dimension("SUIVANT",arial,25)[1]/2)
                            pygame.display.update(rect_start)
                            make_music(os.listdir("playlist_music"))
                            for event in pygame.event.get():
                                if event.type == pygame.KEYDOWN:                                                           
                                    pygame.mixer.music.fadeout(2000)
                                    can_quit = True
                                    break
                                if rect_start.collidepoint(mouse):
                                    if event.type == pygame.MOUSEBUTTONDOWN:
                                        pygame.mixer.music.fadeout(2000)
                                        can_quit = True
                                        break
                            if can_quit:
                                break
                    return joueur,joueur_sprite,sprite_group_right,sprite_group_left
    global masks_ennemie
    masks_ennemie = []
    global mask_ennemie
    mask_ennemie = []
    global current_room
    current_room = -1
    resize_ennemie = (255,210)
    #continuer faire en marche change_room()
    global went_back
    went_back = False
    global rooms
    rooms = []
    global stages
    stages = []
    global heal_rooms
    heal_rooms = []
    global room_passed
    room_passed = 0
    global room_logged
    room_logged = False
    global heal_room
    heal_room = False
    global switch_collision
    switch_collision = []
    global switch_collisions
    switch_collisions = []
    global stage
    stage = 0
    global have_heal_room
    have_heal_room = 0
    can_switch = False
    global current_sprite
    current_sprite = 0
    global boss_room
    boss_room = False
    global max_heal_room
    max_heal_room = 4
    global cooldown_heal_room
    cooldown_heal_room = 2
    switch_collisions = []
    ennemie_data_facile = {1 : pos_img2_, 2 : pos_img3_, 3 : ennemie_easy_3}
    ennemie_data_moyen = {1 :pos_img2_ , 2: pos_img3_,3:ennemie_moyen_3 ,4:ennemie_moyen_4}
    ennemie_data_dur = {1 :pos_img2_ , 2: pos_img3_,3:ennemie_dur_3 ,4:ennemie_dur_4, 5: ennemie_dur_5}
    boss_keep = {0 : boss_ennemie_assassin, 1 : boss_ennemie_guerrier, 2 : boss_ennemie_mage}
    taille = 20
    dict_equivalent_switch = { (rect_screen.w / 2 - taille / 2, 10 - taille / 2,20,20) : "haut", (rect_screen.w / 2 - taille / 2, rect_screen.h - 10 - taille / 2,20,20) : "bas", (10 - taille / 2, rect_screen.h / 2 - taille / 2,20,20) : "gauche", (rect_screen.w - 10 - taille / 2, rect_screen.h / 2 - taille / 2,20,20) : "droit"}
    global inverse_dict_equivalent_switch
    inverse_dict_equivalent_switch =  {"haut" : (rect_screen.w / 2 - taille / 2, 10 - taille / 2,20,20),"bas":(rect_screen.w / 2 - taille / 2, rect_screen.h - 10 - taille / 2,20,20),"droit" : (rect_screen.w - 10 - taille / 2, rect_screen.h / 2 - taille / 2,20,20), "gauche" : (10 - taille / 2, rect_screen.h / 2 - taille / 2,20,20)}
    
    def log_heal_room(list_place):
        """
            fonction permettant de gerer la heal_room
            :param1: dict des pos_swictch possible
            :return: return rooms (contient les ennemies/switch), stage(ennemie mode), switch_collision (position des switch)
        """
        global rooms
        global rect_screen
        global collision
        global collision_
        global stage
        global stages
        global png_heal_room
        global mask_ennemie
        collision = []
        collision_ = []
        switch_collision = []
        mask_ennemie = []
        collision.append(png_heal_room)
        collision_.append(png_heal_room["rect"])
        mask_ennemie.append(png_heal_room["img"])
        stage = 0
        taille = 20
        pos_switch = [[rect_screen.w / 2 - taille / 2, 10 - taille / 2],
                      [rect_screen.w - 10 - taille / 2, rect_screen.h / 2 - taille / 2],
                      [rect_screen.w / 2 - taille / 2, rect_screen.h - 10 - taille / 2],
                      [10 - taille / 2, rect_screen.h / 2 - taille / 2]]

        for i, y in list_place.items():
            if y["etat"] and y["rect"] == "vert":
                random_pos = pos_switch[y["nombre"]]
            elif y["etat"] and y["rect"] == "rouge":
                random_pos2 = pos_switch[y["nombre"]]
        switch_1 = pygame.draw.rect(screen, (0, 0, 0),
                                    (random_pos[0], random_pos[1], taille, taille))
        info_switch1 = {"id": 1, "rect": dict_equivalent_switch[(random_pos[0], random_pos[1], taille, taille)], "type": "switch"}
        switch_2 = pygame.draw.rect(screen, (255, 0, 0),
                                    (random_pos2[0], random_pos2[1], taille, taille))
        info_switch2 = {"id": -1, "rect": dict_equivalent_switch[(random_pos2[0], random_pos2[1], taille, taille)], "type": "switch"}
        room = {"png": png_heal_room, "switch_1" : info_switch1, "switch_2" : info_switch2}
        switch_collision.append(info_switch1)
        switch_collision.append(info_switch2)
        masks_ennemie.append(mask_ennemie)
        stages.append(stage)
        rooms.append(room)
        switch_collisions.append(switch_collision)
        return rooms,stage,switch_collision

    def log_ennemie(current_room,nb_room,room_passed,switch_collision,rooms,list_place):
        """
            fonction qui permet de charger les ennemies et le nécessaire de la room, determine le mode aussi
            :param1: room actuel
            :param2: nombre de room total
            :param3: nombre de room passer
            :param4: rect des switch
            :param5: toute les room ensemble
            :param6: dict des pos_swictch possible
            :return: return rooms (contient les ennemies/switch), stage(ennemie mode), switch_collision (position des switch)

        """
        global rect_screen
        global collision
        global collision_
        global stage
        global stages
        global mask_ennemie
        collision = []
        collision_ = []
        mask_ennemie = []
        switch_collision = []
        taille = 20
        pos_switch = [[rect_screen.w / 2 - taille / 2, 10 - taille / 2],
                      [rect_screen.w - 10 - taille / 2, rect_screen.h / 2 - taille / 2],
                      [rect_screen.w / 2 - taille / 2, rect_screen.h - 10 - taille / 2],
                      [10 - taille / 2, rect_screen.h / 2 - taille / 2]]
        if current_room <= 0:
            for i,y in list_place.items():
                if y["etat"] and y["rect"] == "vert":
                    random_pos = pos_switch[y["nombre"]]
                elif y["etat"] and y["rect"] == "rouge":
                    random_pos2 = pos_switch[y["nombre"]]
            #continuer switch + retour arriere + bot
            switch_1 = pygame.draw.rect(screen, (0, 0, 0),
                                        (random_pos[0], random_pos[1], taille, taille))
            info_switch1 = {"id": 1, "rect": dict_equivalent_switch[(random_pos[0], random_pos[1], taille, taille)], "type" : "switch"}
            info_switch2 = None

        else:
            for i,y in list_place.items():
                if y["etat"] and y["rect"] == "vert":
                    random_pos = pos_switch[y["nombre"]]
                if y["etat"]  and y["rect"] == "rouge":
                    random_pos2 = pos_switch[y["nombre"]]
                    
            switch_1 = pygame.draw.rect(screen, (0, 0, 0),
                                        (random_pos[0], random_pos[1], taille, taille))
            info_switch1 = {"id": 1, "rect": dict_equivalent_switch[(random_pos[0], random_pos[1], taille, taille)], "type" : "switch"}
            switch_2 = pygame.draw.rect(screen, (255, 0, 0),
                                        (random_pos2[0], random_pos2[1], taille, taille))
            info_switch2 = {"id": -1, "rect": dict_equivalent_switch[(random_pos2[0], random_pos2[1], taille, taille)], "type" : "switch"}

        switch_collision.append(info_switch1)
        if info_switch2 != None:
            switch_collision.append(info_switch2)
        calcul_room_difficulty = nb_room / 3
        if current_room <= calcul_room_difficulty and room_passed <= calcul_room_difficulty:
            stage = 1
            random_ennemie = random.randint(1,3)
            random_ennemie2 = random.randint(1,3)
            if random_ennemie2 == random_ennemie:
                erreur = True
                while erreur:
                    random_ennemie2 = random.randint(1,3)
                    if random_ennemie2 != random_ennemie:
                        erreur = False
            room = {"ennemie 1" : ennemie_data_facile[random_ennemie], "ennemie 2" : ennemie_data_facile[random_ennemie2], "switch_1" :
                    info_switch1, "switch_2" : info_switch2}
            ennemie_data_facile[random_ennemie]["mort_def"],ennemie_data_facile[random_ennemie]["etat"] = False,"vivant"
            ennemie_data_facile[random_ennemie2]["mort_def"],ennemie_data_facile[random_ennemie2]["etat"] = False,"vivant"
        if current_room <= calcul_room_difficulty * 2 and room_passed > calcul_room_difficulty:
            stage = 2
            random_ennemie = random.randint(1, 4)
            random_ennemie2 = random.randint(1, 4)
            if random_ennemie2 == random_ennemie:
                erreur = True
                while erreur:
                    random_ennemie2 = random.randint(1, 4)
                    if random_ennemie2 != random_ennemie:
                        erreur = False
            random_ennemie3 = random.randint(1,4)
            if random_ennemie3 == random_ennemie2 or random_ennemie3 == random_ennemie:
                erreur = True
                while erreur:
                    random_ennemie3 = random.randint(1, 4)
                    if random_ennemie3 != random_ennemie2 and random_ennemie3 != random_ennemie:
                        erreur = False
            room = {"ennemie 1": ennemie_data_moyen[random_ennemie], "ennemie 2": ennemie_data_moyen[random_ennemie2], "ennemie 3" : ennemie_data_moyen[random_ennemie3], "switch_1" :
                    info_switch1, "switch_2" : info_switch2}
            ennemie_data_moyen[random_ennemie]["mort_def"],ennemie_data_moyen[random_ennemie]["etat"] = False,"vivant"
            ennemie_data_moyen[random_ennemie2]["mort_def"],ennemie_data_moyen[random_ennemie2]["etat"] = False,"vivant"
            ennemie_data_moyen[random_ennemie3]["mort_def"],ennemie_data_moyen[random_ennemie3]["etat"] = False,"vivant"

        if current_room <= calcul_room_difficulty * 3 and room_passed >= calcul_room_difficulty * 2:
            stage = 3
            random_ennemie = random.randint(1, 5)
            random_ennemie2 = random.randint(1, 5)
            if random_ennemie2 == random_ennemie:
                erreur = True
                while erreur:
                    random_ennemie2 = random.randint(1, 5)
                    if random_ennemie2 != random_ennemie:
                        erreur = False
            random_ennemie3 = random.randint(1, 5)
            if random_ennemie3 == random_ennemie2 or random_ennemie3 == random_ennemie:
                erreur = True
                while erreur:
                    random_ennemie3 = random.randint(1, 5)
                    if random_ennemie3 != random_ennemie2 and random_ennemie3 != random_ennemie:
                        erreur = False
            random_ennemie4 = random.randint(1,5)
            if random_ennemie4 == random_ennemie3 or random_ennemie4 == random_ennemie2 or random_ennemie4 == random_ennemie:
                erreur = True
                while erreur:
                    random_ennemie4 = random.randint(1, 5)
                    if random_ennemie4 != random_ennemie3 and random_ennemie4 != random_ennemie2 and random_ennemie4 != random_ennemie:
                        erreur = False
            room = {"ennemie 1": ennemie_data_dur[random_ennemie], "ennemie 2": ennemie_data_dur[random_ennemie2],
                    "ennemie 3": ennemie_data_dur[random_ennemie3],
                    "ennemie 4" : ennemie_data_dur[random_ennemie4] , "switch_1" : info_switch1, "switch_2" : 
                    info_switch2}
            ennemie_data_dur[random_ennemie]["mort_def"],ennemie_data_dur[random_ennemie]["etat"] = False,"vivant"
            ennemie_data_dur[random_ennemie2]["mort_def"],ennemie_data_dur[random_ennemie2]["etat"] = False,"vivant"
            ennemie_data_dur[random_ennemie3]["mort_def"],ennemie_data_dur[random_ennemie3]["etat"] = False,"vivant"
            ennemie_data_dur[random_ennemie4]["mort_def"],ennemie_data_dur[random_ennemie4]["etat"] = False,"vivant"
        else:
            pass
        rooms.append(room)
        stages.append(stage)
        switch_collisions.append(switch_collision)
        for i in rooms[current_room].values():            
            collision.append(i)
            try:
                img = i["img"]               
                mask_ennemie.append(img)
            except:
                pass
            try:
                if type(i["rect"]) ==  type("s"):
                    pass
                else:
                    collision_.append(i["rect"])
            except:
                pass
        masks_ennemie.append(mask_ennemie)
        return rooms,stage,switch_collision

    def log_room():
        """
            fonction permettant de charger le donjon, charge les rooms et leur élément nécessaire
            :return: return nb_room (nombre max de room), room_passed (nombre de room visité),room_logged (les rooms visité),rooms (données des rooms)
        """
        global room_exist
        global room_pos
        global nb_room
        nb_room = random.randint(10,15)
        
        def valide_test(x,y):
            """
                fonction qui permet de valider si la position voulu est deja créé ou Non
                :param 1: x est l'ajout en x de la futur room
                :param 2: y est l'ajout en y de la futur room
                :CU: arg 1 et arg2 sont des int
                :return: Return si futur case peut etre crée ou pas, True or False
            """
            global room_exist
            global room_pos
            already_exist = False
            for i in room_exist:
                if i == [room_pos[0] + x, room_pos[1] + y]:
                    already_exist = True
            if not already_exist:
                new_room = [room_pos[0] + x, room_pos[1] + y]
                room_pos = new_room
                room_exist.append(new_room)
            return already_exist
            
        def attribute_place(pos,room_exist,current_room):
            """
               fonction permettant le reglage pour attribuer la class
                :param 1: la valeur de la futur position, exemple : x = +1, -x = -1, y = +1, -y = -1
                tout ca bien sur dans leur axe d'origine
                :param 2: le contener de toute les rooms creer
                :param 3: la room actuelle
                :return: return False si on ne peut pas placer la room, sinon True 
            """
            if pos == "x":
                already_exist = valide_test(1,0)
            elif pos == "-x":
                already_exist = valide_test(-1,0)
            elif pos == "y":
                already_exist = valide_test(0,1)
            elif pos == "-y":
                already_exist = valide_test(0,-1)
            if already_exist:
                return False
            return True
            
        def create_dungeon():
            global nb_room
            """
                fonction qui créé le dungeon; change la place de la room si elle ne peut pas etre crée
            """
            pos_switch = {"haut" : "y", "bas": "-y", "droit" : "x", "gauche" : "-y"}
            global room_exist
            global room_pos
            global room_visited
            room_exist = [[0,0]]
            room_pos = [0,0]
            room_visited = [[0,0]]
            mot = ["haut","bas","droit","gauche"]
            for i in range(nb_room-1):
                p = random.randint(0,3)
                pos = pos_switch[mot[p]]
                while not attribute_place(pos,room_exist,room_pos):
                    p = random.randint(0,3)
                    pos = pos_switch[mot[p]]
        create_dungeon()
        room_passed = 0
        room_logged = True
        rooms = []
        return nb_room, room_passed,room_logged,rooms

    def log_boss(rooms,list_place):
        """
            fonction permettant de charger la room du boss
            :param1: donnée de toute les rooms
            :param2: dict des pos_swictch possible
        """
        global rect_screen
        global collision
        global collision_
        global stage
        global stages
        global png_heal_room
        global joueur
        collision = []
        collision_ = []
        switch_collision = []
        stage = 69
        taille = 20
        pos_switch = [[rect_screen.w / 2 - taille / 2, 10 - taille / 2],
                      [rect_screen.w - 10 - taille / 2, rect_screen.h / 2 - taille / 2],
                      [rect_screen.w / 2 - taille / 2, rect_screen.h - 10 - taille / 2],
                      [10 - taille / 2, rect_screen.h / 2 - taille / 2]]
        for i, y in list_place.items():
            if y["etat"] and y["rect"] == "rouge":
                random_pos = pos_switch[y["nombre"]]
        switch_1 = pygame.draw.rect(screen, (255, 0, 0),
                                    (random_pos[0], random_pos[1], taille, taille))
        info_switch1 = {"id": -1, "rect": dict_equivalent_switch[(random_pos[0], random_pos[1], taille, taille)], "type": "switch"}
        info_switch2 = None
        switch_collision.append(info_switch1)
        if "Assassin" in joueur["class"]:
            boss_choose = 0
            music = "playlist_music/boss_assassin_main.ogg"
        elif "Guerrier" in joueur["class"]:
            boss_choose = 1
            music = "playlist_music/boss_chevalier_main.ogg"
        else:
            boss_choose = 2
            music = "playlist_music/boss_mage_main.ogg"
        pygame.mixer.music.load(music)
        pygame.mixer.music.play(-1,0,1000)
        room = {"ennemie 1" : boss_keep[boss_choose], "switch_1" : info_switch1, "switch_2" : 
            info_switch2}
        stages.append(stage)
        switch_collisions.append(switch_collision)
        rooms.append(room)
        collision.append(boss_keep[boss_choose])
        collision_.append(boss_keep[boss_choose]["rect"])
        return rooms,stage,switch_collision

    def change_room(rooms,current_room,nb_room,room_passed, id_):
        global dict_data
        global switch_collisions
        global going_back
        global have_heal_room
        global boss_room
        global room_exist
        global list_place
        global room_visited
        global went_back
        global pos_futur
        global cooldown_heal_room
        global heal_rooms
        global collision
        global collision_
        global mask_ennemie
        going_back = False
        went_back = False
        dict_data = {}
        current_room += id_
        if room_passed + id_ < len(room_exist) and current_room != 0:
            if (room_exist[current_room] in room_visited and room_exist[current_room + 1] in room_visited) or (room_exist[current_room] == room_visited[-1]):
                    went_back = True
        if id_ == -1:
            going_back = True
            went_back = True
        if id_ != -1 and (room_exist[current_room] not in room_visited):
            room_visited.append(room_exist[current_room])
        room_passed += id_
        list_place = {"haut": {"etat": False, "rect": 0, "nombre": 0}, "bas": {"etat": False, "rect": 0, "nombre": 2},
                      "gauche": {"etat": False, "rect": 0, "nombre": 3},
                      "droit": {"etat": False, "rect": 0, "nombre": 1}}
        for i in range(len(room_exist)):
            global room_actu
            room_actu = room_exist[current_room]
            if room_actu[0] + 1 == room_exist[i][0] and room_exist[i][1] == room_actu[1]:
                list_place["droit"]["etat"], list_place["droit"]["rect"] = True, room_exist[i]
            elif room_actu[0] - 1 == room_exist[i][0] and room_exist[i][1] == room_actu[1]:
                list_place["gauche"]["etat"], list_place["gauche"]["rect"] = True, room_exist[i]
            elif room_actu[1] + 1 == room_exist[i][1] and room_exist[i][0] == room_actu[0]:
                list_place["haut"]["etat"], list_place["haut"]["rect"] = True, room_exist[i]
            elif room_actu[1] - 1 == room_exist[i][1] and room_exist[i][0] == room_actu[0]:
                list_place["bas"]["etat"], list_place["bas"]["rect"] = True, room_exist[i]
        try:            
            if room_exist[current_room + 1][0] == room_actu[0]:
                if room_exist[current_room + 1][1] == room_actu[1] + 1:
                    place_first = "haut"
                elif room_exist[current_room + 1][1] == room_actu[1] - 1:
                    place_first = "bas"
            elif room_exist[current_room + 1][0] != room_actu[0]:
                if room_exist[current_room + 1][0] == room_actu[0] - 1:
                    place_first = "gauche"
                elif room_exist[current_room + 1][0] == room_actu[0] + 1:
                    place_first = "droit"
            list_place[place_first]["rect"] = "vert"
        except:
            place_first = "fboss"
        if current_room > 0:
            if room_exist[current_room - 1][0] == room_actu[0]:
                if room_exist[current_room - 1][1] == room_actu[1] + 1:
                    place_second = "haut"
                elif room_exist[current_room - 1][1] == room_actu[1] - 1:
                    place_second = "bas"
            elif room_exist[current_room - 1][0] != room_actu[0]:
                if room_exist[current_room - 1][0] == room_actu[0] - 1:
                    place_second = "gauche"
                elif room_exist[current_room - 1][0] == room_actu[0] + 1:
                    place_second = "droit"
            list_place[place_second]["rect"] = "rouge"
        if current_room != 0:
            if going_back:
                pos_futur = place_first
            else:
                pos_futur = place_second
        else:
            pos_futur = place_first
        heal_room = False
        boss_room = False
        if room_passed >= nb_room:
            boss_room = True
            heal_room = False
        if went_back is False and not boss_room:
            collision = []
            collision_ = []
            switch_collision = []
            mask_ennemie = []
            if have_heal_room <= max_heal_room:
               if current_room < nb_room and cooldown_heal_room <= 0:
                    spawn_heal_room = random.randint(0,8)
                    if spawn_heal_room <= 5:
                        have_heal_room +=1
                        cooldown_heal_room = 2
                        heal_room = True
                    else:
                        heal_room = False
                    boss_room = False
               else:
                   cooldown_heal_room -= 1
            heal_rooms.append(heal_room)
        elif went_back is True and room_passed < nb_room:
            heal_room = heal_rooms[current_room]
            switch_collision = switch_collisions[current_room]
        if not heal_room and boss_room == False:
            if went_back != True:
                rooms,stage,switch_collision = log_ennemie(current_room,nb_room,room_passed,switch_collision,rooms,list_place)
            else:
                """
                mask_ennemie = []
                collision = []
                collision_ = []
                for i in rooms[current_room].values():            
                    collision.append(i)
                    try:
                        if type(i["rect"]) ==  type("s"):
                            pass
                        else:
                            collision_.append(i["rect"])
                    except:
                        pass
                """
                stage = stages[current_room]
                switch_collision = switch_collisions[current_room]
        if boss_room:
            if went_back != True:
                rooms,stage,switch_collision = log_boss(rooms,list_place)
            else:
                if "Assassin" in joueur["class"]:
                    boss_choose = 0
                elif "Guerrier" in joueur["class"]:
                    boss_choose = 1
                else:
                    boss_choose = 2
                collision.append(boss_keep[boss_choose])
                collision_.append(boss_keep[boss_choose]["rect"])
                stage = stages[current_room]
                switch_collision = switch_collisions[current_room]
        if heal_room:
            if went_back != True:
                rooms,stage,switch_collision = log_heal_room(list_place)
            else:
                collision.append(png_heal_room)
                collision_.append(png_heal_room["rect"])
                stage = stages[current_room]
                switch_collision = switch_collisions[current_room]
        return rooms,switch_collision,stage,heal_room,current_room,room_passed,boss_room,going_back

    def pop_up_clavier_tuto():
        screen.fill((200, 200, 200))
        draw_in("Regarder attentivement ! ", 0, clavier_rect, 25,
                color_pick["bordeaux_f"], minecraft_factory, clavier_rect.w / 2 -
                get_dimension("Regarder attentivement ! ", minecraft_factory,
                              25, False, True)[0] / 2,
                -50, False, True)
        screen.blit(clavier, clavier_rect)
        pygame.draw.rect(screen, (0, 0, 0), clavier_rect, 2)
        pygame.display.flip()


    global active
    active = False
    global fix
    fix = 0
    global pos_img1
    pos_img1 = pygame.Rect(0,100,default_size[0],default_size[1])
    global repos_left
    repos_left = 4
    global data_recup
    data_recup = False
    room_logged = False
    
    def menu():
        sound_log = pygame.mixer.music.load("playlist_music/the_dying_main.ogg")
        pygame.mixer.music.play(-1,0,1000)
        can_quit = False
        coupage = 0
        active = False
        input_user = ""
        while True:
            if can_quit:
                break
            screen.fill((200,200,200))            
            if file_full == "":
                log_host()
            if file_full != "" and test_nom_user(file_full) != "" and test_class_user(file_full) != "":
                joueur, joueur_sprite, sprite_group_right,sprite_group_left = presentation(0, file_full)
                break
            if file_full != "" and test_nom_user(file_full) == "":
                max_letter = 20
                screen.fill((200,200,200))
                collide = False
                mouse = pygame.mouse.get_pos()
                pop_up = appear_pop_up()
                text = "Entrez votre pseudo"
                draw_in(text, 0, pop_up, 25, (0, 0, 0), csm, pop_up.w / 2 - get_dimension(text, csm, 25)[0] / 2, 5)
                if not active:
                    text = "clickez sur l'input pour l'activer/desactiver"
                else:
                    text = "bien joué"
                draw_in(text, 0, pop_up, 25, (0, 0, 0), csm, pop_up.w / 2 - get_dimension(text, csm, 25)[0] / 2, pop_up.h)
                box_input = pygame.Rect(pop_up.x + (pop_up.w / 2 - 140 / 2), pop_up.y + pop_up.h / 2 - 32 / 2 + 20, 140, 32)
                color_box = (0, 255, 0)
                color_passive = (255, 0, 0)
                input_place = input_nom.render(input_user[coupage:], True, (255, 255, 255))
                screen.blit(input_place, (box_input.x + 5, box_input.y + box_input.h / 4))
                if len(input_user) > box_input.w - 10:
                    coupage_debut = True
                else:
                    coupage_debut = False
                barre_type = pygame.Surface((1,20))
                barre_type.fill((0,0,0))
                if active:
                    screen.blit(barre_type,(box_input.x + 5 + input_nom.size(input_user)[0], box_input.y + box_input.h / 4))
                    pygame.draw.rect(screen, color_box, box_input, 2)
                else:
                    pygame.draw.rect(screen, color_passive, box_input, 2)
                rect_start = make_suivant_button(mouse = mouse, pos = ((pop_up.x+pop_up.w/2-150/2,pop_up.y+pop_up.h+50)))
                    
            
            if file_full != "" and test_nom_user(file_full) != "" and test_class_user(file_full) == "":
                max_letter = 20
                mouse = pygame.mouse.get_pos()
                pop_up = appear_pop_up()
                text = "CHOISSISEZ UNE CLASSE"
                draw_in(text, 0, pop_up, 25, (255, 255, 255), csm, pop_up.w / 2 - get_dimension(text, csm, 25)[0] / 2, 5)
                if not active:
                    text = "clickez sur l'input pour l'activer/desactiver"
                else:
                    text = "bien joué"
                draw_in(text, 0, pop_up, 25, (0, 0, 0), csm, pop_up.w / 2 - get_dimension(text, csm, 25)[0] / 2, pop_up.h)
                text_class = ["-1- Guerrier","-2- Assassin","-3- Mage"]
                dico_sprite = [pygame.transform.scale(pygame.image.load("image_site\sprite_chevalier_stand.png").convert_alpha(), (50,50))
                                , pygame.transform.scale(pygame.image.load("image_site\sprite_assasin_stand.png").convert_alpha(),(50,50))
                               , pygame.transform.scale(pygame.image.load("image_site\sprite_mage_stand.png").convert_alpha(),(50,50))]
                rect = [x.get_rect() for x in dico_sprite]
                rect_i = [i for i in range(len(dico_sprite))]
                dico_class = {"1": "Guerrier", "2": "Assassin", "3": "Mage", "Assassin" : "Assassin", "Mage" : "Mage", "Guerrier" : "Guerrier"}
                marge = [10, 200, 370]
                for i in range(len(text_class)):
                    draw_in(text_class[i], 0, pop_up, 25, (0, 0, 0), csm, marge[i], 40)
                    screen.blit(dico_sprite[i],(pop_up.x + marge[i] + 20,pop_up.y + 75))
                    rect[i][0] = pop_up.x + marge[i] + 20
                    rect[i][1] = pop_up.y + 75
                anime_sprite_assassin = [pygame.image.load("image_site/sprite_assassin_right_1.png").convert_alpha(),pygame.image.load("image_site/sprite_assassin_right_2.png").convert_alpha(),pygame.image.load("image_site/sprite_assassin_right_3.png").convert_alpha()]
                anime_sprite_assassin = [pygame.transform.scale(element,(50,50)) for element in anime_sprite_assassin]
                anime_sprite_guerrier = [pygame.image.load("image_site/sprite_chevalier_stand.png").convert_alpha(),pygame.image.load("image_site/knigh_1.png").convert_alpha(),pygame.image.load("image_site/knigh_2.png").convert_alpha()]
                anime_sprite_guerrier = [pygame.transform.scale(element,(50,50)) for element in anime_sprite_guerrier]
                sprite_group = [anime_sprite_guerrier,anime_sprite_assassin,0]
                def anime_sprite(sprite_group):
                    global current_sprite
                    current_sprite += 0.5
                    if current_sprite >= len(sprite_group):
                        current_sprite = 0
                    return sprite_group[int(current_sprite)]
                b = 0
                anim = False
                collide = False
                for i in rect:
                    if i.collidepoint(mouse):
                        pygame.draw.rect(screen,(0,200,0),i,1)
                        if sprite_group[b] != 0:
                            anim = True
                        index_anim = b
                        rect_anim = i
                        input_user = f"{dico_class[str(rect_i[rect.index(i)] +1)]}"
                        collide = True
                    b+=1
                if anim:
                    screen.fill((80,80,80),rect_anim)
                    pygame.draw.rect(screen,(0,200,0),(rect_anim[0],rect_anim[1],rect_anim[2]+5,rect_anim[3]+5),1)
                    screen.blit(anime_sprite(sprite_group[index_anim]),rect_anim)
                    pygame.display.update(rect_anim)
                box_input = pygame.Rect(pop_up.x + (pop_up.w / 2 - 140 / 2), pop_up.y + pop_up.h / 2 - 32 / 2 + 20, 140, 32)
                color_box = (0, 255, 0)
                color_passive = (255, 0, 0)
                input_place = input_nom.render(input_user[coupage:], True, (255, 255, 255))
                screen.blit(input_place, (box_input.x + 5, box_input.y + box_input.h / 4))
                if len(input_user) > box_input.w - 10:
                    coupage_debut = True
                else:
                    coupage_debut = False
                barre_type = pygame.Surface((1,20))
                barre_type.fill((0,0,0))
                if active:
                    screen.blit(barre_type,(box_input.x + 5 +input_nom.size(input_user)[0], box_input.y + box_input.h / 4))
                    pygame.draw.rect(screen, color_box, box_input, 2)
                else:
                    pygame.draw.rect(screen, color_passive, box_input, 2)
                rect_start = make_suivant_button(mouse = mouse, pos = ((pop_up.x+pop_up.w/2-150/2,pop_up.y+pop_up.h+50)))
                    
            pygame.display.flip()
            mods = pygame.key.get_mods()
            # vérifier si la touche Verr Maj est enfoncée
            if mods & pygame.KMOD_CAPS:
                maj = True
            else:
                maj = False
            keys = pygame.key.get_pressed()
            mouse_click = pygame.mouse.get_pressed()
            if keys[pygame.K_RSHIFT] or keys[pygame.K_LSHIFT]:
                maj = True
            else:
                if maj != True:
                    maj = False
            for event in pygame.event.get():
                if file_full != "":
                    if box_input.collidepoint(mouse):
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            active = not active
                   
                    if collide:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            class_ = dico_class[str(input_user)]
                            log_class_user(class_, file_full)
                            can_quit = True
                            joueur, joueur_sprite,sprite_group_right,sprite_group_left = presentation(0, file_full)
                            quitter = True
                   
                    
                    if active:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_BACKSPACE:
                                input_user = input_user[:-1]
                                if coupage_debut:
                                    coupage -= 1
                            elif event.key == pygame.K_SPACE and max_letter > len(input_user):
                                input_user = input_user + " "
                                if coupage_debut:
                                    coupage += 1
                            elif event.key == pygame.K_RETURN:
                                if test_nom_user(file_full) == "":
                                    if input_user != "":
                                        log_nom_user(input_user, file_full)
                                        input_user = ""
                                        active = False
                                        coupage_debut = False
                                        coupage = 0
                                    else:
                                        input_user = ""
                                        text = "Input non valide"
                                        center_screen(text, comic_sans_ms, get_dimension(text, csm,20),0,False)
                                        pygame.display.flip()
                                        pygame.time.delay(500)
                                        

                                else:
                                    try:
                                        if input_user in dico_class:
                                            class_ = dico_class[input_user]
                                            log_class_user(class_, file_full)
                                            joueur, joueur_sprite,sprite_group_right,sprite_group_left = presentation(0, file_full)
                                            can_quit = True
                                        else:
                                            input_user = ""
                                            text = "Input non Valide !"
                                            center_screen(text, comic_sans_ms, get_dimension(text, csm,20),0,False)
                                            pygame.display.flip()
                                            pygame.time.delay(500)
                                            

                                    except:
                                        input_user = ""
                            else:
                                if max_letter > len(input_user):
                                    input_user += event.unicode if not maj else event.unicode.upper()
                                    if coupage_debut:
                                        coupage += 3
                    if rect_start.collidepoint(mouse) and event.type == pygame.MOUSEBUTTONDOWN:
                        if test_nom_user(file_full) == "":
                            if input_user != "":
                                log_nom_user(input_user, file_full)
                                input_user = ""
                                active = False
                            else:
                                input_user = ""
                                text = "Input non Valide !"
                                center_screen(text, comic_sans_ms, get_dimension(text, csm,20),0,False)
                                pygame.display.flip()
                                pygame.time.delay(500)
                        else:
                            try:
                                if input_user in dico_class:
                                    class_ = dico_class[input_user]
                                    log_class_user(class_, file_full)
                                    joueur, joueur_sprite,sprite_group_right,sprite_group_left = presentation(0, file_full)
                                    can_quit = True
                                else:
                                    input_user = ""
                                    text = "Input non Valide !"
                                    center_screen(text, comic_sans_ms, get_dimension(text, csm,20),0,False)
                                    pygame.display.flip()
                                    pygame.time.delay(500)

                            except:
                                input_user = ""
                try:
                    if quitter:
                        break
                except:
                    pass
            if can_quit:
                break
    menu()
        
    global text_heal
    text_heal = "Parler au png pour vous Heal ou Sorter."
    global image_charged
    image_charged = False
    global dict_data
    dict_data = {}
    global died_in_game
    died_in_game = False
    
    def rewrite_dos(file = file_full):
        make_sauvegarde(file = file_full,Ingame = False)
        
    wait = False
    sauvegarde_rapide = False
    global Tueur
    Tueur = None
    click_retour = False
    while running:
        clock.tick(100)
        pressed_keys = pygame.key.get_pressed()
        def ecran(dict_data):
            global joueur
            global joueur_sprite
            global new_data
            global sprite_group_right
            global sprite_group_left
            global data_recup         
            global mort_def
            global pos_img1
            global room_logged
            global heal_room
            global boss_room
            global rooms
            global stage
            global stages
            global switch_collision
            global mask_player
            global current_room
            global going_back
            global move_up
            global move_left
            global move_down
            global move_right
            global current_sprite
            global group_using
            global collision
            global collision_           
            global mask_ennemie
            global room_exist
            global room_visited
            global room_actu
            global combat
            global repos_left
            global room_passed
            global nb_room
            global can_switch
            global big_size
            global went_back
            global inverse_dict_equivalent_switch
            global end_game
            global died_in_game
            global heal_rooms
            global switch_collisions
            global Tueur
            if combat == False and not died_in_game:
                with open(file_full, "r") as fichier:
                    li = fichier.read().splitlines()
                    save_recup = False
                    nom_recup = False
                    for i in range(len(li)):
                        global save
                        global nom
                        global class_
                        if "save" in li[i] and not save_recup:
                            save = li[i]
                            save_recup = True
                        if li[i] == "nom" and not nom_recup:
                            nom = li[i+1]
                            nom_recup = True
                        if li[i] == "class":
                            class_ = li[i+1]
                        if "room_already_logged" in li[i]:
                            if not data_recup:
                                room_logged = True
                                with open(file_full, "r") as fichier:
                                    li = fichier.read().splitlines()
                                    for p in range(len(li)):
                                        if "mask_ennemie" in li[p]:
                                            mask_ennemie = json.loads(li[p+1])
                                        if "nb_room" in li[p]:
                                            nb_room = int(li[p+1])
                                        elif "room_passed" in li[p]:
                                            room_passed = int(li[p+1])
                                        elif "rooms" in li[p]:
                                            rooms = json.loads(li[p+1])
                                        elif "switch_collision" in li[p]:
                                            json_object = json.dumps(li[p+1])
                                            switch_collision = eval(json.loads(json_object))
                                        elif "stage" in li[p]:
                                            stage = int(li[p+1])
                                        elif "heal_room" in li[p]:
                                            heal_room = eval(li[p+1])
                                        elif "current_room" in li[p]:
                                            current_room = int(li[p+1])
                                        elif "room_passed" in li[p]:
                                            room_passed = int(li[p+1])
                                        elif "boss_room" in li[p]:
                                            boss_room = eval(li[p+1])
                                        elif "going_back" in li[p]:
                                            going_back = eval(li[p+1])
                                        elif "room_exist" in li[p]:
                                            json_object = json.dumps(li[p+1])
                                            room_exist = eval(json.loads(json_object))
                                        elif "room_visited" in li[p]:
                                            json_object = json.dumps(li[p+1])
                                            room_visited = eval(json.loads(json_object))
                                        elif "room_actu" in li[p]:
                                            json_object = json.dumps(li[p+1])
                                            room_actu = eval(json.loads(json_object))
                                        elif "can_switch" in li[p]:
                                            json_object = json.dumps(li[p+1])
                                            can_switch = eval(json.loads(json_object))
                                        elif "collision1" in li[p]:
                                            collision = json.loads(li[p+1])
                                        elif "collision2" in li[p]:                                        
                                            collision_ = json.loads(li[p+1])
                                        elif "cooldown_heal_room" in li[p]:
                                            cooldown_heal_room = int(li[p+1])
                                        elif "have_heal" in li[p]:
                                            have_heal_room = int(li[p+1])
                                        elif "heal_log" in li[p]:
                                            heal_rooms = json.loads(li[p+1])
                                        elif "repos_left" in li[p]:
                                            repos_left = int(li[p+1])
                                        elif "recup_switch" in li[p]:
                                            switch_collisions = json.loads(li[p+1])
                                        elif "recup_stagz" in li[p]:
                                            stages = json.loads(li[p+1])
                                        elif "went_back" in li[p]:
                                            went_back = eval(li[p+1])
                                    data_recup = True                                   
                screen.fill(background)
                if not room_logged:
                    nb_room,room_passed,room_logged,rooms = log_room()
                    rooms,switch_collision,stage,heal_room,current_room,room_passed,boss_room,going_back = change_room(rooms,current_room,nb_room,room_passed,1)
                if len(dict_data) <= 0:
                    i = 0 #nous permet de mettre des keys identiques
                    for data,key in rooms[current_room].items():
                        if not "switch" in data:
                            if not (i,key["img"]) in dict_data:
                                img = pygame.image.load(key["img"]).convert()
                                img.set_colorkey((0,0,0))
                                dict_data[(i,key["img"])] = pygame.transform.scale(img,resize_ennemie)
                            try:
                                if key["mort_def"] is True and (i,key["img"]) in dict_data:
                                    dict_data.pop((i,key["img"]))
                            except:
                                pass
                            i += 1
                max_x = 0                        
                min_y = 0
                min_x = 0
                max_y = 0
                for i in room_exist:
                    if i[0] > max_x:
                        max_x = i[0]
                    if i[0] < min_x:
                        min_x =  i[0]
                    if i[1] < min_y:
                        min_y = i[1]
                    if i[1] > max_y:
                        max_y = i[1]
                width_x = max_x * 18 - abs(min_x)*18
                height_y = (abs(max_y) * 18) - (abs(min_y) * 18)
                for room in room_exist:
                    for room_ in room_visited:
                        if room == room_:
                            pygame.draw.rect(screen,((0,255,0)), ((room[0] * 18 + rect_screen.w - width_x - 100, -room[1] * 18 + rect_screen.h- 100-abs(height_y), 15,15)))
                    pygame.draw.rect(screen,((0,0,0)), ((room[0] * 18 + rect_screen.w - width_x - 100, -room[1] * 18 + rect_screen.h- 100 - abs(height_y), 15,15)), 1)
                    if room == room_actu:
                        pygame.draw.rect(screen,((0,0,255)), ((room[0] * 18 + rect_screen.w - width_x - 100, -room[1] * 18 + rect_screen.h- 100 - abs(height_y), 15,15)), 3)
                    if room == room_exist[-1]:
                        pygame.draw.rect(screen, ((255, 0, 0)), ((room[0] * 18 + rect_screen.w - width_x - 100,
                                                                  -room[1] * 18 + rect_screen.h - 100 - abs(
                                                                      height_y), 15, 15)),1)
                if heal_room:
                    color = (0,200,0)
                elif boss_room:
                    color = (0,0,200)
                else:
                    color = (200,0,0)
                draw_in(f"{room_passed}","u",rect_screen,500,color,minecraft_factory,rect_screen.w/2 - get_dimension(f"{room_passed}", minecraft_factory,500,False,True)[0]/2,rect_screen.h/2-get_dimension(f"{room_passed}", minecraft_factory,500,False,True)[1]/2,False,True,True)
                joueur_sprite = pygame.transform.scale(joueur_sprite, default_size)
                mask_player = pygame.mask.from_surface(joueur_sprite)            
    
                if not move_left and not move_right and not move_up and not move_down:
                    global current_speed
                    current_speed = 0
                    global current_sprite
                    current_sprite = 0
                    if sprite_group_right != 0:
                        try:
                            group_using[0] = pygame.transform.scale(group_using[0],default_size)
                            screen.blit(group_using[0],pos_img1)
                        except:                           
                            image = pygame.transform.scale(sprite_group_right[0],default_size)
                            screen.blit(image, pos_img1)
                    else:
                        joueur_sprite.set_colorkey((0,0,0))
                        image = pygame.transform.scale(joueur_sprite,default_size)
                        screen.blit(joueur_sprite,pos_img1)
                else:
                    screen.blit(joueur_sprite, pos_img1)
                longueur_vie_restante = (joueur["stat_joueur"]["vie"] / joueur["stat_joueur"]["vie_max"]) * longueur_barre
                pourcentage_vie_restante = 100 * (longueur_vie_restante / longueur_barre)
                pourcentage_energie_restante = (joueur["stat_joueur"]["energie"] / joueur["stat_joueur"]["energie_max"]) *100
                pygame.draw.rect(surface_barre_vie, couleur_barre_vie, (0, 0, longueur_barre, hauteur_barre))
                pygame.draw.rect(surface_barre_vie,couleur_vie_restante, (0, 0, longueur_vie_restante, hauteur_barre))
                screen.blit(surface_barre_vie,(get_dimension(f"Vie : ", csm, 20)[0] + 10 ,10 + hauteur_barre + 2))
                longueur_energie_restante = (joueur["stat_joueur"]["energie"] / joueur["stat_joueur"]["energie_max"]) * longueur_barre
                pygame.draw.rect(surface_barre_vie, couleur_barre_energie, (0, 0, longueur_barre, hauteur_barre))
                pygame.draw.rect(surface_barre_vie,couleur_energie_restante, (0, 0, longueur_energie_restante, hauteur_barre))
                screen.blit(surface_barre_vie,(get_dimension(f"Energie : ", csm, 20)[0] + 10 ,30 + hauteur_barre))
                draw_text(f" {round(pourcentage_vie_restante)}%", comic_sans_ms, (0,0,0), get_dimension(f"Vie : ", csm, 20)[0] + 10 + longueur_barre,10)
                draw_text(f" {round(pourcentage_energie_restante)}%", comic_sans_ms, (0,0,0), get_dimension(f"Energie : ", csm, 20)[0] + 10 + longueur_barre,30)
                draw_text(f"Vie : ", comic_sans_ms, color_pick["vert"],10 ,10)
                draw_text(f"Energie : ", comic_sans_ms, color_pick["bleu_f"],10,30)
                draw_text(f"{nom} - level {int(joueur['level'])}", comic_sans_ms, (255,255,255), rect_screen.w -10 - get_dimension(f"{nom} - level {int(joueur['level'])}",csm,20)[0], 0)
                draw_text(f"gold : {int(joueur['stat_joueur']['or'])}", comic_sans_ms, pygame.Color(255,215,0,10), rect_screen.w -10 - get_dimension(f"gold : {int(joueur['stat_joueur']['or'])}",csm,20)[0], 20)
                draw_text(f"xp : {int(joueur['stat_joueur']['exp'])}/{int(joueur['stat_joueur']['exp_needed'])}", comic_sans_ms, color_pick["cyan"], rect_screen.w -10 - get_dimension(f"xp : {int(joueur['stat_joueur']['exp'])}/{int(joueur['stat_joueur']['exp_needed'])}",csm,20)[0], 40)
                
                def make_barre_repos(repos_restant,pos : tuple,color):
                    width = 0
                    width_box = 20
                    height_box = 10
                    for i in range(repos_restant):
                        pygame.draw.rect(screen,color, (pos[0] + (width_box * i) + 5*i,pos[1],width_box,10))
                        width += width_box + (width_box * i) + 5*i
                    return width
                
                width = 0
                for i in range(repos_left):
                    width += 20 + (20*1)
                height = 10
                make_barre_repos(repos_left,(rect_screen.w - 20 -width/2,60 + height+2),(0,100,200))
                draw_text(f"repos restant : ", comic_sans_ms, (25,25,25), rect_screen.w - 10 - get_dimension(f"repos restant : ",csm,20)[0] - width/2 - 20, 60) if repos_left > 0 else\
                draw_text(f"Aucun repos", comic_sans_ms, (25,25,25), rect_screen.w - 10 - get_dimension(f"Aucun repos",csm,20)[0] - width/2, 60)
                if not heal_room:                    
                    if len(switch_collision) == 1:
                        if boss_room:
                            pygame.draw.rect(screen, (0, 0, 0), inverse_dict_equivalent_switch[rooms[current_room]["switch_1"]["rect"]])
                            pygame.draw.rect(screen, (255, 0, 0), inverse_dict_equivalent_switch[rooms[current_room]["switch_1"]["rect"]], 1)
                        else:
                            pygame.draw.rect(screen,(0,0,0), inverse_dict_equivalent_switch[rooms[current_room]["switch_1"]["rect"]])
                            pygame.draw.rect(screen,(0,255,0), inverse_dict_equivalent_switch[rooms[current_room]["switch_1"]["rect"]],1)
                    else:
                        pygame.draw.rect(screen,(0,0,0), inverse_dict_equivalent_switch[rooms[current_room]["switch_1"]["rect"]])
                        pygame.draw.rect(screen, (0, 255, 0), inverse_dict_equivalent_switch[rooms[current_room]["switch_1"]["rect"]], 1)
                        pygame.draw.rect(screen,(0,0,0), inverse_dict_equivalent_switch[rooms[current_room]["switch_2"]["rect"]])
                        pygame.draw.rect(screen,(255,0,0), inverse_dict_equivalent_switch[rooms[current_room]["switch_2"]["rect"]],1)
                    if went_back:
                        collision = []
                        collision_ = []
                        mask_ennemie = []
                    if not went_back:                      
                        var = 0
                        i = 0
                        for keys,values in rooms[current_room].items():
                            if not "switch" in keys:                            
                                if values["etat"] == "vivant" and values["mort_def"] == False:
                                    img = dict_data[(i,values["img"])]
                                    
                                    screen.blit(img, pygame.Rect(values["rect"]))
                                    draw_in(f"~ {values['categorie']} ~", 0, pygame.Rect(values["rect"]), 20,
                                            (255, 255, 255), csm, pygame.Rect(values["rect"][0],values["rect"][1],255,210).w / 2 -
                                            get_dimension(f"~ {values['categorie']} ~", csm, 20)[0] / 2, -20)
                                if values["etat"] != "vivant" and values["mort_def"] == False:                                
                                    rooms[current_room][keys]["mort_def"] = True
                                    
                                i+=1
                            var += 1
                    if end_game:
                        pop_up = appear_pop_up(1)
                        text = f"Bravo {joueur['nom']} Vous avez fini ce donjon (chomeur) !"
                        draw_in(text, 0, pop_up, 27, (255,255,255), sinistre, pop_up.w/2 - get_dimension(text,sinistre,27,False,True)[0]/2, 20,False,True)
                        rect_quit = pygame.Rect(pop_up.x + pop_up.w/2 - (get_dimension("Quitter(1)",csm,20)[0] + 10)/2, pop_up.y + pop_up.h/2-get_dimension("Quitter(1)",csm,20)[1]/2,
                                                         get_dimension("Quitter(1)",csm,20)[0] + 10, get_dimension("Quitter(1)",csm,20)[1] + 10)
                        rect_restart = pygame.Rect(pop_up.x+pop_up.w/2-(get_dimension("Recommencer(2)",csm,20)[0] + 10)/2, pop_up.y + pop_up.h/2-get_dimension("Recommencer(2)",csm,20)[1]/2 + 100,
                                                         get_dimension("Recommencer(2)",csm,20)[0] + 10, get_dimension("Recommencer(2)",csm,20)[1] + 10)
                        current_room = -1
                        stages = []
                        rooms = []
                        mask_ennemie = []
                        switch_collision = []
                        have_heal_room = False
                        went_back = False
                        going_back = False
                        room_logged = False
                        dict_data = {}
                        end_game = False
                        color_quit = (0,0,0)
                        color_restart=(0,0,0)
                        pygame.display.flip()
                        def repos_life_energie():
                            joueur["stat_joueur"]["vie"] = joueur["stat_joueur"]["vie_max"]
                            joueur["stat_joueur"]["energie"] = joueur["stat_joueur"]["energie_max"]
                            return joueur
                        while True:
                            mouse = pygame.mouse.get_pos()
                            if rect_quit.collidepoint(mouse):
                                color_quit = (200,0,0)
                            else:
                                color_quit = (0,0,0)
                            if rect_restart.collidepoint(mouse):
                                color_restart = (0,200,0)
                            else:
                                color_restart = (0,0,0)
                            pygame.draw.rect(screen,color_quit,rect_quit)
                            pygame.draw.rect(screen,color_restart,rect_restart)
                            text = "Quitter(1)"
                            draw_in(text, 0, pop_up, 20, (255,255,255), csm, pop_up.w/2 - get_dimension(text,csm,20)[0]/2, pop_up.h/2-get_dimension(text,csm,20)[1]/2)
                            text = "Recommencer(2)"
                            draw_in(text, 0, pop_up, 20, (255,255,255), csm, pop_up.w/2 - get_dimension(text,csm,20)[0]/2, pop_up.h/2-get_dimension(text,csm,20)[1]/2 + 100)
                            pygame.display.update(rect_quit)
                            pygame.display.update(rect_restart)
                            event = pygame.event.wait()
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                                    joueur = repos_life_energie()
                                    left_game(Ingame = False)
                                elif event.key == pygame.K_2 or event.key == pygame.K_KP2:
                                    joueur = repos_life_energie()
                                    break
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                if rect_quit.collidepoint(mouse):
                                    joueur = repos_life_energie()
                                    left_game(Ingame = False)
                                elif rect_restart.collidepoint(mouse):
                                    joueur = repos_life_energie()
                                    break
                        switch_collision,nb_room  = ecran(dict_data)                               
                elif heal_room == True and boss_room == False:
                    draw_text(text_heal, pygame.font.SysFont(arial,40),(0,0,0),rect_screen.x + rect_screen.w/2 - get_dimension(text_heal, arial,40)[0]/2, rect_screen.h - 50)
                    pygame.draw.rect(screen, (0, 0, 0), inverse_dict_equivalent_switch[rooms[current_room]["switch_1"]["rect"]])
                    pygame.draw.rect(screen, (0, 255, 0), inverse_dict_equivalent_switch[rooms[current_room]["switch_1"]["rect"]], 1)
                    pygame.draw.rect(screen, (0, 0, 0), inverse_dict_equivalent_switch[rooms[current_room]["switch_2"]["rect"]])
                    pygame.draw.rect(screen, (255, 0, 0), inverse_dict_equivalent_switch[rooms[current_room]["switch_2"]["rect"]], 1)
                    draw_in("Seraphine", 0,pygame.Rect(rooms[current_room]["png"]["rect"]),40,(0,0,0),arial,pygame.Rect(rooms[current_room]["png"]["rect"]).w/2 -
                            get_dimension("Seraphine", arial,40)[0]/2, -60)
                    if len(dict_data) <= 0:
                        for key,data in rooms[current_room].items():
                            if not "switch" in key:
                                img = pygame.image.load(data["img"]).convert()
                                img.set_colorkey((0,0,0))
                                img = pygame.transform.scale(img,resize_ennemie)
                                dict_data[data["img"]] = img
                    img = dict_data[(0,rooms[current_room]["png"]["img"])]
                    screen.blit(img,pygame.Rect(rooms[current_room]["png"]["rect"]))
            elif died_in_game:         
                class_ = joueur["class"]
                nom = joueur["nom"]
                if class_ == "Guerrier":
                    joueur = {"class" : "Guerrier", "nom" : nom, "level" : 1, "stat_joueur" : {"reflexe" : 10,"force" : 5, "vitesse" : 2, "agilite" : 1, "magie" : 0, "vie" : 150, "vie_max" : 150,"vol_de_vie" : 0, "energie" : 150, "energie_max" : 150, "item" : [item_holder["potion_force_base"], item_holder["potion_defence_base"], item_holder["potion_endurance_base"]], "abilite" : [{"nom" : "coup de poing","degat" : 10,  "coup_en_energie" : 0, "vitesse" : 5, "damage_reduction" : 0, "ulti" : False, "turn_to_work" : None, "atk_type": "force"}, {"nom" : "slash", "degat" :  10,  "coup_en_energie" : 5, "vitesse" : 9, "damage_reduction" : 0, "ulti" : False, "turn_to_work" : None, "atk_type": "force"},{"nom" : "Combo Barbare", "degat" : 50,  "coup_en_energie" : 15, "vitesse" : 25, "damage_reduction" : 0, "ulti" : True, "turn_to_work" : 4, "atk_type": "force"}, {"nom" : "Garde du chevalier", "degat" : 0,  "coup_en_energie" : 10, "vitesse" : 2, "damage_reduction" : 25, "ulti" : False, "turn_to_work" : None, "atk_type": "aucun", "tour_effect" : 2, "defence_reduction" : 2}],"exp" : 0, "exp_needed" : 69,"or" : 0}, "item_bag" : []}
                    joueur_sprite = pygame.image.load("image_site/sprite_chevalier_stand.png").convert_alpha()
                    sprite_group_right,sprite_group_left = 0,0
                    image_stand = joueur_sprite
                elif class_ == "Assassin":
                    joueur = {"class" : "Assassin", "nom" : nom, "level" : 1, "stat_joueur" : {"reflexe" : 15,"force" : 2, "vitesse" : 5, "agilite" : 3, "magie" : 0, "vie" : 130,"vie_max" : 130, "vol_de_vie" : 0, "energie" : 150, "energie_max" : 150, "item" : [item_holder["potion_force_base"], item_holder["potion_defence_base"], item_holder["potion_endurance_base"]], "abilite" : [{"nom" : "coup de poing","degat" : 10,  "coup_en_energie" : 0, "vitesse" : 5, "damage_reduction" : 0, "ulti" : False, "turn_to_work" : None, "atk_type": "force"}, {"nom" : "Coup rapide", "degat" :  13,  "coup_en_energie" : 15, "vitesse" : 12, "damage_reduction" : 0, "ulti" : False, "turn_to_work" : None, "atk_type": "force"},{"nom" : "Mise a mort", "degat" : 50,  "coup_en_energie" : 15, "vitesse" : 30, "damage_reduction" : 0, "ulti" : True, "turn_to_work" : 4, "atk_type": "force"}, {"nom" : "Invisibilité", "degat" : 0,  "coup_en_energie" : 5, "vitesse" : 100, "damage_reduction" : 100, "ulti" : False, "turn_to_work" : None, "atk_type": "aucun", "tour_effect" : 2}],"exp" : 0, "exp_needed" : 69,"or" : 0}, "item_bag" : []}
                    joueur_sprite = pygame.image.load("image_site/sprite_assasin_stand.png").convert_alpha()
                    sprite_group_right = [pygame.image.load("image_site/sprite_assassin_right_1.png").convert_alpha(),pygame.image.load("image_site/sprite_assassin_right_2.png").convert_alpha(),pygame.image.load("image_site/sprite_assassin_right_3.png").convert_alpha()]
                    sprite_group_left = [pygame.image.load("image_site/sprite_assassin_left_1.png").convert_alpha(),pygame.image.load("image_site/sprite_assassin_left_2.png").convert_alpha(),pygame.image.load("image_site/sprite_assassin_left_3.png").convert_alpha()]
                    
                    image_stand =  joueur_sprite
                else:
                    joueur = {"class" : "Mage", "nom" : nom, "level" : 1, "stat_joueur" : {"reflexe" : 5,"force" : 0, "vitesse" : 1, "agilite" : 3, "magie" : 5, "vie" : 110, "vie_max" : 110,"vol_de_vie" : 0, "energie" : 150, "energie_max" : 150, "item" : [item_holder["potion_force_base"], item_holder["potion_defence_base"], item_holder["potion_endurance_base"]], "abilite" : [{"nom" : "boule de feu","degat" : 15,  "coup_en_energie" : 7, "vitesse" : 20, "damage_reduction" : 0, "ulti" : False, "turn_to_work" : None, "atk_type": "magie"}, {"nom" : "Mur de Mana", "degat" :  1,  "coup_en_energie" : 20, "vitesse" : 25, "damage_reduction" : 35, "ulti" : False, "turn_to_work" : None, "atk_type": "magie","tour_effect" : 2, "defence_reduction" : 2},{"nom" : "Void Hole", "degat" : 50,  "coup_en_energie" : 15, "vitesse" : 30, "damage_reduction" : 0, "ulti" : True, "turn_to_work" : 4, "atk_type": "force"}, {"nom" : "coup de poing","degat" : 5,  "coup_en_energie" : 0, "vitesse" : 5, "damage_reduction" : 0, "ulti" : False, "turn_to_work" : None, "atk_type": "force"}],"exp" : 0, "exp_needed" : 69,"or" : 0}, "item_bag" : []}
                    joueur_sprite = pygame.image.load("image_site/sprite_mage_stand.png").convert_alpha()
                    sprite_group_right,sprite_group_left = 0,0
                    image_stand = joueur_sprite
                joueur_sprite = pygame.transform.scale(joueur_sprite, default_size)
                joueur["item_bag"] = [item for item in joueur["stat_joueur"]["item"]]
                current_room = -1
                stages = []
                rooms = []
                rewrite_dos()
                switch_collision = []
                collision_ = []
                collision = []
                heal_rooms = []
                cooldown_heal_room = 2
                have_heal_room = 0
                pos_img1.x,pos_img1.y = 0,200
                went_back = False
                going_back = False
                room_logged = False
                dict_data = {}
                color_quit = (0,0,0)
                pop_up = appear_pop_up(1)
                rect_quit = pygame.Rect(pop_up.x + pop_up.w/2 - (get_dimension("Quitter(1)",csm,20)[0] + 10)/2, pop_up.y + pop_up.h/2-get_dimension("Quitter(1)",csm,20)[1]/2,
                                                         get_dimension("Quitter(1)",csm,20)[0] + 10, get_dimension("Quitter(1)",csm,20)[1] + 10)
                rect_restart = pygame.Rect(pop_up.x+pop_up.w/2-(get_dimension("Recommencer(2)",csm,20)[0] + 10)/2, pop_up.y + pop_up.h/2-get_dimension("Recommencer(2)",csm,20)[1]/2 + 100,
                                                         get_dimension("Recommencer(2)",csm,20)[0] + 10, get_dimension("Recommencer(2)",csm,20)[1] + 10)
                color_restart = (0,0,0)
                global recommencer
                global quit1
                recommencer,quit1 = False,False
                def repos_life_energie():
                    joueur["stat_joueur"]["vie"] = joueur["stat_joueur"]["vie_max"]
                    joueur["stat_joueur"]["energie"] = joueur["stat_joueur"]["energie_max"]
                    return joueur
                while True:
                    left = False
                    color_restart,color_quit = (0,0,0),(100,0,225)
                    pop_up = appear_pop_up(1)
                    Tueur = "No data" if Tueur == None else Tueur
                    text = f"Merde {Tueur} vous a tué ! (soyez meilleur !)"
                    draw_in(text, 0, pop_up, 27, (255,255,255), sinistre, pop_up.w/2 - get_dimension(text,sinistre,27,False,True)[0]/2, 20,False,True)
                    mouse = pygame.mouse.get_pos()
                    if rect_quit.collidepoint(mouse):
                        color_quit = (200,0,0)                       
                    if rect_restart.collidepoint(mouse):
                        color_restart = (0,200,0)
                    pygame.draw.rect(screen,color_quit,rect_quit)
                    pygame.draw.rect(screen,color_restart,rect_restart)
                    text = "Quitter(1)"
                    draw_in(text, 0, pop_up, 20, (255,255,255), csm, pop_up.w/2 - get_dimension(text,csm,20)[0]/2, pop_up.h/2-get_dimension(text,csm,20)[1]/2)
                    text = "Recommencer(2)"
                    draw_in(text, 0, pop_up, 20, (255,255,255), csm, pop_up.w/2 - get_dimension(text,csm,20)[0]/2, pop_up.h/2-get_dimension(text,csm,20)[1]/2 + 100)
                    pygame.display.update(pop_up)
                    for event in [pygame.event.poll()]:
                        if event.type == pygame.KEYDOWN:
                            if (event.key == pygame.K_KP1 or event.key == pygame.K_1):
                                joueur = repos_life_energie()
                                pygame.mixer.music.fadeout(1000)
                                left_game(0,False)
                            elif (event.key == pygame.K_KP2 or event.key == pygame.K_2):
                                joueur = repos_life_energie()
                                left = True
                                break
                        if rect_quit.collidepoint(mouse):
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                joueur = repos_life_energie()
                                pygame.mixer.music.fadeout(1000)
                                left_game(0,False)
                        if rect_restart.collidepoint(mouse):
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                joueur = repos_life_energie()
                                died_in_game = False
                                left = True
                                break
                    if left:
                        break
                pygame.mixer.music.fadeout(1000)
                switch_collision,nb_room  = ecran(dict_data)
            return switch_collision,nb_room       
                        
        if not combat :
            switch_collision,nb_room = ecran(dict_data)
        b = 0        
        for i in collision_:
            collide_png = False
            print(mask_ennemie,b)
            img = pygame.image.load(mask_ennemie[b]).convert()
            img.set_colorkey((0,0,0))
            img_resize = pygame.transform.scale(img,resize_ennemie)
            img_mask = pygame.mask.from_surface(img_resize)
            if mask_player.overlap(img_mask,(pygame.Rect(i)[0] - pos_img1.x, pygame.Rect(i)[1] - pos_img1.y)):
                if(collision[b]["type"] == "ennemie" and collision[b]["etat"] == "vivant"):
                    mouse = pygame.mouse.get_pos()
                    mort_def = False
                    combat = True
                    global joueur
                    global player
                    player = joueur["stat_joueur"]
                    global vie_ennemie
                    vie_ennemie = collision[b]["data_ennemie"]["vie"]
                    global vie_joueur
                    vie_joueur = player['vie']
                    global energy_joueur
                    global image_stand
                    energy_joueur = player['energie']
                    nom = collision[b]["data_ennemie"]["nom"]
                    ennemie = collision[b]["data_ennemie"]
                    collisionneur = pygame.Rect(collision[b]["rect"])
                    if not image_charged:
                        sprite_ennemie = pygame.image.load(collision[b]["img"])
                        image_charged = True
                    sprite_ennemie = pygame.transform.scale(sprite_ennemie,(255,200))
                    ennemie_choose = collision[b]                    
                    global vie_max_ennemie
                    vie_max_ennemie = collision[b]["data_ennemie"]["vie_max"]                    
                    x = 0                    
                    for ability in player["abilite"]:
                        if ability["ulti"] == True:
                            ulti_cooldown = ability["turn_to_work"]
                            break
                        x+= 1
                    if combat == True:
                        if not debut_combat:
                            appear_pop_up(0)
                            pop_up = appear_pop_up(0)
                            pygame.display.flip()
                            y_marge = [20 + 100*x for x in range(len(joueur["stat_joueur"]["item"]))]
                            add = 0
                            all_touch_item =[]                            
                            for i in joueur["stat_joueur"]["item"]:
                                bonus = {}
                                ajout = []
                                img = pygame.image.load(i["img"])
                                if "attaque" in i["fonction"]:
                                    fonction = i["fonction"]
                                    img = pygame.transform.scale(img, default_size)
                                    img.set_colorkey((255, 255, 255))
                                    image = img
                                    image_rect = pop_up.x + pop_up.w/2 - img.get_rect()[2]/2, pop_up.y + y_marge[add]
                                    rect_image = pygame.Rect((pop_up.x + pop_up.w/2 - img.get_rect()[2]/2, pop_up.y + y_marge[add], default_size[0], default_size[1]))
                                    bonus["attaque"] = i["bonus_attaque"]
                                    item_click = i["nom"]
                                    if "attaque" not in ajout:
                                        ajout.append("attaque")
                                if "defence" in i["fonction"]:
                                    fonction = i["fonction"]
                                    img = pygame.transform.scale(img, default_size)
                                    img.set_colorkey((255, 255, 255))
                                    image = img
                                    image_rect = pop_up.x + pop_up.w/2 - img.get_rect()[2]/2, pop_up.y + y_marge[add]
                                    rect_image = pygame.Rect((pop_up.x + pop_up.w/2 - img.get_rect()[2]/2, pop_up.y + y_marge[add], default_size[0], default_size[1]))
                                    bonus["defence"] = i["bonus_defence"]
                                    item_click = i["nom"]
                                    if "defence" not in ajout:
                                        ajout.append("defence")
                                if "endurance" in i["fonction"]:
                                    fonction = i["fonction"]
                                    img = pygame.transform.scale(img, default_size)
                                    img.set_colorkey((255, 255, 255))
                                    image = img
                                    image_rect = pop_up.x + pop_up.w/2 - img.get_rect()[2]/2, pop_up.y + y_marge[add]
                                    rect_image = pygame.Rect((pop_up.x + pop_up.w/2 - img.get_rect()[2]/2, pop_up.y + y_marge[add], default_size[0], default_size[1]))
                                    bonus["endurance"] = i["bonus_endurance"]
                                    item_click = i["nom"]
                                    if "endurance" not in ajout:
                                        ajout.append("endurance")
                                add_all = {"endurance" : i["bonus_endurance"], "attaque" : i["bonus_attaque"], "defence" : i["bonus_defence"]}
                                del img
                                screen.blit(image,image_rect)
                                marge_y = [0, 10, 20]
                                draw_in(f"{item_click}", 1, rect_image, 15, (255,215,0), csm, -get_dimension(f"{item_click}", csm,15)[0]/4,-15)
                                margex = [0]
                                for i in ajout:
                                    x = get_dimension(f" + {bonus[i] * 100}% {i}",csm,15)[0]
                                    margex.append(x)
                                width_z = sum(margex)
                                elt = 0
                                phrase = ""
                                for element in ajout:
                                    phrase += f" + {bonus[element] * 100}% {element}"
                                draw_in(phrase, 1, rect_image, 15, (0,0,0), csm, rect_image.w/2 - width_z/2 ,rect_image.h + marge_y[0])
                                touch_item = {"rect" : rect_image, "bonus" : bonus, "nom" : item_click, "fonction" : ajout,"all_fonction" : add_all }
                                all_touch_item.append(touch_item)
                                add += 1
                            pygame.display.flip()
                            while debut_combat == False:
                                mouse = pygame.mouse.get_pos()
                                for i in range(len(all_touch_item)):
                                    if all_touch_item[i]["rect"].collidepoint(mouse):
                                        if pygame.mouse.get_pressed()[0]:                                            
                                            global buff
                                            buff = all_touch_item[i]                                            
                                            debut_combat = True
                                event = pygame.event.poll()
                                if event.type == pygame.KEYDOWN:
                                    if debut_combat:
                                        break
                                    elif event.key == pygame.K_p:
                                        pause = True
                                        pygame.mixer.music.pause()
                                    elif event.key == pygame.K_u:
                                        pause = False
                                        pygame.mixer.music.unpause()
                                    elif event.key == pygame.K_SPACE:
                                        pygame.mixer.music.fadeout(1000)
                                        make_music(os.listdir("playlist_music"), "switch")
                                    elif event.key == pygame.K_r:
                                        pygame.mixer.music.rewind()
                                    elif event.key == pygame.K_KP6:
                                        volume = get_volume(1)
                                    elif event.key == pygame.K_KP4:
                                        volume = get_volume(-1)
                                    elif event.key == pygame.K_y:
                                        make_sauvegarde(file_full,Ingame = True,cryptage = False)
                                        sauvegarde_rapide = True
                                if sauvegarde_rapide:
                                    if not wait:
                                        time_start = pygame.time.get_ticks()
                                        time_elapsed= 0
                                        wait = True
                                    time_elapsed = pygame.time.get_ticks() - time_start
                                    screen.fill((100,100,100),(rect_screen.w/2 - get_dimension("Sauvegarde effectuée", csm, 20)[0]/2, 20, get_dimension("Sauvegarde effectuée", csm, 20)[0],get_dimension("Sauvegarde effectuée", csm, 20)[1] ))
                                    center_screen("Sauvegarde effectuée", comic_sans_ms, get_dimension("Sauvegarde effectuée", csm, 20), 20, False)
                                    if time_elapsed >= 1000:
                                        screen.fill((100,100,100),(rect_screen.w/2 - get_dimension("Sauvegarde effectuée", csm, 20)[0]/2, 20, get_dimension("Sauvegarde effectuée", csm, 20)[0],get_dimension("Sauvegarde effectuée", csm, 20)[1] ))

                                        sauvegarde_rapide = False
                                        wait = False
                                        del time_elapsed
                                        del time_start
                                if event.type == pygame.QUIT:
                                    running = left_game()
                                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                                    running = left_game()
                                pygame.display.flip()
                        def ecran_combat(collision,joueur_sprite,):
                            global energy_joueur
                            global vie_joueur
                            global player
                            global joueur
                            global buff
                            global image_stand
                            global bonus
                            bonus = buff["all_fonction"]#dict
                            fonction = buff["fonction"]                           
                            screen.fill(background)
                            vie_joueur = player["vie"] * (1 + bonus["defence"])
                            energy_joueur = energy_joueur * (1+bonus["endurance"])                            
                            global grossissement
                            grossissement = (200,200)
                            joueur_sprite = pygame.transform.scale(image_stand, grossissement)
                            global new_rect_joueur
                            new_rect_joueur = pygame.Rect(contener_.x + 70,contener_.y - 150,grossissement[0],grossissement[1])
                            screen.blit(joueur_sprite, new_rect_joueur )
                            global rect_ennemi
                            rect_ennemi = pygame.Rect(contener_.x + contener_.w - 300 ,contener_.y-320,sprite_ennemie.get_rect()[2],sprite_ennemie.get_rect()[3])
                            screen.blit(sprite_ennemie, rect_ennemi)
                            global mini_contener
                            global mini_contener2
                            global mini_contener3
                            global mini_contener4
                            mini_contener = pygame.Rect(contener_.x+220,contener_.y+50, 150,70)
                            mini_contener2 = pygame.Rect(contener_.x+520,contener_.y+50, 150,70)
                            mini_contener3 = pygame.Rect(contener_.x+220,contener_.y+270, 150,70)
                            mini_contener4 = pygame.Rect(contener_.x+520,contener_.y+270, 150,70)
                            screen.blit(btn_retour, (0,0))
                            vie_ennemie =  collision[b]["data_ennemie"]["vie"]
                            somme = 0
                            for i in range(len(energy_cost)):
                                somme += energy_cost[i]
                            energy_joueur = (player['energie'] * (1+bonus["endurance"])) - somme
                            if not indice_combat % 2 and indice_combat != 0:
                                energy_joueur += 1
                            global make_barre                            
                            def make_barre(text1,text2,couleur1,couleur2,rect,stat2,stat1,longueur_barre,hauteur_barre,margex1 = 10, margex2 = 30):
                                if stat2 != None and stat1 != None:
                                    p1 = 100 * (stat2[0]/stat2[1])
                                    if stat2[0] <= 0:
                                        stat2 = (0,stat2[1])
                                        p1 = 0
                                    width_universel = get_dimension(text1,csm,20)[0] + longueur_barre + get_dimension(" 10000% (10000)",csm,20)[0]
                                    width_universel2 = get_dimension(text2,csm,20)[0] + longueur_barre + get_dimension(" 10000% (10000)",csm,20)[0]
                                    screen.fill((100,100,100), (rect.x +rect.w/2 -width_universel/2,rect.y -margex2-20, width_universel,get_dimension(text2,csm,20)[1]))
                                    screen.fill((100,100,100), (rect.x+rect.w/2 - width_universel2/2,rect.y -margex1-15, width_universel2,get_dimension(text2,csm,20)[1]))
                                    longueur_energie_restante = (stat1[0] / stat1[1]) * longueur_barre
                                    longueur_vie_restante = (stat2[0]/ stat2[1]) * longueur_barre
                                    pygame.draw.rect(surface_barre_vie, couleur_barre_vie, (0, 0, longueur_barre, hauteur_barre))
                                    pygame.draw.rect(surface_barre_vie,couleur_vie_restante, (0, 0, longueur_vie_restante, hauteur_barre))
                                    screen.blit(surface_barre_vie,(get_dimension(text1, csm, 20)[0] + rect.x + rect.w/2 -width_universel/2 ,rect.y - margex2 + hauteur_barre + 2-20))
                                    surface_energie = surface_barre_vie.copy()
                                    p2 = 100 * (stat1[0] / stat1[1])
                                    if stat1[0] <= 0:
                                        stat1 = (0,stat1[1])
                                        p2 = 0
                                    longueur_energie_restante = (stat1[0] / stat1[1]) * longueur_barre
                                    pygame.draw.rect(surface_energie, couleur_barre_energie, (0, 0, longueur_barre, hauteur_barre))
                                    pygame.draw.rect(surface_energie,couleur_energie_restante, (0, 0, longueur_energie_restante, hauteur_barre))
                                    screen.blit(surface_energie,(get_dimension(text2, csm, 20)[0] + rect.x + rect.w/2 -width_universel2/2 ,rect.y - margex1 + hauteur_barre +2 -15))
                                    draw_in(text1,0,rect,20,couleur1,csm,rect.w/2 - width_universel/2,-margex2-20)                                    
                                    draw_in(text2,0,rect,20,couleur2,csm,rect.w/2 - width_universel2/2,-margex1-15)                                
                                    screen.fill((100,100,100), (get_dimension(text1, csm, 20)[0] + rect.x + rect.w/2 - width_universel/2 +
                                              longueur_barre,rect.y - margex2-20,get_dimension(f" {1000}% (100000)",csm,20)[0],get_dimension(f" {1000}% (100000)",csm,20)[1]))
                                    draw_text(f" {round(p1,1)}% ({round(stat2[0],1)})",comic_sans_ms,(0,0,0),get_dimension(text1, csm, 20)[0] + rect.x + rect.w/2 -width_universel/2 +
                                              longueur_barre,rect.y - margex2-20)
                                    screen.fill((100,100,100),(get_dimension(text2, csm, 20)[0] + rect.x + rect.w/2 - width_universel2/2 +
                                              longueur_barre,rect.y - margex1-15,get_dimension(f" {1000}% (100000)",csm,20)[0],get_dimension(f" {1000}% (100000)",csm,20)[1]))
                                    draw_text(f" {round(p2,1)}% ({round(stat1[0],1)})",comic_sans_ms,(0,0,0),get_dimension(text2, csm, 20)[0] + rect.x + rect.w/2 - width_universel2/2 +
                                              longueur_barre,rect.y - margex1-15)
                                else:
                                    try:
                                        longueur_vie_restante = (stat1[0] / stat1[1]) * longueur_barre
                                        stat = stat1
                                    except:
                                        longueur_vie_restante = (stat2[0]/ stat2[1]) * longueur_barre
                                        stat = stat2
                                    width_universel = get_dimension(text1,csm,20)[0] + longueur_barre + get_dimension(" 10000% (1000000000)",csm,20)[0]
                                    screen.fill((100,100,100), (rect.x ,rect.y -margex1, width_universel,get_dimension(text1,csm,20)[1]))
                                    pygame.draw.rect(surface_barre_vie, couleur_barre_vie, (0, 0, longueur_barre, hauteur_barre))
                                    pygame.draw.rect(surface_barre_vie,couleur_vie_restante, (0, 0, longueur_vie_restante, hauteur_barre))
                                    screen.blit(surface_barre_vie,(get_dimension(text1, csm, 20)[0] + rect.x + rect.w/2 - get_dimension(text1,csm,20)[0]/2 - longueur_barre/2 ,rect.y - margex1 + hauteur_barre +2))
                                    draw_in(text1,0,rect,20,couleur1,csm,rect.w/2 - get_dimension(text1,csm,20)[0]/2 - longueur_barre/2,-margex1)
                                    p1 = 100 * (longueur_vie_restante/longueur_barre)
                                    if stat[0] <= 0:
                                        stat = (0,stat[1])
                                        p1 = 0
                                    change_text(get_dimension(text1, csm, 20)[0] + rect.x + rect.w/2 - get_dimension(text1,csm,20)[0]/2 - longueur_barre/2 + longueur_barre,rect.y - margex1,get_dimension(text1,csm,20)[0],get_dimension(text1,csm,20)[1],(100,100,100))
                                    draw_text(f" {round(p1,1)}% ({round(stat[0],1)})", comic_sans_ms,(0,0,0),get_dimension(text1, csm, 20)[0] + rect.x + rect.w/2 - get_dimension(text1,csm,20)[0]/2 - longueur_barre/2 + longueur_barre,
                                              rect.y - margex1)
                                    
                           
                            somme = 0
                            for i in range(len(degat_ennemie)):
                                somme += degat_ennemie[i]
                            vie_joueur = (player['vie']  * (1+bonus["defence"])) - somme
                            text = "Vie :"
                            make_barre("Vie : ", "Energie : ", color_pick["vert"], color_pick["bleu_f"], new_rect_joueur, (vie_joueur,joueur["stat_joueur"]["vie_max"]), (energy_joueur, joueur["stat_joueur"]["energie_max"]),longueur_barre,hauteur_barre)
                            global pos_text_vie_joueur
                            pos_text_vie_joueur = pygame.Rect(new_rect_joueur.x + new_rect_joueur.w/2 - get_dimension(text,csm,20)[0]/2 - longueur_barre/2,new_rect_joueur.y - 30, get_dimension(f"Vie : ",csm,20)[0] + 100, get_dimension(f"Vie : ",csm,20)[1])
                            global pos_text_energy_joueur
                            pos_text_energy_joueur = pygame.Rect(new_rect_joueur.x + new_rect_joueur.w/2 - get_dimension(text,csm,20)[0]/2 - longueur_barre/2, new_rect_joueur.y - 10, get_dimension(f"Energie :",csm,20)[0] + 100, get_dimension(f"Energie : ",csm,20)[1])                            
                            for degat_add in degat_encaissé:
                                vie_ennemie -= degat_add
                            make_barre(f"Vie {nom} : ",None,color_pick["vert"],None,rect_ennemi,(vie_ennemie,vie_max_ennemie),None,longueur_barre,hauteur_barre,10)
                            global pos_text_vie_ennemie
                            pos_text_vie_ennemie = pygame.Rect(rect_ennemi.x + rect_ennemi.w/2 - get_dimension(f"Vie {nom} : ", csm, 20)[0] + longueur_barre,rect_ennemi.y - 10, get_dimension((f"Vie {nom} : "), csm,20)[0] + longueur_barre,get_dimension((f"Vie {nom} : "),csm,20)[1])
                            global appear_contener
                            def appear_contener():
                                """
                                    fonction permettant de faire apparaitre le ccontener pour attaque,info,item
                                """
                                screen.blit(contener, contener_)
                                contener.fill((200,200,200))
                                pygame.draw.rect(screen, (1, 1, 1), contener_, 10)
                                text = ["ITEM", "ATTAQUE", "INFO"]
                                for x in range(3):
                                    screen.blit(contener_btn,contener_btn_pos[x])
                                    pos = contener_btn_pos[x]
                                    draw_text(text[x],comic_sans_ms, (255,255,255), pos.x + 10, pos.y + 20)
                                screen.blit(ligne, (contener_.x + contener_btn_pos[0].w, contener_.y))
                                         
                            appear_contener()                          
                            return bonus,fonction
                        
                        bonus,fonction = ecran_combat(collision,joueur_sprite)                       
                        i = 0
                        active = False
                        anti_bug = False
                        pygame.event.clear()
                        if indice_combat % 2 == 0 and mort == False:
                            for e in range(len(contener_btn_pos)):
                                if (contener_btn_pos[e].collidepoint(mouse)):
                                    screen.fill((200,200,200),(contener_.x + contener_btn_pos[0].w + 10 ,contener_.y + 10,contener_.w - contener_btn_pos[0].w - 20,contener_.h - 20))
                                    type_ = contener_btn_pos_[i]["nom"]
                                    event = pygame.event.wait()
                                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) and type_ == "item":
                                        attaque = False
                                        item = True                                        
                                        text_replace = [f"votre item actuelle est {item_click}"]
                                        text_replace_bonus = []
                                        x = 0
                                        max_ = {}
                                        for key,bonud_add in bonus.items():
                                            if bonud_add != 0:
                                                max_[key] = bonud_add
                                        for bonus_add in max_:
                                            text = f"il vous procure {bonus[fonction[x]] * 100}% de bonus {fonction[x]}"
                                            text_replace_bonus.append(text)
                                            x+=1                                            
                                        def change_text(locationx, locationy , width, heigh, color):
                                            screen.fill(color,(locationx, locationy, width,heigh))
                                        change_text(contener_.x + 150,contener_.y + 170, 588, 26, (200,200,200))
                                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) and type_ == "atk":
                                        attaque = True
                                        item = False
                                        text_replace = [player["abilite"][x]["nom"] for x in range(4)]
                                        element = [player["abilite"][x] for x in range(len(player["abilite"]))]
                                        def change_text(locationx, locationy , width, heigh, color):
                                            screen.fill(color,(locationx, locationy, width,heigh))
                                        change_text(contener_.x + 150,contener_.y + 170, 588, 26, (200,200,200))
                                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) and type_ == "info":
                                        if "Assassin" in joueur["class"]:
                                            text_replace = [(f"vous etes un {joueur['class']}"), (f"vous avez {player['agilite']} d'agilite(es)"),(f"vous avez {player['reflexe']} de réflexe"),(f"vous avez {player['agilite']} d'agilité"), (f"vous avez {player['force']} de force"), (f"vous avez {player['vitesse']} de vitesse") ]
                                        elif "Mage" in joueur["class"]:
                                            text_replace = [(f"vous etes un {joueur['class']}"), (f"vous avez {player['magie']} de magies"),(f"vous avez {player['reflexe']} de réflexe"),(f"vous avez {player['magie']} de magie"), (f"vous avez {player['force']} de force"), (f"vous avez {player['vitesse']} de vitesse") ]
                                        elif "Guerrier" in joueur["class"]:
                                            text_replace = [(f"vous etes un {joueur['class']}"), (f"vous avez {player['agilite']} d'agilite(es)"),(f"vous avez {player['force']} de force"),(f"vous avez {player['reflexe']} de reflexe"), (f"vous avez {player['vie']} de vies"), (f"vous avez {player['vitesse']} de vitesse") ]
                                        attaque = False
                                        item = False
                                        def change_text(locationx, locationy , width, heigh, color):
                                            screen.fill(color,(locationx, locationy, width,heigh))
                                        change_text(contener_.x + 150,contener_.y + 170, 588, 26, (200,200,200))
                                    try:
                                        pass_ = True                                        
                                        if attaque == False:
                                            if item:
                                                part = 1
                                                marge = [0, 20, 40, 80, 100, 120]
                                                draw_in(text_replace[0], contener,contener_, 18,(0,0,0),csm, 200,30 + marge[0])
                                                for x in range(len(text_replace_bonus)):                                                   
                                                    draw_in(text_replace_bonus[x], contener,contener_, 18,(0,0,0),csm, 230,30 + marge[x+1])
                                            else:
                                                part = 2
                                                marge = [0, 60, 120, 180, 240, 300]
                                                for x in range(len(text_replace)):
                                                    draw_in(text_replace[x], contener,contener_, 18,(0,0,0),csm, 200,30 + marge[x])

                                        else:
                                            if indice_combat % 2 == 0:
                                                screen.fill((105,105,105), mini_contener)
                                                screen.fill((105,105,105), mini_contener2)
                                                screen.fill((105,105,105), mini_contener3)
                                                screen.fill((105,105,105), mini_contener4)
                                                pygame.draw.rect(screen, (0,0,0), mini_contener, 2)
                                                pygame.draw.rect(screen, (0,0,0), mini_contener2, 2)
                                                pygame.draw.rect(screen, (0,0,0), mini_contener3, 2)
                                                pygame.draw.rect(screen, (0,0,0), mini_contener4, 2)
                                                part = 3
                                                marge = [20, 80, 140, 200, 260, 320]
                                                mini_contener_ = [mini_contener, mini_contener2, mini_contener3,mini_contener4]                                                 
                                                taille = 18
                                                var = 0
                                                for x in range(len(text_replace)):
                                                    while get_dimension(text_replace[x].upper(), csm, taille)[0] + 10 >= mini_contener_[x].w:
                                                        taille -= 1
                                                    if element[var]["ulti"]:
                                                        color = (200,10,145)
                                                    else:
                                                        color = (0,0,0)
                                                    draw_in(text_replace[x].upper(), "useless",mini_contener_[x], taille,color,csm, 10,20)
                                                    var+=1
                                            

                                    except:
                                        pass
                                        
                                else:
                                    try:                                        
                                        screen.fill((200,200,200),(contener_.x + contener_btn_pos[0].w + 10 ,contener_.y + 10,contener_.w - contener_btn_pos[0].w - 20,contener_.h - 20))
                                        anti_bug = False                                        
                                        if pass_:
                                            def change_text(locationx, locationy , width, heigh, color):
                                                screen.fill(color,(locationx, locationy, width,heigh))
                                            change_text(contener_.x + 150,contener_.y + 170, 588, 26, (200,200,200))
                                            if part == 3:
                                                marge = [20, 80, 140, 200, 260, 320]
                                            elif part == 2:
                                                marge = [0, 60, 120, 180, 240, 300]
                                            elif part == 1:
                                                marge = [0, 20, 40, 80, 100, 120]
                                            if part == 1:
                                                draw_in(text_replace[0], contener,contener_, 18,(0,0,0),csm, 200,30 + marge[0])
                                                for x in range(len(text_replace_bonus)):                                                   
                                                    draw_in(text_replace_bonus[x], contener,contener_, 18,(0,0,0),csm, 230,30 + marge[x+1])
                                            if part == 2:
                                                for x in range(len(text_replace)):
                                                    draw_in(text_replace[x], contener,contener_, 18,(0,0,0),csm, 200,30 + marge[x])
                                            for x in range(len(text_replace)):                                         
                                                if part == 3 and indice_combat % 2 == 0:                                                    
                                                    screen.fill((105,105,105), mini_contener)
                                                    screen.fill((105,105,105), mini_contener2)
                                                    screen.fill((105,105,105), mini_contener3)
                                                    screen.fill((105,105,105), mini_contener4)
                                                    pygame.draw.rect(screen, (0,0,0), mini_contener, 2)
                                                    pygame.draw.rect(screen, (0,0,0), mini_contener2, 2)
                                                    pygame.draw.rect(screen, (0,0,0), mini_contener3, 2)
                                                    pygame.draw.rect(screen, (0,0,0), mini_contener4, 2)
                                                    mini_contener_ = [mini_contener, mini_contener2, mini_contener3,
                                                                      mini_contener4]
                                                    taille = 18
                                                    var = 0
                                                    for x in range(len(text_replace)):
                                                        while get_dimension(text_replace[x].upper(), csm, taille)[0] + 10 >=  mini_contener_[x].w:
                                                            taille -= 1
                                                        if element[var]["ulti"]:
                                                            color = (200,10,145)
                                                        else:
                                                            color = (0,0,0)
                                                        draw_in(text_replace[x].upper(), "useless", mini_contener_[x], taille,
                                                                color, csm, 10, 20)
                                                        var+=1
                                                    draw_contener = True
                                                    anti_bug = False
                                                    c = 0
                                                    break_ = False
                                                    for mini in mini_contener_:
                                                        mouse = pygame.mouse.get_pos()
                                                        if mini.collidepoint(mouse):
                                                            rect = pygame.Rect(contener_.x + contener_btn_pos[1].w +20+ contener_.w/2 - 200,contener_.y+contener_.h/2 - 100/2,200,100)
                                                            screen.fill((200,200,200),rect)
                                                            if draw_contener:
                                                                pygame.draw.rect(screen,(0,0,0),rect,2)
                                                                attaque = element[c]["degat"]
                                                                vitesse = element[c]["vitesse"]
                                                                energie = element[c]['coup_en_energie']
                                                                dommage_reduction= element[c]["damage_reduction"]
                                                                draw_in(f"dégat : {attaque * (1 + bonus['attaque'])}",0,rect,18,(0,0,0),csm,10,10) 
                                                                draw_in(f"Energie : {energie}",0,rect,18,(0,0,0),csm,10,30)
                                                                draw_in(f"vitesse : {vitesse}",0,rect,18,(0,0,0),csm,10,50)
                                                                draw_in(f"reduction_degat : {dommage_reduction * (1+bonus['defence'])}",0,rect,15,(0,0,0),csm,10,70)
                                                            pygame.display.update(contener_)
                                                            atk = element[c]
                                                            block = False
                                                            click_actu = False
                                                            for event in [pygame.event.poll()]:
                                                                if event.type == pygame.MOUSEBUTTONDOWN and not click_actu:
                                                                   click_actu = True
                                                                   pygame.event.clear()
                                                                   can_attack = False
                                                                   if atk["atk_type"] == "aucun":
                                                                       if attaque_in_effect == None:
                                                                           reduction_attaque = atk["damage_reduction"]*(1 + bonus["defence"])
                                                                           cooldown = atk["tour_effect"]
                                                                           attaque_in_effect = atk
                                                                           try_illegal = False
                                                                       else:
                                                                           screen.fill((200,200,200),rect)
                                                                           text_ephemere("capacité déjà activé", sinistre, 30, 2000, 200, 170,True,(200,200,200))
                                                                           try_illegal = True
                                                                           block = True
                                                                   else:
                                                                       try_illegal = False
                                                                   if atk["ulti"]:
                                                                       if atk["turn_to_work"] > tour_sans_utilise:
                                                                           text_appear = True
                                                                           try_illegal = True
                                                                           screen.fill((200,200,200),rect)
                                                                           text_ephemere(f"vous ne pouvez pas l'utiliser pour le moment :) ({atk['turn_to_work'] - tour_sans_utilise} tours restants)", sinistre, 20, 2000,150,170, True, (200,200,200))
                                                                           block = True
                                                                       else:
                                                                           try_illegal = False
                                                                           text_appear = False
                                                                           tour_sans_utilise = 0
                                                                   else:
                                                                       try_illegal = False
                                                                   if try_illegal is False:
                                                                       if energy_joueur  - atk['coup_en_energie'] < 0:
                                                                           can_attack = False
                                                                           block = True
                                                                           screen.fill((200,200,200),rect)                      
                                                                           text_ephemere("Vous n'avez pas assez d'energie", csm, 20, 2000, 200, 170,False,(200,200,200))
                                                                       else:
                                                                           can_attack = True
                                                                   if not block:
                                                                       if can_attack:
                                                                           chance_esquive = 2
                                                                           if player["abilite"][c]["vitesse"] * player["agilite"] >= ennemie["agilite"] * ennemie["reflexe"]:
                                                                               chance_esquive = 1
                                                                           elif (player["abilite"][c]["vitesse"] * player["agilite"]) * 2 <= ennemie["agilite"] * ennemie["reflexe"]:
                                                                               chance_equive = 3
                                                                           look_miss = random.randint(0,100)
                                                                           miss = False
                                                                           if look_miss <= chance_esquive:
                                                                               miss = True
                                                                           if atk["atk_type"] == "aucun":
                                                                               miss = False
                                                                           if not miss:
                                                                               if atk["atk_type"] == "force":
                                                                                   type_ = player["force"]
                                                                               elif atk["atk_type"] == "magie":
                                                                                   type_ = player["magie"]
                                                                               elif atk["atk_type"] == "agilite":
                                                                                   type_ = player["agilite"]
                                                                               if atk["degat"] != 0:
                                                                                   make_hit(sprite_ennemie,100,contener_.x + contener_.w - 300 ,contener_.y - 320, sprite_ennemie.get_rect()[2], sprite_ennemie.get_rect()[3])                
                                                                                   degat_encaissé.append((atk['degat'] + atk['degat']* bonus["attaque"])+ ((joueur["level"]+20)*(type_/20)))
                                                                               energy_cost.append(atk['coup_en_energie'])
                                                                           else:                                                                           
                                                                              draw_in("Raté ! :(",0,rect_ennemi,30,(0,0,0),csm,-100,rect_ennemi.h/2 -
                                                                                      get_dimension("Raté ! :(",csm,30)[1]/2)
                                                                       somme = 0
                                                                       for energy_add in energy_cost:
                                                                           somme += energy_add
                                                                       energy_joueur = (player["energie"] + player["energie"] * bonus["endurance"]) - somme
                                                                       if energy_joueur < 0:
                                                                           energy_joueur = 0
                                                                       somme = 0                                                                          
                                                                       for degat_add in degat_encaissé:
                                                                           somme += degat_add
                                                                       vie_ennemie = vie_ennemie - somme                                                                   
                                                                       make_barre("Vie : ", "Energie : ", color_pick["vert"], color_pick["bleu_f"], new_rect_joueur, (vie_joueur,joueur["stat_joueur"]["vie_max"]), (energy_joueur, joueur["stat_joueur"]["energie_max"]),longueur_barre,hauteur_barre)
                                                                       make_barre(f"Vie {nom} : ",None,color_pick["vert"],None,rect_ennemi,(vie_ennemie,vie_max_ennemie),None,longueur_barre,hauteur_barre,10)
                                                                       pygame.display.flip()
                                                                       pygame.time.delay(700)
                                                                       pygame.display.flip()
                                                                       if vie_ennemie <= 0:
                                                                           mort = True
                                                                       if can_attack:
                                                                           indice_combat += 1
                                                                           if not atk["ulti"]:
                                                                               tour_sans_utilise +=1
                                                                           if cooldown != None:
                                                                               cooldown -= 1
                                                                               if cooldown < 0:
                                                                                   attaque_in_effect = None
                                                                                   cooldown = None
                                                                                   reduction_attaque = 0
                                                                           pygame.time.delay(200)
                                                                           break_ = True
                                                                           break
                                                        if break_:
                                                            break
                                                        c+=1
                                    except:
                                        def change_text(locationx, locationy , width, heigh, color):
                                            screen.fill(color,(locationx, locationy, width,heigh))
                                        change_text(contener_.x + 200,contener_.y + 170, get_dimension("clickez sur une case !",csm,20)[0], get_dimension("clickez sur une case !",csm,20)[1], (200,200,200))
                                        if anti_bug == False and text_appear == False:
                                            draw_in("clickez sur une case !", contener,contener_, 20,(0,0,0),csm, 200,170)
                                        pass
                                i+=1
                        elif indice_combat % 2 != 0 and mort == False:
                            draw_contener = False
                            
                            def choose_ennemie_attaque(ennemie,player):
                                """
                                    fonction permettant de choisir l'attaque de l'ennemie
                                    :param1: dict des data ennemie
                                    :param2: dict des data du joueur
                                """
                                attaque_ennemie = random.randint(0,len(ennemie["abilite"]) -1)
                                esquive_possible = random.randint(1,100)
                                if ennemie["abilite"][attaque_ennemie]["vitesse"] * ennemie["reflexe"] <= player["agilite"] * player["reflexe"]:
                                    esquive_point = 2 * (player["reflexe"]/20)
                                else:
                                    esquive_point = 1 * (player["reflexe"]/20)
                                if ennemie["abilite"][attaque_ennemie]["type"] == "force":
                                    type_ = ennemie["force"]
                                else:
                                    type_ = ennemie["magie"]
                                attaque_d = ennemie["abilite"][attaque_ennemie]["degat"] + ((ennemie["level"] + 20) * (type_/20))
                                return esquive_point,ennemie["abilite"][attaque_ennemie],attaque_d,ennemie["abilite"][attaque_ennemie]["nom"],esquive_possible
                            esquive_point,attaque_ennemie,attaque_ennemie_degat,nom_attaque,esquive_possible = choose_ennemie_attaque(ennemie,player)                            
                            
                            def look_if_ennemie_can_attaque(attaque):
                                """Fonction permettant de verifier si l'ennemie peut attaquer ou non

                                Args:
                                    attaque (dict): stat de l'attaque choisi

                                Returns:
                                    bool: return si l'ennemie peut attaquer True ou pas False
                                """
                                if attaque["ulti"]:
                                    if tour_sans_utilise_ennemie >= attaque["turn_to_work"]:
                                        return True                                    
                                    tour_sans_utilise_ennemie += 1
                                    return False
                                return True
                            while not look_if_ennemie_can_attaque(attaque_ennemie):
                                esquive_point,attaque_ennemie,attaque_ennemie_degat,nom_attaque = choose_ennemie_attaque(ennemie,player)
                            if esquive_possible >= esquive_point:
                                draw_in("Votre ennemie attaque !", contener,contener_, 40,(0,0,0),csm,200,170)
                                pygame.display.flip()
                                pygame.time.delay(1000)
                                def change_text(locationx, locationy , width, heigh, color):
                                    screen.fill(color,(locationx, locationy, width,heigh))
                                change_text(contener_.x + 200, contener_.y + 170, get_dimension("Votre ennemie attaque !", csm, 40)[0], get_dimension("Votre ennemie attaque !", csm, 40)[1], fond_contener)
                                pygame.display.flip()
                                pygame.time.delay(1000)
                                draw_in(f"votre ennemie lance {nom_attaque}", contener,contener_, 20,(0,0,0),minecraft_factory, contener_.w/2 - get_dimension(f"votre ennemie lance {nom_attaque}", minecraft_factory,20, False, True)[0]/2 + contener_btn_dimension.w/2, contener_.h/2 - get_dimension(f"votre ennemie lance {nom_attaque}", minecraft_factory,20, False, True)[1]/2, False, True)
                                pygame.display.flip()
                                pygame.time.delay(1000)
                                degat_ajout = attaque_ennemie_degat - reduction_attaque
                                if degat_ajout < 0:
                                    degat_ajout = 0
                                    text_en_plus = "votre capacité a tanker les degats"
                                else:
                                    text_en_plus = ""
                                degat_ennemie.append(degat_ajout)
                                somme = 0
                                for i in range(len(degat_ennemie)):
                                    somme += degat_ennemie[i]
                                vie_joueur = (player["vie"] + player["vie"] * bonus["defence"]) - somme
                                if vie_joueur <= 0:
                                    mort = True
                                make_hit(image_stand,100,contener_.x + 70,contener_.y -150)
                                make_barre("Vie : ", "Energie : ", color_pick["vert"], color_pick["bleu_f"], new_rect_joueur, (vie_joueur,joueur["stat_joueur"]["vie_max"]), (energy_joueur, joueur["stat_joueur"]["energie_max"]),longueur_barre,hauteur_barre)
                                draw_in(f"votre ennemie lance {nom_attaque}", contener,
                                        contener_, 20, (0, 0, 0), minecraft_factory, contener_.w / 2 - get_dimension(
                                        f"votre ennemie lance {nom_attaque}",
                                        minecraft_factory, 20, False, True)[0] / 2 + contener_btn_dimension.w / 2,
                                        contener_.h / 2 - get_dimension(
                                            f"votre ennemie lance {nom_attaque}",
                                            minecraft_factory, 20, False, True)[1] / 2, False, True)                                
                                draw_in(f"Cela vous a infligé : {degat_ajout} degat; {text_en_plus}", contener,contener_, 20,(0,0,0),csm, contener_.w/2 - get_dimension(f"Cela vous a infligé : {degat_ajout} degat; {text_en_plus}", csm,20)[0]/2 + contener_btn_dimension.w/2, contener_.h/2 - get_dimension(f"Cela vous a infligé : {degat_ajout} degat; {text_en_plus}", csm,20)[1]/2 +50)                                                       
                                pygame.display.flip()
                                pygame.time.delay(700)                                
                                pygame.display.flip()
                                draw_in("Appuyer sur une touche !", contener,contener_, 40,color_pick["bordeaux"],sinistre, contener_.w/2 - get_dimension("Appuyer sur une touche !", sinistre,40,False, True)[0]/2 + contener_btn_dimension.w/2 +5, contener_.h/2 - get_dimension("Appuyer sur une touche !", sinistre,40, False, True)[1]/2 +100, False, True)
                                pygame.display.flip()                                
                                pygame.event.clear()
                                while True:
                                    event = pygame.event.wait()
                                    if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                                        indice_combat +=1
                                        break
                                pygame.event.clear()

                            else:
                                draw_in("Votre ennemie attaque !", contener,contener_, 40,(0,0,0),csm, contener_.w/2 - get_dimension("Votre ennemie attaque !", csm, 40)[0]/2 + contener_btn_dimension.w/2, contener_.h/2 - get_dimension("Votre ennemie attaque !", csm, 40)[1]/2)
                                pygame.display.flip()
                                pygame.time.delay(1000)
                                def change_text(locationx, locationy , width, heigh, color):
                                    screen.fill(color,(locationx, locationy, width,heigh))
                                change_text(contener_.x + contener_.w/2 - get_dimension("Votre ennemie attaque !", csm, 40)[0]/2 + contener_btn_dimension.w/2, contener_.y + contener_.h/2 - get_dimension("Votre ennemie attaque !", csm, 40)[1]/2, get_dimension("Votre ennemie attaque !", csm, 40)[0], get_dimension("Votre ennemie attaque !", csm, 40)[1], fond_contener)
                                draw_in("Vous avez esquivé(e)", contener,contener_, 40,(0,0,0),sinistre, contener_.w/2 - get_dimension("Vous avez esquivé(e)", sinistre, 40, False, True)[0]/2 + contener_btn_dimension.w/2, contener_.h/2 - get_dimension("Vous avez esquivé(e)", sinistre, 40, False, True)[1]/2, False, True)
                                pygame.display.flip()
                                pygame.time.delay(1000)
                                draw_in("Appuyer sur une touche !", contener,contener_, 40,color_pick["bordeaux"],sinistre, contener_.w/2 - get_dimension("Appuyer sur une touche !", sinistre,40,False, True)[0]/2 + contener_btn_dimension.w/2 +5, contener_.h/2 - get_dimension("Appuyer sur une touche !", sinistre,40, False, True)[1]/2 +100, False, True)
                                pygame.display.flip()                                
                                pygame.event.clear()
                                while True:
                                    event = pygame.event.wait()
                                    if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                                        indice_combat +=1
                                        break
                                pygame.event.clear()


                        else:
                            del part
                            appear_pop_up()
                            debut_combat = False
                            attaque_in_effect = None
                            cooldown = None
                            reduction_attaque = 0
                            for degat_add in degat_encaissé:
                                vie_ennemie = vie_ennemie - degat_add
                            indice_drop = random.randint(0, 100)
                            sac_plein = False
                            if vie_ennemie <= 0:
                                perdu = False
                                text = "vous avez gagnez :)"
                                try:
                                    if ennemie["boss"]:
                                        end_game = True
                                except:
                                    pass
                                pygame.display.flip()
                                collision[b]["etat"] = "mort"
                                equil = {0 : "ennemie 1", 1 : "ennemie 2", 2: "ennemie 3", 3:"ennemie 4", 4 : "ennemie 5"}                                                    
                                rooms[current_room][equil[b]]["etat"] = "mort"                            
                                joueur, level_gagner = uptade_data(bonus_enchainement_combat,bonus = bonus)
                                drop = False
                                already_have = False
                                if ennemie["loot"]["item_drop"] in joueur["item_bag"]:
                                    already_have = True
                                
                                if indice_drop <= ennemie["loot"]["chance_drop"] and not already_have:
                                    if len(joueur["item_bag"]) <= 5:
                                        drop = True
                                        joueur["item_bag"].append(ennemie["loot"]["item_drop"])
                                    else:
                                       sac_plein = True                               
                                
                            else:
                                perdu = True
                                died_in_game = True
                                global phase
                                text = "vous avez perdue :("
                                Tueur = ennemie["nom"]
                                pygame.mixer.music.fadeout(500)
                                sound_game_over = pygame.mixer.music.load("playlist_music/game_over_main.ogg")
                                pygame.mixer.music.play(-1)
                                joueur = uptade_data(bonus_enchainement_combat,1)
                                level_gagner = 0
                            draw_in(text, 0, pop_up, 40, (0,0,0), csm, pop_up.w/2 - get_dimension(text,csm,40)[0]/2, pop_up.h/2 - 50-get_dimension(text,csm,40)[1]/2)
                            pygame.display.flip()
                            if not perdu:
                                if drop:
                                    draw_in(f"{ennemie['loot']['item_drop']['nom']} a été ajouté au sac..", "useless", pop_up,
                                            20, color_pick["bordeaux"], sinistre, pop_up.w / 2 -
                                            get_dimension(f"{ennemie['loot']['item_drop']['nom']} a été ajouté au sac..",
                                                          sinistre, 20, False, True)[0]/2, 5, False, True)
                                if already_have:
                                    draw_in("Vous avez drop mais vous possedez déjà l'item", "useless", pop_up,
                                            20, color_pick["bordeaux"], sinistre, pop_up.w / 2 -
                                            get_dimension("Vous avez drop mais vous possedez déjà l'item",
                                                          sinistre, 20, False, True)[0]/2, 5, False, True)
                                
                                if (not drop and not already_have and not sac_plein):
                                    draw_in("Vous n'avez pas drop d'item..", "useless", pop_up, 20, color_pick["bordeaux"], sinistre,
                                            pop_up.w / 2 -
                                            get_dimension("Vous n'avez pas drop d'item..", sinistre,
                                                          20, False, True)[0] / 2, 5, False, True)
                                if sac_plein:                                       
                                   draw_in("Votre sac est plein..", "useless", pop_up, 20, color_pick["bordeaux"], sinistre,
                                            pop_up.w / 2 -
                                            get_dimension("Votre sac est plein..", sinistre,
                                                          20, False, True)[0] / 2, 5, False, True)

                                draw_in(f"+{ennemie['loot']['xp_drop'] + ennemie['loot']['xp_drop']  * bonus_enchainement_combat }Xp ; +{ennemie['loot']['gold_drop']}Gold", "useless", pop_up, 20, color_pick["jaune"], sinistre,
                                        pop_up.w / 2 -
                                        get_dimension(f"+{ennemie['loot']['xp_drop'] + ennemie['loot']['xp_drop']  * bonus_enchainement_combat }Xp ; +{ennemie['loot']['gold_drop']}Gold", sinistre,
                                                    20, False, True)[0] / 2, pop_up.h/2 - get_dimension(f"+{ennemie['loot']['xp_drop'] + ennemie['loot']['xp_drop']  * bonus_enchainement_combat }Xp ; +{ennemie['loot']['gold_drop']}Gold", sinistre, 20, False, True)[1] / 2  + 50, False, True)
                                if level_gagner > 0:
                                    joueur["level"] += level_gagner
                                    adjust_all_stat(joueur,level_gagner)
                                    draw_in(f"Vous avez gagnez {level_gagner} Levels :)", "useless", pop_up, 20, color_pick["bleu_f"],sinistre,pop_up.w / 2 -get_dimension(f"Vous avez gagnez {level_gagner} Levels :)", sinistre,20, False, True)[0] / 2, pop_up.h/2 - get_dimension(f"il vous reste {joueur['stat_joueur']['exp_needed'] - joueur['stat_joueur']['exp']}" , sinistre,20, False, True)[1] / 2 +100, False, True)
                                else:
                                    draw_in(f"il vous reste {joueur['stat_joueur']['exp_needed'] - joueur['stat_joueur']['exp']}xp avant de changer de level", "useless", pop_up, 20,color_pick["bleu_f"],sinistre,pop_up.w / 2 - get_dimension(f"il vous reste {joueur['stat_joueur']['exp_needed'] - joueur['stat_joueur']['exp']}xp avant de changer de levels", sinistre,20, False, True)[0]/2, pop_up.h/2 - get_dimension(f"il vous reste {joueur['stat_joueur']['exp_needed'] - joueur['stat_joueur']['exp']}xp avant de changer de levels" , sinistre,20, False, True)[1]/2 +100, False, True)
                            pygame.display.flip()
                            pygame.time.delay(700)
                            pygame.display.flip()
                            if repos_left > 0 :
                                can_repos = True
                            else:
                                can_repos = False
                            rect_dispo = {}
                            draw_dispo = []
                            if not perdu and can_repos is True:
                                text = "Se REPOSER (1)"
                                draw_in(text, 0, pop_up, 20, (0,0,0), csm, pop_up.w/4 - get_dimension(text,csm,20)[0]/2, pop_up.h/2-get_dimension(text,csm,20)[1]/2)
                                rect_dispo["repos"] = (pygame.Rect(
                                                        pop_up.x + pop_up.w/4 - (get_dimension(text,csm,20)[0] + 10)/2,
                                                        pop_up.y + pop_up.h/2-(get_dimension(text,csm,20)[1]+5)/2,
                                                        get_dimension(text,csm,20)[0] + 10,
                                                        get_dimension(text,csm,20)[1] + 5),text)
                                
                                text = "CONTINUER (2)"
                                draw_in(text, 0, pop_up, 20, (0,0,0), csm, (pop_up.w - pop_up.w/4) - get_dimension(text,csm,20)[0]/2, pop_up.h/2-get_dimension(text,csm,20)[1]/2)
                                rect_dispo["continuer"] = (pygame.Rect(
                                                        pop_up.x + (pop_up.w - pop_up.w/4) - (get_dimension(text,csm,20)[0]+10)/2,
                                                        pop_up.y + pop_up.h/2-(get_dimension(text,csm,20)[1]+5)/2,
                                                        get_dimension(text,csm,20)[0]+10,
                                                        get_dimension(text,csm,20)[1]+5),text)
                            elif not perdu and can_repos is False:
                                text = "CONTINUER (2)"
                                rect_dispo["continuer"] = (pygame.Rect(
                                                        pop_up.x + pop_up.w/2 - (get_dimension(text,csm,20)[0]+10)/2,
                                                        pop_up.y + pop_up.h/2-(get_dimension(text,csm,20)[1]+5)/2,
                                                        get_dimension(text,csm,20)[0]+10,
                                                        get_dimension(text,csm,20)[1]+5),text)
                                draw_in(text, 0, pop_up, 20, (0,0,0), csm, pop_up.w/2 - get_dimension(text,csm,20)[0]/2, pop_up.h/2-get_dimension(text,csm,20)[1]/2)
                            else:
                                died_in_game = True
                                text = "POURSUIVRE(2)"
                                rect_dispo["continuer"] = (pygame.Rect(
                                                        pop_up.x + pop_up.w/2 - (get_dimension(text,csm,20)[0]+10)/2,
                                                        pop_up.y + pop_up.h/2-(get_dimension(text,csm,20)[1]+5)/2,
                                                        get_dimension(text,csm,20)[0]+10,
                                                        get_dimension(text,csm,20)[1]+5),text)
                                draw_in(text, 0, pop_up, 20, (0,0,0), csm, pop_up.w/2 - get_dimension(text,csm,20)[0]/2, pop_up.h/2-get_dimension(text,csm,20)[1]/2)
                            text = "Si vous continuez vous aurez un bonus de 13% d'xp en plus au prochain combat"
                            text2 = "mais vous ne regagnerez pas votre vie ni energie"
                            pygame.draw.rect(screen, (0,0,0), (pop_up.x + pop_up.w/2 - get_dimension(text,sinistre,20, False, True)[0]/2 - 5,pop_up.y + pop_up.h +10,get_dimension(text,sinistre,20,False,True)[0] + 10, get_dimension(text, sinistre,20,False,True)[1] + get_dimension(text2, sinistre,20,False,True)[1] - 5))
                            draw_in(text, 0, pop_up, 20, (255,255,255), sinistre, pop_up.w/2 - get_dimension(text,sinistre,20, False, True)[0]/2, pop_up.h + 10, False, True)
                            draw_in(text2, 0, pop_up, 20, (255,255,255), sinistre, pop_up.w/2 - get_dimension(text2,sinistre,20, False, True)[0]/2, pop_up.h + 30, False, True)
                            del text
                            del text2
                            del pass_
                            del mouse
                            del attaque
                            del item
                            tour_sans_utilise = 0
                            mort = False
                            image_charged = False
                            indice_combat = 0
                            color = [(0,0,0)]*2
                            while True:
                                all_rect = []
                                left = False
                                repos = None
                                i = 0
                                for value,rect in rect_dispo.items():
                                    pygame.draw.rect(screen,color[i],rect[0])
                                    draw_text(color = (255,255,255), x = rect[0].x + 5, y = rect[0].y, text = rect[1])
                                    pygame.display.update(rect[0])
                                    all_rect.append((rect[0],rect[1],value))
                                    i += 1
                                for event in pygame.event.get():
                                    mouse = pygame.mouse.get_pos()
                                    for i in range(len(all_rect)):
                                        mouse = pygame.mouse.get_pos()
                                        if all_rect[i][0].collidepoint(mouse):
                                            color[i] = (200,200,200)
                                            if event.type == pygame.MOUSEBUTTONDOWN:
                                                if all_rect[i][2] == "repos":
                                                    repos_left -=1
                                                    repos = True
                                                else:
                                                    repos = False
                                            break
                                        else:
                                            color[i] = (0,0,0)
                                    if event.type == pygame.KEYDOWN:
                                        if event.key == pygame.K_KP1 or event.key == pygame.K_1 and can_repos is True:
                                            repos_left -= 1
                                            repos = True
                                        elif event.key == pygame.K_KP2 :
                                            repos = False
                                    if repos != None:
                                        if not died_in_game:
                                            def appliquer_bonus(repos, bonus_enchainement_combat):
                                                if not repos:
                                                    bonus_enchainement_combat += 0.50
                                                else:
                                                    bonus_enchainement_combat = 0
                                                return bonus_enchainement_combat
                                            if not repos and perdu is False:
                                                bonus_enchainement_combat = appliquer_bonus(repos, bonus_enchainement_combat)
                                            else:
                                                def repos_life_energie():
                                                    joueur["stat_joueur"]["vie"] = joueur["stat_joueur"]["vie_max"]
                                                    joueur["stat_joueur"]["energie"] = joueur["stat_joueur"]["energie_max"]
                                                    return joueur
                                                joueur = repos_life_energie()
                                        left = True
                                        left_combat(btn[0]["nom"], pos_img1,collisionneur,collision_tolerance)
                                        break
                                if left:
                                    break
                                pygame.display.flip()
                    e = 0
                    mouse = pygame.mouse.get_pos()
                    collide_retour = False
                    for i in btn:
                        if (combat):
                            if (btn[e]["rect"].collidepoint(mouse)):                                
                                d = btn[e]["nom"]
                                if pygame.mouse.get_pressed()[0]:
                                    if d == "retour":
                                        if joueur["stat_joueur"]["energie"] >= joueur["stat_joueur"]["energie_max"] / 2:
                                            pos_img1.left = collisionneur.left - 60
                                            print(pos_img1,collisionneur)
                                            combat = False
                                            debut_combat = False
                                            joueur["stat_joueur"]["energie"] -= 20
                                            image_charged = False
                                            indice_combat = 0
                                            try:
                                                del pass_
                                                del attaque
                                                del item
                                                del part_
                                            except:
                                                pass
                                        else:
                                            center_screen("Vous n'avez pas le droit !", comic_sans_ms, get_dimension("Vous n'avez pas le droit !", csm, 20), 0, False)
                                            pygame.display.flip()
                                            pygame.time.delay(1000)
                        e+=1
                    if combat == False:
                        collision_test(collisionneur,pos_img1,collision_tolerance)
                        joueur_sprite = pygame.transform.scale(joueur_sprite, default_size)
                        ecran(dict_data)
                elif collision[b]["type"] == "obstacle":
                    combat = False
                    collision_test(collisionneur,pos_img1,collision_tolerance)
                elif collision[b]["type"] == "png":
                    
                    if collision[b]["fonction"] == "healeur":
                        text_heal = "Appuyer sur f pour vous Heal. Vos repos restant seront remis a 4." if repos_left <4 else "Vous avez le max de repos"
                        def repos_life_energie():
                            joueur["stat_joueur"]["vie"] = joueur["stat_joueur"]["vie_max"]
                            joueur["stat_joueur"]["energie"] = joueur["stat_joueur"]["energie_max"]
                            return joueur
                        pressed_keys = pygame.key.get_pressed()
                        if (pressed_keys[pygame.K_f]):
                            joueur = repos_life_energie()
                            repos_left = 4
                        collision_test(pygame.mask.from_surface(pygame.image.load(mask_ennemie[0])).get_rect(),pos_img1,10)
                        
            elif combat == False:
                text_heal = "Parler au png pour vous Heal ou Sorter"
            b += 1
        for i in switch_collision:
            global pos_futur
            def look_for_can_switch(rooms,switch):
                if went_back and current_room != 0:
                    return True
                elif heal_room:
                    return True
                for data,key in rooms.items():
                    if not "switch" in data:
                        try:
                            if key["etat"] == "vivant":
                                return False
                        except:
                            pass
                return True
            can_switch = look_for_can_switch(rooms[current_room],i)
            can_switch = True
            if pos_img1.colliderect(pygame.Rect(inverse_dict_equivalent_switch[i["rect"]])) and can_switch:
                rooms,switch_collision,stage,heal_room,current_room,room_passed,boss_room,going_back = change_room(rooms, current_room, nb_room, room_passed, i["id"])
                collisionneur = pygame.Rect(inverse_dict_equivalent_switch[i["rect"]])
                pos_joueur = spawn_equivalent_rect[pos_futur]
                pos_img1.x,pos_img1.y = pos_joueur[0],pos_joueur[1]
                sortir_combat(collisionneur, pos_img1, 20)
            elif pos_img1.colliderect(pygame.Rect(inverse_dict_equivalent_switch[i["rect"]])) and can_switch == False:
                center_screen("Battez les ennemies !", comic_sans_ms, get_dimension("Battez les ennemies !", csm, 20), 20, False)
                pygame.display.flip()
                collision_test(pygame.Rect(inverse_dict_equivalent_switch[i["rect"]]),pos_img1,10)
        if combat == False:
            pos_img1.x, pos_img1.y,move_left,move_right,move_down,move_up,joueur_sprite,group_using= move(pos_img1.x, pos_img1.y,sprite_group_right,sprite_group_left)
        collision_screen(pos_img1, rect_screen)
        make_music(os.listdir("playlist_music"))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = left_game()
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = left_game()
                elif event.key == pygame.K_b:
                    appear_tuto_touche()
                elif event.key == pygame.K_p:
                    pause = True
                    pygame.mixer.music.pause()
                elif event.key == pygame.K_u:
                    pause = False
                    pygame.mixer.music.unpause()
                elif event.key == pygame.K_SPACE:
                    pygame.mixer.music.fadeout(1000)
                    make_music(os.listdir("playlist_music"), "switch")
                elif event.key == pygame.K_r:
                    pygame.mixer.music.rewind()
                elif event.key == pygame.K_i:
                    inventaire_item()
                elif event.key == pygame.K_KP6:
                    volume = get_volume(1)
                elif event.key == pygame.K_KP4:
                    volume = get_volume(-1)
                elif event.key == pygame.K_y:
                    make_sauvegarde(file_full,Ingame = True,cryptage = False)
                    sauvegarde_rapide = True
                elif event.key == pygame.K_t:
                   #reset tout
                   file_full = ""
                   current_room = -1
                   went_back = False
                   rooms = []
                   stages = []
                   heal_rooms = []
                   room_passed = 0
                   room_logged = False
                   heal_room = False
                   switch_collision = []
                   switch_collisions = []
                   stage = 0
                   dict_data = {}
                   have_heal_room = 0
                   cooldown_heal_room = 2
                   can_switch = False
                   current_sprite = 0
                   boss_room = False
                   data_recup = False
                   switch_collisions = []                
                   menu()
                    
        if sauvegarde_rapide:
            if not wait:
                time_start = pygame.time.get_ticks()
                time_elapsed = 0
                wait = True
            time_elapsed = pygame.time.get_ticks() - time_start
            center_screen("Sauvegarde effectuée", comic_sans_ms, get_dimension("Sauvegarde effectuée", csm, 20), 20, False)
            if time_elapsed >= 1000:
                sauvegarde_rapide = False
                wait = False
                del time_elapsed
                del time_start
        pygame.display.flip()

py_start()
pygame.quit()
sys.exit()