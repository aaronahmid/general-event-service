"""role.py
Module description goes here

Classes
-------
   -- Role class
"""

from django.db import models
from django.contrib.auth.models import Permission
from django.utils.translation import gettext_lazy as _


# class SystemPermission(Permission):
#     """A proxy permission class to allow us control
#     and add to django's built in permissions
#     """

#     class Meta:
#         proxy = True


class Role(models.Model):
    """Data Model for Manager
    ...
    Attributes
    ----------
    name:            char
    system:          ForeignKey

    Methods
    -------
    save:            saves object
    __str__:         Prints the manager's last_name
    """

    name = models.CharField(max_length=45, unique=True, blank=False)
    system = models.CharField(max_length=50, blank=True)
    # permissions = models.ManyToManyField(
    #    SystemPermission,
    #    verbose_name=_("permissions"),
    #    blank=True,
    # )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """change the model save method"""
        system = self.system.name.lower()
        self.name = f"{system.replace(' ', '_')}.{self.name}"
        return super().save(*args, **kwargs)
