#
# Copyright 2019 Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

"""Model for permission management."""
from django.db import models
from management.workspace.model import Workspace
from django.core.exceptions import ObjectDoesNotExist

from api.models import TenantAwareModel


class Permission(TenantAwareModel):
    """A Permission."""

    application = models.TextField(null=False)
    resource_type = models.TextField(null=False)
    verb = models.TextField(null=False)
    permission = models.TextField(null=False, unique=True)
    description = models.TextField(default="")
    permissions = models.ManyToManyField("self", symmetrical=False, related_name="requiring_permissions")
    workspace = models.ForeignKey(Workspace, related_name='permissions', on_delete=models.CASCADE, null=True)


    def save(self, *args, **kwargs):
        """Populate the application, resource_type and verb field before saving."""
        context = self.permission.split(":")
        self.application = context[0]
        self.resource_type = context[1]
        self.verb = context[2]
        super(Permission, self).save(*args, **kwargs)

    def change_workspace_to(self, workspace_target_uuid):
        try:
            # Assuming you have a Workspace model with a uuid field and a name field
            target_workspace = Workspace.objects.get(uuid=workspace_target_uuid)

            self.workspace = target_workspace
            self.application = target_workspace.name

            # Update the permission string
            if self.permission:
                parts = self.permission.split(":")
                if len(parts) >= 3:  # Make sure the permission string is in the expected format
                    parts[0] = target_workspace.name  # Replace the workspace name in the permission string
                    self.permission = ":".join(parts)

            # Save the changes
            self.save()
        except ObjectDoesNotExist:
            print(f"No workspace found with uuid {workspace_target_uuid}")
        return self