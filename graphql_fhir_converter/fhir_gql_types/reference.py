import graphene
from fhir.resources.reference import Reference
from .identifier import IdentifierGQLType


class ReferenceGQLType(graphene.ObjectType):
    """
    GraphQL type for FHIR Reference
    """

    reference = graphene.String(
        description="Literal reference, Relative, internal or absolute URL"
    )
    type = graphene.String(description="Type the reference refers to")
    identifier = graphene.Field(IdentifierGQLType, description="Logical reference")
    display = graphene.String(description="Text alternative for the resource")

    @classmethod
    def from_fhir(cls, fhir_reference: Reference):
        """
        Convert FHIR Reference to GraphQL type
        """
        if not fhir_reference:
            return None

        return cls(
            reference=fhir_reference.reference,
            type=fhir_reference.type,
            identifier=IdentifierGQLType.from_fhir(fhir_reference.identifier)
            if fhir_reference.identifier
            else None,
            display=fhir_reference.display,
        )

    def to_fhir(self) -> Reference:
        """
        Convert GraphQL type to FHIR Reference
        """
        data = {"reference": self.reference}

        if self.type:
            data["type"] = self.type
        if self.identifier:
            data["identifier"] = self.identifier.to_fhir()
        if self.display:
            data["display"] = self.display

        return Reference(**data)
