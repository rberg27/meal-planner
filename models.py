"""
Data models for the meal planning system.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class MealPlanInput:
    """Input parameters for meal planning."""

    dietary_preferences: List[str] = field(default_factory=list)
    """Dietary preferences (e.g., 'vegetarian', 'high-protein', 'low-carb')"""

    current_inventory: List[str] = field(default_factory=list)
    """List of ingredients currently available"""

    scheduled_dinners: Dict[str, str] = field(default_factory=dict)
    """Pre-scheduled dinners {day: meal_description}"""

    dietary_restrictions: List[str] = field(default_factory=list)
    """Dietary restrictions (e.g., 'no dairy', 'gluten-free', 'nut allergy')"""

    budget: Optional[float] = None
    """Weekly budget in dollars"""

    cooking_skill: str = "intermediate"
    """Cooking skill level: 'beginner', 'intermediate', 'advanced'"""

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "dietary_preferences": self.dietary_preferences,
            "current_inventory": self.current_inventory,
            "scheduled_dinners": self.scheduled_dinners,
            "dietary_restrictions": self.dietary_restrictions,
            "budget": self.budget,
            "cooking_skill": self.cooking_skill,
        }


@dataclass
class Meal:
    """Represents a single meal."""

    name: str
    ingredients_owned: List[str]
    ingredients_needed: List[str]
    prep_time_minutes: int
    instructions: str
    estimated_cost: float


@dataclass
class MealPlan:
    """Complete 7-day meal plan with metrics."""

    daily_meals: Dict[str, Meal]
    """Meals for each day (Monday-Sunday)"""

    shopping_list: Dict[str, List[str]]
    """Shopping list organized by category"""

    inventory_usage_percent: float
    """Percentage of existing inventory used"""

    variety_score: float
    """Nutritional variety score (0-100)"""

    total_estimated_cost: float
    """Total estimated cost for the week"""

    reasoning: str
    """Explanation of plan choices"""


@dataclass
class CriterionScore:
    """Score for a single evaluation criterion."""

    score: float
    """Score from 0-100"""

    feedback: str
    """Detailed feedback explaining the score"""

    suggestions: List[str] = field(default_factory=list)
    """Specific suggestions for improvement"""


@dataclass
class EvalScore:
    """Multi-criteria evaluation of a meal plan."""

    inventory_optimization: CriterionScore
    """Score for inventory usage (35% weight)"""

    nutritional_variety: CriterionScore
    """Score for nutritional balance and variety (20% weight)"""

    practicality: CriterionScore
    """Score for skill level, prep times, scheduled dinners (20% weight)"""

    cost_efficiency: CriterionScore
    """Score for staying within budget (15% weight)"""

    preference_alignment: CriterionScore
    """Score for matching dietary preferences (10% weight)"""

    overall_score: float
    """Weighted overall score (0-100)"""

    improvement_notes: str
    """Summary of key improvements needed"""

    @staticmethod
    def calculate_weighted_score(scores: Dict[str, CriterionScore]) -> float:
        """Calculate weighted overall score."""
        weights = {
            "inventory_optimization": 0.35,
            "nutritional_variety": 0.20,
            "practicality": 0.20,
            "cost_efficiency": 0.15,
            "preference_alignment": 0.10,
        }

        total = sum(scores[criterion].score * weight
                   for criterion, weight in weights.items())
        return round(total, 2)
