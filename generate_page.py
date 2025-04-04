import os
import requests
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from dotenv import load_dotenv  # For local .env loading

load_dotenv()  # Load variables from .env file if it exists

# --- Configuration ---
API_KEY = os.environ.get('FINANCIAL_API_KEY')
if not API_KEY:
    print("Error: FINANCIAL_API_KEY environment variable not set.")
    exit(1)

# Example using Finnhub - adapt URL and parsing for your chosen API
FINANCIAL_API_BASE_URL = 'https://finnhub.io/api/v1'
# We ONLY need the index symbol now
INDEX_SYMBOL = 'SPY'  # S&P 500 ETF often used as proxy
HTML_TEMPLATE_FILE = 'template.html'
OUTPUT_HTML_FILE = 'index.html'  # Output path - adjust if needed
# Define path to the directory containing the script and template
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = SCRIPT_DIR  # Assuming template is in the same directory


def get_market_data():
    """Fetches S&P 500 index data and determines market status + arrow."""
    print(f"[{datetime.now()}] Fetching market data for index: {INDEX_SYMBOL}...")
    overall_index_change = 0
    current_price = None
    error_msg = None
    status_text = 'MAYBE?'  # Default status
    status_class = 'maybe'
    subtitle = 'Checking the market pulse...'
    arrow_character = ''  # Initialize arrow character

    session = requests.Session()

    try:
        # --- Fetch Overall Index (e.g., SPY) ---
        print(f"Fetching quote for index: {INDEX_SYMBOL}")
        quote_url = f"{FINANCIAL_API_BASE_URL}/quote?symbol={INDEX_SYMBOL}&token={API_KEY}"
        response = session.get(quote_url, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        index_data = response.json()

        # dp = Daily percent change, c = current price
        overall_index_change = index_data.get('dp')
        current_price = index_data.get('c')

        if overall_index_change is None:
            print(f"Warning: Could not get daily percentage change ('dp') for {INDEX_SYMBOL}. Treating as flat.")
            overall_index_change = 0  # Treat as flat if data is missing
            error_msg = f"Could not retrieve percent change for {INDEX_SYMBOL}."  # Inform user

        print(f"Data fetch complete: Index Change={overall_index_change:.2f}%")

        # --- Determine Status based ONLY on index change ---
        if overall_index_change <= -10:  # Crash threshold
            status_text = 'YES!';
            status_class = 'yes';
            subtitle = f'S&P 500 down {overall_index_change:.2f}%. Deep breaths.'
            arrow_character = '▼'  # Down arrow
        elif overall_index_change <= -5:  # Significant drop
            status_text = 'BLEEDING';
            status_class = 'bleeding';
            subtitle = f'S&P 500 down {overall_index_change:.2f}%. Minor dip.'
            arrow_character = '▼'  # Down arrow
        elif overall_index_change < -2:  # Mildly down
            status_text = 'WOBBLY';
            status_class = 'wobbly';
            subtitle = f'S&P 500 down {overall_index_change:.2f}%. Looking shaky.'
            arrow_character = '▼'  # Down arrow
        elif overall_index_change > 2:  # Significant rise
            status_text = 'NOT YET!';
            status_class = 'no';
            subtitle = f'S&P 500 up {overall_index_change:.2f}%. Still climbing!'
            arrow_character = '▲'  # Up arrow
        elif overall_index_change > 0.2:  # Mildly up
            status_text = 'CLIMBING';
            status_class = 'climbing';
            subtitle = f'S&P 500 up {overall_index_change:.2f}%. Gentle rise.'
            arrow_character = '▲'  # Up arrow
        else:  # Flat-ish
            status_text = 'FLAT';
            status_class = 'sideways';
            subtitle = f'S&P 500 change: {overall_index_change:.2f}%. Holding steady...'
            arrow_character = '▬'  # Flat bar/rectangle

    except requests.exceptions.Timeout:
        error_msg = "API request timed out."
        print(f"Error: {error_msg}")
        status_text = 'ERROR';
        status_class = 'error';
        subtitle = 'Could not fetch market data.';
        arrow_character = '?'  # Error indicator
    except requests.exceptions.HTTPError as http_err:
        try:
            err_details = http_err.response.json()
            error_msg = f"API HTTP error: {http_err} - {err_details}"
        except:
            error_msg = f"API HTTP error occurred: {http_err}"
        print(f"Error: {error_msg}")
        status_text = 'ERROR';
        status_class = 'error';
        subtitle = 'Could not fetch market data.';
        arrow_character = '?'
    except requests.exceptions.RequestException as req_err:
        error_msg = f"API Request error occurred: {req_err}"
        print(f"Error: {error_msg}")
        status_text = 'ERROR';
        status_class = 'error';
        subtitle = 'Could not fetch market data.';
        arrow_character = '?'
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(f"Error: {error_msg}")
        status_text = 'ERROR';
        status_class = 'error';
        subtitle = 'Could not determine market status.';
        arrow_character = '?'

    # Get the visual humor embed code
    giphy_embed_code = get_visual_humor_embed(status_class)  # Changed function call

    # --- Modify the return dictionary ---
    # REMOVED image_url and image_alt_text
    # ADDED giphy_embed_code
    return {
        "status_text": status_text,
        "status_class": status_class,
        "status_arrow": arrow_character,
        "subtitle": subtitle,
        "giphy_embed_code": giphy_embed_code,  # Pass the embed code string
        "index_change_percent": f"{overall_index_change:.2f}%" if overall_index_change is not None else "N/A",
        "index_current_price": f"{current_price:.2f}" if current_price is not None else "N/A",
        "index_symbol": INDEX_SYMBOL,
        "generation_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z'),
        "error_message": error_msg
    }


def get_visual_humor_embed(status_class):
    """Selects a Giphy Embed Code string based on status."""

    # --- USER ACTION REQUIRED ---
    # Paste the FULL Giphy Embed codes you copied below, replacing these examples.
    # Make sure to use triple quotes """<iframe...></iframe>""" for multi-line strings.
    embed_map = {
        'yes': """
            <div style="width:100%;height:0;padding-bottom:56%;position:relative;"><iframe src="https://giphy.com/embed/1rNWZu4QQqCUaq434T" width="100%" height="100%" style="position:absolute" frameBorder="0" class="giphy-embed" allowFullScreen></iframe></div><p><a href="https://giphy.com/gifs/this-is-fine-dumpster-fire-floating-1rNWZu4QQqCUaq434T">via GIPHY</a></p>
            """,  # Example: Dumpster fire
        'wobbly': """
            <div style="width:100%;height:0;padding-bottom:100%;position:relative;"><iframe src="https://giphy.com/embed/NTur7XlVDUdqM" width="100%" height="100%" style="position:absolute" frameBorder="0" class="giphy-embed" allowFullScreen></iframe></div><p><a href="https://giphy.com/gifs/this-is-fine-dog-ntur7xldudqm">via GIPHY</a></p>
            """,  # Example: This is fine dog
        'bleeding': """
            <div style="width:100%;height:0;padding-bottom:50%;position:relative;"><iframe src="https://giphy.com/embed/3IMr40UId6417vSWZ6" width="100%" height="100%" style="position:absolute" frameBorder="0" class="giphy-embed" allowFullScreen></iframe></div><p><a href="https://giphy.com/gifs/a24-lamb-3IMr40UId6417vSWZ6">via GIPHY</a></p>
            """,  # Example: Sweating nervous
        'no': """
            <div style="width:100%;height:0;padding-bottom:100%;position:relative;"><iframe src="https://giphy.com/embed/d8SRR4aDUINuU" width="100%" height="100%" style="position:absolute" frameBorder="0" class="giphy-embed" allowFullScreen></iframe></div><p><a href="https://giphy.com/gifs/nooooo-d8SRR4aDUINuU">via GIPHY</a></p>
            """,  # Example: Stonks Up
        'climbing': """
            <div style="width:100%;height:0;padding-bottom:75%;position:relative;"><iframe src="https://giphy.com/embed/NEvPzZ8bd1V4Y" width="100%" height="100%" style="position:absolute" frameBorder="0" class="giphy-embed" allowFullScreen></iframe></div><p><a href="https://giphy.com/gifs/reactionseditor-yes-nice-nevpzz8bd1v4y">via GIPHY</a></p>
            """,  # Example: Nice / Thumbs up
        'sideways': """
            <div style="width:100%;height:0;padding-bottom:56%;position:relative;"><iframe src="https://giphy.com/embed/l1J3VHwlmsc9vsmju" width="100%" height="100%" style="position:absolute" frameBorder="0" class="giphy-embed" allowFullScreen></iframe></div><p><a href="https://giphy.com/gifs/masterchef-fox-season-8-l1J3VHwlmsc9vsmju">via GIPHY</a></p>
            """,  # Example: Shrug / Confused / Whatever
        'error': """
            <div style="width:100%;height:0;padding-bottom:56%;position:relative;"><iframe src="https://giphy.com/embed/JliGmPEIgzGLe" width="100%" height="100%" style="position:absolute" frameBorder="0" class="giphy-embed" allowFullScreen></iframe></div><p><a href="https://giphy.com/gifs/computer-computers-problems-JliGmPEIgzGLe">via GIPHY</a></p>
            """  # Example: Computer says no
        # Add entries for 'maybe' or any other status_class you use if needed
    }

    # Get the embed code string based on the calculated class
    # Provide a default fallback if a specific status isn't mapped
    default_embed = """
        <div style="width:100%;height:0;padding-bottom:100%;position:relative;"><iframe src="https://giphy.com/embed/l0HlHFRbmaZtBRhXG" width="100%" height="100%" style="position:absolute" frameBorder="0" class="giphy-embed" allowFullScreen></iframe></div><p><a href="https://giphy.com/gifs/reactionseditor-shrug-l0hlhfrbmaztbrhxg">via GIPHY</a></p>
        """  # Example: Shrug as default
    return embed_map.get(status_class, default_embed)


def generate_html(data):
    """Renders the HTML template with the provided data."""
    print("Generating HTML file...")
    try:
        # Set up Jinja2 environment
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)
        template = env.get_template(HTML_TEMPLATE_FILE)

        # Render the template
        output_content = template.render(data)

        # Write the output file
        output_path = os.path.join(SCRIPT_DIR, OUTPUT_HTML_FILE)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_content)
        print(f"Successfully generated {output_path}")
        return True
    except Exception as e:
        print(f"Error generating HTML: {e}")
        return False


# --- Main Execution ---
if __name__ == "__main__":
    # Ensure necessary libraries are installed
    try:
        import requests
        from jinja2 import Environment, FileSystemLoader
        from dotenv import load_dotenv
    except ImportError as e:
        print(f"Error: Missing required library - {e}. Please run 'pip install requests Jinja2 python-dotenv'")
        exit(1)

    market_data = get_market_data()
    generate_html(market_data)
    print(f"[{datetime.now()}] Script finished.")
