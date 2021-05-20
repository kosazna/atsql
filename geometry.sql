SELECT
    check_date,
    has_probs,
    ota
FROM
    p_geometry
WHERE
    meleti = :meleti
    AND mode = :mode
    AND shape = :shape