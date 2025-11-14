# Quick Start Guide

## Setup (30 seconds)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your API key:**
   ```bash
   cp .env.example .env
   # Edit .env and add your Anthropic API key
   ```

3. **Run the demo:**
   ```bash
   python demo.py
   ```

## What You'll See

The system will:
1. Generate an initial 7-day meal plan
2. Evaluate it across 5 criteria (inventory, nutrition, practicality, cost, preferences)
3. If score < 85/100, automatically improve the plan
4. Repeat until quality threshold is met (up to 3 iterations)

## Example Output

```
======================================================================
🍽️  AGENTIC MEAL PLANNER - Iterative Self-Evaluation
======================================================================

──────────────────────────────────────────────────────────────────────
Iteration 1/3
──────────────────────────────────────────────────────────────────────
📝 Generating initial meal plan...
📊 Evaluating meal plan...

  📊 Evaluation Results (Iteration 1):
  ──────────────────────────────────────────────────────────────────
  Inventory Optimization.....  78.0/100 (35%) [███████████████     ]
  Nutritional Variety........  72.0/100 (20%) [██████████████      ]
  Practicality...............  85.0/100 (20%) [█████████████████   ]
  Cost Efficiency............  80.0/100 (15%) [████████████████    ]
  Preference Alignment.......  90.0/100 (10%) [██████████████████  ]
  ──────────────────────────────────────────────────────────────────
  OVERALL SCORE..............  79.5/100      [███████████████     ]

⚠️  Score below threshold (79.5 < 85.0)
   Proceeding to iteration 2...
```

## Try Different Scenarios

Run the test suite to see 4 diverse scenarios:
```bash
python test_planner.py
```

Scenarios include:
- **Scenario 1:** Basic family meal planning
- **Scenario 2:** Budget vegetarian planning
- **Scenario 3:** Multiple dietary restrictions
- **Scenario 4:** Nearly empty kitchen

## Customization

### Adjust Quality Threshold

Edit `meal_planner.py`:
```python
QUALITY_THRESHOLD = 90.0  # Raise for stricter quality
MAX_ITERATIONS = 5        # Allow more improvement rounds
```

### Adjust Evaluation Weights

Edit `models.py` in the `EvalScore.calculate_weighted_score()` method:
```python
weights = {
    "inventory_optimization": 0.40,  # Increase inventory priority
    "nutritional_variety": 0.25,
    "practicality": 0.15,
    "cost_efficiency": 0.10,
    "preference_alignment": 0.10,
}
```

## Custom Meal Plans

Create your own script:
```python
from models import MealPlanInput
from meal_planner import MealPlannerAgent

# Define your needs
user_input = MealPlanInput(
    dietary_preferences=["keto", "high-protein"],
    current_inventory=["eggs", "chicken", "broccoli", "cheese"],
    budget=50.0,
    cooking_skill="beginner"
)

# Generate plan
agent = MealPlannerAgent()
plan, evals = agent.plan_meals(user_input)
```

## Troubleshooting

**API Key Error:**
- Ensure `.env` file exists with `ANTHROPIC_API_KEY=your-key`
- Get a key from: https://console.anthropic.com/settings/keys

**Low Scores:**
- Check evaluation feedback for specific issues
- Try relaxing constraints (higher budget, more inventory)
- Adjust `MAX_ITERATIONS` to allow more improvement

**JSON Parsing Error:**
- Usually temporary - retry the request
- Check that your API key is valid

## Project Structure

```
meal-planner/
├── models.py           # Data structures
├── meal_planner.py     # Main agent (iterative evaluation)
├── demo.py            # Simple demo
├── test_planner.py    # 4 test scenarios
├── requirements.txt   # Dependencies
└── README.md          # Full documentation
```

## Next Steps

- Read the full [README.md](README.md) for architecture details
- Explore [test_planner.py](test_planner.py) for usage examples
- Customize evaluation criteria for your needs
- Adjust weights to match your priorities

Happy meal planning! 🍽️
