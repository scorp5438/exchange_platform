from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):

    message = "Вы можете редактировать только свои объявления"

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user or request.user.is_staff


class IsSenderOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method in ['PATCH', 'PUT']:
            changing_fields = set(request.data.keys())

            if obj.ad_sender.user == request.user:
                allowed_fields = {'ad_sender', 'comment'}
                return changing_fields.issubset(allowed_fields)

            elif obj.ad_receiver.user == request.user:
                return changing_fields == {'status'}

        return False