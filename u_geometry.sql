UPDATE
    p_geometry
SET
    check_date = :check_date,
    has_probs = :has_probs,
    ota = :ota
WHERE
    meleti = :meleti
    AND mode = :mode
    AND shape = :shape