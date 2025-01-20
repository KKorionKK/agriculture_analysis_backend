from api.common.handler import BaseHandler
from api.schemas.analyze_request import AnalyzeRequestCreate

from api.common.exceptions import ExceptionCodes, CustomHTTPException
from api.schemas.organizations import RestrictionsSchema
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
        schema = AnalyzeRequestCreate(**data)
        if schema.origin_ndvi_data is None and schema.origin_plants_data is None:
            raise CustomHTTPException(ExceptionCodes.NeedData)

        request = await self.pg.analrequests.create_request(schema, self.current_user)

        await self.emitter.send_task(request.id)

        self.write(request.as_schema())


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
