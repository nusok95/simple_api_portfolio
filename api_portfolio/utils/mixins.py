from django.utils.dateparse import parse_date
from rest_framework import serializers

class DateValidationMixin:
    def validate_dates(self, date_str):
        errors = {}
        date = None
        if date_str:
            try:
                date = parse_date(date_str)
                if not date:
                    errors['date'] = "Invalid format. Use YYYY-MM-DD."
            except (ValueError, TypeError):
                errors['start_date'] = "Invalid format. Use YYYY-MM-DD."
        
        if errors:
            raise serializers.ValidationError(errors)

        return date
