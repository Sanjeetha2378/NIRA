import sqlite3


def create_database():

    conn = sqlite3.connect("nira.db")
    cursor = conn.cursor()

    # Create table if it does not already exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risk_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            rainfall REAL,
            water_level REAL,
            drainage TEXT,
            risk_score INTEGER,
            risk_level TEXT
        )
    """)

    # Check whether location column already exists
    cursor.execute("PRAGMA table_info(risk_analysis)")
    columns = [column[1] for column in cursor.fetchall()]

    # Add location column to old database
    if "location" not in columns:
        cursor.execute("""
            ALTER TABLE risk_analysis
            ADD COLUMN location TEXT
        """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_database()
    print("NIRA database created successfully!")
    