"""
Test script for the Agentic Meal Planner.

Demonstrates the system with various scenarios showing:
- Iterative improvement
- Inventory optimization
- Constraint handling
- Multi-criteria evaluation
"""
import os
import json
from dotenv import load_dotenv
from models import MealPlanInput
from meal_planner import MealPlannerAgent, format_meal_plan_output


def test_scenario_1_basic():
    """Scenario 1: Basic meal planning with good inventory."""
    print("\n" + "🔵" * 35)
    print("SCENARIO 1: Basic Family Meal Planning")
    print("🔵" * 35)
    print("\nA family with a well-stocked pantry wants a healthy, varied week.")
    print("Budget is moderate, cooking skill is intermediate.\n")

    user_input = MealPlanInput(
        dietary_preferences=["balanced", "family-friendly"],
        current_inventory=[
            "chicken breast",
            "ground beef",
            "rice",
            "pasta",
            "canned tomatoes",
            "onions",
            "garlic",
            "olive oil",
            "chicken broth",
            "eggs",
            "milk",
            "cheese",
            "potatoes",
            "carrots",
            "bell peppers",
            "frozen peas",
        ],
        scheduled_dinners={
            "Friday": "Pizza night (family tradition)"
        },
        dietary_restrictions=[],
        budget=60.0,
        cooking_skill="intermediate",
    )

    agent = MealPlannerAgent()
    final_plan, evaluations = agent.plan_meals(user_input, verbose=True)

    print(format_meal_plan_output(final_plan))
    print_iteration_summary(evaluations)


def test_scenario_2_vegetarian():
    """Scenario 2: Vegetarian with limited inventory and tight budget."""
    print("\n" + "🟢" * 35)
    print("SCENARIO 2: Budget Vegetarian Meal Planning")
    print("🟢" * 35)
    print("\nA vegetarian on a tight budget with minimal inventory.")
    print("Needs creative, cost-effective meals.\n")

    user_input = MealPlanInput(
        dietary_preferences=["vegetarian", "high-protein"],
        current_inventory=[
            "lentils",
            "chickpeas",
            "rice",
            "onions",
            "canned tomatoes",
            "olive oil",
            "garlic",
            "cumin",
            "paprika",
        ],
        scheduled_dinners={},
        dietary_restrictions=["no meat", "no fish"],
        budget=35.0,
        cooking_skill="beginner",
    )

    agent = MealPlannerAgent()
    final_plan, evaluations = agent.plan_meals(user_input, verbose=True)

    print(format_meal_plan_output(final_plan))
    print_iteration_summary(evaluations)


def test_scenario_3_restrictions():
    """Scenario 3: Multiple dietary restrictions with good inventory."""
    print("\n" + "🟡" * 35)
    print("SCENARIO 3: Multiple Dietary Restrictions")
    print("🟡" * 35)
    print("\nGluten-free, dairy-free, and nut-free requirements.")
    print("Well-stocked kitchen, advanced cooking skills.\n")

    user_input = MealPlanInput(
        dietary_preferences=["gluten-free", "dairy-free", "high-protein"],
        current_inventory=[
            "salmon",
            "chicken thighs",
            "quinoa",
            "sweet potatoes",
            "broccoli",
            "spinach",
            "eggs",
            "coconut milk",
            "olive oil",
            "garlic",
            "ginger",
            "soy sauce",
            "rice vinegar",
            "sesame oil",
            "avocados",
        ],
        scheduled_dinners={
            "Wednesday": "Dinner with friends (make something impressive)"
        },
        dietary_restrictions=["gluten-free", "dairy-free", "nut-free"],
        budget=80.0,
        cooking_skill="advanced",
    )

    agent = MealPlannerAgent()
    final_plan, evaluations = agent.plan_meals(user_input, verbose=True)

    print(format_meal_plan_output(final_plan))
    print_iteration_summary(evaluations)


def test_scenario_4_minimal_inventory():
    """Scenario 4: Almost empty fridge - tests how agent handles low inventory."""
    print("\n" + "🔴" * 35)
    print("SCENARIO 4: Nearly Empty Kitchen")
    print("🔴" * 35)
    print("\nMinimal inventory - testing inventory optimization edge case.")
    print("Should recognize that buying ingredients is necessary.\n")

    user_input = MealPlanInput(
        dietary_preferences=["quick and easy"],
        current_inventory=[
            "eggs",
            "butter",
            "salt",
            "pepper",
            "olive oil",
        ],
        scheduled_dinners={},
        dietary_restrictions=[],
        budget=50.0,
        cooking_skill="beginner",
    )

    agent = MealPlannerAgent()
    final_plan, evaluations = agent.plan_meals(user_input, verbose=True)

    print(format_meal_plan_output(final_plan))
    print_iteration_summary(evaluations)


def print_iteration_summary(evaluations):
    """Print summary of how scores improved across iterations."""
    print("\n" + "=" * 70)
    print("📈 ITERATION SUMMARY")
    print("=" * 70)

    print(f"\n{'Iteration':<12} {'Inventory':<12} {'Nutrition':<12} {'Practical':<12} {'Cost':<12} {'Preference':<12} {'OVERALL':<12}")
    print("─" * 84)

    for i, eval_score in enumerate(evaluations, 1):
        print(
            f"{i:<12} "
            f"{eval_score.inventory_optimization.score:<12.1f} "
            f"{eval_score.nutritional_variety.score:<12.1f} "
            f"{eval_score.practicality.score:<12.1f} "
            f"{eval_score.cost_efficiency.score:<12.1f} "
            f"{eval_score.preference_alignment.score:<12.1f} "
            f"{eval_score.overall_score:<12.1f}"
        )

    if len(evaluations) > 1:
        improvement = evaluations[-1].overall_score - evaluations[0].overall_score
        print()
        print(f"Total Improvement: {improvement:+.1f} points")

    print()


def main():
    """Run test scenarios."""
    load_dotenv()

    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set.")
        print("\nPlease set your API key:")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        print("\nOr create a .env file with:")
        print("  ANTHROPIC_API_KEY=your-key-here")
        return

    print("=" * 70)
    print("🧪 AGENTIC MEAL PLANNER - TEST SUITE")
    print("=" * 70)
    print("\nThis test suite demonstrates:")
    print("  ✓ Iterative self-evaluation and improvement")
    print("  ✓ Multi-criteria weighted scoring")
    print("  ✓ Inventory optimization (primary goal: 80%+ usage)")
    print("  ✓ Constraint handling (budget, skill level, restrictions)")
    print("  ✓ Quality threshold achievement (target: 85/100)")
    print("\nRunning 4 diverse scenarios...\n")

    # Run all scenarios
    scenarios = [
        ("Scenario 1", test_scenario_1_basic),
        ("Scenario 2", test_scenario_2_vegetarian),
        ("Scenario 3", test_scenario_3_restrictions),
        ("Scenario 4", test_scenario_4_minimal_inventory),
    ]

    # Let user choose which scenarios to run
    print("Which scenarios would you like to run?")
    print("  1. Scenario 1: Basic Family Meal Planning")
    print("  2. Scenario 2: Budget Vegetarian")
    print("  3. Scenario 3: Multiple Dietary Restrictions")
    print("  4. Scenario 4: Nearly Empty Kitchen")
    print("  5. All scenarios")
    print()

    choice = input("Enter your choice (1-5) or press Enter for all: ").strip()

    if choice == "1":
        test_scenario_1_basic()
    elif choice == "2":
        test_scenario_2_vegetarian()
    elif choice == "3":
        test_scenario_3_restrictions()
    elif choice == "4":
        test_scenario_4_minimal_inventory()
    else:
        # Run all scenarios
        for name, scenario_func in scenarios:
            try:
                scenario_func()
            except Exception as e:
                print(f"\n❌ Error in {name}: {str(e)}\n")
                import traceback
                traceback.print_exc()

    print("\n" + "=" * 70)
    print("✅ TEST SUITE COMPLETE")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
