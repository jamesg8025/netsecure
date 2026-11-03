-- Devices tab: backend must authorize :scan_id for the signed-in user.
-- One row per service. A device with no services still appears.
SELECT h.host_id, h.ip_address, h.hostname,
       s.service_id, s.port, s.protocol,
       s.service_name AS service, s.product, s.version
FROM hosts AS h
LEFT JOIN services AS s ON s.host_id = h.host_id
WHERE h.scan_id = :scan_id
ORDER BY h.ip_address, s.port, s.protocol;
