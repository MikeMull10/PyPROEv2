from PySide6.QtWidgets import QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QIcon
from handlers.stylesheet import resource_path, ICON_COLORS
from sympy import parse_expr, latex, symbols, sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, sqrt, floor, exp, log, pi, Abs
from numpy import ceil
import re


theme_dict = {
    "white": "#F5F5F5",
    "dark": "#151515",
    "navy": "#051923",
    "crimson": "#890620",
    "raspberry": "#5f0f40",
    "neon": "#151515",
}

color_dict = {
    "white": "black",
    "dark": "#F5F5F5",
    "navy": "white",
    "crimson": "white",
    "raspberry": "white",
}

for color in ICON_COLORS:
    if "Neon" in color:
        color_dict[color.lower()] = ICON_COLORS[color]

def equation_to_latex(equation_str):
    """
    Converts a mathematical equation in string format to LaTeX.
    Automatically detects variables, replaces incorrect operators,
    and ensures proper parsing of functions with consistent multiplication symbols.
    """
    # Replace ^ with ** for exponentiation
    equation_str = equation_str.replace("^", "**")

    # Extract variable names (basic pattern for identifiers)
    variable_names = set(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', equation_str))

    # Define symbolic variables, avoiding function names
    functions = {
        "abs": Abs, "pow": pow, "log": log, "ln": log, "exp": exp,
        "sin": sin, "cos": cos, "tan": tan, "asin": asin, "acos": acos, "atan": atan,
        "sinh": sinh, "cosh": cosh, "tanh": tanh,
        "sqrt": sqrt, "ceil": ceil, "floor": floor,
        "sign": lambda x: x / Abs(x) if x != 0 else 0,  # Custom sign function
        "pi": pi  # Math constant
    }
    symbols_dict = {var: symbols(var) for var in variable_names if var not in functions}

    # Parse the expression
    expr = parse_expr(equation_str, evaluate=False, local_dict={**symbols_dict, **functions})

    # Convert to LaTeX with explicit multiplication symbols
    return str(latex(expr, mul_symbol="\\cdot")).replace("\\cdot", "\\cdot ")

def generate_html(data, main: str = "white", text: str = "black"):
    """
    Generates an HTML page to display LaTeX using MathJax.
    """
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: {main};
            }}
            div {{
                text-align: left;
                border-radius: 8px;
                display: inline-block;
            }}
            .equation-container {{
                text-align: left; /* Align equations to the left */
                border-radius: 8px;
                display: block;
                cursor: pointer;
                width: fit-content; /* Prevents stretching */
            }}
            .katex {{
                color: {text} !important; /* Change equation text color */
                font-size: 18px !important; /* Adjust equation size */
            }}
            .katex-display {{
                display: block !important;
                text-align: left !important; /* Ensure left alignment */
                font-weight: bold;
            }}
        </style>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.2/katex.min.css">
        <script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.2/katex.min.js"></script>
        <script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.2/contrib/auto-render.min.js"
            onload="renderMathInElement(document.body);"></script>
        <script>
            function copyToClipboard(latex, element) {{
                if (navigator.clipboard && navigator.clipboard.writeText) {{
                    navigator.clipboard.writeText(latex).then(() => {{
                        /* showCopiedMessage(element); */
                    }}).catch(err => {{
                        console.error("Clipboard copy failed:", err);
                    }});
                }} else {{
                    // Fallback for older browsers
                    let textarea = document.createElement("textarea");
                    textarea.value = latex;
                    document.body.appendChild(textarea);
                    textarea.select();
                    document.execCommand("copy");
                    document.body.removeChild(textarea);
                    /* showCopiedMessage(element); */
                }}
            }}
        </script>
    </head>
    <body>
        {data}
    </body>
    </html>
    """
    return html_template

class LaTeXViewer(QMainWindow):
    def __init__(self, functions: list = [], equality_constraints: list = [], inequality_constraints: list = [], theme_data: dict = {}):
        super().__init__()
        self.setWindowTitle("LaTeX Equation Viewer")
        self.resize(800, 600)
        self.setWindowIcon(QIcon(resource_path("PyPROE.ico")))

        # Create web view widget
        self.latex_browser = QWebEngineView()
        self.setCentralWidget(self.latex_browser)

        data = ""
        for t, function_type in enumerate([functions, equality_constraints, inequality_constraints]):
            for i, eq in enumerate(function_type):
                latex = equation_to_latex(eq.lower())
                d = f"{['F', 'EC', 'INEC'][t]}{i + 1} = " + latex
                replaced = latex.replace("\\", "\\\\")
                data += f"""
                <div class="equation-container" onclick="copyToClipboard('{replaced}', this)">
                    $$ {d} $$
                </div>
                """

        # Handle Colors
        theme = theme_data.get('theme', 'white')
        color = theme_data.get('color', 'black')

        if theme.lower() != 'neon':
            color = theme
        else:
            color = "Neon " + color.capitalize()

        # Load LaTeX HTML
        html_content = generate_html(data, theme_dict.get(theme.lower(), 'white'), color_dict.get(color.lower(), 'black'))
        self.latex_browser.setHtml(html_content)
