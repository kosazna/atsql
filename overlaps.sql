SELECT
    check_date,
    precision,
    astenot,
    asttom,
    pst
FROM
    p_overlaps
WHERE
    meleti = :meleti
    AND mode = :mode