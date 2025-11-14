# 🍽️ Agentic Meal Planner

An intelligent meal planning system powered by Claude that uses **iterative self-evaluation** to generate optimized 7-day meal plans.

## 🎯 Key Features

- **Single Agent Architecture**: One agent that generates, evaluates, and improves plans iteratively
- **Inventory Optimization**: Primary goal of 80%+ usage of existing ingredients
- **Multi-Criteria Evaluation**: Weighted scoring across 5 dimensions:
  - Inventory Optimization (35% weight)
  - Nutritional Variety (20% weight)
  - Practicality (20% weight)
  - Cost Efficiency (15% weight)
  - Preference Alignment (10% weight)
- **Iterative Improvement**: Agent critiques its own work and makes targeted improvements
- **Quality Threshold**: Continues improving until score ≥ 85/100 or max iterations reached

## 🏗️ Architecture

The system follows a **draft → critique → revise** workflow:

1. **Generate**: Create initial meal plan optimized for inventory usage
2. **Evaluate**: Score the plan across 5 weighted criteria
3. **Improve**: If score < threshold, identify issues and regenerate
4. **Validate**: Ensure new plan is better, repeat until threshold met

This single-agent approach is simpler and more efficient than multi-agent systems for iterative refinement tasks.

## 📋 Requirements

- Python 3.8+
- Anthropic API key
- Dependencies: see `requirements.txt`

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Key

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=your-actual-api-key-here
```

### 3. Run Test Scenarios

```bash
python test_planner.py
```

The test script includes 4 diverse scenarios:
- Basic family meal planning
- Budget vegetarian
- Multiple dietary restrictions
- Nearly empty kitchen

## 💡 Usage

### Basic Example

```python
from models import MealPlanInput
from meal_planner import MealPlannerAgent, format_meal_plan_output

# Define your requirements
user_input = MealPlanInput(
    dietary_preferences=["balanced", "family-friendly"],
    current_inventory=[
        "chicken breast", "rice", "pasta", "onions",
        "garlic", "canned tomatoes", "eggs", "cheese"
    ],
    scheduled_dinners={
        "Friday": "Pizza night"
    },
    dietary_restrictions=[],
    budget=60.0,
    cooking_skill="intermediate"
)

# Generate optimized meal plan
agent = MealPlannerAgent()
final_plan, evaluations = agent.plan_meals(user_input, verbose=True)

# Display the plan
print(format_meal_plan_output(final_plan))
```

### Customizing Parameters

You can adjust the system's behavior in `meal_planner.py`:

```python
class MealPlannerAgent:
    QUALITY_THRESHOLD = 85.0  # Adjust quality target (0-100)
    MAX_ITERATIONS = 3        # Adjust max improvement rounds
```

You can also customize evaluation weights in `models.py`:

```python
weights = {
    "inventory_optimization": 0.35,  # Adjust these weights
    "nutritional_variety": 0.20,
    "practicality": 0.20,
    "cost_efficiency": 0.15,
    "preference_alignment": 0.10,
}
```

## 📊 Output Format

The system provides:

- **7-Day Meal Plan**: Complete dinners for Monday-Sunday
  - Meal names and descriptions
  - Ingredients (marked as "owned" vs "needed")
  - Prep times and instructions
  - Cost estimates per meal

- **Shopping List**: Organized by category (Produce, Proteins, Pantry, Dairy)

- **Metrics**:
  - Inventory usage percentage
  - Variety score
  - Total estimated cost

- **Iteration Progress**: Shows score improvements across iterations

## 🎓 Design Philosophy

### Why Single Agent?

Unlike multi-agent systems with separate specialized agents, this system uses **one intelligent agent that self-critiques**:

- **Simpler**: Easier to understand and maintain
- **More Efficient**: No coordination overhead between agents
- **Better for Iteration**: Natural fit for refinement loops
- **Human-Like**: Mirrors how humans actually plan (draft, review, revise)

### Evaluation Criteria Weights

The weights reflect real-world priorities:

1. **Inventory Optimization (35%)**: Reduces waste and saves money
2. **Nutritional Variety (20%)**: Ensures balanced diet
3. **Practicality (20%)**: Must be realistic for user's skill/schedule
4. **Cost Efficiency (15%)**: Stay within budget
5. **Preference Alignment (10%)**: Nice-to-have, but less critical than other factors

## 📁 Project Structure

```
meal-planner/
├── models.py              # Data structures (MealPlanInput, MealPlan, EvalScore)
├── meal_planner.py        # Main agent implementation
├── test_planner.py        # Test scenarios
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variable template
└── README.md             # This file
```

## 🔧 Advanced Usage

### Custom Evaluation Logic

Modify the evaluation prompt in `meal_planner.py` → `evaluate_meal_plan()` to add custom criteria or change scoring logic.

### Different Models

Change the model in `meal_planner.py`:

```python
MODEL = "claude-sonnet-4-20250514"  # or other Claude models
```

### Verbose Output Control

Disable progress output:

```python
final_plan, evaluations = agent.plan_meals(user_input, verbose=False)
```

## 🐛 Troubleshooting

### API Key Issues

If you see "ANTHROPIC_API_KEY environment variable not set":

1. Ensure `.env` file exists in the project root
2. Check that it contains `ANTHROPIC_API_KEY=your-key`
3. Try running: `source .env` (Linux/Mac) or restart your terminal

### JSON Parsing Errors

The agent uses regex to extract JSON from Claude's responses. If you encounter parsing errors:

1. Check that Claude's response contains valid JSON
2. Verify the response format matches expected structure
3. Adjust `_extract_json()` method if needed

### Low Scores

If the agent consistently scores below threshold:

1. Review the evaluation feedback to understand issues
2. Check if user requirements are too constrained
3. Adjust weights or threshold as needed
4. Consider increasing `MAX_ITERATIONS`

## 📝 Example Output

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

──────────────────────────────────────────────────────────────────────
Iteration 2/3
──────────────────────────────────────────────────────────────────────
🔄 Generating improved plan...
📊 Evaluating meal plan...

  📊 Evaluation Results (Iteration 2):
  ──────────────────────────────────────────────────────────────────
  Inventory Optimization.....  88.0/100 (35%) [█████████████████   ]
  Nutritional Variety........  82.0/100 (20%) [████████████████    ]
  Practicality...............  87.0/100 (20%) [█████████████████   ]
  Cost Efficiency............  85.0/100 (15%) [█████████████████   ]
  Preference Alignment.......  92.0/100 (10%) [██████████████████  ]
  ──────────────────────────────────────────────────────────────────
  OVERALL SCORE..............  86.2/100      [█████████████████   ]

✅ Quality threshold met! (86.2 >= 85.0)
   Final plan achieved after 2 iteration(s).

======================================================================
✨ Meal planning complete!
======================================================================
```

## 📄 License

MIT License - feel free to use and modify for your needs.

## 🙏 Acknowledgments

Built with [Anthropic's Claude API](https://www.anthropic.com/api) and the Claude Agent SDK.
