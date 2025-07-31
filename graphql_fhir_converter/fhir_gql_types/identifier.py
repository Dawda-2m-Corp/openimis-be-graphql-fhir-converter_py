import graphene
from fhir.resources.identifier import Identifier


class IdentifierGQLType(graphene.ObjectType):
    """
    GraphQL type for FHIR Identifier
    """

    use = graphene.String(description="usual | official | temp | secondary | old")
    type = graphene.JSONString(description="Description of identifier")
    system = graphene.String(description="The namespace for the identifier value")
    value = graphene.String(description="The value that is unique")
    period = graphene.JSONString(description="Time period when id is/was valid for use")
    assigner = graphene.JSONString(description="Organization that issued id")

    @classmethod
    def from_fhir(cls, fhir_identifier):
        """
        Convert FHIR Identifier to GraphQL type
        """
        if not fhir_identifier:
            return None

        return cls(
            use=fhir_identifier.use,
            type=fhir_identifier.type.model_dump() if fhir_identifier.type else None,
            system=fhir_identifier.system,
            value=fhir_identifier.value,
            period=fhir_identifier.period.model_dump()
            if fhir_identifier.period
            else None,
            assigner=fhir_identifier.assigner.model_dump()
            if fhir_identifier.assigner
            else None,
        )

    def to_fhir(self) -> Identifier:
        """
        Convert GraphQL type to FHIR Identifier
        """
        data = {"use": self.use, "system": self.system, "value": self.value}

        if self.type:
            data["type"] = self.type
        if self.period:
            data["period"] = self.period
        if self.assigner:
            data["assigner"] = self.assigner

        return Identifier(**data)
