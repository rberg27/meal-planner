"""
Agentic Meal Planning System with Iterative Self-Evaluation.

This module implements a single agent that generates meal plans, evaluates them,
and iteratively improves them until a quality threshold is met.
"""
import json
import os
import re
from typing import Dict, List, Tuple, Optional
from anthropic import Anthropic
from models import MealPlanInput, MealPlan, Meal, EvalScore, CriterionScore


class MealPlannerAgent:
    """
    Single agent that generates and iteratively improves meal plans.

    The agent follows a draft → critique → revise workflow:
    1. Generate initial meal plan optimized for inventory usage
    2. Evaluate plan across 5 weighted criteria
    3. If score below threshold, identify issues and regenerate
    4. Validate improvements and repeat until threshold met or max iterations
    """

    # Configuration
    MODEL = "claude-sonnet-4-20250514"
    QUALITY_THRESHOLD = 85.0  # Stop when overall score >= this
    MAX_ITERATIONS = 3  # Maximum number of improvement iterations

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the meal planner agent.

        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
        """
        self.client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))

    def generate_meal_plan(
        self,
        user_input: MealPlanInput,
        previous_plan: Optional[str] = None,
        previous_eval: Optional[EvalScore] = None,
    ) -> str:
        """
        Generate a meal plan using Claude.

        Args:
            user_input: User preferences and constraints
            previous_plan: Previous plan JSON (for improvements)
            previous_eval: Previous evaluation scores (for targeted improvements)

        Returns:
            JSON string containing the meal plan
        """
        # Build the prompt
        if previous_plan is None:
            # Initial generation
            prompt = self._build_initial_prompt(user_input)
        else:
            # Improvement iteration
            prompt = self._build_improvement_prompt(user_input, previous_plan, previous_eval)

        # Call Claude
        message = self.client.messages.create(
            model=self.MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text
        return self._extract_json(response_text)

    def evaluate_meal_plan(
        self, user_input: MealPlanInput, meal_plan_json: str
    ) -> EvalScore:
        """
        Evaluate a meal plan across multiple criteria.

        Args:
            user_input: Original user input
            meal_plan_json: Generated meal plan as JSON string

        Returns:
            EvalScore with detailed scoring and feedback
        """
        prompt = f"""You are a meal planning expert evaluating a 7-day meal plan.

USER INPUT:
{json.dumps(user_input.to_dict(), indent=2)}

MEAL PLAN:
{meal_plan_json}

Evaluate this meal plan across the following criteria. For each criterion, provide:
- A score from 0-100
- Detailed feedback explaining the score
- Specific, actionable suggestions for improvement

EVALUATION CRITERIA:

1. **Inventory Optimization (35% weight)**: How well does the plan use existing inventory?
   - Target: 80%+ inventory usage
   - Check if ingredients are creatively reused across meals
   - Penalize if good inventory items are ignored

2. **Nutritional Variety (20% weight)**: Is there good nutritional balance and variety?
   - Check protein sources vary (not just chicken every day)
   - Verify vegetables, grains, and food groups are diverse
   - Ensure meals aren't too repetitive

3. **Practicality (20% weight)**: Is the plan realistic for the user's skill level and schedule?
   - Match cooking skill level ({user_input.cooking_skill})
   - Verify scheduled dinners are respected
   - Check prep times are reasonable (not 2+ hours every night)

4. **Cost Efficiency (15% weight)**: Does the plan stay within budget?
   - Budget: ${user_input.budget or "not specified"}
   - Avoid expensive/exotic ingredients if budget is tight
   - Maximize value for money

5. **Preference Alignment (10% weight)**: Does the plan match dietary preferences and restrictions?
   - Preferences: {user_input.dietary_preferences}
   - Restrictions: {user_input.dietary_restrictions}
   - Ensure strict compliance with restrictions

Provide your evaluation in this EXACT JSON format:
```json
{{
  "inventory_optimization": {{
    "score": 85,
    "feedback": "Detailed feedback here...",
    "suggestions": ["Specific suggestion 1", "Specific suggestion 2"]
  }},
  "nutritional_variety": {{
    "score": 70,
    "feedback": "Detailed feedback here...",
    "suggestions": ["Suggestion 1", "Suggestion 2"]
  }},
  "practicality": {{
    "score": 90,
    "feedback": "Detailed feedback here...",
    "suggestions": ["Suggestion 1"]
  }},
  "cost_efficiency": {{
    "score": 80,
    "feedback": "Detailed feedback here...",
    "suggestions": ["Suggestion 1"]
  }},
  "preference_alignment": {{
    "score": 95,
    "feedback": "Detailed feedback here...",
    "suggestions": []
  }},
  "improvement_notes": "Summary of top 3 priorities for improvement..."
}}
```

Be critical and thorough. The goal is to identify real issues, not just validate the plan."""

        message = self.client.messages.create(
            model=self.MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text
        eval_json = self._extract_json(response_text)
        return self._parse_evaluation(eval_json)

    def plan_meals(self, user_input: MealPlanInput, verbose: bool = True) -> Tuple[str, List[EvalScore]]:
        """
        Generate an optimized meal plan with iterative improvement.

        Args:
            user_input: User preferences and constraints
            verbose: Whether to print progress updates

        Returns:
            Tuple of (final_meal_plan_json, list_of_evaluations)
        """
        if verbose:
            print("=" * 70)
            print("🍽️  AGENTIC MEAL PLANNER - Iterative Self-Evaluation")
            print("=" * 70)
            print()

        evaluations = []
        current_plan = None

        for iteration in range(self.MAX_ITERATIONS):
            if verbose:
                print(f"{'─' * 70}")
                print(f"Iteration {iteration + 1}/{self.MAX_ITERATIONS}")
                print(f"{'─' * 70}")

            # Generate plan
            if iteration == 0:
                if verbose:
                    print("📝 Generating initial meal plan...")
                current_plan = self.generate_meal_plan(user_input)
            else:
                if verbose:
                    print(f"🔄 Generating improved plan (targeting: {prev_eval.improvement_notes})...")
                current_plan = self.generate_meal_plan(
                    user_input, current_plan, prev_eval
                )

            # Evaluate plan
            if verbose:
                print("📊 Evaluating meal plan...")
            current_eval = self.evaluate_meal_plan(user_input, current_plan)
            evaluations.append(current_eval)

            # Display scores
            if verbose:
                self._print_evaluation(current_eval, iteration + 1)

            # Check if we've met the threshold
            if current_eval.overall_score >= self.QUALITY_THRESHOLD:
                if verbose:
                    print()
                    print(f"✅ Quality threshold met! ({current_eval.overall_score:.1f} >= {self.QUALITY_THRESHOLD})")
                    print(f"   Final plan achieved after {iteration + 1} iteration(s).")
                break

            # If not the last iteration, prepare for next round
            if iteration < self.MAX_ITERATIONS - 1:
                prev_eval = current_eval
                if verbose:
                    print()
                    print(f"⚠️  Score below threshold ({current_eval.overall_score:.1f} < {self.QUALITY_THRESHOLD})")
                    print(f"   Proceeding to iteration {iteration + 2}...")
                    print()
            else:
                if verbose:
                    print()
                    print(f"⚠️  Max iterations reached. Final score: {current_eval.overall_score:.1f}")

        if verbose:
            print()
            print("=" * 70)
            print("✨ Meal planning complete!")
            print("=" * 70)
            print()

        return current_plan, evaluations

    def _build_initial_prompt(self, user_input: MealPlanInput) -> str:
        """Build prompt for initial meal plan generation."""
        return f"""You are an expert meal planner. Create a 7-day meal plan (Monday-Sunday) that maximizes the use of existing inventory while meeting all user requirements.

USER INPUT:
- Dietary Preferences: {user_input.dietary_preferences or "None specified"}
- Dietary Restrictions: {user_input.dietary_restrictions or "None"}
- Cooking Skill Level: {user_input.cooking_skill}
- Weekly Budget: ${user_input.budget or "Not specified"}
- Current Inventory: {", ".join(user_input.current_inventory) if user_input.current_inventory else "None"}
- Scheduled Dinners: {user_input.scheduled_dinners or "None"}

PRIMARY GOAL: Maximize use of existing inventory (target 80%+ usage). Be creative in reusing ingredients across multiple meals.

REQUIREMENTS:
1. Create exactly 7 dinners (Monday-Sunday)
2. For scheduled dinners, use the user's requested meal
3. Mark each ingredient as either "owned" (from inventory) or "needed" (to buy)
4. Provide realistic prep times and simple instructions
5. Estimate costs for ingredients to buy
6. Ensure nutritional variety across the week
7. Match the user's cooking skill level
8. Respect all dietary restrictions (STRICT - no violations)
9. Align with dietary preferences when possible

Provide your meal plan in this EXACT JSON format:
```json
{{
  "daily_meals": {{
    "Monday": {{
      "name": "Meal Name",
      "ingredients_owned": ["ingredient1", "ingredient2"],
      "ingredients_needed": ["ingredient3"],
      "prep_time_minutes": 30,
      "instructions": "Step by step instructions...",
      "estimated_cost": 5.50
    }},
    ... (continue for all 7 days)
  }},
  "shopping_list": {{
    "Produce": ["item1", "item2"],
    "Proteins": ["item1"],
    "Pantry": ["item1", "item2"],
    "Dairy": ["item1"]
  }},
  "inventory_usage_percent": 85.5,
  "variety_score": 78.0,
  "total_estimated_cost": 45.75,
  "reasoning": "Explanation of your planning decisions, especially how you maximized inventory usage..."
}}
```

Be strategic and creative in using inventory items across multiple meals!"""

    def _build_improvement_prompt(
        self, user_input: MealPlanInput, previous_plan: str, previous_eval: EvalScore
    ) -> str:
        """Build prompt for improving an existing meal plan."""
        return f"""You are an expert meal planner tasked with IMPROVING a previous meal plan based on evaluation feedback.

USER INPUT:
{json.dumps(user_input.to_dict(), indent=2)}

PREVIOUS MEAL PLAN:
{previous_plan}

EVALUATION SCORES:
- Inventory Optimization: {previous_eval.inventory_optimization.score:.1f}/100 (weight: 35%)
  Feedback: {previous_eval.inventory_optimization.feedback}
  Suggestions: {previous_eval.inventory_optimization.suggestions}

- Nutritional Variety: {previous_eval.nutritional_variety.score:.1f}/100 (weight: 20%)
  Feedback: {previous_eval.nutritional_variety.feedback}
  Suggestions: {previous_eval.nutritional_variety.suggestions}

- Practicality: {previous_eval.practicality.score:.1f}/100 (weight: 20%)
  Feedback: {previous_eval.practicality.feedback}
  Suggestions: {previous_eval.practicality.suggestions}

- Cost Efficiency: {previous_eval.cost_efficiency.score:.1f}/100 (weight: 15%)
  Feedback: {previous_eval.cost_efficiency.feedback}
  Suggestions: {previous_eval.cost_efficiency.suggestions}

- Preference Alignment: {previous_eval.preference_alignment.score:.1f}/100 (weight: 10%)
  Feedback: {previous_eval.preference_alignment.feedback}
  Suggestions: {previous_eval.preference_alignment.suggestions}

OVERALL SCORE: {previous_eval.overall_score:.1f}/100 (Target: {self.QUALITY_THRESHOLD})

KEY IMPROVEMENTS NEEDED:
{previous_eval.improvement_notes}

TASK: Generate an IMPROVED meal plan that addresses the feedback above. Focus especially on the lowest-scoring criteria and the specific suggestions provided.

- Keep what's working well from the previous plan
- Make targeted improvements to address the identified issues
- Ensure the new plan is measurably better than the previous one

Provide your IMPROVED meal plan in the same JSON format as before:
```json
{{
  "daily_meals": {{ ... }},
  "shopping_list": {{ ... }},
  "inventory_usage_percent": ...,
  "variety_score": ...,
  "total_estimated_cost": ...,
  "reasoning": "Explain specifically how you addressed the evaluation feedback..."
}}
```"""

    def _extract_json(self, text: str) -> str:
        """Extract JSON from markdown code blocks or raw text."""
        # Try to find JSON in code blocks
        pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            return matches[0]

        # Try to find raw JSON
        pattern = r"\{.*\}"
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            # Return the longest match (likely the complete JSON)
            return max(matches, key=len)

        # If no JSON found, return the original text
        return text

    def _parse_evaluation(self, eval_json: str) -> EvalScore:
        """Parse evaluation JSON into EvalScore object."""
        data = json.loads(eval_json)

        # Create criterion scores
        scores = {
            "inventory_optimization": CriterionScore(
                score=data["inventory_optimization"]["score"],
                feedback=data["inventory_optimization"]["feedback"],
                suggestions=data["inventory_optimization"].get("suggestions", []),
            ),
            "nutritional_variety": CriterionScore(
                score=data["nutritional_variety"]["score"],
                feedback=data["nutritional_variety"]["feedback"],
                suggestions=data["nutritional_variety"].get("suggestions", []),
            ),
            "practicality": CriterionScore(
                score=data["practicality"]["score"],
                feedback=data["practicality"]["feedback"],
                suggestions=data["practicality"].get("suggestions", []),
            ),
            "cost_efficiency": CriterionScore(
                score=data["cost_efficiency"]["score"],
                feedback=data["cost_efficiency"]["feedback"],
                suggestions=data["cost_efficiency"].get("suggestions", []),
            ),
            "preference_alignment": CriterionScore(
                score=data["preference_alignment"]["score"],
                feedback=data["preference_alignment"]["feedback"],
                suggestions=data["preference_alignment"].get("suggestions", []),
            ),
        }

        # Calculate overall score
        overall = EvalScore.calculate_weighted_score(scores)

        return EvalScore(
            inventory_optimization=scores["inventory_optimization"],
            nutritional_variety=scores["nutritional_variety"],
            practicality=scores["practicality"],
            cost_efficiency=scores["cost_efficiency"],
            preference_alignment=scores["preference_alignment"],
            overall_score=overall,
            improvement_notes=data.get("improvement_notes", ""),
        )

    def _print_evaluation(self, eval_score: EvalScore, iteration: int):
        """Pretty print evaluation scores."""
        print()
        print(f"  📊 Evaluation Results (Iteration {iteration}):")
        print(f"  {'─' * 66}")

        criteria = [
            ("Inventory Optimization", eval_score.inventory_optimization, 35),
            ("Nutritional Variety", eval_score.nutritional_variety, 20),
            ("Practicality", eval_score.practicality, 20),
            ("Cost Efficiency", eval_score.cost_efficiency, 15),
            ("Preference Alignment", eval_score.preference_alignment, 10),
        ]

        for name, criterion, weight in criteria:
            bar = self._create_progress_bar(criterion.score)
            print(f"  {name:.<28} {criterion.score:>5.1f}/100 ({weight}%) {bar}")

        print(f"  {'─' * 66}")
        bar = self._create_progress_bar(eval_score.overall_score)
        print(f"  {'OVERALL SCORE':.<28} {eval_score.overall_score:>5.1f}/100      {bar}")
        print()

    def _create_progress_bar(self, score: float, width: int = 20) -> str:
        """Create a text-based progress bar."""
        filled = int((score / 100) * width)
        empty = width - filled

        if score >= 85:
            bar_char = "█"
            color = "🟩"
        elif score >= 70:
            bar_char = "█"
            color = "🟨"
        else:
            bar_char = "█"
            color = "🟥"

        return f"[{bar_char * filled}{' ' * empty}]"


def format_meal_plan_output(meal_plan_json: str) -> str:
    """Format meal plan JSON into human-readable output."""
    plan = json.loads(meal_plan_json)

    output = []
    output.append("\n" + "=" * 70)
    output.append("📅 YOUR 7-DAY MEAL PLAN")
    output.append("=" * 70 + "\n")

    # Daily meals
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for day in days:
        if day not in plan["daily_meals"]:
            continue

        meal = plan["daily_meals"][day]
        output.append(f"▸ {day.upper()}: {meal['name']}")
        output.append(f"  ⏱  Prep time: {meal['prep_time_minutes']} minutes")
        output.append(f"  💰 Cost: ${meal['estimated_cost']:.2f}")

        if meal.get("ingredients_owned"):
            output.append(f"  ✓ Using from inventory: {', '.join(meal['ingredients_owned'])}")
        if meal.get("ingredients_needed"):
            output.append(f"  ○ Need to buy: {', '.join(meal['ingredients_needed'])}")

        output.append(f"  📝 {meal['instructions'][:100]}...")
        output.append("")

    # Shopping list
    output.append("─" * 70)
    output.append("🛒 SHOPPING LIST")
    output.append("─" * 70)
    for category, items in plan["shopping_list"].items():
        if items:
            output.append(f"\n{category}:")
            for item in items:
                output.append(f"  • {item}")

    # Metrics
    output.append("\n" + "─" * 70)
    output.append("📊 PLAN METRICS")
    output.append("─" * 70)
    output.append(f"Inventory Usage: {plan['inventory_usage_percent']:.1f}%")
    output.append(f"Variety Score: {plan['variety_score']:.1f}/100")
    output.append(f"Total Estimated Cost: ${plan['total_estimated_cost']:.2f}")

    # Reasoning
    output.append("\n" + "─" * 70)
    output.append("💡 PLANNING NOTES")
    output.append("─" * 70)
    output.append(plan['reasoning'])
    output.append("")

    return "\n".join(output)
