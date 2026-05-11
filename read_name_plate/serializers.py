from rest_framework import serializers


class NamePlateSerializer(serializers.Serializer):

    serial_number = serializers.CharField(required=False)
    power = serializers.IntegerField(required=False)
    nominal_tension = serializers.IntegerField(required=False)
    vendor = serializers.CharField(required=False)
    short_circuit_voltage = serializers.FloatField(required=False)
