from sqlalchemy import text
from .models import db
from flask import current_app

def fetch_query_results(start_datetime, end_datetime, where_clause):
    """Fetch query results from the qdb1 database based on time and other filters."""
    # Modify the query to include where_clause only if it's not empty
    base_query = """
        SELECT * FROM qdb1
        WHERE UP_TIME BETWEEN :start_datetime AND :end_datetime
    """
    
    # Append the where clause conditionally
    if where_clause:
        base_query += f" AND {where_clause}"

    query = text(base_query)

    # Get the specific engine for the 'qdb1' database
    engine = db.get_engine(bind='qdb1')

    # Execute the query using the 'qdb1' bind
    with engine.connect() as connection:
        result = connection.execute(
            query,
            {'start_datetime': start_datetime, 'end_datetime': end_datetime}
        )

        # Fetch all rows and convert each to a dictionary
        rows = result.fetchall()

        # If there are no results, return an empty list
        if not rows:
            print("No results found")
            return []

        # Extract column names from the first row
        column_names = result.keys()

        # Convert the rows into dictionaries, mapping columns to values
        results = []
        for row in rows:
            row_dict = dict(zip(column_names, row))
            
            # Transform MEDIA column to include full file paths for display
            media_files = row_dict.get("MEDIA")
            if media_files:
                base_path = current_app.config['DOWNLOADED_MEDIA_PATH']
                # Split filenames, prepend full path, and generate HTML-safe data
                media_paths = [
                    f"/media/{filename.strip()}" for filename in media_files.split(",")
                ]
                row_dict["MEDIA"] = media_paths

            results.append(row_dict)

    return results
