DROP DATABASE IF EXISTS humidity_tracker;

CREATE DATABASE humidity_tracker;

USE humidity_tracker;

CREATE TABLE Device(
    DeviceID INT NOT NULL AUTO_INCREMENT,
    DevName VARCHAR(100) NOT NULL,
    CONSTRAINT DevName_pk PRIMARY KEY (DeviceID)
);

CREATE TABLE IF NOT EXISTS History(
    HistoryID INTEGER NOT NULL AUTO_INCREMENT,
    CurrentDateTime DATETIME NOT NULL,
    DeviceID INTEGER NOT NULL,
    Temperature FLOAT(2),
    Humidity FLOAT(2),
    PRIMARY KEY (HistoryID),
    CONSTRAINT DeviceID_fk FOREIGN KEY (DeviceID) REFERENCES Device(DeviceID) ON DELETE CASCADE
);

INSERT INTO Device(DevName) VALUES ("Office"),("Bedroom"),("Living Room"),("Kitchen");

-- CREATE USER 'user1'@localhost IDENTIFIED BY 'password1';
-- GRANT ALL PRIVILEGES ON *.* TO <user>@<ip> IDENTIFIED BY '<pw>';
-- update 50-server.cnf 127.0.0.1 -> 0.0.0.0