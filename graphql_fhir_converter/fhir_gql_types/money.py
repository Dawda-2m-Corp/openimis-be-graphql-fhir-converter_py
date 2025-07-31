import graphene
from fhir.resources.money import Money


class MoneyGQLType(graphene.ObjectType):
    """
    GraphQL type for FHIR Money
    """

    value = graphene.Float(description="Numerical value")
    currency = graphene.String(description="ISO 4217 Currency Code")

    @classmethod
    def from_fhir(cls, fhir_money: Money):
        """
        Convert FHIR Money to GraphQL type
        """
        if not fhir_money:
            return None

        return cls(value=fhir_money.value, currency=fhir_money.currency)

    def to_fhir(self) -> Money:
        """
        Convert GraphQL type to FHIR Money
        """
        data = {"value": self.value}

        if self.currency:
            data["currency"] = self.currency

        return Money(**data)
