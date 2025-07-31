import graphene
from fhir.resources.humanname import HumanName
from .period import PeriodGQLType


class HumanNameGQLType(graphene.ObjectType):
    """
    GraphQL type for FHIR HumanName
    """

    use = graphene.String(
        description="usual | official | temp | nickname | anonymous | old | maiden"
    )
    text = graphene.String(description="Text representation of the full name")
    family = graphene.String(description="Family name")
    given = graphene.List(graphene.String, description="Given names")
    prefix = graphene.List(
        graphene.String, description="Parts that come before the name"
    )
    suffix = graphene.List(
        graphene.String, description="Parts that come after the name"
    )
    period = graphene.Field(
        PeriodGQLType, description="Time period when name was/is in use"
    )

    @classmethod
    def from_fhir(cls, fhir_human_name: HumanName):
        """
        Convert FHIR HumanName to GraphQL type
        """
        if not fhir_human_name:
            return None

        return cls(
            use=fhir_human_name.use,
            text=fhir_human_name.text,
            family=fhir_human_name.family,
            given=fhir_human_name.given,
            prefix=fhir_human_name.prefix,
            suffix=fhir_human_name.suffix,
            period=PeriodGQLType.from_fhir(fhir_human_name.period)
            if fhir_human_name.period
            else None,
        )

    def to_fhir(self) -> HumanName:
        """
        Convert GraphQL type to FHIR HumanName
        """
        data = {}

        if self.use:
            data["use"] = self.use
        if self.text:
            data["text"] = self.text
        if self.family:
            data["family"] = self.family
        if self.given:
            data["given"] = self.given
        if self.prefix:
            data["prefix"] = self.prefix
        if self.suffix:
            data["suffix"] = self.suffix
        if self.period:
            data["period"] = self.period.to_fhir()

        return HumanName(**data)
