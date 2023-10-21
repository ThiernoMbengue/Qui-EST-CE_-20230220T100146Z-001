
--verifier si le joueur peut jouer le niveau demander
CREATE OR REPLACE TRIGGER t_b_i_partie
BEFORE INSERT ON partie
FOR EACH ROW
DECLARE
	niveau_j joueur.idniveau%type;
BEGIN
    select idniveau into niveau_j from joueur 
    where joueur.idjoueur=:new.idjoueur;
    
    if niveau_j <:new.idniveau then 
    raise_application_error(-20001,'niveau joueur trop bas');--on bloque la demande si le niveau est trop bas
    end if;
end;
/
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--Limitation des parties : Un joueur ayant perdu plus de 5 parties dans l'heure ne pourra pas jouer pendant 4h.       
-- joueur a perdu
-- a priori on a le declencement du triggger t_b_u_Partie deja
create or replace Trigger t_b_i_Partie_2
Before INSERT on Partie
for each row
declare 
v_partieperdues int;
v_daterejouer Joueur.daterejouer%Type;
BEGIN

    -- on regarde si le joueur peut jouer ou pas (bloquage des 5 parties)
    select daterejouer into v_daterejouer from Joueur where idjoueur = :new.idjoueur;
    if v_daterejouer > SYSDATE then
        raise_application_error(-20001, 'Vous ne pouvez pas encore jouer. revenez à '||to_char(v_daterejouer, 'DD-MM-YYYY  HH24:MI:SS'));
    end if;
    -- le joueur n'est pas bloqué
    -- on peut donc mettre a jour son compte de parties perdues dans l'heure en ayant calculé cette valeur
    
    -- on calcule d'abord le nombre de parties que le joueur a perdu dans l'heure
    select count(idp) into v_partieperdues from Partie 
    where idjoueur = :new.idjoueur and 
        partie_finie = 'False' and
        heurefinp > SYSDATE - interval '1' hour;
    
    -- on met a jour le compte des parties perdues dans l'heure avec la valeur qu'on vient de trouver
    update Joueur
    SET partieperdues = v_partieperdues
    where idjoueur = :new.idjoueur;
    
    
END;
/

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- trigger pour  eviter de poser une question  dans une partie déjà finie 

CREATE OR REPLACE TRIGGER t_b_i_question 
BEFORE INSERT ON poser 
FOR EACH ROW 
DECLARE 
vetat partie.partie_finie%TYPE;
BEGIN 
    SELECT partie_finie into vetat FROM Partie where idp= :new.idp;
    if vetat = 'True' then -- si la partie est terminé, on bloque l'insertion sur poser
        raise_application_error(-20004, 'Partie Terminée');
    end if;
    
END;
/

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- passage d'un niveau
--On supposse que le joueur passe a un niveau des qu'il gagne  et a chaque partie on fait des modification
create or replace trigger t_b_u_Partie
before update on Partie
FOR EACH ROW
DECLARE 
v_niveau_partie niveau.idniveau%type;
v_niveau_joueur niveau.idniveau%type;
v_partieperdues Joueur.partieperdues%type;
BEGIN
    -- si on a une partie gagnée, on regarde si le niveau du joueur doit etre augmenté :
    if :new.partie_finie = 'True' then
        -- on récupere le niveau de la partie pour le comparer au niveau du joueur
        select idniveau into v_niveau_partie from Grille                                --voire si on recuperer le niveau grille de jeu ou niveau partie
                                                                                        --des doutes car niveau partie c'est a nous de le mettre
        where idg = :old.idg;
        -- on recupere le niveau du joueur
        select idniveau into v_niveau_joueur from Joueur
        where idjoueur = :old.idjoueur;
        
        -- si le joueur a gagné une partie du niveau qu'il a débloqué on l'augmente de niveau (sauf si il a atteint le niveau max)
        if v_niveau_joueur = v_niveau_partie - 1 then
            if v_niveau_partie != 3 then -- on a pas besoin de modifier le niveau d'un joueur qui a atteint le niveau maximum
                update Joueur 
                set idniveau = idniveau + 1 -- on augmente de 1 le niveau du joueur
                where idjoueur = :old.idjoueur;
            end if;
        end if;
    elsif :new.partie_finie = 'False' then
        -- on regarde si il doit etre bloqué pendant 4h :
        select partieperdues into v_partieperdues from Joueur where idjoueur = :old.idjoueur;
        if v_partieperdues > 5 then
            update Joueur 
            set partieperdues = partieperdues + 1, -- on augmente de 1 le nombre de parties perdues dans l'heure d'un joueur
                daterejouer = SYSDATE + interval '4' hour -- on le bloque pendant 4 heures pour voire l 'utuiliser dans le triggrer 2
            where idjoueur = :old.idjoueur;
        else -- dans ce cas (moins de 5 parties perdues) la on a pas besoin de bloquer le joueur pendant 4 heures
            update Joueur 
            set partieperdues = partieperdues + 1 -- on augmente de 1 le nombre de parties perdues dans l'heure d'un joueur
            where idjoueur = :old.idjoueur;
        end if;
    end if;
END;
/
