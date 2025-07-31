import graphene
from fhir.resources.period import Period


class PeriodGQLType(graphene.ObjectType):
    """
    GraphQL type for FHIR Period
    """

    start = graphene.String(description="Starting time with inclusive boundary")
    end = graphene.String(description="End time with inclusive boundary")

    @classmethod
    def from_fhir(cls, fhir_period: Period):
        """
        Convert FHIR Period to GraphQL type
        """
        if not fhir_period:
            return None

        return cls(
            start=fhir_period.start.isoformat() if fhir_period.start else None,
            end=fhir_period.end.isoformat() if fhir_period.end else None,
        )

    def to_fhir(self) -> Period:
        """
        Convert GraphQL type to FHIR Period
        """
        data = {}

        if self.start:
            data["start"] = self.start
        if self.end:
            data["end"] = self.end

        return Period(**data)
