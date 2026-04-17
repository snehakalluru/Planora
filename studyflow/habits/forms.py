from django import forms

from .models import Habit, MoodLog


class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ["title", "category", "cue", "why", "target_minutes", "difficulty_level"]
        widgets = {
            "why": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
        self.fields["category"].widget.attrs["class"] = "form-select"
        self.fields["difficulty_level"].widget.attrs["class"] = "form-select"
        self.fields["title"].widget.attrs["placeholder"] = "Example: 30-minute physics recall"
        self.fields["cue"].widget.attrs["placeholder"] = "When the evening study block starts..."
        self.fields["why"].widget.attrs["placeholder"] = "Why this habit matters right now"
        self.fields["target_minutes"].widget.attrs["min"] = 5
        self.fields["difficulty_level"].help_text = "The system can evolve this upward as your streak stabilizes."

    def clean_title(self):
        return self.cleaned_data["title"].strip()

    def clean_target_minutes(self):
        value = self.cleaned_data["target_minutes"]
        if value < 5:
            raise forms.ValidationError("Target minutes should be at least 5.")
        return value


class MoodLogForm(forms.ModelForm):
    class Meta:
        model = MoodLog
        fields = ["mood_score", "energy_score", "stress_score", "note"]
        widgets = {
            "note": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
        self.fields["mood_score"].widget.attrs["class"] = "form-select"
        self.fields["energy_score"].widget.attrs["type"] = "range"
        self.fields["energy_score"].widget.attrs["min"] = 1
        self.fields["energy_score"].widget.attrs["max"] = 5
        self.fields["stress_score"].widget.attrs["type"] = "range"
        self.fields["stress_score"].widget.attrs["min"] = 1
        self.fields["stress_score"].widget.attrs["max"] = 5
        self.fields["note"].widget.attrs["placeholder"] = "What influenced today's energy or focus?"

