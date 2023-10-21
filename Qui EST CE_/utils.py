from flask import Flask, render_template, Markup, request, session, url_for, flash, redirect, json, jsonify
from sqlalchemy import create_engine, func, select
import cx_Oracle
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
from flask_bcrypt import Bcrypt
import random as rd

engine = create_engine('oracle://MBT2903A:Mbengue99@telline.univ-tlse3.fr:1521/etupre')
app = Flask(__name__)


#Pour afficher la liste des question
def liste_question(collection):
    
    code_html1=""  
    strSql='select q.idq, intitulé from MBT2903A.question q, MBT2903A.dependre d where q.idq=d.idq and d.idcollection='+str(collection)
    with engine.connect() as con:
        rs = con.execute(strSql)
    for row in rs:
        idq,intitule=row
        code_html1+='<li><a>'+ str(idq)+'    '+str(intitule)+'</a></li>'
        code_html1+="<option value =" + str(idq)+" "+str(intitule) + ">" + str(idq)+" "+str(intitule) + "</option>"
    return(code_html1)


#Pour afficher la grille de jeu

def tableau(collection,niveau):
    listerobot=[]
    strSql='select i.idim, i.chemin from MBT2903A.image i, MBT2903A.collectionner c where i.idim=c.idim and c.idcollection='+str(collection)
    compteur=0
    if niveau==1:
        longueur,largeur=4,4
    else:
        longueur,largeur=6,5

    #Le joueur peut clignoter une imaage
        
    code_html='<script language="javascript">function swap(id){if (id.style.display != "none" ){id.style.display = "none";}else{id.style.display = "inline";}}</script>'
    code_html+="<table width='1000'>"
    with engine.connect() as con:
      rs = con.execute(strSql)
    compteur2=1
    for row in rs:
        idim,chemin=row
        if compteur2%largeur==1:
            code_html+="<tr>"
        code_html+="<td><button type='button' onclick='swap(monImage"+str(idim)+");'>"
        #code_html+="<td><button type='button' onclick='hideImg()'>"
        code_html += "<img src='"+chemin+"' height=\"150px\" id='monImage"+str(idim)+"'/></button></td>"
        if compteur2%largeur==0:
            code_html+="</tr>"
        if niveau==1:
            compteur+=1
        listerobot.append(idim)
        if compteur==16:
            if 'listerobot' not in session:
                session['listerobot']=listerobot
                session['listejoueur']=listerobot #on initialise les deux liste de la même façon car ils joue avec la même grille de jeu
            return(code_html)
        compteur2+=1
    code_html+="</table>"
    return(code_html)

    
#Pour recuperer liste d'image robot  et jouer

def initliste(collection, niveau):
    L=[]
    taille=16
    debut=1
    if niveau==2:
        taille=30
    if collection==2:
        debut=31
    for i in range(debut, debut+taille):
        L.append(i)
    session['listerobot']=L
    session['listejoueur']=L
    
#Qui nous retourne true ou false en fonction de la question et de l'image choisi
def reponsequestion(question):
    if question==0:
        return 'init'
    if session['collection']==1:
        reprobot=1 #pour collection =1 Le robot prend toujours la l'image d'id 1
    else:
        reprobot=31#pour collection =2 Le robot prend toujours la l'image d'id 31
    connection = engine.raw_connection()
    strSql='select ELIMINERQE from MBT2903A.Eliminer where idq='+str(question)+'and idim='+str(reprobot)
    with engine.connect() as con:
        rs = con.execute(strSql)
        for row in rs:
            return row[0]
    



#Pour faire les mises en jours de liste de joueur     
def update_liste_joueur(boolean,question):
    if question==0:
        return
    liste=session['listejoueur']#on récupère la liste des image
    nouvelleliste=[]#on initialise une nouvelle liste
    connection = engine.raw_connection()
    for i in liste:
        strSql='select ELIMINERQE from MBT2903A.Eliminer where idq='+str(question)+'and idim='+str(i) 
        with engine.connect() as con:
            rs = con.execute(strSql)
        for row in rs:
            if boolean==row[0]:
                nouvelleliste.append(i)
    
    session['listejoueur']=nouvelleliste


#Pour faire les mises en jours de liste ROBOT
    
def update_liste_robot(boolean,question):
    if question==0:
        return
    liste=session['listerobot']#on récupère la liste des image
    print('liste avant for',liste)
    nouvelleliste=[]#on initialise une nouvelle liste
    connection = engine.raw_connection()
    for i in liste:
        strSql='select ELIMINERQE from MBT2903A.Eliminer where idq='+str(question)+'and idim='+str(i)  
        with engine.connect() as con:
            rs = con.execute(strSql)
        for row in rs:
            if boolean==row[0]:
                nouvelleliste.append(i)
    print('nouvelle',nouvelleliste)
    session['listerobot']=nouvelleliste


#Pour que le robot Pose des question aleatoirement
def robotposequestion():
    listequestion=session['listequestionpossible']
    questionpose=rd.choices(listequestion)[0]
    del listequestion[listequestion.index(questionpose)] # a chaque question poser on le supprime de la liste pour maximiser les chances que le RObot gagne
    
    session['listequestionpossible']=listequestion
    connection = engine.raw_connection()
    cursor = connection.cursor()
    retour = cursor.var(cx_Oracle.NUMBER)  
    cursor.callproc("MBT2903A.Inserer_poser",
                ['robot',int(questionpose),session['ordrerobot'],retour])
    session['ordrerobot']+=1

    strSql="select intitulé from MBT2903A.question  where idq='"+str(questionpose)+"'"
    with engine.connect() as con:
        rs = con.execute(strSql)
    for row in rs:
        intitule=str(row[0])
    cursor.close()
    connection.commit()
    return(questionpose,intitule)



  
def reponsequestionreplay(question,reponse):
    connection = engine.raw_connection()
    strSql='select ELIMINERQE from MBT2903A.Eliminer where idq='+str(question)+'and idim='+str(reponse)
    with engine.connect() as con:
        rs = con.execute(strSql)
        for row in rs:
            return row[0]

