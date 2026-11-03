-- Findings tab: backend must authorize :scan_id.
-- Findings must be supplied by a separate security-checking component.
SELECT f.finding_id, f.severity,
       COALESCE(f.title, 'Untitled finding') AS finding,
       h.ip_address AS host, s.port, s.protocol,
       s.service_name AS service, f.description
FROM findings AS f
JOIN services AS s ON s.service_id = f.service_id
JOIN hosts AS h ON h.host_id = s.host_id
WHERE h.scan_id = :scan_id
ORDER BY CASE f.severity
    WHEN 'critical' THEN 1 WHEN 'high' THEN 2
    WHEN 'medium' THEN 3 WHEN 'low' THEN 4 WHEN 'info' THEN 5
END, h.ip_address, s.port;
