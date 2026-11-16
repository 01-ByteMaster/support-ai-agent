

from sqlalchemy import text
from app.database import engine

def main():
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT
                    current_database(),
                    current_user,
                    version()
            """)
        )

        database, user, version = result.fetchone()

        print("SUPABASE CONNECTION SUCCESSFUL")
        print("Database:", database)
        print("User:", user)
        print("PostgreSQL:", version)

        vector = connection.execute(
            text("""
                SELECT extname
                FROM pg_extension
                WHERE extname = 'vector'
            """)
        ).fetchone()

        print("pgvector enabled:", vector is not None)

    engine.dispose()


if __name__ == "__main__":
    main()
