from rest_framework import serializers


class NamePlateSerializer(serializers.Serializer):

    serial_number = serializers.CharField(required=False)
    power = serializers.CharField(required=False)
    nominal_tension = serializers.CharField(required=False)
    vendor = serializers.CharField(required=False)
    short_circuit_voltage = serializers.CharField(required=False)
