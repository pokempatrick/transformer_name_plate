from rest_framework import response, status
from csv_export.views import CSVExportView


class CreateUpdateMixin:
    # Un mixin est une classe qui ne fonctionne pas de façon autonome
    # Elle permet d'ajouter des fonctionnalités aux classes qui les étendent

    detail_serializer_class = None

    list_serialiser_class = None

    nested_attributs = None

    nested_serialisers = None

    def get_serializer_class(self):
        # Notre mixin détermine quel serializer à utiliser
        # même si elle ne sait pas ce que c'est ni comment l'utiliser
        if hasattr(self, "action") and self.action == 'retrieve' and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        if hasattr(self, "action") and self.action == 'list' and self.list_serialiser_class is not None:
            return self.list_serialiser_class
        return super().get_serializer_class()

    def create(self, request, **kwargs):
        if self.nested_attributs:
            return_value = self.add_nested_object(request)
            if (return_value):
                return return_value
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(added_by=self.request.user, **kwargs)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)

        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, **kwargs):
        object = self.get_object()
        serializer = self.serializer_class(object, data=request.data)
        if serializer.is_valid():
            serializer.save(updated_by=self.request.user, **kwargs)
            return response.Response(serializer.data, status=status.HTTP_200_OK)

        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None, **kwargs):
        object = self.get_object()
        serializer = self.serializer_class(
            object, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=self.request.user, **kwargs)
            return response.Response(serializer.data, status=status.HTTP_200_OK)

        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def add_nested_object(self, request):

        for attribut in self.nested_attributs:
            if attribut in request.data.keys():
                nested_object = request.data[attribut]
                if "id" in nested_object.keys():
                    request.data[attribut] = nested_object["id"]
                else:
                    nested_object_serialiser = self.nested_serialisers[attribut](
                        data=nested_object)
                    if nested_object_serialiser.is_valid():
                        request.data[attribut] = nested_object_serialiser.save().id
                    else:
                        return response.Response(nested_object_serialiser.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomExportCSV(CSVExportView):
    fields = "__all__"
    header = True
    specify_separator = False
    verbose_names = True
    filename = "data-export.csv"
