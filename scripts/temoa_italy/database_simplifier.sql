--BEGIN TRANSACTION;
--
---- Remove ExistingCapacity entries whose lifetime expires before time_future begins
---- FIX 1: lp.life_process (not lp.life) — LifetimeProcess uses column "life_process"
---- FIX 2: LifetimeTech JOIN includes regions to avoid duplicate matches
--DELETE FROM ExistingCapacity
--WHERE rowid IN (
--    SELECT ec.rowid
--    FROM ExistingCapacity ec
--    LEFT JOIN LifetimeProcess lp
--        ON ec.regions = lp.regions
--        AND ec.tech    = lp.tech
--        AND ec.vintage = lp.vintage
--    LEFT JOIN LifetimeTech lt
--        ON ec.regions = lt.regions
--        AND ec.tech   = lt.tech
--    CROSS JOIN (
--        SELECT MIN(t_periods) AS first_future
--        FROM time_periods
--        WHERE flag = 'f'
--    ) tf
--    WHERE (ec.vintage + COALESCE(lp.life_process, lt.life, 40)) <= tf.first_future
--);
--BEGIN TRANSACTION;
--
---- Step 0: identifica le tuple (regions, tech, vintage) da espellere
--CREATE TEMP TABLE _expired_processes AS
--SELECT ec.regions, ec.tech, ec.vintage
--FROM ExistingCapacity ec
--LEFT JOIN LifetimeProcess lp
--    ON ec.regions=lp.regions AND ec.tech=lp.tech AND ec.vintage=lp.vintage
--LEFT JOIN LifetimeTech lt
--    ON ec.regions=lt.regions AND ec.tech=lt.tech
--CROSS JOIN (SELECT MIN(t_periods) AS first_future FROM time_periods WHERE flag='f') tf
--WHERE (ec.vintage + COALESCE(lp.life_process, lt.life, 40)) <= tf.first_future;
--
---- Step 1: rimuovi da ExistingCapacity (come prima)
--DELETE FROM ExistingCapacity
--WHERE (regions, tech, vintage) IN (SELECT regions, tech, vintage FROM _expired_processes);
--
---- Step 2: propaga la pulizia a TUTTE le tabelle vintage-indexed
--DELETE FROM Efficiency             WHERE (regions, tech, vintage) IN (SELECT regions, tech, vintage FROM _expired_processes);
--DELETE FROM CapacityFactor         WHERE (regions, tech, vintage) IN (SELECT regions, tech, vintage FROM _expired_processes);
--DELETE FROM CapacityFactorProcess  WHERE (regions, tech, vintage) IN (SELECT regions, tech, vintage FROM _expired_processes);
--DELETE FROM EmissionActivity       WHERE (regions, tech, vintage) IN (SELECT regions, tech, vintage FROM _expired_processes);
--DELETE FROM CostFixed              WHERE (regions, tech, vintage) IN (SELECT regions, tech, vintage FROM _expired_processes);
--DELETE FROM CostInvest             WHERE (regions, tech, vintage) IN (SELECT regions, tech, vintage FROM _expired_processes);
--DELETE FROM CostVariable           WHERE (regions, tech, vintage) IN (SELECT regions, tech, vintage FROM _expired_processes);
--DELETE FROM LifetimeProcess        WHERE (regions, tech, vintage) IN (SELECT regions, tech, vintage FROM _expired_processes);
--DELETE FROM MaterialIntensity      WHERE (regions, tech, vintage) IN (SELECT regions, tech, vintage FROM _expired_processes);
--DELETE FROM TechnologyMaterialSupplyRisk WHERE (regions, tech, vintage) IN (SELECT regions, tech, vintage FROM _expired_processes);
--DELETE FROM CapacityCredit         WHERE (regions, tech, vintage) IN (SELECT regions, tech, vintage FROM _expired_processes);
--
--DROP TABLE _expired_processes;
--
---- ... (qui segue il resto del tuo simplifier sui periodi 2007/2008/.../2045)
--
--DELETE FROM "CapacityCredit" WHERE "vintage" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "CapacityCredit" WHERE "periods" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "CapacityFactor" WHERE "vintage" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "CapacityFactorProcess" WHERE "vintage" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "CostFixed" WHERE "vintage" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "CostFixed" WHERE "periods" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "CostInvest" WHERE "vintage" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "CostVariable" WHERE "vintage" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "CostVariable" WHERE "periods" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "CostEmission" WHERE "periods" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "Demand" WHERE "periods" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "DiscountRate" WHERE "vintage" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "Driver" WHERE "periods" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "Efficiency" WHERE "vintage" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "Elasticity" WHERE "periods" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "EmissionActivity" WHERE "vintage" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "EmissionLimit" WHERE "periods" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "EnergyCommodityConcentrationIndex" WHERE "periods" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "LifetimeProcess" WHERE "vintage" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "MaterialIntensity" WHERE "vintage" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "MaxActivity" WHERE "periods" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "MaxActivityGroup" WHERE "periods" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "MaxCapacity" WHERE "periods" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "MaxCapacityGroup" WHERE "periods" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "MaxInputGroup" WHERE "periods" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "MaxOutputGroup" WHERE "periods" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "MinActivity" WHERE "periods" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "MinActivityGroup" WHERE "periods" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "MinCapacity" WHERE "periods" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "MinCapacityGroup" WHERE "periods" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "MinInputGroup" WHERE "periods" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "MinOutputGroup" WHERE "periods" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "TechInputSplit" WHERE "periods" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "TechOutputSplit" WHERE "periods" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "TechnologyMaterialSupplyRisk" WHERE "vintage" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--DELETE FROM "time_periods" WHERE "t_periods" IN (2007, 2008, 2009, 2012, 2014, 2016, 2018, 2022, 2025, 2035, 2045);
--
--COMMIT;
PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

-- Step 0: snapshot dei processi scaduti
-- NOTA: first_future calcolato come il MIN futuro POST-semplificazione
DROP TABLE IF EXISTS _expired_processes;
CREATE TEMP TABLE _expired_processes AS
SELECT ec.regions, ec.tech, ec.vintage
FROM ExistingCapacity ec
LEFT JOIN LifetimeProcess lp
    ON ec.regions = lp.regions AND ec.tech = lp.tech AND ec.vintage = lp.vintage
LEFT JOIN LifetimeTech lt
    ON ec.regions = lt.regions AND ec.tech = lt.tech
CROSS JOIN (
    SELECT MIN(t_periods) AS first_future
    FROM time_periods
    WHERE flag = 'f'
      AND t_periods NOT IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045)
) tf
WHERE (ec.vintage + COALESCE(lp.life_process, lt.life, 40)) <= tf.first_future;

CREATE INDEX _idx_expired ON _expired_processes(regions, tech, vintage);

-- Step 1: rimuovi da ExistingCapacity
DELETE FROM ExistingCapacity WHERE EXISTS (
    SELECT 1 FROM _expired_processes ep
    WHERE ep.regions=ExistingCapacity.regions AND ep.tech=ExistingCapacity.tech AND ep.vintage=ExistingCapacity.vintage);

-- Step 2: propaga
DELETE FROM Efficiency             WHERE EXISTS (SELECT 1 FROM _expired_processes ep WHERE ep.regions=Efficiency.regions             AND ep.tech=Efficiency.tech             AND ep.vintage=Efficiency.vintage);
DELETE FROM CapacityFactor         WHERE EXISTS (SELECT 1 FROM _expired_processes ep WHERE ep.regions=CapacityFactor.regions         AND ep.tech=CapacityFactor.tech         AND ep.vintage=CapacityFactor.vintage);
DELETE FROM CapacityFactorProcess  WHERE EXISTS (SELECT 1 FROM _expired_processes ep WHERE ep.regions=CapacityFactorProcess.regions  AND ep.tech=CapacityFactorProcess.tech  AND ep.vintage=CapacityFactorProcess.vintage);
DELETE FROM EmissionActivity       WHERE EXISTS (SELECT 1 FROM _expired_processes ep WHERE ep.regions=EmissionActivity.regions       AND ep.tech=EmissionActivity.tech       AND ep.vintage=EmissionActivity.vintage);
DELETE FROM CostFixed              WHERE EXISTS (SELECT 1 FROM _expired_processes ep WHERE ep.regions=CostFixed.regions              AND ep.tech=CostFixed.tech              AND ep.vintage=CostFixed.vintage);
DELETE FROM CostInvest             WHERE EXISTS (SELECT 1 FROM _expired_processes ep WHERE ep.regions=CostInvest.regions             AND ep.tech=CostInvest.tech             AND ep.vintage=CostInvest.vintage);
DELETE FROM CostVariable           WHERE EXISTS (SELECT 1 FROM _expired_processes ep WHERE ep.regions=CostVariable.regions           AND ep.tech=CostVariable.tech           AND ep.vintage=CostVariable.vintage);
DELETE FROM LifetimeProcess        WHERE EXISTS (SELECT 1 FROM _expired_processes ep WHERE ep.regions=LifetimeProcess.regions        AND ep.tech=LifetimeProcess.tech        AND ep.vintage=LifetimeProcess.vintage);
DELETE FROM DiscountRate           WHERE EXISTS (SELECT 1 FROM _expired_processes ep WHERE ep.regions=DiscountRate.regions           AND ep.tech=DiscountRate.tech           AND ep.vintage=DiscountRate.vintage);
DELETE FROM MaterialIntensity      WHERE EXISTS (SELECT 1 FROM _expired_processes ep WHERE ep.regions=MaterialIntensity.regions      AND ep.tech=MaterialIntensity.tech      AND ep.vintage=MaterialIntensity.vintage);
DELETE FROM TechnologyMaterialSupplyRisk WHERE EXISTS (SELECT 1 FROM _expired_processes ep WHERE ep.regions=TechnologyMaterialSupplyRisk.regions AND ep.tech=TechnologyMaterialSupplyRisk.tech AND ep.vintage=TechnologyMaterialSupplyRisk.vintage);
DELETE FROM CapacityCredit         WHERE EXISTS (SELECT 1 FROM _expired_processes ep WHERE ep.regions=CapacityCredit.regions         AND ep.tech=CapacityCredit.tech         AND ep.vintage=CapacityCredit.vintage);

DROP TABLE _expired_processes;

-- Blocco originale: pulizia periodi intermedi
DELETE FROM "CapacityCredit" WHERE "vintage" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "CapacityCredit" WHERE "periods" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "CapacityFactor" WHERE "vintage" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "CapacityFactorProcess" WHERE "vintage" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "CostFixed" WHERE "vintage" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "CostFixed" WHERE "periods" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "CostInvest" WHERE "vintage" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "CostVariable" WHERE "vintage" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "CostVariable" WHERE "periods" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "CostEmission" WHERE "periods" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "Demand" WHERE "periods" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "DiscountRate" WHERE "vintage" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "Driver" WHERE "periods" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "Efficiency" WHERE "vintage" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "Elasticity" WHERE "periods" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "EmissionActivity" WHERE "vintage" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "EmissionLimit" WHERE "periods" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "EnergyCommodityConcentrationIndex" WHERE "periods" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "LifetimeProcess" WHERE "vintage" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "MaterialIntensity" WHERE "vintage" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "MaxActivity" WHERE "periods" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "MaxActivityGroup" WHERE "periods" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "MaxCapacity" WHERE "periods" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "MaxCapacityGroup" WHERE "periods" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "MaxInputGroup" WHERE "periods" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "MaxOutputGroup" WHERE "periods" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "MinActivity" WHERE "periods" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "MinActivityGroup" WHERE "periods" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "MinCapacity" WHERE "periods" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "MinCapacityGroup" WHERE "periods" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "MinInputGroup" WHERE "periods" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "MinOutputGroup" WHERE "periods" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "TechInputSplit" WHERE "periods" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "TechOutputSplit" WHERE "periods" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "TechnologyMaterialSupplyRisk" WHERE "vintage" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);
DELETE FROM "time_periods" WHERE "t_periods" IN (2007,2008,2009,2012,2014,2016,2018,2022,2025,2035,2045);

COMMIT;
PRAGMA foreign_keys = ON;