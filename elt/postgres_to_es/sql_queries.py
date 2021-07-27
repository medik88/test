PRODUCE_FILMWORKS = (
    "SELECT id FROM movies_filmwork WHERE modified > '%s' ORDER BY modified"
)
PRODUCE_PERSONS = (
    "SELECT id, modified FROM movies_person WHERE modified > '%s' ORDER BY modified"
)
PRODUCE_GENRES = (
    "SELECT id, modified FROM movies_genre WHERE modified > '%s' ORDER BY modified"
)

ENRICH_PERSONS = (
    "SELECT f.id, f.modified AS modified, pf.person_id, f.title, f.imdb_rating, "
    "concat(p.first_name, ' ', p.last_name) AS name, p.modified AS person_modified "
    "FROM movies_filmwork f "
    "JOIN movies_personfilmwork pf on f.id = pf.filmwork_id "
    "JOIN movies_person p on p.id = pf.person_id "
    "WHERE pf.person_id IN (%s) "
    "ORDER BY f.modified"
)
ENRICH_GENRES = (
    "SELECT f.id, f.modified FROM movies_filmwork f "
    "JOIN movies_filmwork_genres fg on f.id = fg.filmwork_id "
    "WHERE fg.genre_id IN (%s) "
    "ORDER BY f.modified"
)

MERGE = (
    "SELECT "
    "pf.filmwork_id, f.title, f.description, f.imdb_rating, f.work_type, f.created, f.modified, pf.profession, "
    "pf.person_id, concat(p.first_name, ' ', p.last_name) AS person_name, p.modified AS person_modified, "
    "fg.genre_id, g.name AS genre_name, g.modified AS genre_modified "
    "FROM movies_filmwork f "
    "LEFT JOIN movies_personfilmwork pf on f.id = pf.filmwork_id "
    "LEFT JOIN movies_person p on p.id = pf.person_id "
    "LEFT JOIN movies_filmwork_genres fg on f.id = fg.filmwork_id "
    "LEFT JOIN movies_genre g on g.id = fg.genre_id "
    "WHERE f.id IN (%s)"
)
