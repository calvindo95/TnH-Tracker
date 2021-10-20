CREATE TABLE DevName(
    DevNameID INT NOT NULL AUTO_INCREMENT,
    DevName VARCHAR(100) NOT NULL,
    CONSTRAINT DevName_pk PRIMARY KEY (DevNameID)
)

CREATE TABLE IF NOT EXISTS History (
    HistoryID INTEGER NOT NULL AUTO_INCREMENT,
    Temperature FLOAT(2),
    Humidity FLOAT(2),
    CONSTRAINT History_pk PRIMARY KEY (HistoryID)
)

CREATE TABLE IF NOT EXISTS Device(
    DeviceID INTEGER NOT NULL AUTO_INCREMENT,
    DevNameID INTEGER NOT NULL,
    CONSTRAINT Device_pk PRIMARY KEY (DeviceID),
    CONSTRAINT DevNameID_fk FOREIGN KEY (DevNameID) REFERENCES DevName(DevNameID)
)

CREATE TABLE IF NOT EXISTS Data_History(
    Data_HistoryID INTEGER NOT NULL AUTO_INCREMENT,
    DeviceID INTEGER NOT NULL,
    HistoryID INTEGER NOT NULL,
    CurrentDateTime DATETIME NOT NULL,
    PRIMARY KEY (Data_HistoryID),
    CONSTRAINT HistoryID_fk FOREIGN KEY (HistoryID) REFERENCES History(HistoryID),
    CONSTRAINT DeviceID_fk FOREIGN KEY (DeviceID) REFERENCES Device(DeviceID)
)

SELECT DevName.DevName, Data_History.CurrentDateTime, History.Temperature, History.Humidity FROM Device
LEFT JOIN DevName ON Device.DevNameID=DevName.DevNameID
LEFT JOIN Data_History ON Data_History.DeviceID=Device.DeviceID
LEFT JOIN History ON History.HistoryID=Data_History.HistoryID
WHERE Device.DeviceID=1