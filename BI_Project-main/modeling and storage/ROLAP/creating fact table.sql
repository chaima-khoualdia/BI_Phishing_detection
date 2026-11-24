

DROP TABLE IF EXISTS staging_phishing_clean;
DROP TABLE IF EXISTS staging_phishing_clean_temp;

CREATE TABLE staging_phishing_clean (
    url TEXT,
    domain_name VARCHAR(255),
    label VARCHAR(50),
    is_phishing TINYINT(1),
    url_length INT,
    has_ip TINYINT(1),
    special_char_count INT,
    has_suspicious_keyword TINYINT(1)
);

SHOW VARIABLES LIKE 'secure_file_priv';

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/fact_phishing_incident.csv'
 INTO TABLE staging_phishing_clean
 FIELDS TERMINATED BY ',' 
 ENCLOSED BY '"'
 LINES TERMINATED BY '\r\n'
 IGNORE 1 ROWS
 (url, domain_name, label, url_length, @is_phishing, @has_ip, special_char_count, @has_suspicious_keyword)
 SET 
     is_phishing = CAST(TRIM(@is_phishing) AS UNSIGNED),
     has_ip = CAST(TRIM(@has_ip) AS UNSIGNED),
     has_suspicious_keyword = CAST(TRIM(@has_suspicious_keyword) AS UNSIGNED)
     
SET SQL_SAFE_UPDATES = 0;

-- Update fact table to reference dimensions
ALTER TABLE staging_phishing_clean
    ADD COLUMN label_id INT,
    ADD COLUMN domain_id INT,
    ADD COLUMN characteristic_id INT,
    ADD COLUMN length_id INT;

-- Add foreign key constraints
ALTER TABLE staging_phishing_clean
    ADD CONSTRAINT fk_label FOREIGN KEY (label_id) REFERENCES dim_label(label_id),
    ADD CONSTRAINT fk_domain FOREIGN KEY (domain_id) REFERENCES dim_domain(domain_id),
    ADD CONSTRAINT fk_characteristics FOREIGN KEY (characteristic_id) REFERENCES dim_url_characteristics(characteristic_id),
    ADD CONSTRAINT fk_length FOREIGN KEY (length_id) REFERENCES dim_url_length(length_id);

-- Update fact table with dimension keys
UPDATE staging_phishing_clean f
INNER JOIN dim_label l ON f.label = l.label_name
SET f.label_id = l.label_id;

UPDATE staging_phishing_clean f
INNER JOIN dim_domain d ON f.domain_name = d.domain_name
SET f.domain_id = d.domain_id;

UPDATE staging_phishing_clean f
INNER JOIN dim_url_length ul ON 
    CASE 
        WHEN f.url_length < 20 THEN 'Very Short (<20)'
        WHEN f.url_length < 30 THEN 'Short (20-29)'
        WHEN f.url_length < 50 THEN 'Medium (30-49)'
        WHEN f.url_length < 100 THEN 'Long (50-99)'
        ELSE 'Very Long (100+)'
    END = ul.length_category
SET f.length_id = ul.length_id;

UPDATE staging_phishing_clean f
INNER JOIN dim_url_characteristics c ON 
    f.has_ip = c.has_ip 
    AND f.has_suspicious_keyword = c.has_suspicious_keyword
    AND CASE 
        WHEN f.special_char_count = 0 THEN 'None'
        WHEN f.special_char_count <= 3 THEN 'Low (1-3)'
        WHEN f.special_char_count <= 7 THEN 'Medium (4-7)'
        WHEN f.special_char_count <= 15 THEN 'High (8-15)'
        ELSE 'Very High (15+)'
    END = c.special_char_range
    AND CASE 
        WHEN f.url_length < 20 THEN 'Very Short (<20)'
        WHEN f.url_length < 30 THEN 'Short (20-29)'
        WHEN f.url_length < 50 THEN 'Medium (30-49)'
        WHEN f.url_length < 100 THEN 'Long (50-99)'
        ELSE 'Very Long (100+)'
    END = c.length_category
SET f.characteristic_id = c.characteristic_id;


-- Step 1: Increase timeouts
SET SESSION max_execution_time = 0;
SET SESSION wait_timeout = 28800;
SET SQL_SAFE_UPDATES = 0;

-- Add indexes to speed up the joins
CREATE INDEX idx_staging_domain ON staging_phishing_clean(domain_name);
CREATE INDEX idx_staging_label ON staging_phishing_clean(label);
CREATE INDEX idx_staging_length ON staging_phishing_clean(url_length);
CREATE INDEX idx_staging_flags ON staging_phishing_clean(has_ip, has_suspicious_keyword, special_char_count);