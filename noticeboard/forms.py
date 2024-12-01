from django import forms

class FeedbackForm(forms.Form):
    comments = forms.CharField(
        label="Your Feedback",
        widget=forms.Textarea(
            attrs={
                "id": "feedbackText",
                "class": "form-control feedback-box",
                "rows": "5",
                "placeholder": "Give your feedback"
            }
        ),
        max_length=1000
    )