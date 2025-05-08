from api.common.handler import BaseHandler
from api.schemas.analyze_request import AnalyzeRequestCreate

from api.common.exceptions import ExceptionCodes, CustomHTTPException
from api.schemas.organizations import RestrictionsSchema, OrganizationCreateSschema
from api.common.enumerations import Roles


class OrganizationsHandler(BaseHandler):
    async def get(self):
        organizations = (
            await self.pg.organizations.get_users_organizations_and_participants_count(
                self.current_user.id
            )
        )
        self.write(
            {
                "organizations": [
                    organization.as_items_schema() for organization in organizations
                ]
            }
        )

    async def post(self):
        data = self.get_body()
        schema = OrganizationCreateSschema(**data)

        request = await self.pg.organizations.create_organization(schema, self.current_user)

        self.write(request)


class OneOrganizationHandler(BaseHandler):
    async def get(self, organization_id):
        restrictions = RestrictionsSchema(
            edit=await self.check_roles(Roles.admin, organization_id, True),
            delete=await self.check_roles(Roles.owner, organization_id, True),
        )
        organization = await self.pg.organizations.get_organization_details_by_id(
            organization_id
        )
        organization.restrictions = restrictions

        self.write({"organization": organization})

    async def delete(self, field_id):
        await self.pg.fields.delete_field_by_id(field_id, self.current_user.id)
        self.write({"message": "OK"})


class OrganizationInviteHandler(BaseHandler):
    async def post(self, organization_id):
        pass


class OrganizationFieldsHandler(BaseHandler):
    async def get(self, organization_id):
        restrictions = RestrictionsSchema(
            edit=await self.check_roles(Roles.admin, organization_id, True),
            delete=await self.check_roles(Roles.owner, organization_id, True),
        )
        fields = await self.pg.organizations.get_field_by_organization_id(
            organization_id
        )
        # organization.restrictions = restrictions

        self.write({"fields": fields})

    async def delete(self, field_id):
        await self.pg.fields.delete_field_by_id(field_id, self.current_user.id)
        self.write({"message": "OK"})
