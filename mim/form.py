from django import forms
from .models import MIM, Comment

class MIMForm(forms.ModelForm):
    class Meta:
        model = MIM
        fields = ['file', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'placeholder': 'description (Optional), max 250 chars', 'rows': 1, 'maxlength': 250}),
        }

    def clean_file(self):
        file = self.cleaned_data['file']
        if file.size > 10*1024*1024:
            raise forms.ValidationError("file size must be < 10MB")
        valid_extensions = ['jpg', 'png', 'gif', 'mp4']
        if not file.name.split('.')[-1].lower() in valid_extensions:
            raise forms.ValidationError("unsupported file extension")
        return file

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={'placeholder': 'Write a comment...', 'class': 'comment-input'}),
        }