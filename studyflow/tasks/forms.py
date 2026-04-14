from django import forms

from .models import Task


class TaskForm(forms.ModelForm):
    deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M")
    )
    reminder_time = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
    )

    class Meta:
        model = Task
        fields = ["title", "description", "deadline", "reminder_time", "priority", "status"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
        self.fields["priority"].widget.attrs["class"] = "form-select"
        self.fields["status"].widget.attrs["class"] = "form-select"
        self.fields["title"].widget.attrs["placeholder"] = "Enter task title"
        self.fields["description"].widget.attrs["placeholder"] = "Add notes, study topics, or steps"
        self.fields["reminder_time"].help_text = "Optional. Leave blank to auto-set a reminder 2 hours before the deadline."

        if self.instance and self.instance.pk and self.instance.deadline:
            self.initial["deadline"] = self.instance.deadline.strftime("%Y-%m-%dT%H:%M")
        if self.instance and self.instance.pk and self.instance.reminder_time:
            self.initial["reminder_time"] = self.instance.reminder_time.strftime("%Y-%m-%dT%H:%M")

    def clean_title(self):
        return self.cleaned_data["title"].strip()

    def clean(self):
        cleaned_data = super().clean()
        deadline = cleaned_data.get("deadline")
        reminder_time = cleaned_data.get("reminder_time")

        if reminder_time and deadline and reminder_time > deadline:
            self.add_error("reminder_time", "Reminder time must be before the task deadline.")

        return cleaned_data


class ExamPlannerForm(forms.Form):
    LEVEL_CHOICES = [
        ("Easy", "Easy"),
        ("Medium", "Medium"),
        ("Hard", "Hard"),
    ]

    subject = forms.CharField(max_length=150)
    topics = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}))
    difficulty = forms.ChoiceField(choices=LEVEL_CHOICES)
    file = forms.FileField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "form-control")
            if field_name == "difficulty":
                field.widget.attrs["class"] = "form-select"

        self.fields["subject"].widget.attrs["placeholder"] = "Example: Mathematics"
        self.fields["topics"].widget.attrs["placeholder"] = "Enter topics separated by commas"
        self.fields["file"].widget.attrs["accept"] = "application/pdf"
        self.fields["file"].help_text = "Optional. Upload a PDF to generate a summary from your study material."

    def clean_file(self):
        uploaded_file = self.cleaned_data.get("file")
        if uploaded_file and not uploaded_file.name.lower().endswith(".pdf"):
            raise forms.ValidationError("Only PDF files are allowed.")
        return uploaded_file
