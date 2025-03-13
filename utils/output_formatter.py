"""
Output formatter for the CMYK Retro Lo-Fi Solana Vanity Generator
Formats generation results in various styles
"""

import os
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from utils.ascii_art import CMYKColors


def format_address_table(results: List[Dict[str, Any]], color: bool = True) -> str:
    """
    Format a table of vanity addresses
    
    Args:
        results: List of result dictionaries with 'pubkey' and 'path'
        color: Whether to include ANSI color codes
        
    Returns:
        str: Formatted table as string
    """
    if not results:
        return "No addresses found."
    
    # Define colors
    cyan = CMYKColors.BRIGHT_CYAN if color else ""
    magenta = CMYKColors.BRIGHT_MAGENTA if color else ""
    yellow = CMYKColors.BRIGHT_YELLOW if color else ""
    reset = CMYKColors.RESET if color else ""
    
    # Calculate column widths
    address_width = max(len("Address"), max(len(r["pubkey"]) for r in results))
    path_width = max(len("Path"), max(len(r["path"]) for r in results))
    
    # Create header
    header = f"{cyan}{'#':<4} {'Address':<{address_width}} {'Path':<{path_width}}{reset}"
    
    # Create separator
    separator = f"{magenta}{'-' * 4} {'-' * address_width} {'-' * path_width}{reset}"
    
    # Create rows
    rows = []
    for i, result in enumerate(results):
        pubkey = result["pubkey"]
        path = result["path"]
        
        row = f"{yellow}{i+1:<4}{reset} {pubkey:<{address_width}} {path:<{path_width}}"
        rows.append(row)
    
    # Combine all parts
    table = "\n".join([header, separator] + rows)
    
    return table


def format_json_output(results: Dict[str, Any], pretty: bool = True) -> str:
    """
    Format results as JSON
    
    Args:
        results: Results dictionary
        pretty: Whether to pretty-print the JSON
        
    Returns:
        str: JSON string
    """
    if pretty:
        return json.dumps(results, indent=2)
    else:
        return json.dumps(results)


def create_html_report(results: Dict[str, Any], output_path: str) -> str:
    """
    Create an HTML report of generation results
    
    Args:
        results: Results dictionary
        output_path: Path to save the HTML file
        
    Returns:
        str: Path to the generated HTML file
    """
    # Extract results
    addresses = results.get("results", [])
    success = results.get("success", False)
    count = results.get("count", 0)
    
    # Create HTML content
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CMYK Vanity Address Report</title>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            background-color: #282828;
            color: #f0f0f0;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #00FFFF, #FF00FF, #FFFF00);
            background-clip: text;
            -webkit-background-clip: text;
            color: transparent;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
        }}
        h1 {{
            font-size: 2.5em;
            margin: 0;
        }}
        .timestamp {{
            margin-top: 10px;
            font-size: 0.9em;
            color: #aaa;
        }}
        .summary {{
            background-color: #333;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 5px solid #00FFFF;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            table-layout: fixed;
        }}
        th {{
            text-align: left;
            padding: 12px;
            background-color: #222;
            color: #00FFFF;
            border-bottom: 2px solid #00FFFF;
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #444;
            word-break: break-all;
        }}
        tr:nth-child(even) {{
            background-color: #333;
        }}
        tr:hover {{
            background-color: #3a3a3a;
        }}
        .address {{
            font-family: monospace;
            color: #00FFFF;
        }}
        .path {{
            font-size: 0.9em;
            color: #FFFF00;
        }}
        .footer {{
            margin-top: 40px;
            text-align: center;
            font-size: 0.8em;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>CMYK Solana Vanity Addresses</h1>
            <div class="timestamp">Generated on {time.strftime("%Y-%m-%d %H:%M:%S")}</div>
        </header>
        
        <div class="summary">
            <p>Successfully generated {count} vanity address{'' if count == 1 else 'es'}.</p>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th style="width: 5%;">#</th>
                    <th style="width: 45%;">Address</th>
                    <th style="width: 50%;">Path</th>
                </tr>
            </thead>
            <tbody>
"""
    
    # Add table rows
    for i, address in enumerate(addresses):
        html += f"""                <tr>
                    <td>{i+1}</td>
                    <td class="address">{address['pubkey']}</td>
                    <td class="path">{address['path']}</td>
                </tr>
"""
    
    # Finish HTML
    html += """            </tbody>
        </table>
        
        <div class="footer">
            <p>Generated with CMYK Retro Lo-Fi Solana Vanity Generator</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Write HTML to file
    with open(output_path, 'w') as f:
        f.write(html)
    
    return output_path


def format_error(error_message: str, color: bool = True) -> str:
    """
    Format an error message
    
    Args:
        error_message: Error message to format
        color: Whether to include ANSI color codes
        
    Returns:
        str: Formatted error message
    """
    error_color = CMYKColors.BRIGHT_MAGENTA if color else ""
    reset = CMYKColors.RESET if color else ""
    
    return f"{error_color}ERROR: {error_message}{reset}"


def format_success_message(message: str, color: bool = True) -> str:
    """
    Format a success message
    
    Args:
        message: Success message to format
        color: Whether to include ANSI color codes
        
    Returns:
        str: Formatted success message
    """
    success_color = CMYKColors.BRIGHT_CYAN if color else ""
    reset = CMYKColors.RESET if color else ""
    
    return f"{success_color}SUCCESS: {message}{reset}"


def format_address_summary(results: Dict[str, Any], color: bool = True) -> str:
    """
    Format a summary of generated addresses
    
    Args:
        results: Results dictionary
        color: Whether to include ANSI color codes
        
    Returns:
        str: Formatted summary
    """
    # Define colors
    cyan = CMYKColors.BRIGHT_CYAN if color else ""
    magenta = CMYKColors.BRIGHT_MAGENTA if color else ""
    yellow = CMYKColors.BRIGHT_YELLOW if color else ""
    white = CMYKColors.WHITE if color else ""
    reset = CMYKColors.RESET if color else ""
    
    # Extract data
    success = results.get("success", False)
    addresses = results.get("results", [])
    count = len(addresses)
    
    if not success:
        error = results.get("error", "Unknown error")
        return format_error(error, color)
    
    # Create summary
    summary = []
    summary.append(f"{cyan}=== Vanity Address Generation Summary ==={reset}")
    summary.append(f"{white}Total Addresses: {yellow}{count}{reset}")
    
    if count > 0:
        # Show a few examples
        summary.append(f"\n{white}Example Addresses:{reset}")
        for i, addr in enumerate(addresses[:3]):
            summary.append(f"{yellow}{i+1}.{reset} {cyan}{addr['pubkey']}{reset}")
            summary.append(f"   {magenta}Path: {addr['path']}{reset}")
        
        if count > 3:
            summary.append(f"\n{white}... and {count - 3} more{reset}")
    
    return "\n".join(summary)


def export_addresses_to_file(results: Dict[str, Any], format_type: str, output_path: str) -> Tuple[bool, str]:
    """
    Export addresses to file in specified format
    
    Args:
        results: Results dictionary
        format_type: Format type ('json', 'csv', 'html', 'txt')
        output_path: Path to save the file
        
    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        if format_type == 'json':
            # Export as JSON
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
                
        elif format_type == 'csv':
            # Export as CSV
            import csv
            addresses = results.get("results", [])
            
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Index", "Address", "Path"])
                
                for i, addr in enumerate(addresses):
                    writer.writerow([i+1, addr['pubkey'], addr['path']])
                    
        elif format_type == 'html':
            # Create HTML report
            create_html_report(results, output_path)
            
        elif format_type == 'txt':
            # Export as plain text
            addresses = results.get("results", [])
            
            with open(output_path, 'w') as f:
                f.write(f"CMYK Solana Vanity Addresses\n")
                f.write(f"Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                for i, addr in enumerate(addresses):
                    f.write(f"{i+1}. {addr['pubkey']}\n")
                    f.write(f"   Path: {addr['path']}\n\n")
        else:
            return False, f"Unsupported export format: {format_type}"
        
        return True, f"Successfully exported {len(results.get('results', []))} addresses to {output_path}"
        
    except Exception as e:
        return False, f"Error exporting addresses: {str(e)}"


def print_progress(current: int, total: int, prefix: str = "Progress", 
                   suffix: str = "Complete", length: int = 50, color: bool = True) -> None:
    """
    Print a progress bar to the console
    
    Args:
        current: Current progress value
        total: Total progress value
        prefix: Text before the progress bar
        suffix: Text after the progress bar
        length: Length of the progress bar in characters
        color: Whether to include ANSI color codes
    """
    # Define colors
    cyan = CMYKColors.BRIGHT_CYAN if color else ""
    magenta = CMYKColors.BRIGHT_MAGENTA if color else ""
    yellow = CMYKColors.BRIGHT_YELLOW if color else ""
    gray = CMYKColors.GRAY if color else ""
    reset = CMYKColors.RESET if color else ""
    
    # Calculate progress
    percent = int(100 * (current / float(total)))
    filled_length = int(length * current // total)
    
    # Create the bar with CMYK colors
    bar = ""
    for i in range(length):
        if i < filled_length:
            if i % 4 == 0:
                bar += f"{cyan}█{reset}"
            elif i % 4 == 1:
                bar += f"{magenta}█{reset}"
            elif i % 4 == 2:
                bar += f"{yellow}█{reset}"
            else:
                bar += f"{gray}█{reset}"
        else:
            bar += "░"
    
    # Print the progress bar
    print(f"\r{prefix} |{bar}| {percent}% {suffix}", end="", flush=True)
    
    # Print newline when complete
    if current == total:
        print()