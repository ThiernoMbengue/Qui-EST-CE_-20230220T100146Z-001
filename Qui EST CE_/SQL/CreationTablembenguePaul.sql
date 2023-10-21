drop table collectionner;
drop table poser;
drop table eliminer;
drop table composer;
drop table reponse;
drop table dependre;
drop table question;
drop table partie;
drop table joueur;
drop table collection;
drop table grille;
drop table image;
drop table niveau;



--table niveau
create table niveau( idniveau number(5) primary key not null,constraint check_niveau check(idniveau in (1,2,3)));


--table joueur
create table joueur(idjoueur varchar2(30) primary key not null,
--pseudo varchar2(30),constraint nn_pseudo unique(pseudo),
mdp varchar2(30) constraint nn_mdp not null,
Daterejouer Date,
idniveau number(5) default 1,
partieperdues int DEFAULT 0, --ajout� pour calculer le nombre de fois que le joueur a perdu une partie dans l'heure
constraint fk_niveau foreign key(idniveau) references niveau(idniveau)
);
--table question
create table question(idQ number(5) primary key not null,intitulé varchar2(100) not null);

--table collection
create table collection(idcollection number(5) primary key not null,typeC varchar2(10),constraint ch_type check (typec in ('individue','vehicule')));



--table grille
create table grille(idg number(5) primary key not null,
idniveau number(5) ,constraint fk_idniveaug foreign key(idniveau) references niveau(idniveau),
taille number(5));



--table image
create table image(idim number(5) primary key not null,chemin varchar2(100)
--caracteristiques 
);

--table eliminer

create table eliminer(
idQ number(5) constraint nn_idQe not null,
idim number(5) constraint nn_idime not null,
eliminerQe varchar2(10),constraint ch_eliminerQ check (eliminerQe in ('True','False')),
constraint pk_eleiminer primary key(idQ,idim),
constraint fk_idime foreign key (idim) references image(idim),
constraint fk_idQ2 foreign key (idQ) references question(idQ)
);
--table collectionner
create table collectionner(
idcollection number(5) constraint  nn_idcoll1 not null,
idim number(5) constraint  nn_idmc not null,
constraint pk_collectionner primary key(idcollection,idim),
constraint fk_idimc foreign key (idim) references image(idim),
constraint fk_idcollc foreign key (idcollection) references collection(idcollection)

);
--table composer
create table composer(
idim number(5) constraint nn_idimc not null,
idg number(5) constraint nn_idgc not null,
positionx number(2),
positiony number(2),
constraint pk_composer primary key(idim,idg),
constraint fk_idimcp foreign key (idim) references image(idim),
constraint fk_idgc foreign key (idg) references grille(idg)
);

--table dependre
create table dependre (
idQ number(5) constraint  nn_idQ2 not null,
idcollection number(5) constraint  nn_idcoll not null,
constraint pk_dependre primary key(idQ,idcollection),
constraint fk_idQd foreign key (idQ) references question(idQ),
constraint fk_idcolld foreign key (idcollection) references collection(idcollection)

);

--table partie
create table partie(
idp number(5) primary key not null,
datep date,
partie_finie varchar2(5),constraint ch_pf check (partie_finie in ('False','True')),
idcollection number(5) ,
constraint fk_idc foreign key (idcollection) references collection(idcollection),
idg number(5),constraint fk_idg foreign key(idg) references grille(idg),
idniveau number(5) ,constraint fk_idniveau foreign key(idniveau) references niveau(idniveau),
idjoueur varchar2(20),constraint fk_idj foreign key (idjoueur) references joueur(idjoueur),
score int,
heurefinp date
);

--table poser
create table poser(
idjoueur varchar2(20) constraint nn_idj not null,
idp number(5) constraint nn_idp not null,
idQ number(5) constraint nn_idQ not null,
ordre number(10) constraint nn_ordre not null,
constraint pk_poser primary key(idjoueur,idp,idQ,ordre),
constraint fk_idj1 foreign key (idjoueur) references joueur(idjoueur),
constraint fk_idp1 foreign key(idp) references partie(idp),
constraint fk_idQ1 foreign key (idQ) references question(idQ)
);

--table reponse
create table reponse(
idimr number(5) constraint nn_idimr not null,
idimj number(5) constraint nn_idimj not null,
idp number(5) constraint nn_idpr not null,

constraint pk_reponse primary key(idimr,idimj,idp),
constraint fk_idpr foreign key (idp) references partie(idp),
constraint fk_idimr foreign key (idimr) references image(idim),
constraint fk_idimj foreign key (idimj) references image(idim)
);


