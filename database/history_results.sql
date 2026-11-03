-- Bind :user_id from authenticated backend context.
-- timestamp is scan start in UTC; pending scans have NULL start time.
-- Counts reflect saved data; the importer does not stream partial results.
SELECT sc.scan_id, sc.target, sc.started_at AS timestamp, sc.finished_at,
       CASE sc.status
           WHEN 'pending' THEN 'Pending'
           WHEN 'running' THEN 'In-Progress'
           WHEN 'completed' THEN 'Completed'
           WHEN 'failed' THEN 'Failed'
       END AS status,
       (SELECT COUNT(*) FROM hosts AS h
        WHERE h.scan_id = sc.scan_id) AS devices_found,
       (SELECT COUNT(*) FROM findings AS f
        JOIN services AS s ON s.service_id = f.service_id
        JOIN hosts AS h ON h.host_id = s.host_id
        WHERE h.scan_id = sc.scan_id) AS findings_found
FROM scans AS sc
WHERE sc.user_id = :user_id
ORDER BY sc.scan_id DESC;
