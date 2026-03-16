from sample_manager.db.connection import get_connection


def create_sample(path, filename, extension, size, hash_val=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO samples (path, filename, extension, size, hash)
        VALUES (?, ?, ?, ?, ?)
        """,
        (path, filename, extension, size, hash_val),
    )

    conn.commit()


def get_sample_by_id(sample_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM samples WHERE id=?", (sample_id,))
    return cursor.fetchone()


def get_all_samples(sort_by="filename", sort_order="ASC"):
    conn = get_connection()
    cursor = conn.cursor()

    # Vulnerable to SQL injection if sort_by/sort_order are from user input unchecked
    # But we will control these from the parser
    allowed_sort_fields = {"filename", "rating", "bpm", "created_at"}
    if sort_by not in allowed_sort_fields:
        sort_by = "filename"
    
    order = "ASC" if sort_order.upper() == "ASC" else "DESC"

    cursor.execute(
        f"""
        SELECT 
            s.*, 
            GROUP_CONCAT(t.name, ', ') as tags,
            r.rating
        FROM samples s
        LEFT JOIN sample_tags st ON s.id = st.sample_id
        LEFT JOIN tags t ON st.tag_id = t.id
        LEFT JOIN ratings r ON s.id = r.sample_id
        GROUP BY s.id
        ORDER BY {sort_by} {order}
        """
    )
    return cursor.fetchall()


def delete_sample(sample_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM samples WHERE id=?", (sample_id,))
    conn.commit()


def get_duplicates_grouped():
    """
    Get groups of samples that share the same hash.
    Only returns hashes that appear more than once.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT hash, COUNT(*) as count
        FROM samples
        WHERE hash IS NOT NULL AND hash != ''
        GROUP BY hash
        HAVING count > 1
        """
    )
    duplicate_hashes = cursor.fetchall()

    groups = []
    for row in duplicate_hashes:
        h = row["hash"]
        cursor.execute(
            """
            SELECT s.*, r.rating, GROUP_CONCAT(t.name, ', ') as tags
            FROM samples s
            LEFT JOIN sample_tags st ON s.id = st.sample_id
            LEFT JOIN tags t ON st.tag_id = t.id
            LEFT JOIN ratings r ON s.id = r.sample_id
            WHERE s.hash = ?
            GROUP BY s.id
            """,
            (h,),
        )
        samples = cursor.fetchall()
        groups.append({"hash": h, "samples": samples})

    return groups


def bulk_create_samples(samples_list):
    conn = get_connection()
    cursor = conn.cursor()
    
    data_to_insert = [
        (s["path"], s["filename"], s["extension"], s["size"], s.get("hash"))
        for s in samples_list
    ]
    
    cursor.executemany(
        """
        INSERT INTO samples (path, filename, extension, size, hash)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(path) DO UPDATE SET
            size = excluded.size,
            filename = excluded.filename,
            hash = excluded.hash
        """,
        data_to_insert
    )
    conn.commit()

def search_samples(filters=None, sort_by="filename", sort_order="ASC"):
    """
    Advanced search with filters:
    - query: text search in filename/extension
    - tag: specific tag name
    - type: extension
    - rating: (operator, value) e.g. ('>', 3)
    """
    conn = get_connection()
    cursor = conn.cursor()

    base_query = """
        SELECT 
            s.*, 
            GROUP_CONCAT(t.name, ', ') as tags,
            r.rating
        FROM samples s
        LEFT JOIN sample_tags st ON s.id = st.sample_id
        LEFT JOIN tags t ON st.tag_id = t.id
        LEFT JOIN ratings r ON s.id = r.sample_id
    """
    
    where_clauses = []
    params = []

    if filters:
        if "query" in filters and filters["query"]:
            where_clauses.append("(s.filename LIKE ? OR s.extension LIKE ?)")
            q = f"%{filters['query']}%"
            params.extend([q, q])
        
        if "tag" in filters and filters["tag"]:
            # We use a subquery or HAVING later to filter by tags
            # For simplicity in this SQL structure, let's use a subquery to find IDs
            where_clauses.append("s.id IN (SELECT sample_id FROM sample_tags st2 JOIN tags t2 ON st2.tag_id = t2.id WHERE t2.name LIKE ?)")
            params.append(f"%{filters['tag']}%")

        if "type" in filters and filters["type"]:
            where_clauses.append("s.extension LIKE ?")
            params.append(f"%{filters['type']}%")

        if "rating" in filters and filters["rating"]:
            op, val = filters["rating"]
            if op in (">", "<", "=", ">=", "<="):
                where_clauses.append(f"r.rating {op} ?")
                params.append(val)

    query_str = base_query
    if where_clauses:
        query_str += " WHERE " + " AND ".join(where_clauses)
    
    query_str += " GROUP BY s.id"

    # Sorting
    allowed_sort_fields = {
        "id": "s.id",
        "filename": "s.filename", 
        "name": "s.filename",
        "tags": "tags",
        "rating": "r.rating", 
        "bpm": "s.bpm", 
        "date": "s.created_at"
    }
    sort_field = allowed_sort_fields.get(sort_by, "s.filename")
    order = "ASC" if sort_order.upper() == "ASC" else "DESC"
    
    query_str += f" ORDER BY {sort_field} {order}"

    cursor.execute(query_str, params)
    return cursor.fetchall()


def get_sample_count():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM samples")
    return cursor.fetchone()[0]
