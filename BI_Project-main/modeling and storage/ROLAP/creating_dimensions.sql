-- Create dim_label dimension table
CREATE TABLE dim_label (
    label_id INT PRIMARY KEY AUTO_INCREMENT,
    label_name VARCHAR(20) NOT NULL UNIQUE,
    is_phishing TINYINT(1) NOT NULL,
    description VARCHAR(255),
    INDEX idx_label_name (label_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Populate dim_label
INSERT INTO dim_label (label_name, is_phishing, description)
VALUES 
    ('benign', 0, 'Legitimate, safe URLs with no malicious intent'),
    ('phishing', 1, 'Malicious URLs designed to deceive users');
    
-- Create dim_domain dimension table
CREATE TABLE dim_domain (
    domain_id INT PRIMARY KEY AUTO_INCREMENT,
    domain_name VARCHAR(255) NOT NULL UNIQUE,
    total_urls INT DEFAULT 0,
    phishing_count INT DEFAULT 0,
    benign_count INT DEFAULT 0,
    avg_url_length DECIMAL(10,2),
    first_seen_label VARCHAR(20),
    phishing_rate DECIMAL(5,2),
    INDEX idx_domain_name (domain_name),
    INDEX idx_phishing_rate (phishing_rate)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Populate dim_domain from staging table
INSERT INTO dim_domain (
    domain_name, 
    total_urls, 
    phishing_count, 
    benign_count,
    avg_url_length,
    first_seen_label,
    phishing_rate
)
SELECT 
    domain_name,
    COUNT(*) as total_urls,
    SUM(CASE WHEN is_phishing = 1 THEN 1 ELSE 0 END) as phishing_count,
    SUM(CASE WHEN is_phishing = 0 THEN 1 ELSE 0 END) as benign_count,
    ROUND(AVG(url_length), 2) as avg_url_length,
    MAX(label) as first_seen_label,
    ROUND((SUM(CASE WHEN is_phishing = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) as phishing_rate
FROM staging_phishing_clean
GROUP BY domain_name;


-- Create dim_url_characteristics dimension table
CREATE TABLE dim_url_characteristics (
    characteristic_id INT PRIMARY KEY AUTO_INCREMENT,
    has_ip TINYINT(1) NOT NULL,
    has_suspicious_keyword TINYINT(1) NOT NULL,
    special_char_range VARCHAR(20) NOT NULL,
    length_category VARCHAR(20) NOT NULL,
    risk_profile VARCHAR(50),
    UNIQUE KEY unique_characteristics (has_ip, has_suspicious_keyword, special_char_range, length_category),
    INDEX idx_risk_profile (risk_profile)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Populate dim_url_characteristics from staging table
INSERT INTO dim_url_characteristics (
    has_ip,
    has_suspicious_keyword,
    special_char_range,
    length_category,
    risk_profile
)
SELECT DISTINCT
    has_ip,
    has_suspicious_keyword,
    CASE 
        WHEN special_char_count = 0 THEN 'None'
        WHEN special_char_count <= 3 THEN 'Low (1-3)'
        WHEN special_char_count <= 7 THEN 'Medium (4-7)'
        WHEN special_char_count <= 15 THEN 'High (8-15)'
        ELSE 'Very High (15+)'
    END as special_char_range,
    CASE 
        WHEN url_length < 20 THEN 'Very Short (<20)'
        WHEN url_length < 30 THEN 'Short (20-29)'
        WHEN url_length < 50 THEN 'Medium (30-49)'
        WHEN url_length < 100 THEN 'Long (50-99)'
        ELSE 'Very Long (100+)'
    END as length_category,
    CASE 
        WHEN has_ip = 1 AND has_suspicious_keyword = 1 THEN 'Critical Risk'
        WHEN has_ip = 1 OR has_suspicious_keyword = 1 THEN 'High Risk'
        WHEN special_char_count > 7 THEN 'Medium Risk'
        ELSE 'Low Risk'
    END as risk_profile
FROM staging_phishing_clean
ORDER BY has_ip DESC, has_suspicious_keyword DESC, special_char_range, length_category;

-- Create dim_url_length dimension table
CREATE TABLE dim_url_length (
    length_id INT PRIMARY KEY AUTO_INCREMENT,
    length_category VARCHAR(30) NOT NULL UNIQUE,
    min_length INT NOT NULL,
    max_length INT,
    description VARCHAR(100),
    INDEX idx_length_category (length_category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Populate dim_url_length
INSERT INTO dim_url_length (length_category, min_length, max_length, description)
VALUES 
    ('Very Short (<20)', 0, 19, 'URLs shorter than 20 characters'),
    ('Short (20-29)', 20, 29, 'Short URLs between 20-29 characters'),
    ('Medium (30-49)', 30, 49, 'Medium length URLs'),
    ('Long (50-99)', 50, 99, 'Long URLs between 50-99 characters'),
    ('Very Long (100+)', 100, NULL, 'Very long URLs over 100 characters');
    
-- Check dimension table counts
SELECT 'dim_label' as table_name, COUNT(*) as row_count FROM dim_label
UNION ALL
SELECT 'dim_domain', COUNT(*) FROM dim_domain
UNION ALL
SELECT 'dim_url_characteristics', COUNT(*) FROM dim_url_characteristics
UNION ALL
SELECT 'dim_url_length', COUNT(*) FROM dim_url_length;

-- Verify foreign key population
SELECT 
    SUM(CASE WHEN label_id IS NOT NULL THEN 1 ELSE 0 END) as populated_label_id,
    SUM(CASE WHEN domain_id IS NOT NULL THEN 1 ELSE 0 END) as populated_domain_id,
    SUM(CASE WHEN characteristic_id IS NOT NULL THEN 1 ELSE 0 END) as populated_characteristic_id,
    SUM(CASE WHEN length_id IS NOT NULL THEN 1 ELSE 0 END) as populated_length_id,
    COUNT(*) as total_rows
FROM staging_phishing_clean;
SET SQL_SAFE_UPDATES = 0;

-- Add the new columns if they don't exist
ALTER TABLE staging_phishing_clean
ADD COLUMN length_category VARCHAR(20),
ADD COLUMN special_char_range VARCHAR(20);

-- Populate the new columns
UPDATE staging_phishing_clean
SET length_category = CASE 
    WHEN url_length < 20 THEN 'Very Short (<20)'
    WHEN url_length < 30 THEN 'Short (20-29)'
    WHEN url_length < 50 THEN 'Medium (30-49)'
    WHEN url_length < 100 THEN 'Long (50-99)'
    ELSE 'Very Long (100+)'
END,
special_char_range = CASE
    WHEN special_char_count = 0 THEN 'None'
    WHEN special_char_count <= 3 THEN 'Low (1-3)'
    WHEN special_char_count <= 7 THEN 'Medium (4-7)'
    WHEN special_char_count <= 15 THEN 'High (8-15)'
    ELSE 'Very High (15+)'
END;

SET SQL_SAFE_UPDATES = 1;