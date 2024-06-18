from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rockapi.models import Rock, Type
from django.contrib.auth.models import User

class RockView(ViewSet):
    """Rock view set"""


    def create(self, request):
        """Handle POST requests for rocks

        Returns:
            Response: JSON serialized representation of newly created rock
        """

        # Get an object instance of a rock type
        #this is called an ORM .v. this is how we get the data
        # "get" gets a row out of the database
        #() argument is pk=request.data['typeId'] and says get me the row where the PK = this value
        #Django goes to the models directory and finds the type class
        #after all the steps chosen_type = {label:_____}
        chosen_type = Type.objects.get(pk=request.data['typeId'])

        # Create a rock object and assign it property values
        rock = Rock()
        rock.user = request.auth.user
        rock.weight = request.data['weight']
        rock.name = request.data['name']
        rock.type = chosen_type
        rock.save()
        #^ invoking save is the same as the Insert into key word from SQL
        # now its saved^^^

        serialized = RockSerializer(rock, many=False)
        #we are requesting the json format from the server.

        return Response(serialized.data, status=status.HTTP_201_CREATED)
    # this is sent back to the client^ the jason data and the status 


    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single item

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            rock = Rock.objects.get(pk=pk)
            if rock.user.id == request.auth.user.id:
                rock.delete()
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'message': 'You do not own that rock'}, status=status.HTTP_403_FORBIDDEN)


        except Rock.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        # Get query string parameter
        owner_only = self.request.query_params.get("owner", None)

        try:
            # Start with all rows
            rocks = Rock.objects.all()

            # If `?owner=current` is in the URL
            if owner_only is not None and owner_only == "current":
                # Filter to only the current user's rocks
                rocks = rocks.filter(user=request.auth.user)

            serializer = RockSerializer(rocks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)

class RockOwnerSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = User
        fields = ( 'first_name', 'last_name' )

class RockTypeSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = Type
        fields = ( 'label', )


class RockSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    user = RockOwnerSerializer(many=False)
    type = RockTypeSerializer(many=False)

    class Meta:
        model = Rock
        fields = ( 'id', 'name', 'weight', 'user', 'type', )


