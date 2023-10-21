from datetime import datetime
from pydoc import render_doc
from flask import Flask, render_template, Markup, request, session, url_for, flash, redirect, json, jsonify
from sqlalchemy import create_engine, func, select
import cx_Oracle
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
from flask_bcrypt import Bcrypt
import random as rd
from utils import *
from time import time
import datetime



# connect to oracle
engine = create_engine('oracle://MBT2903A:Mbengue99@telline.univ-tlse3.fr:1521/etupre')
app = Flask(__name__)

#Partie connexion--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# secret key for extra protection
app.secret_key = 'Mbengue99'


# More secured password
bcrypt = Bcrypt(app)


#call procédure Oracle
def call_proc(proc, params):
    connection = engine.raw_connection()
    try:
        cursor = connection.cursor()
        retour = cursor.var(cx_Oracle.NUMBER)  # variable OUT
        cursor.callproc(str(proc), params + [retour])
        cursor.close()
        connection.commit()
    finally:
        connection.close()


# Registration Form (https://flask.palletsprojects.com/en/1.1.x/patterns/wtforms/)
class RegistrationForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(),Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Sign up')


# Formulaire d'inscription
class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')



# Vérifier si l'utilisateur est dans la base de donées 
def validate_username(username):
    with engine.connect() as con:
        rs = con.execute('select idjoueur from MBT2903A.Joueur')
        for row in rs:
            for value in row:
                if str(value) == str(username.data):
                    return 1
        return 0





@app.route("/")
# first page
@app.route("/Firstpage")
def Firstpage():
    return render_template("Firstpage.html")


# login/register pages
@app.route("/register", methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('Firstpage'))

    form = RegistrationForm()
    if form.validate_on_submit():
        if validate_username(form.username) == 0:
            connection = engine.raw_connection()
            try:
                cursor = connection.cursor()
                retour = cursor.var(cx_Oracle.NUMBER)  # variable OUT
                cursor.callproc("MBT2903A.Inserer_Joueur",[str(form.username.data),str(form.password.data), retour]) 
                print("On a enregistré le nouveau joueur")
                connection.commit()
                cursor.close()
            finally:
                connection.close()
            flash('Ton compte a été crée ! Tu peux maintenant te connecter',
                  'success')
            return redirect(url_for('login'))
        else:
            flash('Username déjà existant', 'warning')
    return render_template('register.html', form=form)



@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('Firstpage'))
    form = LoginForm()
    if form.validate_on_submit():
        user = form.username.data
        password = form.password.data
        with engine.connect() as con:
            rs = con.execute(
                "select mdp from MBT2903A.Joueur where idjoueur='" +
                str(user) + "'")                                        
            for row in rs:
                for value in row:
                    if str(value)==(password):    #on verifie si les identifiants sont valides
                        print(user)
                        session['username'] = str(user)
                        return redirect(url_for('Firstpage'))
                    else:
                        flash('Identifiant et mot de passe non valide.')
            flash('Identifiant et mot de passe non valide.')
    return render_template('login.html', form=form)




#On se déconnecte 
@app.route('/logout')
def logout():
    session.clear()
    session.pop('username', None)
    return redirect('/Firstpage')



#Algorithme pour le jeu-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#Tableaux des meilleurs scores 
@app.route("/highscores")
def highscores():
    code_htmltoday=""
    code_html1= " "
    code_html2= " "
    #hightscores par niveau
    strSQLnive1 = "select idjoueur,score from MBT2903A.partie WHERE score>0 and idniveau=1 order by score desc"
    strSQLnive2 = "select idjoueur,score from MBT2903A.partie WHERE score>0 and idniveau=2 order by score desc"
    with engine.connect() as con:
        rs = con.execute(strSQLnive1)
        for row in rs:
            #Dans le code html la balise tr correspond au pseudo et au niveau, on va remplir la variable vide du début
            code_html1+= "<tr>"
            for value in row:
                #Ici on ajoute la valeur du score
                code_html1 += "<td>" + str(value) + "</td>"
            code_html1 += "</tr>"

    with engine.connect() as con:   
        #pour niveau 2
        rs = con.execute(strSQLnive2)
        for row in rs:
            #Dans le code html la balise tr correspond au pseudo et au niveau, on va remplir la variable vide du début
            code_html2+= "<tr>"
            for value in row:
                #Ici on ajoute la valeur du score
                code_html2 += "<td>" + str(value) + "</td>"
            code_html2+= "</tr>"
    #hightscores par jour
    strSQLtoday = "select idjoueur,score from MBT2903A.partie WHERE score>0 and datep>=(select sysdate-1 from dual )order by score desc"
    with engine.connect() as con:   
        rs = con.execute(strSQLtoday)
        for row in rs:
            #Dans le code html la balise tr correspond au pseudo et au niveau, on va remplir la variable vide du début
            code_htmltoday= "<tr>"
            for value in row:
                #Ici on ajoute la valeur du score
                code_htmltoday += "<td>" + str(value) + "</td>"
            code_htmltoday+= "</tr>"

    return render_template('highscores.html',
                           high_score_by_lvl1=Markup(code_html1),
                           high_score_by_lvl2=Markup(code_html2),
                           high_score_by_today=Markup(code_htmltoday))


#Profil du joueur
@app.route("/account")
def account():
    niveau = "SELECT idniveau from MBT2903A.joueur where idjoueur='" + session[
        'username'] + "'"
    with engine.connect() as con:
        rs = con.execute(niveau)
        for row in rs:
            for value in row:
                if value == 1:
                    code_html = "Vous êtes au niveau " + str(value + 1)
                else:
                    code_html = "Vous avez débloqué le niveau " + str(value)
    return render_template('account.html', content=Markup(code_html))



#Formulaire du choix de niveau et de collection
#Formulaire du choix de niveau et de collection

@app.route("/nouvellepartie")

def nouvellepartie():
    session['ordrejoueur']=0
    session['ordrerobot']=1
    if session['username'] == "" or session['username'] is None:
        h2 = "Vous n'êtes pas connecté"
        p = "Veuillez vous connecter avant de jouer"
        # on retourne les phrases choisies
        return render_template("erreur.html", h2=h2, p=p)
    else:
        #On a besoin de deux listes : une pour les niveaux, une pour les collections, on les initialise
        code_grille = ""
        code_collections = ""
        with engine.connect() as con:
            #On crée la liste des niveaux
            #On sélectionne l'id et ce que tu veux afficher dans la liste (le libellé du niveau)
            rs = con.execute("SELECT idg FROM MBT2903A.grille ORDER BY idg")
            #On parcourt les lignes de la requête
            for row in rs:
                #La on crée une par une tes lignes de la liste déroulante
                #La value c'est l'id (dont on a besoin pour lier avec la base) [0] parce que c'est le premier
                #paramètre de ta requête
                #et entre deux options c'est le texte que l'utilisateur va voir ici le libellé
                code_grille += "<option value =" + str(row[0]) + ">" + str(row[0]) + "</option>"
            #Je refais exactement la même chose pour la collection
            rt = con.execute("SELECT idcollection, typec FROM collection ORDER BY idcollection")
            for ligne in rt:
                code_collections += "<option value =" + str(ligne[0]) + ">" + str(ligne[0]) + "</option>"
    #Et je retourne le template en remplissant les contents du html
    # add button to save a game, make it send a json that encodes the game.
    return render_template("nouvellepartie.html",grille=Markup(code_grille),collection=Markup(code_collections))


#recuperer le personnage que le joueur a choisi
#Permet de recuperer tous les informations pour creer une partie
@app.route("/getReponse", methods=['GET', 'POST'])
def reponse():
    codeq=""   #pour forcer le request
    code_grille = ""

    
    grilleid1 = int(request.form['grille'])
    session['grille']=grilleid1
    
    
    collectionid1 = int(request.form['collection'])
    session['collection']=collectionid1

    initliste(int(collectionid1),int(grilleid1))
    session['debut']=time()
    
    if collectionid1==1:
        session['listequestionpossible']=[i for i in range(1,11)]
    else:
        session['listequestionpossible']=[i for i in range(24,40)]
    grilleid = ""
    codereponseJ=""
    collectionid = ""
    
    grilleid+="<option value =" + str(grilleid1) + ">" + str(grilleid1) + "</option>"
    
    collectionid+="<option value =" + str(collectionid1) + ">" + str(collectionid1) + "</option>"
    
    codereponseJ+="<option value =" + str('pass') + ">" + str('pass') + "</option>"
    #Déclenche le trigger sur le niveau du joueur avec les retours de la procédure
    connection = engine.raw_connection()
    cursor = connection.cursor()
    retour = cursor.var(cx_Oracle.NUMBER) 
    if retour.getvalue(0) == 4:
        h2 = "Vous n'avez pas encore accès à ce niveau"
        p = "Veuillez en sélectionner un autre"
        return render_template('erreur.html', h2=Markup(h2), p=Markup(p))
    #Déclenche le trigger sur la limitation de parties
    if retour.getvalue(0) == 3:
        #On selectionne la date où le joueur dont la session est active peut rejouer
        dateRejouee = "Select to_char(daterejouer,'hh24:mi:ss') from MBT2903A.joueur where idjoueur='" + session[
            "username"] + "'"
        with engine.connect() as con:
            rs = con.execute(dateRejouee)
            for row in rs:
                for value in row:
                    #On informe le joueur du moment où il pourra rejouer
                    h2 = "Vous avez perdu 5 parties en 1h, vous ne pouvez plus jouer jusqu'à " + str(
                        value)
                    p = "Veuillez patienter"
                    return render_template('erreur.html', h2=h2, p=p)
    

    connection = engine.raw_connection()
    cursor = connection.cursor()
    retour = cursor.var(cx_Oracle.NUMBER)
    # variable OUT
    #On appelle la procédure de création de partie
    
    cursor.callproc("MBT2903A.Inserer_Partie",
                    [session['collection'],session['grille'], session['username'],session['grille'],'01/10/2022', retour])
    
    cursor.close()
    connection.commit()
    codeq+="<option value =0>0</option>"
    compteur=0
    


    strSql='select i.chemin from MBT2903A.image i, MBT2903A.collectionner c where i.idim=c.idim and c.idcollection='+str(collectionid1)
    with engine.connect() as con:
      rs = con.execute(strSql)
    for row in rs:
        code_grille += "<option value =" + str(row[0]) + ">" + str(row[0]) + "</option>"
        compteur+=1
        if compteur==16 and grilleid1==1:
            return render_template("ChoixPersonnage.html",personnage=Markup(code_grille),grille=Markup(grilleid),collection=Markup(collectionid),question=Markup(codeq),reponseJ=Markup(codereponseJ))


    return render_template("ChoixPersonnage.html",personnage=Markup(code_grille),grille=Markup(grilleid),collection=Markup(collectionid),question=Markup(codeq),reponseJ=Markup(codereponseJ))
    
          
#pour jouer une partie
@app.route("/getPartie", methods=['GET', 'POST'])
def Partie():
    
    
    #On prend les niveaux et les collections

    grilleid=session['grille']
    collectionid = session['collection']
    question=int(request.form['question'])
    reponseQJ=request.form['reponseJ']
    ordrequestion=0
    reponseJ=""
    reponseJ+= "<option value =" + str("OUI") + ">" + str("OUI") + "</option>"
    reponseJ+= "<option value =" + str("NON") + ">" + str("NON") + "</option>"
    
    idquestionrobot,intitulequestionrobot=robotposequestion()
    questionrobot="<option value =" + str(intitulequestionrobot) + ">" + str(intitulequestionrobot) + "</option>"

    if 'reponse' in session:
        reponse=session['reponse']
    else :
        reponse=request.form['personnage']
        session['reponse']=reponse
        connection = engine.raw_connection()
        strSql="select idim from MBT2903A.image  where chemin='"+str(reponse)+"'"
    
        with engine.connect() as con:
            rs = con.execute(strSql)
        for row in rs:
            idim=row[0]
            cursor = connection.cursor()
            retour = cursor.var(cx_Oracle.NUMBER)  
            cursor.callproc("MBT2903A.Inserer_reponse",
                        [int(idim),retour])
            cursor.close()
            connection.commit()
   
        
    connection = engine.raw_connection()
    cursor = connection.cursor()
    retour = cursor.var(cx_Oracle.NUMBER)  
    cursor.callproc("MBT2903A.Inserer_poser",
                [session['username'],int(question),session['ordrejoueur'],retour])
    session['ordrejoueur']+=1

    cursor.close()
    connection.commit()
    
    connection.close()
        
    #Déclenche le trigger sur le niveau du joueur avec les retours de la procédure
    #Déclenche le trigger sur la limitation de parties
    #on contruie notre table ici qu'on a deja pour quand il tape sur jouer le jeu commence
    
    boolean=reponsequestion(question)
    update_liste_joueur(boolean,question)
   
    reponserobot= "<option value =attente première question>attente première question</option>"
    if boolean!='init':
        if boolean=='True':
            reponserobot= "<option value =OUI>OUI</option>"
        else:
            
            reponserobot= "<option value =Non>Non</option>"
    
    if reponseQJ=='OUI':
        reponseQJ='True'
    else:
        reponseQJ='False'

    if len(session['listerobot'])<=1:#cas ou le robot gagne
        return redirect('/Firstpage')
    if len(session['listejoueur'])<=1:#cas ou le joueur gagne
        score=1/(time()-session['debut'])*1000
        connection = engine.raw_connection()
        cursor = connection.cursor()
        retour = cursor.var(cx_Oracle.NUMBER)  # variable OUT
        #On appelle la procédure de création de partie
        cursor.callproc("MBT2903A.sauvegardePartie",
                    ['True',score,retour])
    
        cursor.close()
        connection.commit()
        
        return redirect('/Firstpage')
    
        
    return render_template("jouer.html",question=Markup(liste_question(collectionid)),grille=Markup(tableau(collectionid,grilleid)),reponseJ=Markup(reponseJ),reponserobot=Markup(reponserobot),questionrobot=Markup(questionrobot))



#Rejouer une partie-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#pour afficher tous les parties que le joueur a jouer
@app.route("/replayPartie")
def replayPartie():
    code_html_replay=""
    strSql="select idp from partie where idjoueur="+"'"+session['username']+"' and partie_finie='True'"

    with engine.connect() as con:
      rs = con.execute(strSql)
    for row in rs:
        code_html_replay += "<option value =" + str(row[0]) + ">" + str(row[0]) + "</option>"
    session['ordrereplay']=1
    return render_template('replayPartie.html',partie=Markup(code_html_replay))




#pour rejouer une partie
@app.route("/rejouerPartie", methods=['GET', 'POST'])
def rejouerPartie():
    if 'idp' not in session:
        idp=int(request.form['partie'])
        session['idp']=idp
        
        strSql='select idcollection, idniveau from MBT2903A.partie where idp='+str(idp)
        with engine.connect() as con:
            rs = con.execute(strSql)
        for row in rs:
            session['idc_replay'],session['idniveau_replay']=row[0],row[1]
        strSql="select ordre from MBT2903A.poser where idp="+str(idp)+ "and idjoueur!='robot' and ordre>=all(select ordre from MBT2903A.poser where idp="+str(idp)+ "and idjoueur!='robot')"
        with engine.connect() as con:
            rs = con.execute(strSql)
        for row in rs:
            session['ordrefinreplay']=row[0]
        strSql="select idimj from reponse where idp="+str(idp)
        with engine.connect() as con:
            rs = con.execute(strSql)
        for row in rs:
            session['reponsereplay']=row[0]

    if session['ordrefinreplay']==session['ordrereplay']:
        return redirect('/Firstpage')


    #On prend les niveaux et les collections
    grilleid=session['idniveau_replay']
    collectionid = session['idc_replay']
    
    strSqlj="select idq from  MBT2903A.poser where idp="+str(session['idp'])+ " and idjoueur!='robot' and  ordre="+str(session['ordrereplay'])
    with engine.connect() as con:
        rs = con.execute(strSqlj)
    for row in rs:
        question=int(row[0])
        session['question']=question
    print('ok',session['question'])
    reponseQJ=reponsequestionreplay(session['question'],session['reponsereplay'])
    

    reponseJ=""
    reponseJ+= "<option value =" + str("OUI") + ">" + str("OUI") + "</option>"
    reponseJ+= "<option value =" + str("NON") + ">" + str("NON") + "</option>"
    strSql="select p.idq, q.intitulé from  MBT2903A.poser p,MBT2903A.question q where idp="+str(session['idp'])+ " and idjoueur='robot' and p.idq=q.idq and  ordre="+str(session['ordrereplay'])
    with engine.connect() as con:
        rs = con.execute(strSql)
    for row in rs:
        idquestionrobot,intitulequestionrobot=row[0],row[1]
        questionrobot="<option value =" + str(intitulequestionrobot) + ">" + str(intitulequestionrobot) + "</option>"

    if collectionid==1:
        boolean=reponsequestionreplay(idquestionrobot,1)
    else:
        boolean=reponsequestionreplay(idquestionrobot,31)
    reponserobot= "<option value =attente première question>attente première question</option>"
    if reponseQJ=='OUI':
        reponseQJ='True'
    else:
        reponseQJ='False'
    session['ordrereplay']+=1

    
    return render_template("replay.html",question=Markup(liste_question(collectionid)),grille=Markup(tableau(collectionid,grilleid)),reponseJ=Markup(reponseJ),reponserobot=Markup(reponserobot),questionrobot=Markup(questionrobot))

## Run
if __name__ == '__main__':
    app.run(debug=True,port="34392")
