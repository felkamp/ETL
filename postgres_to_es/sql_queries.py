def get_movies_query() -> str:
    return """
        with persons as (
            select film_work_id
                 , jsonb_agg(to_jsonb(p) - 'created_at' - 'updated_at') filter ( where role = 'actor')        actors
                 , jsonb_agg(to_jsonb(p) - 'created_at' - 'updated_at') filter ( where role = 'producer')     directors
                 , jsonb_agg(to_jsonb(p) - 'created_at' - 'updated_at') filter ( where role = 'screenwriter') writers
                 , greatest(max(pfw.updated_at), max(p.updated_at))             persons_updated_at
            from person_film_work pfw
                     join person p on pfw.person_id = p.id
            group by film_work_id
        ),
             genres as (
                 select film_work_id
                      , jsonb_agg(to_jsonb(g) - 'created_at' - 'updated_at' - 'description')  genres
                      , greatest(max(fwg.updated_at), max(g.updated_at)) genres_updated_at
                 from genre_film_work fwg
                          join genre g on fwg.genre_id = g.id
                 group by film_work_id
             ),
             res as (
                 select id
                      , title
                      , description
                      , rating
                      , g.genres
                      , p.actors
                      , p.directors
                      , p.writers
                      , greatest(fw.updated_at, p.persons_updated_at, g.genres_updated_at) as update_time
                 from film_work fw
                          left join persons p on p.film_work_id = fw.id
                          left join genres g on g.film_work_id = fw.id
             )
        select *
        from res
        where update_time >= %s
        order by update_time
            fetch first %s rows only
    """
