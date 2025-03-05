from flask import Flask, request, jsonify
from sympy import symbols, Eq, solve
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allows frontend to communicate with backend

def extract_coefficients(equation):
    variables = re.findall(r'[a-zA-Z]+', equation)
    lhs, rhs = equation.replace(" ", "").split("=")
    coefficients = []
    for var in variables:
        match = re.search(rf'([+-]?\d*){var}', lhs)
        if match:
            coefficient = match.group(1)
            coefficient = int(coefficient) if coefficient not in ["", "+", "-"] else (1 if coefficient in ["", "+"] else -1)
        else:
            coefficient = 0
        coefficients.append(coefficient)
    coefficients.append(int(rhs))
    return coefficients, variables

@app.route("/solve", methods=["POST"])
def solve_equations():
    data = request.json
    equations = data.get("equations", [])

    if not equations:
        return jsonify({"error": "No equations provided"}), 400

    variables_set = set()
    parsed_equations = []

    for eq in equations:
        coeffs, vars_found = extract_coefficients(eq)
        parsed_equations.append(coeffs)
        variables_set.update(vars_found)

    variables = sorted(variables_set)  # Sort to maintain order
    symbols_list = symbols(variables)

    sympy_equations = [Eq(sum(c * s for c, s in zip(eq[:-1], symbols_list)), eq[-1]) for eq in parsed_equations]

    solution = solve(sympy_equations, symbols_list)

    return jsonify({str(var): float(solution.get(var, 0)) for var in symbols_list})


if __name__ == "__main__":
    app.run(debug=True)
