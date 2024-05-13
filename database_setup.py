import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=""
)


cursor = conn.cursor()
cursor.execute("DROP DATABASE IF EXISTS traffic_watcha")
cursor.execute("CREATE DATABASE traffic_watcha")
cursor.execute("USE traffic_watcha")

create_violations_table = """
CREATE TABLE IF NOT EXISTS violations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    type VARCHAR(255),
    location VARCHAR(255),
    creation_time DATETIME,
    file_path VARCHAR(255)
)
"""
create_temp_table = """
CREATE TABLE IF NOT EXISTS temp (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    type VARCHAR(255),
    location VARCHAR(255),
    creation_time DATETIME,
    file_path VARCHAR(255)
)
"""
create_temp_table2 = """
CREATE TABLE IF NOT EXISTS temp2 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    density FLOAT,
    classification VARCHAR(20),
    location VARCHAR(255),
    intersection VARCHAR(255),
    creation_time DATETIME
)
"""

create_police_table = """
CREATE TABLE IF NOT EXISTS police (
    pid INT AUTO_INCREMENT PRIMARY KEY,
    number INT,
    email VARCHAR(255)
)
"""

create_nwa_table = """
CREATE TABLE IF NOT EXISTS nwa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vid INT,
    email VARCHAR(255),
    number INT,
    file_path VARCHAR(255),
    FOREIGN KEY (vid) REFERENCES violations(id) ON DELETE CASCADE ON UPDATE CASCADE
)
"""

create_source_video_table = """
CREATE TABLE IF NOT EXISTS sources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    location VARCHAR(255),
    creation_time DATETIME,
    clip_length FLOAT,
    file_path VARCHAR(255),
    size FLOAT
)
"""

create_traffic_density_table = """
CREATE TABLE IF NOT EXISTS density (
    id INT AUTO_INCREMENT PRIMARY KEY,
    density FLOAT,
    classification VARCHAR(20),
    location VARCHAR(255),
    intersection VARCHAR(255),
    creation_time DATETIME
)
"""


cursor.execute(create_violations_table)
cursor.execute(create_source_video_table)
cursor.execute(create_traffic_density_table)
cursor.execute(create_temp_table)
cursor.execute(create_nwa_table)
cursor.execute(create_police_table)
cursor.execute(create_temp_table2)

cursor.close()