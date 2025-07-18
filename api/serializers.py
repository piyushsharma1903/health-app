from rest_framework import serializers
from .models import MedicalReport
# Serializer for MedicalReport model
class MedicalReportSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = MedicalReport
        fields = '__all__'  # This will include all fields from the MedicalReport model


#class MedicalReportSerializer(serializers.ModelSerializer):
    #class Meta:
        #model = MedicalReport
        #fields = '__all__'
# # This serializer will automatically include all fields from the MedicalReport model
