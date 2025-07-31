import graphene
from fhir.resources.contactpoint import ContactPoint
from .period import PeriodGQLType


class ContactPointGQLType(graphene.ObjectType):
    """
    GraphQL type for FHIR ContactPoint
    """

    system = graphene.String(
        description="phone | fax | email | pager | url | sms | other"
    )
    value = graphene.String(description="The actual contact point details")
    use = graphene.String(description="home | work | temp | old | mobile")
    rank = graphene.Int(description="Specify preferred order of use")
    period = graphene.Field(
        PeriodGQLType, description="Time period when the contact point was/is in use"
    )

    @classmethod
    def from_fhir(cls, fhir_contact_point: ContactPoint):
        """
        Convert FHIR ContactPoint to GraphQL type
        """
        if not fhir_contact_point:
            return None

        return cls(
            system=fhir_contact_point.system,
            value=fhir_contact_point.value,
            use=fhir_contact_point.use,
            rank=fhir_contact_point.rank,
            period=PeriodGQLType.from_fhir(fhir_contact_point.period)
            if fhir_contact_point.period
            else None,
        )

    def to_fhir(self) -> ContactPoint:
        """
        Convert GraphQL type to FHIR ContactPoint
        """
        data = {"system": self.system, "value": self.value}

        if self.use:
            data["use"] = self.use
        if self.rank is not None:
            data["rank"] = self.rank
        if self.period:
            data["period"] = self.period.to_fhir()

        return ContactPoint(**data)
