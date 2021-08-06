SELECT
    *
FROM
    DATA
WHERE
    DATA.ID IN (
        SELECT
            LAST(DATA.ID)
        FROM
            (
                SELECT
                    *
                FROM
                    DATA
                WHERE
                    DATA.BUILDING_ID IN (
                        SELECT
                            DISTINCT DATA.BUILDING_ID
                        FROM
                            DATA
                        WHERE
                            (((DATA.ORIGINATOR) = "EBU"))
                    )
                ORDER BY
                    DATA.BUILDING_ID,
                    DATA.ID
            )
        GROUP BY
            DATA.BUILDING_ID
    )