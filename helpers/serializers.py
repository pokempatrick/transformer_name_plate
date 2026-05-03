from rest_framework import serializers


class TrackingSerializer(serializers.ModelSerializer):

    """ helper to serialise nested object on the side one-many """
    RootObject = None

    NestedObjects = []

    nested_attributs = []

    root_object = None

    def create(self, validated_data):
        nested_list_of_object_list = []
        for i in range(len(self.nested_attributs)):
            nested_list_of_object_list.append(validated_data.pop(
                self.nested_attributs[i]))
        root_object = self.RootObject.objects.create(**validated_data)
        i = 0
        for nested_object_list in nested_list_of_object_list:
            for nested_object in nested_object_list:
                getattr(root_object, self.nested_attributs[i]).create(
                    **nested_object)
            i += 1
        return root_object

    def update(self, instance, validated_data):
        nested_list_of_object_list = []
        for i in range(len(self.nested_attributs)):
            if self.nested_attributs[i] in validated_data.keys():
                nested_list_of_object_list.append(validated_data.pop(
                    self.nested_attributs[i]))
        super().update(instance, validated_data)
        i = 0
        for nested_objects_list in nested_list_of_object_list:
            nested_objects_with_same_root_object_instance = self.NestedObjects[i].objects.filter(
                **{self.root_object: instance.id}).values_list('id', flat=True)

            if (len(nested_objects_list) == 0):
                getattr(
                    instance, self.nested_attributs[i]).all().delete()

            nested_objects_id_pool = []
            for nested_object in nested_objects_list:
                if "id" in nested_object.keys():
                    if self.NestedObjects[i].objects.filter(id=nested_object['id']).exists():
                        nested_object_instance = self.NestedObjects[i].objects.get(
                            id=nested_object.pop('id'))
                        super().update(nested_object_instance, dict(nested_object))
                        nested_objects_id_pool.append(
                            nested_object_instance.id)
                else:
                    nested_object_instance = getattr(
                        instance, self.nested_attributs[i]).create(**nested_object)
                    nested_objects_id_pool.append(nested_object_instance.id)

                for nested_object_id in nested_objects_with_same_root_object_instance:
                    if nested_object_id not in nested_objects_id_pool:
                        self.NestedObjects[i].objects.filter(
                            pk=nested_object_id).delete()
            i += 1
        return instance

# class NestedObjectsSerilizer(serializers.ModelSerializer):
#     """ helper to serialise nested object on the side many-one """

#     RootObject = None

#     NestedObjects = None

#     nested_attributss = None

#     def create(self, validated_data):
#         for nested_attributs in self.nested_attributss:
#             nested_object = validated_data.pop(nested_attributs)
#             if nested_object!=None and  not "id" in nested_object.keys():
#                 nested_object_created = self.NestedObjects.objects.create(**nested_object)
#             else :
#                 nested_object_created = nested_object
#             validated_data[nested_attributs] = nested_object_created

#         return self.RootObject.objects.create(**validated_data)
