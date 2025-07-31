import graphene
from fhir.resources.quantity import Quantity


class QuantityGQLType(graphene.ObjectType):
    """
    GraphQL type for FHIR Quantity
    """

    value = graphene.Float(description="Numerical value")
    comparator = graphene.String(
        description="< | <= | >= | > - how to understand the value"
    )
    unit = graphene.String(description="Unit representation")
    system = graphene.String(description="System that defines coded unit form")
    code = graphene.String(description="Coded form of the unit")

    @classmethod
    def from_fhir(cls, fhir_quantity: Quantity):
        """
        Convert FHIR Quantity to GraphQL type
        """
        if not fhir_quantity:
            return None

        return cls(
            value=fhir_quantity.value,
            comparator=fhir_quantity.comparator,
            unit=fhir_quantity.unit,
            system=fhir_quantity.system,
            code=fhir_quantity.code,
        )

    def to_fhir(self) -> Quantity:
        """
        Convert GraphQL type to FHIR Quantity
        """
        data = {"value": self.value}

        if self.comparator:
            data["comparator"] = self.comparator
        if self.unit:
            data["unit"] = self.unit
        if self.system:
            data["system"] = self.system
        if self.code:
            data["code"] = self.code

        return Quantity(**data)
