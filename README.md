# Python AI Chapter 10: Function Calling Agent

This project is a small Python example that demonstrates a function-calling AI agent built with Semantic Kernel and a local Ollama model. The agent can answer shopping-related questions by calling tools that look up product prices, stock levels, and total costs.

## What this project does

The app exposes a `Shop` plugin with two tools:

- `get_product(product_name)`
  - Returns the price and stock for a product.
- `calculate_total(product_name, quantity)`
  - Calculates the total cost for a quantity of a product.

The agent is intentionally limited to a sample catalog:

- Laptop
- Monitor
- Keyboard

The model is instructed to use the tools for product facts and never invent product information.

## Project files

- `main.py` — CLI chat loop and Semantic Kernel setup
- `requirements.txt` — Python dependencies
- `Chapter10_FunctionCallingAgent.py` — likely a supporting project file for the chapter example
- `Chapter10_FunctionCallingAgent.pyproj` / `Chapter10_FunctionCallingAgent.slnx` — Visual Studio project metadata

## Requirements

- Python 3.10+
- Ollama installed and running locally
- A model available via Ollama, configured in `main.py` as:

```python
MODEL = "qwen3.5:9b"
OLLAMA_URL = "http://localhost:11434/v1"
```

If your local model name differs, update the `MODEL` constant in `main.py` before running.

## Setup

1. Create and activate a virtual environment (optional but recommended):

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
.venv\Scripts\activate     # Windows
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start Ollama and ensure the model is available:

```bash
ollama pull qwen3.5:9b
```

4. Run the app:

```bash
python main.py
```

## Example interaction

```text
You: What is the price of a laptop?
Assistant: Laptop: RM3,500.00; stock: 15 units

You: How much is 2 monitors?
Assistant: 2 x Monitor = RM1,700.00
```

## Notes

- The app validates quantities and stock availability.
- Product answers are grounded in the built-in `ShopTools.PRODUCTS` catalog.
- The agent is designed as a simple educational example for function-calling patterns in Python.

## License

This repository does not currently include an explicit license file. Check the repository settings or upstream source for licensing terms before reusing the code in production or public projects.

## Summary

This is a compact example of an AI function-calling workflow where the model decides whether to call a Python tool to answer a question, instead of guessing from memory.
