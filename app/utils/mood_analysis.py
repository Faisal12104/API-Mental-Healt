from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class MoodAnalyzer:
    # Mood scoring system
    MOOD_SCORES = {
        'veryHappy': 10,
        'happy': 8,
        'excited': 9,
        'calm': 7,
        'neutral': 5,
        'sad': 3,
        'verySad': 1,
        'anxious': 2,
        'stressed': 2,
        'angry': 2
    }
    
    POSITIVE_MOODS = ['veryHappy', 'happy', 'excited', 'calm']
    NEGATIVE_MOODS = ['sad', 'verySad', 'anxious', 'stressed', 'angry']
    
    @staticmethod
    def calculate_mood_score(mood: str) -> int:
        return MoodAnalyzer.MOOD_SCORES.get(mood, 5)
    
    @staticmethod
    def analyze_trends(mood_entries: List[Dict]) -> Dict[str, str]:
        """Analyze mood trends over time"""
        if len(mood_entries) < 2:
            return {"mood_trend": "insufficient_data", "energy_trend": "insufficient_data", "sleep_trend": "insufficient_data"}
        
        # Sort by timestamp
        sorted_entries = sorted(mood_entries, key=lambda x: x['timestamp'])
        
        # Calculate trends
        first_half = sorted_entries[:len(sorted_entries)//2]
        second_half = sorted_entries[len(sorted_entries)//2:]
        
        def get_average_mood_score(entries):
            scores = [MoodAnalyzer.calculate_mood_score(entry['mood']) for entry in entries]
            return sum(scores) / len(scores) if scores else 5
        
        def get_average_energy(entries):
            energies = [entry.get('energy_level', 5) for entry in entries if entry.get('energy_level')]
            return sum(energies) / len(energies) if energies else 5
        
        def get_average_sleep(entries):
            sleeps = [entry.get('sleep_hours', 7) for entry in entries if entry.get('sleep_hours')]
            return sum(sleeps) / len(sleeps) if sleeps else 7
        
        first_mood = get_average_mood_score(first_half)
        second_mood = get_average_mood_score(second_half)
        first_energy = get_average_energy(first_half)
        second_energy = get_average_energy(second_half)
        first_sleep = get_average_sleep(first_half)
        second_sleep = get_average_sleep(second_half)
        
        # Determine trends
        mood_trend = "improving" if second_mood > first_mood + 0.5 else "declining" if second_mood < first_mood - 0.5 else "stable"
        energy_trend = "improving" if second_energy > first_energy + 0.5 else "declining" if second_energy < first_energy - 0.5 else "stable"
        sleep_trend = "improving" if second_sleep > first_sleep + 0.5 else "declining" if second_sleep < first_sleep - 0.5 else "stable"
        
        return {
            "mood_trend": mood_trend,
            "energy_trend": energy_trend,
            "sleep_trend": sleep_trend
        }
    
    @staticmethod
    def generate_insights(statistics: Dict, trends: Dict) -> List[str]:
        """Generate personalized insights based on data"""
        insights = []
        
        avg_mood = statistics.get('average_mood_score', 5)
        avg_energy = statistics.get('average_energy', 5)
        avg_sleep = statistics.get('average_sleep', 7)
        positive_days = statistics.get('positive_days', 0)
        total_entries = statistics.get('total_entries', 0)
        
        # Mood insights
        if avg_mood >= 7:
            insights.append("Your overall mood is positive! Keep up the good work!")
        elif avg_mood <= 4:
            insights.append("Consider activities that boost your mood like exercise or socializing.")
        
        # Energy insights
        if avg_energy <= 4:
            insights.append("Low energy levels detected. Try to improve sleep quality and nutrition.")
        elif avg_energy >= 8:
            insights.append("Great energy levels! You're maintaining good habits.")
        
        # Sleep insights
        if avg_sleep < 6:
            insights.append("Sleep duration is below recommended levels. Aim for 7-9 hours.")
        elif avg_sleep > 9:
            insights.append("You're getting plenty of sleep! This is great for mental health.")
        
        # Consistency insights
        if total_entries > 0:
            positive_ratio = positive_days / total_entries
            if positive_ratio >= 0.7:
                insights.append("You're having more positive than negative days. Excellent!")
            elif positive_ratio <= 0.3:
                insights.append("More negative days detected. Consider talking to someone or trying relaxation techniques.")
        
        # Trend-based insights
        if trends.get('mood_trend') == 'improving':
            insights.append("Your mood is improving! Whatever you're doing, it's working!")
        elif trends.get('mood_trend') == 'declining':
            insights.append("Mood trend is declining. Pay attention to triggers and self-care.")
        
        if len(insights) == 0:
            insights.append("Keep tracking your mood to get more personalized insights!")
        
        return insights
    
    @staticmethod
    def analyze_patterns(mood_entries: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in mood data"""
        if len(mood_entries) < 7:
            return {"weekly_pattern": "insufficient_data", "energy_correlation": 0, "sleep_impact": "unknown"}
        
        # Analyze weekly patterns
        weekday_moods = {}
        for entry in mood_entries:
            if isinstance(entry['timestamp'], str):
                try:
                    date_obj = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                except:
                    continue
            else:
                date_obj = entry['timestamp']
            
            weekday = date_obj.strftime('%A')
            mood_score = MoodAnalyzer.calculate_mood_score(entry['mood'])
            
            if weekday not in weekday_moods:
                weekday_moods[weekday] = []
            weekday_moods[weekday].append(mood_score)
        
        # Find best and worst days
        avg_weekday_moods = {day: sum(scores)/len(scores) for day, scores in weekday_moods.items() if scores}
        best_day = max(avg_weekday_moods, key=avg_weekday_moods.get) if avg_weekday_moods else "unknown"
        worst_day = min(avg_weekday_moods, key=avg_weekday_moods.get) if avg_weekday_moods else "unknown"
        
        # Calculate correlations
        valid_entries = [e for e in mood_entries if e.get('energy_level') and e.get('sleep_hours')]
        if len(valid_entries) >= 5:
            energy_scores = [MoodAnalyzer.calculate_mood_score(e['mood']) for e in valid_entries]
            energy_levels = [e['energy_level'] for e in valid_entries]
            sleep_hours = [e['sleep_hours'] for e in valid_entries]
            
            # Simple correlation calculation
            energy_corr = MoodAnalyzer._calculate_correlation(energy_scores, energy_levels)
            sleep_corr = MoodAnalyzer._calculate_correlation(energy_scores, sleep_hours)
        else:
            energy_corr = 0
            sleep_corr = 0
        
        return {
            "weekly_pattern": f"best_{best_day.lower()}_worst_{worst_day.lower()}",
            "energy_correlation": round(energy_corr, 2),
            "sleep_impact": "high" if abs(sleep_corr) > 0.5 else "medium" if abs(sleep_corr) > 0.3 else "low"
        }
    
    @staticmethod
    def _calculate_correlation(x, y):
        """Calculate simple correlation between two lists"""
        if len(x) != len(y) or len(x) < 2:
            return 0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi ** 2 for xi in x)
        sum_y2 = sum(yi ** 2 for yi in y)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5
        
        return numerator / denominator if denominator != 0 else 0