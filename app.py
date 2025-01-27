from collections import OrderedDict
from flask import Flask, jsonify, request, render_template
import psycopg
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()  # Loads variables from the .env file

DB_PASSWORD = os.getenv('DB_PASSWORD')

DB_CONNECTION = f"postgresql://doadmin:{DB_PASSWORD}@db-postgresql-nyc3-46509-do-user-18251514-0.g.db.ondigitalocean.com:25060/Quest_Top_Times?sslmode=require"


# Endpoint to render the HTML frontend
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint to get dropdown options
@app.route('/get-dropdown-options', methods=['GET'])
def get_dropdown_options():
    options = {
        "courses": ["SCY", "LCM"],
        "events": OrderedDict({
            "SCY": OrderedDict({
                "50 Free": "50 FR SCY",
                "100 Free": "100 FR SCY",
                "200 Free": "200 FR SCY",
                "500 Free": "500 FR SCY",
                "1000 Free": "1000 FR SCY",
                "1650 Free": "1650 FR SCY",
                "50 Back" : "50 BA SCY",
                "100 Back": "100 BK SCY",
                "200 Back": "200 BK SCY",
                "50 Breast" : "50 BR SCY",
                "100 Breast": "100 BR SCY",
                "200 Breast": "200 BR SCY",
                "50 Fly" : "50 FL SCY",
                "100 Fly": "100 FL SCY",
                "200 Fly": "200 FL SCY",
                "100 IM" : "100 IM SCY",
                "200 IM": "200 IM SCY",
                "400 IM": "400 IM SCY",
                "200 Free Relay": "200 FR-R SCY",
                "400 Free Relay": "400 FR-R SCY",
                "800 Free Relay": "800 FR-R SCY",
                "200 Medley Relay": "200 MED-R SCY",
                "400 Medley Relay": "400 MED-R SCY"
            }),
            "LCM": OrderedDict({
                "50 Free": "50 FR LCM",
                "100 Free": "100 FR LCM",
                "200 Free": "200 FR LCM",
                "500 Free": "500 FR LCM",
                "800 Free": "800 FR LCM",
                "1500 Free": "1500 FR LCM",
                "50 Back" : "50 BA LCM",
                "100 Back": "100 BK LCM",
                "200 Back": "200 BK LCM",
                "50 Breast" : "50 BR LCM",
                "100 Breast": "100 BR LCM",
                "200 Breast": "200 BR LCM",
                "50 Fly" : "50 FL LCM",
                "100 Fly": "100 FL LCM",
                "200 Fly": "200 FL LCM",
                "200 IM": "200 IM LCM",
                "400 IM": "400 IM LCM",
                "200 Free Relay": "200 FR-R LCM",
                "400 Free Relay": "400 FR-R LCM",
                "800 Free Relay": "800 FR-R LCM",
                "200 Medley Relay": "200 MED-R LCM",
                "400 Medley Relay": "400 MED-R LCM"
            })
        }),
        "genders": {
            "Male": "M",
            "Female": "F"
        },
        "Age Groups": {
            "10 & Under": "10 & Under",
            "11-12": "11-12",
            "13-14": "13-14",
            "15-16": "15-16",
            "17-18": "17-18",
            "Open": "Open"
        }
    }
    
    print("Dropdown options JSON:", options)  # Log the JSON in the server console
    return jsonify(options)

# Endpoint to get top results based on selections
@app.route('/get-top-results', methods=['POST'])
def get_top_results():
    try:
        data = request.json
        
        # Debugging: Log received payload
        print("Received payload:", data)

        # Align keys with JSON structure
        course = data.get("course")
        event = data.get("event_code")  # Corresponds to JSON's "Event Code"
        gender = data.get("type_code")  # Corresponds to JSON's "Type Code"
        age_group_desc = data.get("age_group_desc")  # Corresponds to JSON's "Age Group Desc"

        # Validate input
        if not all([course, event, gender, age_group_desc]):
            return jsonify({"error": "Missing required parameters"}), 400

        # Determine the table name
        table_name = "scy_top_times" if course == "SCY" else "lcm_top_times"
        
        if table_name not in ["scy_top_times", "lcm_top_times"]:
            return jsonify({"error": "Invalid table name"}), 400


        # Connect to database
        try:
            conn = psycopg.connect(DB_CONNECTION)
            cur = conn.cursor()
        except psycopg.Error as e:
            return jsonify({"error": f"Database connection error: {e}"}), 500

        # SQL query
        query = f"""
            WITH FilteredResults AS (
                SELECT 
                    top_time AS rank, 
                    CONCAT(last_name, ', ', first_name) AS swimmer_name, 
                    swim_time, 
                    textbox59 AS date
                FROM {table_name}
                WHERE event_code = %s 
                    AND type_code = %s 
                    AND age_group_desc = %s
            )
                SELECT rank, swimmer_name, swim_time, date
                FROM FilteredResults
                WHERE rank <= 10
                ORDER BY rank ASC;
        """


        # Execute query
        cur.execute(query, (event, gender, age_group_desc))
        rows = cur.fetchall()
        conn.close()

        # Handle empty results
        if not rows:
            return jsonify({"message": "No results found for the given selection."})

        # Format results
        results = [
            {"rank": row[0], 
             "name": row[1],
             "swim_time": row[2], 
             "date": row[3].strftime("%Y-%m-%d") if row[3] else None}
            for row in rows
        ]
        return jsonify(results)

    except psycopg.Error as e:
        return jsonify({"error": f"Database query error: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 500

if __name__ == "__main__":
    # Use the PORT environment variable provided by Heroku
    port = int(os.environ.get("PORT", 8080))  # Default to 8080 if $PORT is not set

    # Use Waitress for production if necessary
    try:
        from waitress import serve
        print(f"Starting Waitress server on port {port}...")  # Debugging
        serve(app, host="0.0.0.0", port=port)
    except ImportError:
        # Fallback for local development
        print(f"Starting Flask development server on port {port}...")  # Debugging
        app.run(debug=True, host="0.0.0.0", port=port)
