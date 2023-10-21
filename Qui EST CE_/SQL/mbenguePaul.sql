
drop table niveau;
drop table joueur;
drop table grille;
drop table image;
drop table collection;
drop table question;
drop table partie;
drop table poser;
drop table eliminer;
drop table dependre;
drop table collectionner;
drop table composer;
drop table reponse;

create table niveau( idniveau number(5) primary key not null,constraint check_niveau check(idniveau in (1,2,3)));

create table joueur(idjoueur number(5) primary key not null,
pseudo varchar2(30),constraint nn_pseudo unique(pseudo),
mdp varchar2(30) constraint nn_mdp not null,
idniveau number(5) constraint nn_idniveau not null,
constraint fk_niveau foreign key(idniveau) references niveau(idniveau)
);

create table grille(idg number(5) primary key not null,
taille number(5));

create table image(idim number(5) primary key not null,chemin varchar2(100)
);
create table collection(idcollection number(5) primary key not null,typeC varchar2(10),constraint ch_type check (typec in ('individue','vehicule')));

create table question(idQ number(5) primary key not null,intitulé varchar2(100) not null);

create table partie(idp number(5) primary key not null,datep date,partie_finie varchar2(5),constraint ch_pf check (partie_finie in ('False','True')),
idcollection number(5) ,
constraint fk_idc foreign key (idcollection) references collection(idcollection),
idg number(5),constraint fk_idg foreign key(idg) references grille(idg),
idniveau number(5) ,constraint fk_idniveau foreign key(idniveau) references niveau(idniveau),
idjoueur number(5),constraint fk_idj foreign key (idjoueur) references joueur(idjoueur)
);

create table poser(
idjoueur number(5) constraint nn_idj not null,
idp number(5) constraint nn_idp not null,
idQ number(5) constraint nn_idQ not null,
constraint pk_poser primary key(idjoueur,idp,idQ),
constraint fk_idj1 foreign key (idjoueur) references joueur(idjoueur),
constraint fk_idp1 foreign key(idp) references partie(idp),
constraint fk_idQ1 foreign key (idQ) references question(idQ),
ordre number(10) -- a revoir
);


create table eliminer(
idQ number(5) constraint nn_idQ1 not null,
idjoueur number(5) constraint nn_idj1 not null,
constraint pk_eleiminer primary key(idQ,idjoueur),
constraint fk_idj2 foreign key (idjoueur) references joueur(idjoueur),
constraint fk_idQ2 foreign key (idQ) references question(idQ)
);

create table dependre (
idQ number(5) constraint  nn_idQ2 not null,
idcollection number(5) constraint  nn_idcoll not null,
constraint pk_dependre primary key(idQ,idcollection),
constraint fk_idQd foreign key (idQ) references question(idQ),
constraint fk_idcolld foreign key (idcollection) references collection(idcollection)

);
create table collectionner(
idjoueur number(5) constraint  nn_idj3 not null,
idcollection number(5) constraint  nn_idcoll1 not null,
constraint pk_collectionner primary key(idjoueur,idcollection),
constraint fk_idjc foreign key (idjoueur) references joueur(idjoueur),
constraint fk_idcollc foreign key (idcollection) references collection(idcollection)


);

create table composer(
idjoueur number(5) constraint nn_idjC not null,
idg number(5) constraint nn_idgc not null,
positionx number(2),
positiony number(2),
constraint pk_composer primary key(idjoueur,idg),
constraint fk_idjcp foreign key (idjoueur) references joueur(idjoueur),
constraint fk_idgc foreign key (idg) references grille(idg)

);

create table reponse(
idim number(5) constraint nn_idim not null,
idp number(5) constraint nn_idpr not null,
constraint pk_reponse primary key(idim,idp),
constraint fk_idpr foreign key (idp) references partie(idp),
constraint fk_idim foreign key (idim) references image(idim)
);





