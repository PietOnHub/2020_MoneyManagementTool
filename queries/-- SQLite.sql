-- SQLite
SELECT Datum, Betrag FROM buchung

SELECT Datum, Betrag, Kategorie FROM buchung

SELECT Kategorie, SUM(Betrag) as 'All' FROM buchung GROUP BY Kategorie

SELECT Kategorie, SUM(Betrag) as '360' FROM buchung  
WHERE Datum BETWEEN date('now','-1 year') and date('now')
GROUP BY Kategorie

SELECT Kategorie, SUM(Betrag) as '30' FROM buchung  
WHERE Datum BETWEEN date('now','-1 months') and date('now')
GROUP BY Kategorie

SELECT * FROM buchung WHERE Kategorie = "Konsum"

SELECT Kategorie, * FROM buchung 
WHERE Datum >= date('now','-1 months') 
ORDER BY Kategorie
