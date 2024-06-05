CREATE TABLE versicherung (
    id INT AUTO_INCREMENT PRIMARY KEY,
    erfassung_id VARCHAR(36),
    grund varchar(50),
    versicherungsbeginn DATE,
    versicherungsart VARCHAR(50),
    deckungssumme INT
);

CREATE TABLE auto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    erfassung_id VARCHAR(36),
    hersteller VARCHAR(50),
    modell VARCHAR(50),
    hsn VARCHAR(20),
    tsn VARCHAR(20),
    baujahr INT
);

CREATE TABLE nutzung (
    id INT AUTO_INCREMENT PRIMARY KEY,
    erfassung_id VARCHAR(36),
    jahresfahrleistung INT,
    nutzungsart VARCHAR(50)
);

CREATE TABLE versicherungsnehmer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    erfassung_id VARCHAR(36),
    anrede VARCHAR(25),
    name VARCHAR(100),
    vorname VARCHAR(100),
    strasse VARCHAR(100),
    plz VARCHAR(10),
    ort VARCHAR(100),
    geburtsdatum DATE,
    fuehrerschein DATE
);

CREATE TABLE vorversicherung (
    id INT AUTO_INCREMENT PRIMARY KEY,
    erfassung_id VARCHAR(36),
    vorversicherer VARCHAR(50),
    schadenfreiheitsrabatt varchar(10),
    schadenfreiheitsrabatt_vk varchar(10)
);




