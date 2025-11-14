"""
Simple demo script showing how to use the meal planner.

This is a minimal example - see test_planner.py for comprehensive scenarios.
"""
import os
from dotenv import load_dotenv
from models import MealPlanInput
from meal_planner import MealPlannerAgent, format_meal_plan_output


def main():
    """Run a simple meal planning demo."""
    load_dotenv()

    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY not found.")
        print("\nPlease either:")
        print("  1. Create a .env file with: ANTHROPIC_API_KEY=your-key")
        print("  2. Or export it: export ANTHROPIC_API_KEY='your-key'")
        print("\nGet your API key from: https://console.anthropic.com/settings/keys")
        return

    print("=" * 70)
    print("🍽️  MEAL PLANNER DEMO")
    print("=" * 70)
    print("\nGenerating a 7-day meal plan with iterative improvement...\n")

    # Simple example: family with a reasonably stocked kitchen
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
            "eggs",
            "cheese",
            "potatoes",
            "carrots",
        ],
        scheduled_dinners={
            "Friday": "Pizza night (family tradition)"
        },
        dietary_restrictions=[],
        budget=60.0,
        cooking_skill="intermediate",
    )

    # Create agent and generate plan
    agent = MealPlannerAgent()
    final_plan, evaluations = agent.plan_meals(user_input, verbose=True)

    # Display the final plan
    print(format_meal_plan_output(final_plan))

    # Show iteration summary
    print("\n" + "=" * 70)
    print("📈 SCORE PROGRESSION")
    print("=" * 70)
    for i, eval_score in enumerate(evaluations, 1):
        print(f"Iteration {i}: {eval_score.overall_score:.1f}/100")

    if len(evaluations) > 1:
        improvement = evaluations[-1].overall_score - evaluations[0].overall_score
        print(f"\nTotal improvement: {improvement:+.1f} points")

    print("\n✅ Demo complete! See test_planner.py for more scenarios.")


if __name__ == "__main__":
    main()
