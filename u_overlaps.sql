UPDATE
    p_overlaps
SET
    check_date = :check_date,
    decimals = :decimals,
    astenot = :astenot,
    asttom = :asttom,
    pst = :pst
WHERE
    meleti = :meleti
    AND mode = :mode