import sqlite3

class DatabaseHandler:
    """
    A class for handling SQLite database operations.
    """
    def __init__(self, db_path: str = "alienvault.db"):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """
        Establish a connection to the SQLite database and create tables if necessary.
        Returns:
            A sqlite3.Connection object.
        """
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()
        return self.conn

    def create_tables(self):
        """
        Create the pulses table if it does not exist.
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pulses (
                id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                author_name TEXT,
                created TIMESTAMP,
                modified TIMESTAMP,
                tlp TEXT,
                attack_vector TEXT,  -- AI-Generated Attack Vector
                mitre_ttps TEXT,      -- AI-Generated MITRE ATT&CK TTPs
                cves TEXT             -- AI-Generated CVEs
            )
        ''')
        self.conn.commit()

    def insert_or_update_pulse(self, pulse: dict):
        """
        Insert or update a pulse record based on modified timestamp.
        Args:
            pulse: A dictionary containing pulse information.
        """
        cursor = self.conn.cursor()

        # Check if pulse exists and its last modified timestamp
        cursor.execute("SELECT modified FROM pulses WHERE id = ?", (pulse.get("id"),))
        existing = cursor.fetchone()

        if existing and existing[0] == pulse.get("modified"):
            return  # No update needed if nothing has changed

        # Insert or update the pulse
        cursor.execute('''
            INSERT OR REPLACE INTO pulses (id, name, description, author_name, created, modified, tlp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            pulse.get("id"),
            pulse.get("name"),
            pulse.get("description"),
            pulse.get("author", {}).get("name"),
            pulse.get("created"),
            pulse.get("modified"),
            pulse.get("tlp", "white")
        ))
        self.conn.commit()

    def update_pulse_with_analysis(self, pulse_id, attack_vector, mitre_ttps, cves):
        """
        Updates a pulse with AI-generated threat classification.
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE pulses 
            SET attack_vector = ?, mitre_ttps = ?, cves = ?
            WHERE id = ?
        ''', (attack_vector, mitre_ttps, cves, pulse_id))
        self.conn.commit()

    def fetch_all_pulses(self):
        """
        Retrieve all pulses stored in the database.
        Returns:
            A list of pulse records.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM pulses")
        return cursor.fetchall()

    def fetch_recent_pulses(self, limit=5):
        """
        Retrieve the most recent cyber threats from the database.
        Args:
            limit (int): Number of recent threats to fetch.
        Returns:
            A list of recent pulse records.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM pulses ORDER BY created DESC LIMIT ?", (limit,))
        return cursor.fetchall()

    def search_pulses(self, keyword):
        """
        Search for pulses related to a specific keyword in name or description.
        Args:
            keyword (str): The search term to filter threats.
        Returns:
            A list of matching pulse records.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM pulses WHERE name LIKE ? OR description LIKE ?",
            (f"%{keyword}%", f"%{keyword}%")
        )
        return cursor.fetchall()
