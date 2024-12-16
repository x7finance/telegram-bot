import mysql.connector
import os


def create_db_connection():
    return mysql.connector.connect(
        host = os.getenv("DB_HOST"),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD"),
        database = os.getenv("DB_NAME") ,
        port = os.getenv("DB_PORT")
    )


def close_db_connection(db_connection, cursor):
    cursor.close()
    db_connection.close()


def clicks_check_is_fastest(time_to_check):
    try:
        db_connection = create_db_connection()
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT MIN(time_taken)
            FROM leaderboard
            WHERE time_taken IS NOT NULL
        """)
        fastest_time = cursor.fetchone()[0]
        close_db_connection(db_connection, cursor)

        if isinstance(time_to_check, (int, float)) and isinstance(fastest_time, (int, float)):
            if time_to_check < fastest_time:
                return True
            else:
                return None
        else:
            return None
    except mysql.connector.Error:
        return None
        

def clicks_check_highest_streak():
    db_connection = create_db_connection()
    cursor = db_connection.cursor()

    cursor.execute("""
        SELECT name, streak
        FROM leaderboard
        WHERE streak = (SELECT MAX(streak) FROM leaderboard WHERE streak > 0)
        LIMIT 1
    """)
    user_with_highest_streak = cursor.fetchone()

    close_db_connection(db_connection, cursor)

    return user_with_highest_streak if user_with_highest_streak else None


def clicks_fastest_time():
    try:
        db_connection = create_db_connection()
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT name, MIN(time_taken)
            FROM leaderboard
            WHERE time_taken = (SELECT MIN(time_taken) FROM leaderboard WHERE time_taken IS NOT NULL)
        """)
        fastest_time_taken_data = cursor.fetchone()
        close_db_connection(db_connection, cursor)
        return fastest_time_taken_data if fastest_time_taken_data else ("No user", 0)
    except mysql.connector.Error:
        return ("No user", 0)
    

def clicks_get_by_name(name):
    try:
        db_connection = create_db_connection()
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT clicks, time_taken, streak
            FROM leaderboard
            WHERE name = %s
        """, (name,))
        user_data = cursor.fetchone()
        close_db_connection(db_connection, cursor)
        return user_data if user_data else (0, 0, 0)
    except mysql.connector.Error:
        return (0, 0, 0)


def clicks_get_leaderboard(limit=10):
    try:
        db_connection = create_db_connection()
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT name, clicks
            FROM leaderboard
            ORDER BY clicks DESC
            LIMIT %s
        """, (limit,))
        leaderboard_data = cursor.fetchall()
        leaderboard_text = ""
        for rank, (name, clicks) in enumerate(leaderboard_data, start=1):
            leaderboard_text += f"{rank} {name}: {clicks}\n"
        close_db_connection(db_connection, cursor)
        return leaderboard_text
    except mysql.connector.Error:
        return "Error retrieving leaderboard data"


def clicks_get_total():
    try:
        db_connection = create_db_connection()
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT SUM(clicks)
            FROM leaderboard
        """)
        total_clicks = cursor.fetchone()
        close_db_connection(db_connection, cursor)
        return total_clicks[0] if total_clicks else 0
    except mysql.connector.Error:
        return 0


async def clicks_remove(name):
    db_connection = create_db_connection()
    cursor = db_connection.cursor()

    try:
        cursor.execute("""
            UPDATE leaderboard
            SET clicks = 0, time_taken = NULL, streak = 0
            WHERE name = %s
        """, (name,))

        db_connection.commit()
    except mysql.connector.Error:
        return "Error removing clicks"
    finally:
        close_db_connection(db_connection, cursor)

    return "Clicks removed successfully"


def clicks_reset():
    db_connection = create_db_connection()
    cursor = db_connection.cursor()

    try:
        cursor.execute("DELETE FROM leaderboard")
        db_connection.commit()
    except mysql.connector.Error:
        return "Error resetting clicks"
    finally:
        close_db_connection(db_connection, cursor)

    return "Clicks leaderboard reset successfully"


async def clicks_update(name, time_taken):
    db_connection = create_db_connection()
    cursor = db_connection.cursor()

    cursor.execute("""
        SELECT clicks, time_taken, streak
        FROM leaderboard
        WHERE name = %s
    """, (name,))
    user_data = cursor.fetchone()

    if user_data is None:
        cursor.execute("""
            INSERT INTO leaderboard (name, clicks, time_taken, streak)
            VALUES (%s, 1, %s, 1)
        """, (name, time_taken))
    else:
        clicks, current_time_taken, current_streak = user_data

        if current_time_taken is None or time_taken < current_time_taken:
            new_time = time_taken
        else:
            new_time = current_time_taken

        cursor.execute("""
            UPDATE leaderboard
            SET clicks = %s, time_taken = %s, streak = %s
            WHERE name = %s
        """, (clicks + 1, new_time, current_streak + 1, name))

    cursor.execute("""
            UPDATE leaderboard
            SET streak = 0
            WHERE name <> %s
        """, (name,))
        
    db_connection.commit()
    close_db_connection(db_connection, cursor)


def settings_set(setting_name: str, value: bool):
    try:
        db_connection = create_db_connection()
        cursor = db_connection.cursor()

        cursor.execute("""
            UPDATE settings SET value = %s WHERE setting_name = %s
        """, (1 if value else 0, setting_name))
        
        db_connection.commit()
    except mysql.connector.Error as e:
        return f"Error updating {setting_name}: {e}"
    finally:
        cursor.close()
        db_connection.close()


def settings_get(setting_name: str) -> bool:
    try:
        db_connection = create_db_connection()
        cursor = db_connection.cursor()

        cursor.execute("""
            SELECT value FROM settings WHERE setting_name = %s
        """, (setting_name,))
        
        result = cursor.fetchone()
        cursor.close()
        db_connection.close()

        return result[0] == 1 if result else False
    except mysql.connector.Error as e:
        return False
    

def settings_get_all():
    try:
        db_connection = create_db_connection()
        cursor = db_connection.cursor()

        cursor.execute("SELECT setting_name, value FROM settings")
        results = cursor.fetchall()

        cursor.close()
        db_connection.close()

        return {setting: value == 1 for setting, value in results}
    except mysql.connector.Error as e:
        return {}


def wallet_add(user_id, wallet, private_key):
    db_connection = None
    cursor = None
    try:
        db_connection = create_db_connection()
        cursor = db_connection.cursor()
        
        check_user_query = "SELECT 1 FROM wallets WHERE user_id = %s"
        cursor.execute(check_user_query, (user_id,))
        user_exists = cursor.fetchone()
        
        if user_exists:
            return "Error: You already have a wallet registered, use /me in private to view it"
        
        wallet_add_query = """
        INSERT INTO wallets (user_id, wallet, private_key)
        VALUES (%s, %s, %s)
        """
        cursor.execute(wallet_add_query, (user_id, wallet, private_key))

        db_connection.commit()
        close_db_connection(db_connection, cursor)

        return "Wallet added successfully"
    
    except mysql.connector.Error as err:
        return(f"Error: {err}")


def wallet_count():
    try:
        db_connection = create_db_connection()
        cursor = db_connection.cursor()

        get_count_query = """
        SELECT COUNT(DISTINCT user_id) AS total_count
        FROM wallets
        """
        cursor.execute(get_count_query)

        total_count = cursor.fetchone()[0]

        close_db_connection(db_connection, cursor)

        return total_count

    except mysql.connector.Error:
        return "N/A"  


def wallet_get(user_id):
    db_connection = None
    cursor = None
    try:
        db_connection = create_db_connection()
        cursor = db_connection.cursor()

        get_wallet_query = """
        SELECT wallet, private_key
        FROM wallets
        WHERE user_id = %s
        """
        cursor.execute(get_wallet_query, (user_id,))
        
        result = cursor.fetchone()
        close_db_connection(db_connection, cursor)

        if result:
            wallet, private_key = result
            return {"user_id": user_id, "wallet": wallet, "private_key": private_key}
        else:
            return None

    except mysql.connector.Error:
        return None
    

def wallet_remove(user_id):
    db_connection = None
    cursor = None
    try:
        db_connection = create_db_connection()
        cursor = db_connection.cursor()
        
        wallet_remove_query = """
        DELETE FROM wallets
        WHERE user_id = %s
        """
        cursor.execute(wallet_remove_query, (user_id,))
        db_connection.commit()
        close_db_connection(db_connection, cursor)
        
        if cursor.rowcount > 0:
            return (f"Wallet entry for user ID {user_id} removed.")
        else:
            return (f"No wallet entry found for user ID {user_id}")
    
    except mysql.connector.Error as err:
        return (f"Error: {err}")