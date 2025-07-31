import graphene
from fhir.resources.address import Address
from .period import PeriodGQLType


class AddressGQLType(graphene.ObjectType):
    """
    GraphQL type for FHIR Address
    """

    use = graphene.String(description="home | work | temp | old | billing")
    type = graphene.String(description="postal | physical | both")
    text = graphene.String(description="Text representation of the address")
    line = graphene.List(
        graphene.String, description="Street name, number, direction & P.O. Box etc."
    )
    city = graphene.String(description="Name of city, town etc.")
    district = graphene.String(description="District name")
    state = graphene.String(description="Sub-unit of country")
    postalCode = graphene.String(description="Postal code for area")
    country = graphene.String(description="Country")
    period = graphene.Field(
        PeriodGQLType, description="Time period when address was/is in use"
    )

    @classmethod
    def from_fhir(cls, fhir_address: Address):
        """
        Convert FHIR Address to GraphQL type
        """
        if not fhir_address:
            return None

        return cls(
            use=fhir_address.use,
            type=fhir_address.type,
            text=fhir_address.text,
            line=fhir_address.line,
            city=fhir_address.city,
            district=fhir_address.district,
            state=fhir_address.state,
            postalCode=fhir_address.postalCode,
            country=fhir_address.country,
            period=PeriodGQLType.from_fhir(fhir_address.period)
            if fhir_address.period
            else None,
        )

    def to_fhir(self) -> Address:
        """
        Convert GraphQL type to FHIR Address
        """
        data = {}

        if self.use:
            data["use"] = self.use
        if self.type:
            data["type"] = self.type
        if self.text:
            data["text"] = self.text
        if self.line:
            data["line"] = self.line
        if self.city:
            data["city"] = self.city
        if self.district:
            data["district"] = self.district
        if self.state:
            data["state"] = self.state
        if self.postalCode:
            data["postalCode"] = self.postalCode
        if self.country:
            data["country"] = self.country
        if self.period:
            data["period"] = self.period.to_fhir()

        return Address(**data)
