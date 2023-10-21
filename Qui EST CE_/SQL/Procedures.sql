--create sequence sequence_joueur
--;/
create sequence sequence_partie 
;/

SET SERVEROUTPUT ON;
create or replace procedure Inserer_Joueur( vidj joueur.idjoueur%type, vmdp joueur.mdp%type,pretour out NUMBER) is
begin
    insert into joueur values (vidj,vmdp,SYSDATE,1,0);
    pretour:=0;
    commit;
exception
    when dup_val_on_index then
    dbms_output.put_line('identifiant joueur existe deja');
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE (SQLERRM || '   ' || sqlcode);
        pretour:=sqlcode;

end;
/
--SET SERVEROUTPUT ON;
--create or replace procedure Inserer_Joueur( vidj joueur.idjoueur%type, vmdp joueur.mdp%type) is
--begin
--    insert into joueur values (vidj,vmdp,SYSDATE,1,0);
--    commit;
--exception
--    when dup_val_on_index then
--    dbms_output.put_line('identifiant joueur existe deja');
--    WHEN OTHERS THEN
--        DBMS_OUTPUT.PUT_LINE ('error'  );
--
--end;
--/
--



--procedure insertion partie
create or replace procedure Inserer_Partie(vidcollection collection.idcollection%type,vidgrille grille.idg%type,vidjoueur joueur.idjoueur%type,Vidniveau partie.idniveau%type,vheurfin date,pretour out number) is
    vdate date;
    idp number;
    id1 number;
    cle_etrangere_non_trouve exception;
    PRAGMA EXCEPTION_INIT(cle_etrangere_non_trouve,-2291);
begin
    select sysdate into vdate from dual;
    select sequence_partie.nextval into id1 from dual;
    select sequence_partie.currval into idp from dual;
    insert into partie values(idp,vdate,'False',vidcollection,vidgrille,Vidniveau,vidjoueur,0,vheurfin);
    pretour:=0;
    commit;
exception
    when cle_etrangere_non_trouve then
        if (SQLERRM like '%fk_idniveau%') then 
            DBMS_OUTPUT.PUT_LINE('Niveau n existe pas');
                pretour:= 1;
        end if;
        if (SQLERRM like '%fk_idg%') then 
            DBMS_OUTPUT.PUT_LINE('grille n existe pas');
                pretour:= 2;
        end if;
        if (SQLERRM like '%fk_idc%') then 
            DBMS_OUTPUT.PUT_LINE('la collection n existe pas');
                pretour:= 3;
  
        else 
            DBMS_OUTPUT.PUT_LINE('Utilisateur n existe pas');
            pretour:=3;
        end if;
    WHEN others THEN 
        DBMS_OUTPUT.PUT_LINE (SQLERRM || '   ' || sqlcode);
        pretour:=sqlcode;
        
end;
/

--procedure insertion ordre

create or replace procedure Inserer_poser(vidjoueur joueur.idjoueur%type,vidQ question.idq%type,vordre number,pretour out number) is
    cle_etrangere_non_trouve1 exception;
    PRAGMA EXCEPTION_INIT(cle_etrangere_non_trouve1,-2291);
    vidp partie.idp%type;
begin
    
    select idp into vidp  from partie where idp>=all(select idp from partie);
    insert into poser values(vidjoueur,vidp,vidQ,vordre);
    pretour:=0;
    commit;
exception
    when cle_etrangere_non_trouve1 then
         if (SQLERRM like '%fk_idj1%') then 
            DBMS_OUTPUT.PUT_LINE('le joueur n existe pas');
                pretour:= 1;
        end if;
        if (SQLERRM like '%fk_idp1%') then 
            DBMS_OUTPUT.PUT_LINE('la partie n existe pas');
                pretour:= 2;
        else
            DBMS_OUTPUT.PUT_LINE('la question nexiste pas');
                pretour:= 2;
        end if;
     WHEN others THEN 
        DBMS_OUTPUT.PUT_LINE (SQLERRM || '   ' || sqlcode);
        pretour:=sqlcode;
        


end;
/
--procedure insertion reponse

create or replace procedure inserer_reponse(vidI image.idim%type,pretour out number)is

    vidp partie.idp%type;
    cle_etranger_non_trouve2 exception;
    PRAGMA EXCEPTION_INIT(cle_etranger_non_trouve2,-2291);
begin
    select idp into vidp  from partie where idp>=all(select idp from partie);
    insert into reponse values (vidI,vidp);
    pretour:=0;
commit;
exception
    when cle_etranger_non_trouve2 then
        if (SQLERRM like '%fk_idpr%') then 
            DBMS_OUTPUT.PUT_LINE('la partie n existe pas');
                pretour:= 1;
        else
            DBMS_OUTPUT.PUT_LINE('l image n existe pas');
                pretour:= 2;
        end if;
    WHEN others THEN 
        DBMS_OUTPUT.PUT_LINE (SQLERRM || '   ' || sqlcode);
        pretour:=sqlcode;
        

end;
/


    
-- recuperer Nbr de partie perdu dans 1h et declancher trigger si perdu + de 5 fois et remettre partie perdu a  0

CREATE OR REPLACE PROCEDURE recupPartiePerdues(pid_joueur Joueur.idjoueur%type, pretour out number) as

nbPartiesPerdues int;

BEGIN
-- selectionner  les partie perdue jouer dans l'heure entre la date systeme et 1h avant la date systeme
SELECT sum(idp) INTO nbPartiesPerdues FROM Partie WHERE partie_finie='False' and heurefinP between (sysdate-interval '1' hour) and sysdate and idjoueur = pid_joueur;

if nbPartiesPerdues > 4 then  -- a revoir car le joeur doit attendre 4h avant de rejouer
    update Joueur set partieperdues=0 where idjoueur=pid_joueur;
end if;

COMMIT;
END;

/

--revoir le procedures precedentes et faire hight score



--Sauvegarder une partie 

CREATE OR REPLACE PROCEDURE sauvegardePartie (vetat partie.partie_finie%TYPE, vscore partie.score%TYPE,retour OUT NUMBER) IS

vidp int;
BEGIN
select idp into vidp from partie where idp>=all(select idp from partie);
UPDATE Partie SET partie_finie= vetat, score = vscore
WHERE idp = vidp;
retour:=0;

UPDATE Partie SET heurefinp = sysdate
WHERE idp= vidp;
retour:=1;

--voir si on doit mettre a jour score aussi

END;
/ 

COMMIT;


SET SERVEROUTPUT ON;
create or replace procedure Inserer_reponse( vidimr image.idim%type,vidimj image.idim%type,vidp partie.idp%type,pretour out number) is
begin
    insert into reponse values (vidimr,vidimj,vidp);
    pretour:=0;
    commit;
exception
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE (SQLERRM || '   ' || sqlcode);
        pretour:=sqlcode;

end;
/
commit;